import arcade

class Hero(arcade.Sprite):
    def __init__(self):
        # Нужно передать текстуру в родительский конструктор
        super().__init__("character/11.png", scale=0.3)
        
        # Основные характеристики
        self.speed = 300
        self.health = 100
        
        # Центрируем персонажа
        self.center_x = 400
        self.center_y = 200

        # Загрузка текстур для анимации
        self.walk_textures = []
        for i in range(1, 11):
            try:
                texture = arcade.load_texture(f"character/{i}.png")
                self.walk_textures.append(texture)
            except:
                # Заглушка если файл не найден
                texture = arcade.make_soft_square_texture(50, arcade.color.BLUE)
                self.walk_textures.append(texture)
        
        # Первая текстура как idle
        self.idle_texture = self.walk_textures[0] if self.walk_textures else arcade.make_soft_square_texture(50, arcade.color.RED)
        self.texture = self.idle_texture
            
        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1
        self.is_walking = False

    def update_animation(self, delta_time: float = 1/60):
        """ Обновление анимации """
        if self.is_walking:
            self.texture_change_time += delta_time
            if self.texture_change_time >= self.texture_change_delay:
                self.texture_change_time = 0
                self.current_texture += 1
                if self.current_texture >= len(self.walk_textures):
                    self.current_texture = 0
                self.texture = self.walk_textures[self.current_texture]
        else:
            self.texture = self.idle_texture

    def update_movement(self, delta_time, left_pressed, right_pressed, up_pressed, down_pressed):
        """ Перемещение персонажа по клавишам """
        old_x = self.center_x
        old_y = self.center_y
        
        # Сбрасываем флаг движения
        self.is_walking = False
        
        # Движение по клавишам
        if left_pressed:
            self.center_x -= self.speed * delta_time
            self.is_walking = True
        if right_pressed:
            self.center_x += self.speed * delta_time
            self.is_walking = True
        if up_pressed:
            self.center_y += self.speed * delta_time
            self.is_walking = True
        if down_pressed:
            self.center_y -= self.speed * delta_time
            self.is_walking = True
        
        # Ограничение в пределах экрана
        margin = 20
        self.center_x = max(margin, min(800 - margin, self.center_x))
        self.center_y = max(margin, min(600 - margin, self.center_y))
        
        # Обновляем анимацию
        self.update_animation(delta_time)


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.ASH_GREY)
        
        # Флаги нажатых клавиш
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def setup(self):
        # Создаём SpriteList для разных типов объектов
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        
        # Создаём игрока
        self.player = Hero()
        self.player_list.append(self.player)

    def on_draw(self):
        self.clear()
        # Рисуем все списки в правильном порядке
        self.wall_list.draw()
        self.player_list.draw()
        self.bullet_list.draw()
        

    def on_update(self, delta_time):
        # Обновляем движение игрока
        self.player.update_movement(delta_time, 
                                   self.left_pressed, 
                                   self.right_pressed, 
                                   self.up_pressed, 
                                   self.down_pressed)
        
        # Обновляем списки спрайтов
        self.player_list.update()

    def on_key_press(self, key, modifiers):
        """ Обработка нажатия клавиш """
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        """ Обработка отпускания клавиш """
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False

def main():
    game = MyGame(800, 600, "Character Game")
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()