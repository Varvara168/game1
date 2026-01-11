import arcade
from arcade.gui import UIManager, UITextureButton
from arcade.gui.widgets.layout import UIAnchorLayout

from config import BG_DIR
from views.map_view import MapView


class Start(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = UIManager()
        self.background_texture = arcade.load_texture(str(BG_DIR / "start.jpg"))
        self.texture_normal = arcade.load_texture(str(BG_DIR / "start_button.png"))
        self.texture_hovered = arcade.load_texture(str(BG_DIR / "point_start_button.png"))

    def on_show_view(self):
        self.manager.enable()
        self.manager.clear()

        start_button = UITextureButton(
            texture=self.texture_normal,
            texture_hovered=self.texture_hovered,
            width=350,
            height=105,
        )

        @start_button.event("on_click")
        def on_click_start(event):
            self.window.show_view(MapView())

        anchor = UIAnchorLayout()
        anchor.padding = [390, 400, 0, 400]
        anchor.add(start_button, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background_texture,
            arcade.rect.XYWH(
                self.window.width / 2,
                self.window.height / 2,
                self.window.width,
                self.window.height
            )
        )
        self.manager.draw()
