import sqlite3

import arcade
import arcade.gui
from arcade.gui import UIManager, UITextureButton
from arcade.gui.widgets.layout import UIAnchorLayout


def get_value():
    conn = sqlite3.connect('bd/LVL_NUM.db')
    cursor = conn.cursor()
    query = f"SELECT Number FROM LVL"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None


class MapView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = UIManager()
        self.lvl_num = get_value()
        print(self.lvl_num)
        self.background_texture = arcade.load_texture("backgrounds/photo_2026-01-06_21-39-47.jpg")
        self.texture_normal = arcade.load_texture("backgrounds/53a0aa6f-9669-45b4-b76a-3878fc8e7675.png")
        self.texture_hovered = arcade.load_texture("backgrounds/129.png")
        self.texture_block = arcade.load_texture("backgrounds/8c43b195-c8bf-47a0-99d2-d63be80d2c6f.png")

    def on_show_view(self):
        self.manager.enable()
        self.setup_ui()

    def setup_ui(self):
        self.manager.clear()
        r = int(self.lvl_num) - 1
        for i in range(10):
            if i <= r:
                door = UITextureButton(
                    texture=self.texture_normal,
                    texture_hovered=self.texture_hovered,
                    width=130,
                    height=230,
                )

                @door.event("on_click")
                def on_click_start(event):
                    self.window.close()
            else:
                door = UITextureButton(
                    texture=self.texture_block,
                    width=130,
                    height=230,
                )


            if i == 0:
                anchor_layout = UIAnchorLayout()
                anchor_layout.padding = [-100, 290, 300, -1020]
                anchor_layout.add(child=door, anchor_x="center_x", anchor_y="center_y")
                self.manager.add(anchor_layout)
            elif i == 1:
                anchor_layout = UIAnchorLayout()
                anchor_layout.padding = [-45, 400, 200, -233]
                anchor_layout.add(child=door, anchor_x="center_x", anchor_y="center_y")
                self.manager.add(anchor_layout)
            elif i == 2:
                anchor_layout = UIAnchorLayout()
                anchor_layout.padding = [-140, 400, 0, 420]
                anchor_layout.add(child=door, anchor_x="center_x", anchor_y="center_y")
                self.manager.add(anchor_layout)
            elif i == 3:
                anchor_layout = UIAnchorLayout()
                anchor_layout.padding = [-110, 400, 0, 1165]
                anchor_layout.add(child=door, anchor_x="center_x", anchor_y="center_y")
                self.manager.add(anchor_layout)
            elif i == 4:
                anchor_layout = UIAnchorLayout()
                anchor_layout.padding = [-510, 400, 0, 1978]
                anchor_layout.add(child=door, anchor_x="center_x", anchor_y="center_y")
                self.manager.add(anchor_layout)
            elif i == 5:
                anchor_layout = UIAnchorLayout()
                anchor_layout.padding = [730, 400, 0, -1280]
                anchor_layout.add(child=door, anchor_x="center_x", anchor_y="center_y")
                self.manager.add(anchor_layout)
            elif i == 6:
                anchor_layout = UIAnchorLayout()
                anchor_layout.padding = [330, 400, 0, -814]
                anchor_layout.add(child=door, anchor_x="center_x", anchor_y="center_y")
                self.manager.add(anchor_layout)
            elif i == 7:
                anchor_layout = UIAnchorLayout()
                anchor_layout.padding = [550, 400, 0, -310]
                anchor_layout.add(child=door, anchor_x="center_x", anchor_y="center_y")
                self.manager.add(anchor_layout)
            elif i == 8:
                anchor_layout = UIAnchorLayout()
                anchor_layout.padding = [700, 400, 0, 603]
                anchor_layout.add(child=door, anchor_x="center_x", anchor_y="center_y")
                self.manager.add(anchor_layout)
            elif i == 9:
                anchor_layout = UIAnchorLayout()
                anchor_layout.padding = [400, 400, 0, 1370]
                anchor_layout.add(child=door, anchor_x="center_x", anchor_y="center_y")
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
        self.background_texture = arcade.load_texture("backgrounds/photo_2026-01-07_21-47-51.jpg")
        self.texture_normal = arcade.load_texture("backgrounds/125.png")
        self.texture_hovered = arcade.load_texture("backgrounds/126.png")

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
    window = arcade.Window(800, 600, "Game Example", resizable=True, fullscreen=True)
    menu_view = Start()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
