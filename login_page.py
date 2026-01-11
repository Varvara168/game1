import sqlite3
import arcade
import arcade.gui
from arcade.gui import UIManager, UITextureButton
from arcade.gui.widgets.layout import UIAnchorLayout
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # абс путь до папки
BG_DIR = BASE_DIR / "images" / "backgrounds"  # абс путь до фонов
CHAR_DIR = BASE_DIR / "images" / "character"  # абс путь до персонажа


# получение кол-во пройденных лвл из бд
def get_value():
    conn = sqlite3.connect(BASE_DIR / "bd" / "LVL_NUM.db")
    cursor = conn.cursor()
    query = f"SELECT Number FROM LVL"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None


# Персонаж
class Hero(arcade.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__(scale=0.3)
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height

        self.FLOOR_Y_PERCENT = 0.1  # Пол на 10% от высоты экрана
        self.MARGIN_X_PERCENT = 0.05  # Отступы по 5% с боков
        self.MARGIN_TOP_PERCENT = 0.9  # Потолок на 90% высоты

        # ФИЗИКА
        self.speed = 200  # Увеличил
        self.jump_speed = 28
        self.gravity = 2
        self.max_fall_speed = -15
        self.on_ground = False
        self.can_jump = True
        self.change_y = 0

        # Центрируем персонажа
        self.center_x = self.SCREEN_WIDTH / 2  # теперь по центру относительно сторон, а не по пикселям
        self.center_y = self.SCREEN_HEIGHT * self.FLOOR_Y_PERCENT + 20

        self.facing_right = True  # True = смотрит вправо, False = влево

        # Загрузка текстур для анимации
        def load_animation(base_path, prefix, frames):

            textures = []

            for i in range(1, frames + 1):
                file_path = base_path / f"{prefix}_{i:02}.png"
                try:
                    t = arcade.load_texture(str(file_path))
                except Exception as e:
                    t = arcade.make_soft_square_texture(50, arcade.color.BLUE)
                textures.append(t)

            return textures

        # ходьба вправо
        self.walk_right_textures = load_animation((CHAR_DIR / "walk" / "right"), "walk", 10)

        # ходьба влево
        self.walk_left_textures = load_animation((CHAR_DIR / "walk" / "left"), "walk", 10)

        # приседание фазы право
        self.crouch_enter_textures = load_animation((CHAR_DIR / "crouch" / "right"), "crouch_enter",
                                                    3)  # crouch_enter_01 - crouch_enter_03: вход в присед

        self.crouch_loop_textures = load_animation((CHAR_DIR / "crouch" / "right"), "crouch_loop",
                                                   3)  # crouch_loop_01 - crouch_loop_03: цикл в приседе

        self.crouch_exit_textures = list(reversed(
            self.crouch_enter_textures))  # crouch_enter_03 - crouch_enter_01: выход из приседа (обратный порядок)

        # приседание фазы лево
        self.crouch_left_enter_textures = load_animation((CHAR_DIR / "crouch" / "left"), "crouch_enter",
                                                         3)  # crouch_enter_01 - crouch_enter_03: вход в присед

        self.crouch_left_loop_textures = load_animation((CHAR_DIR / "crouch" / "left"), "crouch_loop",
                                                        3)  # crouch_loop_01 - crouch_loop_03: цикл в приседе

        self.crouch_left_exit_textures = list(reversed(
            self.crouch_enter_textures))  # crouch_enter_03 - crouch_enter_01: выход из приседа (обратный порядок)

        self.jump_right_textures = load_animation((CHAR_DIR / "jump" / "right"), "jump", 3)

        self.jump_left_textures = load_animation((CHAR_DIR / "jump" / "left"), "jump", 3)

        # Первая текстура как idle
        if self.walk_right_textures:
            self.idle_texture = self.walk_right_textures[0]
        elif self.walk_left_textures:
            self.idle_texture = self.walk_left_textures[0]
        else:
            self.idle_texture = arcade.make_soft_square_texture(50, arcade.color.RED)
        self.texture = self.idle_texture

        # ходьба
        self.texture_walking = 0
        self.walk_timer = 0

        # приседание
        self.crouch_state = "idle"  # "idle", "entering", "looping", "exiting"
        self.texture_crouching = 0
        self.crouch_timer = 0

        # прыжок
        self.texture_jumping = 0
        self.jump_timer = 0

        self.texture_change_delay = 0.1  # общая задержка между сменой текстур

        self.is_walking_right = False
        self.is_crouching = False
        self.is_jumping = False
        self.can_jump = True  # можно ли прыгать

    def update_animation(self, delta_time: float = 1 / 60):
        """Обновление анимации"""

        # прыжок самый высокий приоритет
        if self.is_jumping:
            self.jump_timer += delta_time
            if self.jump_timer >= self.texture_change_delay:
                self.jump_timer = 0
                self.texture_jumping = (self.texture_jumping + 1) % len(self.jump_right_textures)

                # выбираем текстуру в зависимости от направления
                if self.facing_right:
                    self.texture = self.jump_right_textures[self.texture_jumping]
                else:
                    self.texture = self.jump_left_textures[self.texture_jumping]
            return

            # приседание
        elif self.crouch_state != "idle":
            textures_enter = self.crouch_enter_textures if self.facing_right else self.crouch_left_enter_textures
            textures_loop = self.crouch_loop_textures if self.facing_right else self.crouch_left_loop_textures
            textures_exit = self.crouch_exit_textures if self.facing_right else self.crouch_left_exit_textures

            self.crouch_timer += delta_time
            if self.crouch_timer >= self.texture_change_delay:
                self.crouch_timer = 0

                if self.crouch_state == "entering":
                    self.texture_crouching += 1
                    if self.texture_crouching >= len(textures_enter) - 1:
                        self.texture_crouching = len(textures_enter) - 1
                        self.crouch_state = "looping"
                    self.texture = textures_enter[self.texture_crouching]

                elif self.crouch_state == "looping":
                    self.texture_crouching = (self.texture_crouching + 1) % len(textures_loop)
                    self.texture = textures_loop[self.texture_crouching]

                elif self.crouch_state == "exiting":
                    self.texture_crouching += 1
                    if self.texture_crouching >= len(textures_exit) - 1:
                        self.texture_crouching = len(textures_exit) - 1
                        self.crouch_state = "idle"
                        if self.facing_right:
                            self.texture = self.walk_right_textures[
                                0] if self.walk_right_textures else self.idle_texture
                        else:
                            self.texture = self.walk_left_textures[0] if self.walk_left_textures else self.idle_texture
                    else:
                        self.texture = textures_exit[self.texture_crouching]

            return

        # ходьба вправо
        elif self.is_walking_right:
            self.walk_timer += delta_time
            if self.walk_timer >= self.texture_change_delay:
                self.walk_timer = 0
                self.texture_walking += 1
                if self.texture_walking >= len(self.walk_right_textures):
                    self.texture_walking = 0
                self.texture = self.walk_right_textures[self.texture_walking]

        # ходьба влево
        elif self.is_walking_left:
            self.walk_timer += delta_time
            if self.walk_timer >= self.texture_change_delay:
                self.walk_timer = 0
                self.texture_walking += 1
                if self.texture_walking >= len(self.walk_left_textures):
                    self.texture_walking = 0
                self.texture = self.walk_left_textures[self.texture_walking]

        # idle - текстура по направлению
        else:
            if self.facing_right:
                # Смотрим вправо - используем первую текстуру ходьбы вправо
                if self.walk_right_textures:
                    self.texture = self.walk_right_textures[0]
                else:
                    self.texture = self.idle_texture
            else:
                # Смотрим влево - используем первую текстуру ходьбы влево
                if self.walk_left_textures:
                    self.texture = self.walk_left_textures[0]
                else:
                    self.texture = self.idle_texture

            # Сбрасываем счетчики
            self.texture_walking = 0
            self.texture_crouching = 0

    def update_physics(self, delta_time):
        """Обновление физики - плавная версия"""
        # Применяем МАЛЕНЬКУЮ гравитацию
        self.change_y -= self.gravity

        # Ограничиваем МЕДЛЕННУЮ скорость падения
        if self.change_y < self.max_fall_speed:
            self.change_y = self.max_fall_speed

        # Умножаем на delta_time для плавности
        self.center_y += self.change_y * delta_time

        # Проверяем пол
        floor_level = 100
        if self.center_y <= floor_level:
            self.center_y = floor_level
            self.change_y = 0
            self.on_ground = True
            self.is_jumping = False
            self.can_jump = True
        else:
            self.on_ground = False

        # Показываем анимацию прыжка если в воздухе
        if not self.on_ground:
            self.is_jumping = True

    def update_movement(self, delta_time, left_pressed, right_pressed, up_pressed, down_pressed):
        """Перемещение персонажа"""

        # Обновляем физику
        self.update_physics(delta_time)

        # Определяем новое состояние приседа
        currently_crouching = down_pressed

        # Логика переходов между состояниями приседа
        if currently_crouching and not self.is_crouching and self.crouch_state == "idle":
            # Начали приседать
            self.crouch_state = "entering"
            self.crouch_frame = 0

        elif not currently_crouching and self.is_crouching:
            # Перестали приседать - начинаем выход
            if self.crouch_state == "looping":
                self.crouch_state = "exiting"
                self.crouch_frame = 0
            elif self.crouch_state == "entering":
                # Если еще не дошли до конца входа - сразу выходим
                self.crouch_state = "exiting"
                # Начинаем с текущего кадра в обратном порядке
                if self.crouch_frame > 0:
                    self.crouch_frame = len(self.crouch_exit_textures) - self.crouch_frame - 1

        # Сохраняем состояние для следующего кадра
        self.is_crouching = currently_crouching

        # ПРЫЖОК
        if up_pressed and self.on_ground and self.can_jump and not self.is_crouching:
            self.change_y = self.jump_speed
            self.is_jumping = True
            self.on_ground = False
            self.can_jump = False
            self.jump_frame = 0
            self.jump_timer = 0

        # Ходьба
        self.is_walking_right = False
        self.is_walking_left = False
        if left_pressed:
            self.center_x -= self.speed * delta_time
            self.is_walking_left = True
            self.facing_right = False  # влево

        if right_pressed:
            self.center_x += self.speed * delta_time
            self.is_walking_right = True
            self.facing_right = True  # вправо

        # Границы по X
        margin_left = 25
        margin_right = 1900
        self.center_x = max(margin_left, min(margin_right, self.center_x))

        # Граница по Y сверху
        margin_top = 550
        if self.center_y > margin_top:
            self.center_y = margin_top
            self.change_y = min(self.change_y, 0)  # останавливаем движение вверх

        self.update_animation(delta_time)


class BaseLevel(arcade.View):
    def __init__(self, level_number: int, background_name: str):
        super().__init__()
        self.lvl_num = level_number
        print(str(BG_DIR / background_name))

        # Загружаем фон с заглушкой
        try:
            self.background_texture = arcade.load_texture(
                str(BG_DIR / background_name)
            )
        except:
            self.background_texture = None

        # Флаги нажатых клавиш
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # SpriteLists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        self.player = None

        self.manager = UIManager()
        self.manager.enable()

    # ⚠️ setup сохранён, но НЕ обязателен
    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

    def on_show_view(self):
        self.setup_game_elements()

    def setup_game_elements(self):
        self.player = Hero(self.window.width, self.window.height)
        self.player_list.append(self.player)

    def on_draw(self):
        self.clear()

        # Фон
        if self.background_texture:
            arcade.draw_texture_rect(
                texture=self.background_texture,
                rect=arcade.rect.XYWH(
                    self.window.width / 2,
                    self.window.height / 2,
                    self.window.width,
                    self.window.height
                )
            )

        # Объекты
        self.wall_list.draw()
        self.player_list.draw()
        self.bullet_list.draw()

        self.manager.draw()

    def on_update(self, delta_time):
        if self.player:
            self.player.update_movement(
                delta_time,
                self.left_pressed,
                self.right_pressed,
                self.up_pressed,
                self.down_pressed
            )
            self.player_list.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MapView())

        elif key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = False

    def on_resize(self, width, height):
        super().on_resize(width, height)
        if self.player:
            self.player.SCREEN_WIDTH = width
            self.player.SCREEN_HEIGHT = height
            self.player.update_physics(0)



