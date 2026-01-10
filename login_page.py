import sqlite3
import arcade
import arcade.gui
from arcade.gui import UIManager, UITextureButton
from arcade.gui.widgets.layout import UIAnchorLayout
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent
BG_DIR = BASE_DIR / "images" / "backgrounds"
CHAR_DIR = BASE_DIR / "character"


def get_value():
    conn = sqlite3.connect(BASE_DIR / "bd" / "LVL_NUM.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Number FROM LVL")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 1



class Hero(arcade.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__(scale=0.3)

        self.speed = 200
        self.center_x = screen_width / 2
        self.center_y = screen_height * 0.1 + 20
        self.facing_right = True

        self.walk_right = [
            arcade.load_texture(str(CHAR_DIR / f"{i}.png"))
            for i in range(1, 11)
        ]
        self.walk_left = [
            arcade.load_texture(str(CHAR_DIR / "влево" / f"{i}.png"))
            for i in range(1, 11)
        ]

        self.texture = self.walk_right[0]
        self.frame = 0
        self.timer = 0

    def update_animation(self, delta_time):
        self.timer += delta_time
        if self.timer > 0.1:
            self.timer = 0
            self.frame = (self.frame + 1) % 10
            self.texture = (
                self.walk_right[self.frame]
                if self.facing_right
                else self.walk_left[self.frame]
            )

    def update(self, delta_time):
        self.update_animation(delta_time)


class BaseLevel(arcade.View):
    def __init__(self, level_number: int, background_name: str):
        super().__init__()
        self.level_number = level_number
        self.background = arcade.load_texture(
            str(BG_DIR / background_name)
        )

        self.left = False
        self.right = False
        self.player = None
        self.player_list = arcade.SpriteList()

    def on_show_view(self):
        self.player = Hero(self.window.width, self.window.height)
        self.player_list.append(self.player)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.rect.XYWH(
                self.window.width / 2,
                self.window.height / 2,
                self.window.width,
                self.window.height
            )
        )
        self.player_list.draw()

    def on_update(self, delta_time):
        if self.left:
            self.player.center_x -= self.player.speed * delta_time
            self.player.facing_right = False
        if self.right:
            self.player.center_x += self.player.speed * delta_time
            self.player.facing_right = True
        self.player_list.update(delta_time)

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.left = True
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right = True
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MapView())

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.left = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right = False


class MapView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = UIManager()
        self.lvl_num = int(get_value())

        self.bg = arcade.load_texture(str(BG_DIR / "photo_2026-01-06_21-39-47.jpg"))
        self.lock_door = arcade.load_texture(str(BG_DIR / "lock_door.png"))
        self.open_door = arcade.load_texture(str(BG_DIR / "open_door.png"))
        self.point_door = arcade.load_texture(str(BG_DIR / "point_door.png"))

    def on_show_view(self):
        self.manager.enable()
        self.manager.clear()

        for i in range(10):
            unlocked = i < self.lvl_num
            texture = self.open_door if unlocked else self.lock_door

            door = UITextureButton(
                texture=texture,
                texture_hovered=self.point_door if unlocked else None,
                width=130,
                height=230,
            )

            if unlocked:
                @door.event("on_click")
                def on_click(event, lvl=i + 1):
                    self.window.show_view(
                        BaseLevel(
                            lvl,
                            "photo_2026-01-06_21-39-45.jpg"
                        )
                    )

            layout = UIAnchorLayout()
            layout.add(door, anchor_x="center_x", anchor_y="center_y")
            self.manager.add(layout)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.bg,
            arcade.rect.XYWH(
                self.window.width / 2,
                self.window.height / 2,
                self.window.width,
                self.window.height
            )
        )
        self.manager.draw()


# ===================== START =====================
class Start(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = UIManager()

        self.bg = arcade.load_texture(
            str(BG_DIR / "photo_2026-01-07_21-47-51.jpg")
        )
        self.btn = arcade.load_texture(str(BG_DIR / "start_button.png"))
        self.btn_hover = arcade.load_texture(str(BG_DIR / "point_start_button.png"))

    def on_show_view(self):
        self.manager.enable()
        self.manager.clear()

        button = UITextureButton(
            texture=self.btn,
            texture_hovered=self.btn_hover,
            width=350,
            height=105,
        )

        @button.event("on_click")
        def start_game(event):
            self.window.show_view(MapView())

        layout = UIAnchorLayout()
        layout.add(button, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(layout)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.bg,
            arcade.rect.XYWH(
                self.window.width / 2,
                self.window.height / 2,
                self.window.width,
                self.window.height
            )
        )
        self.manager.draw()


# ===================== MAIN =====================
def main():
    window = arcade.Window(title="Game", fullscreen=True)
    window.show_view(Start())
    arcade.run()


if __name__ == "__main__":
    main()
