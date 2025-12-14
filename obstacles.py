import pygame
import random
import os
from settings import SCREEN_WIDTH, SPRITE_SHEET_PATH, GROUND_Y_POS
from sprite_sheet import SpriteSheet


class Obstacle:
    def __init__(self, image, speed: float, y_pos: int, type_obj: str):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + 50
        self.rect.y = y_pos
        self.type = type_obj

        self.exact_x = float(self.rect.x)

        self.step_index = 0
        self.images = [image]

    def update(self, speed: float) -> None:
        self.exact_x -= speed
        self.rect.x = int(self.exact_x)

        if self.type == "bird" and len(self.images) > 1:
            self.step_index += 1
            if self.step_index >= 10:
                self.step_index = 0
            frame = 0 if self.step_index < 5 else 1
            self.image = self.images[frame]

    def draw(self, screen) -> None:
        screen.blit(self.image, (self.rect.x, self.rect.y))


class ObstacleManager:
    def __init__(self):
        self.sheet = SpriteSheet(SPRITE_SHEET_PATH)
        self.obstacles = []
        self.ground_offset = 15
        self.last_spawn_time = 0

        def load_bird(name):
            path = os.path.join("sprites", name)
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (46, 40))

        self.bird_images = [
            load_bird("Terodactilo1.png"),
            load_bird("Terodactilo2.png"),
        ]

        self.small_cactus = [
            self.sheet.get_image(446, 2, 34, 70),
            self.sheet.get_image(480, 2, 34, 70),
            self.sheet.get_image(514, 2, 34, 70),
            self.sheet.get_image(548, 2, 34, 70),
            self.sheet.get_image(582, 2, 34, 70),
            self.sheet.get_image(616, 2, 34, 70),
        ]

        self.large_cactus = [
            self.sheet.get_image(652, 2, 50, 100),
            self.sheet.get_image(702, 2, 50, 100),
            self.sheet.get_image(752, 2, 98, 100),
        ]

        self.bird_heights = [270, 220, 160]
        self.distance_to_next_spawn = random.randint(800, 1200)
        self.distance_traveled = 0

    def update(self, current_speed: float, current_score: int) -> None:
        if self.obstacles:
            if self.obstacles[0].rect.right < -100:
                self.obstacles.pop(0)

        for obs in self.obstacles:
            obs.update(current_speed)

        self.distance_traveled += current_speed

        if self.distance_traveled >= self.distance_to_next_spawn:
            self.spawn_obstacle(current_speed, current_score)
            self.distance_traveled = 0
            self.distance_to_next_spawn = self.calculate_next_gap(
                current_speed, current_score
            )

    def calculate_next_gap(self, speed: float, score: int) -> float:
        base_gap = speed * 75
        if score < 150:
            variance = random.randint(400, 900)
        elif score < 500:
            variance = random.randint(250, 600)
        else:
            variance = random.randint(150, 400)
        return base_gap + variance

    def spawn_obstacle(self, speed: float, score: int) -> None:
        final_y_pos = 0

        if score < 150:
            img = random.choice(self.small_cactus)
            final_y_pos = GROUND_Y_POS - img.get_height() + self.ground_offset
            obs = Obstacle(img, speed, final_y_pos, "cactus")
            self.obstacles.append(obs)

        elif score < 450:
            if random.random() < 0.5:
                img = random.choice(self.small_cactus)
                final_y_pos = GROUND_Y_POS - img.get_height() + self.ground_offset
            else:
                img = random.choice(self.large_cactus)
                final_y_pos = GROUND_Y_POS - img.get_height() + self.ground_offset + 5
            obs = Obstacle(img, speed, final_y_pos, "cactus")
            self.obstacles.append(obs)

        else:
            if random.random() < 0.25:
                y_pos = random.choice(self.bird_heights)
                if score < 700 and y_pos == self.bird_heights[0]:
                    y_pos = self.bird_heights[1]

                obs = Obstacle(self.bird_images[0], speed, y_pos, "bird")
                obs.images = self.bird_images
                self.obstacles.append(obs)
            else:
                if random.random() < 0.5:
                    img = random.choice(self.small_cactus)
                    final_y_pos = GROUND_Y_POS - img.get_height() + self.ground_offset
                else:
                    img = random.choice(self.large_cactus)
                    final_y_pos = (
                        GROUND_Y_POS - img.get_height() + self.ground_offset + 5
                    )
                obs = Obstacle(img, speed, final_y_pos, "cactus")
                self.obstacles.append(obs)

    def draw(self, screen) -> None:
        for obs in self.obstacles:
            obs.draw(screen)
