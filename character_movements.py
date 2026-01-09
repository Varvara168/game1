import arcade

class Hero(arcade.Sprite):
    def __init__(self):
        # Нужно передать текстуру в родительский конструктор
        super().__init__(scale=0.3) # scale=0.3 уменьшает размер спрайта
        
        # Основные характеристики
        self.speed = 100
        self.jump_speed = 25
        self.health = 100 #нужно ли?
        
        # Физика
        self.change_y = 0  # вертикальная скорость
        self.gravity = 2  # сила гравитации
        self.on_ground = False  # стоит ли на земле
        self.max_fall_speed = -10  
        
        # Центрируем персонажа
        self.center_x = 400
        self.center_y = 200

        self.facing_right = True  # True = смотрит вправо, False = влево
        
        # Загрузка текстур для анимации
        #ходьба вправо
        self.walk_right_textures = []
        for i in range(1, 11):
            try:
                texture = arcade.load_texture(f"character/{i}.png")
                self.walk_right_textures.append(texture)
            except:
                # Заглушка если файл не найден
                texture = arcade.make_soft_square_texture(50, arcade.color.BLUE)
                self.walk_right_textures.append(texture)

        #ходьба влево
        self.walk_left_textures = []
        for i in range(1, 11):
            try:
                texture = arcade.load_texture(f"character/влево/{i}.png")
                self.walk_left_textures.append(texture)
            except:
                # Заглушка если файл не найден
                texture = arcade.make_soft_square_texture(50, arcade.color.BLUE)
                self.walk_left_textures.append(texture)

        
        # приседание фазы право
        self.crouch_enter_textures = []  # 11-13: вход в присед
        self.crouch_loop_textures = []   # 14-16: цикл в приседе
        self.crouch_exit_textures = []   # 13-11: выход из приседа (обратный порядок)


        all_crouch_textures = []
        for i in range(11, 17):
            try:
                texture = arcade.load_texture(f"character/{i}.png")
                all_crouch_textures.append(texture)

            except:
                # Заглушка если файл не найден
                texture = arcade.make_soft_square_texture(50, arcade.color.GREEN)
                all_crouch_textures.append(texture)
        
        # Разделяем на фазы
        if len(all_crouch_textures) >= 6:
            self.crouch_enter_textures = all_crouch_textures[0:3]  # 11,12,13
            self.crouch_loop_textures = all_crouch_textures[3:6]   # 14,15,16
            self.crouch_exit_textures = [
                all_crouch_textures[2],  # 13
                all_crouch_textures[1],  # 12
                all_crouch_textures[0]   # 11
            ]  # выход в обратном порядке
        
        # присед влево
        self.crouch_left_textures = []
        for i in range(11, 17):
            try:
                texture = arcade.load_texture(f"character/влево/{i}.png")
                self.crouch_left_textures.append(texture)
            except:
                texture = arcade.make_soft_square_texture(50, arcade.color.GREEN)
                self.crouch_left_textures.append(texture)

        # разделяем присед влево на фазы
        if len(self.crouch_left_textures) >= 6:
            self.crouch_left_enter_textures = self.crouch_left_textures[0:3]
            self.crouch_left_loop_textures = self.crouch_left_textures[3:6]
            self.crouch_left_exit_textures = [
                self.crouch_left_textures[2],
                self.crouch_left_textures[1],
                self.crouch_left_textures[0]
            ]

        # прыжок вправо
        self.jump_right_textures = []
        for i in range(17, 20):
            try:
                texture = arcade.load_texture(f"character/{i}.png")
                self.jump_right_textures.append(texture)
            except:
                texture = arcade.make_soft_square_texture(50, arcade.color.YELLOW)
                self.jump_right_textures.append(texture)

        # прыжок влево
        self.jump_left_textures = []
        for i in range(17, 21):
            try:
                texture = arcade.load_texture(f"character/влево/{i}.png")
                self.jump_left_textures.append(texture)
            except:
                texture = arcade.make_soft_square_texture(50, arcade.color.YELLOW)
                self.jump_left_textures.append(texture)

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
        self.walk_texture_change_delay = 0.1  # Задержка между сменой текстур ходьбы
        
        
        # приседание
        self.crouch_state = "idle"  # "idle", "entering", "looping", "exiting"
        self.texture_crouching = 0
        self.crouch_timer = 0
        self.crouch_texture_change_delay = 0.1  # Задержка между сменой текстур приседания

        # прыжок
        self.texture_jumping = 0
        self.jump_timer = 0
        self.jump_texture_change_delay = 0.1

        self.is_walking_right = False
        self.is_walking_left = False
        self.is_crouching = False
        self.is_jumping = False
        self.can_jump = True  # можно ли прыгать

    def update_animation(self, delta_time: float = 1/60):
        """Обновление анимации"""

        # прыжок самый высокий приоритет
        if self.is_jumping:
            self.jump_timer += delta_time
            if self.jump_timer >= self.jump_texture_change_delay:
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
            if self.crouch_timer >= self.crouch_texture_change_delay:
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
                            self.texture = self.walk_right_textures[0] if self.walk_right_textures else self.idle_texture
                        else:
                            self.texture = self.walk_left_textures[0] if self.walk_left_textures else self.idle_texture
                    else:
                        self.texture = textures_exit[self.texture_crouching]
            
            return
        
        # ходьба вправо
        elif self.is_walking_right:
            self.walk_timer += delta_time
            if self.walk_timer >= self.walk_texture_change_delay:
                self.walk_timer = 0
                self.texture_walking += 1
                if self.texture_walking >= len(self.walk_right_textures):
                    self.texture_walking = 0
                self.texture = self.walk_right_textures[self.texture_walking]
        
        # ходьба влево
        elif self.is_walking_left:
            self.walk_timer += delta_time
            if self.walk_timer >= self.walk_texture_change_delay:
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
            self.facing_right = False #влево

        if right_pressed:
            self.center_x += self.speed * delta_time
            self.is_walking_right = True
            self.facing_right = True #вправо

        # Границы по X
        margin_left = 50
        margin_right = 750
        self.center_x = max(margin_left, min(margin_right, self.center_x))
        
        # Граница по Y сверху
        margin_top = 550
        if self.center_y > margin_top:
            self.center_y = margin_top
            self.change_y = min(self.change_y, 0)  # останавливаем движение вверх

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
        self.player_list = arcade.SpriteList() # Список игроков
        self.wall_list = arcade.SpriteList() # Список стен
        self.bullet_list = arcade.SpriteList() # Список пуль
        
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