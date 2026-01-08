import arcade
import arcade.gui
from arcade.gui import UIManager, UITextureButton
from arcade.gui.widgets.layout import UIAnchorLayout


class MyGame(arcade.Window):
    def __init__(self):
        # Используем фиксированный размер окна для простоты примера,
        # или можно оставить fullscreen=True
        super().__init__(800, 600, "Game Example",  fullscreen=True)

        self.background_texture = None
        self.manager = UIManager()
        self.manager.enable()
        self.setup()

    def setup(self):
        self.background_texture = arcade.load_texture("backgrounds/photo_2026-01-07_21-47-51.jpg")
        texture_normal = arcade.load_texture("backgrounds/125.png")
        texture_hovered = arcade.load_texture("backgrounds/126.png")
        start_button = UITextureButton(
            texture=texture_normal,
            texture_hovered=texture_hovered,
            width=350, 
            height=105,
        )

        @start_button.event("on_click")
        def on_click_start(event):

            self.close()
        anchor_layout = UIAnchorLayout()
        anchor_layout.padding = [390, 400, 0, 400]

        anchor_layout.add(
            child=start_button,
            anchor_x="center_x",
            anchor_y="center_y"
        )
        self.manager.add(anchor_layout)

    def on_draw(self):
        self.clear()
        # Рисуем фон, если он загружен
        if self.background_texture:
            arcade.draw_texture_rect(
                self.background_texture,
                rect=arcade.rect.XYWH(self.width // 2, self.height // 2, self.width, self.height)
            )
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.close()





game = MyGame()
arcade.run()



