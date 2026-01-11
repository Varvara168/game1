import arcade
from arcade.gui import UIManager, UITextureButton
from arcade.gui.widgets.layout import UIAnchorLayout

from config import BG_DIR
from db import get_value
from basic.base_level import BaseLevel


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
            [-45, 400, 200, -233],
            [-140, 400, 0, 420],
            [-110, 400, 0, 1165],
            [-510, 400, 0, 1978],
            [730, 400, 0, -1280],
            [330, 400, 0, -814],
            [550, 400, 0, -310],
            [700, 400, 0, 603],
            [400, 400, 0, 1370]
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
                    self.window.show_view(
                        BaseLevel(
                            level_number=button.level_index,
                            background_name=f"bg.jpg"
                        )
                    )
            else:
                door = UITextureButton(
                    texture=self.texture_block,
                    width=130,
                    height=230,
                )

            anchor = UIAnchorLayout()
            anchor.padding = paddings[i]
            anchor.add(door, anchor_x="center_x", anchor_y="center_y")
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

    def on_hide_view(self):
        self.manager.disable()
