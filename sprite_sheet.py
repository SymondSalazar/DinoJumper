import pygame


class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height, scale=0.5):
        """
        Extrae una imagen del sprite sheet y la escala (por defecto al 50%
        para ajustar la versión 2x a nuestras físicas 1x).
        """
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))

        # Escalamos la imagen (ej. de 88px a 44px)
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = pygame.transform.scale(image, (new_width, new_height))

        return image