class MapView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = UIManager()
        self.lvl_num = get_value()

        self.background_texture = arcade.load_texture(str(BG_DIR / "map.jpg"))
        self.texture_normal = arcade.load_texture(str(BG_DIR / "open_door.png"))
        self.texture_hovered = arcade.load_texture(str(BG_DIR / "point_door.png"))
        self.texture_block = arcade.load_texture(str(BG_DIR / "lock_door.png"))

    def on_show_view(self):
        self.manager.enable()
        self.setup_ui()

    def setup_ui(self):
        self.manager.clear()
        r = int(self.lvl_num) - 1

        paddings = [
            [-100, 290, 300, -1020],
            [-45,  400, 200, -233],
            [-140, 400,   0,  420],
            [-110, 400,   0, 1165],
            [-510, 400,   0, 1978],
            [730,  400,   0, -1280],
            [330,  400,   0, -814],
            [550,  400,   0, -310],
            [700,  400,   0,  603],
            [400,  400,   0, 1370]
        ]

        for i in range(10):
            if i <= r:
                door = UITextureButton(
                    texture=self.texture_normal,
                    texture_hovered=self.texture_hovered,
                    width=130,
                    height=230,
                )

                door.level_index = i + 1

                @door.event("on_click")
                def on_click_start(event, button=door):
                    game_view = BaseLevel(
                        level_number=button.level_index,
                        background_name=f"level_{button.level_index}.png"
                    )
                    self.window.show_view(game_view)
            else:
                door = UITextureButton(
                    texture=self.texture_block,
                    width=130,
                    height=230,
                )

            anchor_layout = UIAnchorLayout()
            anchor_layout.padding = paddings[i]
            anchor_layout.add(
                child=door,
                anchor_x="center_x",
                anchor_y="center_y"
            )
            self.manager.add(anchor_layout)

    def on_draw(self):
        self.clear()
        if self.background_texture:
            arcade.draw_texture_rect(
                texture=self.background_texture,
                rect=arcade.rect.XYWH(
                    self.window.width / 2,
                    self.window.height / 2,
                    self.window.width,
                    self.window.height
                )
            )
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.close()




