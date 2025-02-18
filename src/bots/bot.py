import pygame
import asyncio
from src.flappy import Flappy

class Bot:
    flappy: Flappy

    def __init__(self, flappy: Flappy) -> None:
        self.flappy = flappy

    def _flap(self):
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        pygame.event.post(event)

    def _get_next_pipe(self): 
        """Return the next pair of pipes that the player will encounter"""
        player_left_x = self.flappy.player.x - self.flappy.player.w

        for upper_pipe, lower_pipe in zip(self.flappy.pipes.upper, self.flappy.pipes.lower):
            if upper_pipe.rect.left > player_left_x:
                return upper_pipe, lower_pipe
        return None, None    

    def _get_midpoint_between_pipes(self):
        """Return the midpoint between the next pair of pipes"""
        upper_pipe, lower_pipe = self._get_next_pipe()

        return (
            upper_pipe.rect.centerx,  
            (upper_pipe.rect.bottom + lower_pipe.rect.top) // 2  
        )

    def _get_distance_to_midpoint(self, midpoint):  
        """Return the distance between the player and the midpoint of the two pipes"""
        return (midpoint[0] - self.flappy.player.cx, midpoint[1] - self.flappy.player.cy)        

    async def start(self):
        while True:

            midpoint = self._get_midpoint_between_pipes()

            if self.flappy.player.cy > midpoint[1]:
                self._flap()
            
            await asyncio.sleep(0.001)
