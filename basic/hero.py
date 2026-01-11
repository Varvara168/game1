import arcade
from config import CHAR_DIR


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