class Start(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = UIManager()
        self.background_texture = arcade.load_texture(str(BG_DIR / "start.jpg"))
        self.texture_normal = arcade.load_texture(str(BG_DIR / "start_button.png"))
        self.texture_hovered = arcade.load_texture(str(BG_DIR / "point_start_button.png"))

    def on_show_view(self):
        self.manager.enable()
        self.setup_ui()

    def setup_ui(self):
        self.manager.clear()

        start_button = UITextureButton(
            texture=self.texture_normal,
            texture_hovered=self.texture_hovered,
            width=350,
            height=105,
        )

        @start_button.event("on_click")
        def on_click_start(event):
            map_view = MapView()
            self.window.show_view(map_view)

        anchor_layout = UIAnchorLayout()
        anchor_layout.padding = [390, 400, 0, 400]
        anchor_layout.add(child=start_button, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor_layout)

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        if self.background_texture:
            arcade.draw_texture_rect(
                texture=self.background_texture,
                rect=arcade.rect.XYWH(
                    self.window.width / 2,
                    self.window.height / 2,
                    self.window.width,
                    self.window.height
                )
            )
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.close()


def main():
    window = arcade.Window(title="Game", fullscreen=True)
    window.show_view(Start())
    arcade.run()


if __name__ == "__main__":
    main()
