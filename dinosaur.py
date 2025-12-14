import pygame
import os
from settings import *


class Dinosaur:
    def __init__(self):
        # Estados
        self.is_jumping = False
        self.is_ducking = False
        self.is_running = True
        self.on_ground = True

        # Física
        self.y_velocity = 0
        self.step_index = 0

        # --- AJUSTE VISUAL (Offset) ---
        # Mantenemos el offset para que pise bien el suelo
        self.y_pos_offset = 15

        # --- CARGA Y ESCALADO DE IMÁGENES ---
        def load_img(name, w, h):
            path = os.path.join("sprites", name)
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (w, h))

        # 1. Correr (Running) - AUMENTADO (Antes 44x47)
        # Ahora 48x50 para que se vea más robusto
        self.run_img_1 = load_img("dino_running_1.png", 48, 50)
        self.run_img_2 = load_img("dino_running_2.png", 48, 50)
        self.run_list = [self.run_img_1, self.run_img_2]

        # 2. Saltar (Jumping) - Igual al de correr
        self.jump_img = load_img("dino_jumping.png", 48, 50)

        # 3. Agacharse (Ducking) - REDUCIDO (Antes 59x35)
        # Ahora 55x30 para que no parezca gigante al lado del otro
        self.duck_img_1 = load_img("dino_down_1.png", 57, 32)
        self.duck_img_2 = load_img("dino_down_2.png", 57, 32)
        self.duck_list = [self.duck_img_1, self.duck_img_2]

        # Configuración inicial
        self.image = self.run_list[0]
        self.rect = self.image.get_rect()
        self.rect.x = DINO_X_POS

        # Posición inicial calculada dinámicamente con la altura actual
        self.rect.y = GROUND_Y_POS - self.rect.height + self.y_pos_offset

    def update(self, input_handler):
        # Lógica de Animación
        if self.is_ducking:
            self.animate(self.duck_list)
        elif self.is_jumping:
            self.animate([self.jump_img])
        else:
            self.animate(self.run_list)

        # Lógica de Salto
        if input_handler.is_jump_just_pressed() and self.on_ground:
            self.start_jump()

        # Corte de salto
        if (
            self.is_jumping
            and not input_handler.is_jump_held()
            and self.y_velocity < MIN_JUMP_HEIGHT
        ):
            self.y_velocity = MIN_JUMP_HEIGHT

        # Lógica de Agacharse
        if input_handler.is_duck_held():
            if not self.is_ducking:
                self.start_duck()
            if not self.on_ground:
                self.y_velocity += GRAVITY * 2
        else:
            if self.is_ducking:
                self.end_duck()

        self.apply_physics()

    def animate(self, img_list):
        if len(img_list) > 1:
            self.step_index += 1
            if self.step_index >= 10:
                self.step_index = 0

            frame = 0 if self.step_index < 5 else 1
            self.image = img_list[frame]
        else:
            self.image = img_list[0]

        # Actualizamos el rect
        current_x = self.rect.x
        current_y = self.rect.y
        self.rect = self.image.get_rect()
        self.rect.x = current_x
        self.rect.y = current_y

    def start_jump(self):
        self.is_jumping = True
        self.on_ground = False
        self.y_velocity = JUMP_VELOCITY
        if self.is_ducking:
            self.end_duck()

    def start_duck(self):
        self.is_ducking = True
        # Forzamos la posición Y inmediatamente para evitar saltos visuales
        self.rect.y = GROUND_Y_POS - self.rect.height + self.y_pos_offset

    def end_duck(self):
        self.is_ducking = False
        # Al levantarse, volvemos a calcular la Y basada en la nueva altura (más alta)
        # Esto evita que el dino se hunda en el suelo al crecer
        self.rect.y = GROUND_Y_POS - self.rect.height + self.y_pos_offset

    def apply_physics(self):
        self.y_velocity += GRAVITY
        self.rect.y += self.y_velocity

        # Objetivo Y: El suelo menos la altura del sprite actual + el offset visual
        target_y = GROUND_Y_POS - self.rect.height + self.y_pos_offset

        # Ajuste fino: Cuando se agacha, a veces necesita un empujoncito extra visual
        if self.is_ducking:
            target_y += 5

        if self.rect.y >= target_y:
            self.rect.y = target_y
            self.y_velocity = 0
            self.on_ground = True
            self.is_jumping = False
        else:
            self.on_ground = False

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
