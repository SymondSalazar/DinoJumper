import pygame


class SpriteSheet:
    def __init__(self, filename: str):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_image(
        self, x: int, y: int, width: int, height: int, scale: float = 0.5
    ) -> pygame.Surface:
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))

        new_width = int(width * scale)
        new_height = int(height * scale)
        image = pygame.transform.scale(image, (new_width, new_height))

        return image
