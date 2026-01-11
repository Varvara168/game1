import arcade
from views.start import Start


def main():
    window = arcade.Window(title="Game", fullscreen=True)
    window.show_view(Start())
    arcade.run()


if __name__ == "__main__":
    main()
