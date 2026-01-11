import arcade
from arcade.gui import UIManager

from config import BG_DIR
from basic.hero import Hero


class BaseLevel(arcade.View):
    def __init__(self, level_number: int, background_name: str):
        super().__init__()
        self.lvl_num = level_number

        try:
            self.background_texture = arcade.load_texture(
                str(BG_DIR / background_name)
            )
        except:
            self.background_texture = None

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        self.player = None

        self.manager = UIManager()
        self.manager.enable()

    def on_show_view(self):
        self.player = Hero(self.window.width, self.window.height)
        self.player_list.append(self.player)

    def on_draw(self):
        self.clear()
        if self.background_texture:
            arcade.draw_texture_rect(
                self.background_texture,
                arcade.rect.XYWH(
                    self.window.width / 2,
                    self.window.height / 2,
                    self.window.width,
                    self.window.height
                )
            )

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
            from views.map_view import MapView
            self.window.show_view(MapView())
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = True
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = True
        elif key in (arcade.key.W, arcade.key.UP):
            self.up_pressed = True
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = False
        elif key in (arcade.key.W, arcade.key.UP):
            self.up_pressed = False
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.down_pressed = False

    def on_hide_view(self):
        self.manager.disable()
