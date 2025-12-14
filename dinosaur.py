import pygame
import os
from settings import DINO_X_POS, GROUND_Y_POS, GRAVITY, JUMP_VELOCITY, MIN_JUMP_HEIGHT


class Dinosaur:
    def __init__(self):
        self.is_jumping = False
        self.is_ducking = False
        self.is_running = True
        self.on_ground = True

        self.y_velocity = 0
        self.step_index = 0

        self.y_pos_offset = 15

        def load_img(name, w, h):
            path = os.path.join("sprites", name)
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (w, h))

        self.run_img_1 = load_img("dino_running_1.png", 48, 50)
        self.run_img_2 = load_img("dino_running_2.png", 48, 50)
        self.run_list = [self.run_img_1, self.run_img_2]

        self.jump_img = load_img("dino_jumping.png", 48, 50)

        self.duck_img_1 = load_img("dino_down_1.png", 57, 32)
        self.duck_img_2 = load_img("dino_down_2.png", 57, 32)
        self.duck_list = [self.duck_img_1, self.duck_img_2]

        self.image = self.run_list[0]
        self.rect = self.image.get_rect()
        self.rect.x = DINO_X_POS

        self.rect.y = GROUND_Y_POS - self.rect.height + self.y_pos_offset

    def update(self, input_handler) -> None:
        if self.is_ducking:
            self.animate(self.duck_list)
        elif self.is_jumping:
            self.animate([self.jump_img])
        else:
            self.animate(self.run_list)

        if input_handler.is_jump_just_pressed() and self.on_ground:
            self.start_jump()

        if (
            self.is_jumping
            and not input_handler.is_jump_held()
            and self.y_velocity < MIN_JUMP_HEIGHT
        ):
            self.y_velocity = MIN_JUMP_HEIGHT

        if input_handler.is_duck_held():
            if not self.is_ducking:
                self.start_duck()
            if not self.on_ground:
                self.y_velocity += GRAVITY * 2
        else:
            if self.is_ducking:
                self.end_duck()

        self.apply_physics()

    def animate(self, img_list) -> None:
        if len(img_list) > 1:
            self.step_index += 1
            if self.step_index >= 10:
                self.step_index = 0

            frame = 0 if self.step_index < 5 else 1
            self.image = img_list[frame]
        else:
            self.image = img_list[0]

        current_x = self.rect.x
        current_y = self.rect.y
        self.rect = self.image.get_rect()
        self.rect.x = current_x
        self.rect.y = current_y

    def start_jump(self) -> None:
        self.is_jumping = True
        self.on_ground = False
        self.y_velocity = JUMP_VELOCITY
        if self.is_ducking:
            self.end_duck()

    def start_duck(self) -> None:
        self.is_ducking = True
        self.rect.y = GROUND_Y_POS - self.rect.height + self.y_pos_offset

    def end_duck(self) -> None:
        self.is_ducking = False
        self.rect.y = GROUND_Y_POS - self.rect.height + self.y_pos_offset

    def apply_physics(self) -> None:
        self.y_velocity += GRAVITY
        self.rect.y += self.y_velocity

        target_y = GROUND_Y_POS - self.rect.height + self.y_pos_offset

        if self.is_ducking:
            target_y += 5

        if self.rect.y >= target_y:
            self.rect.y = target_y
            self.y_velocity = 0
            self.on_ground = True
            self.is_jumping = False
        else:
            self.on_ground = False

    def draw(self, screen) -> None:
        screen.blit(self.image, (self.rect.x, self.rect.y))
