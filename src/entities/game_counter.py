import pygame

from ..utils import GameConfig
from .entity import Entity

class GameCounter(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(config)
        self.y = self.config.window.height - 100
        self.score = 0

    def reset(self) -> None:
        self.score = 0

    def add(self) -> None:
        self.score += 1
        self.config.sounds.point.play()

    @property
    def rect(self) -> pygame.Rect:
        score_digits = [int(x) for x in list(str(self.score))]
        images = [self.config.images.numbers[digit] for digit in score_digits]
        w = sum(image.get_width() for image in images)
        x = (self.config.window.width - w) / 2
        h = max(image.get_height() for image in images)
        return pygame.Rect(x, self.y, w, h)

    def draw(self) -> None:
        """displays score in left of screen"""
        
        score_digits = [int(x) for x in list(str(self.score))]
        images = [self.config.images.numbers[digit] for digit in score_digits]
        digits_width = sum(image.get_width() for image in images)
        x_offset = (self.config.window.width - digits_width) / 2 # place the score in the center of the screen
        x_offset = 10

        for image in images:
            self.config.screen.blit(image, (x_offset, self.y))
            font = pygame.font.Font(None, 36)
            text = font.render("Game", True, (0, 0, 0))
            self.config.screen.blit(text, (x_offset, self.y - 40))
            x_offset += image.get_width()