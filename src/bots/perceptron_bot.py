import asyncio
import os
import pickle

import numpy as np
import pygame
from sklearn.linear_model import Perceptron

from src.flappy import Flappy


class PerceptronBot:
    def __init__(self, flappy: Flappy, train: bool = False):
        self.flappy = flappy
        self.model = Perceptron(max_iter=1000, tol=1e-3, warm_start=True)
        self.last_features = None
        self.last_decision = None
        self.train = train

        print("Treinando: ", self.train)

        if os.path.exists(self.model_path):
            self.load_model()
            print("Modelo carregado com sucesso.")
            self.trained = True
        else:
            print("Modelo criado, mas ainda não treinado.")
            self.trained = False

    @property
    def model_path(self):
        return "flappy_model.pkl"

    def _flap(self):
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        pygame.event.post(event)

    def _get_next_pipe(self):
        player_left_x = self.flappy.player.x - self.flappy.player.w

        for upper_pipe, lower_pipe in zip(
            self.flappy.pipes.upper, self.flappy.pipes.lower
        ):
            if upper_pipe.rect.left > player_left_x:
                return upper_pipe, lower_pipe
        return None, None

    def _get_midpoint_between_pipes(self):
        upper_pipe, lower_pipe = self._get_next_pipe()
        return (
            upper_pipe.rect.centerx,
            (upper_pipe.rect.bottom + lower_pipe.rect.top) // 2,
        )

    def _get_distance_to_midpoint(self, midpoint):
        return (
            midpoint[0] - self.flappy.player.cx,
            midpoint[1] - self.flappy.player.cy,
        )

    async def start(self):
        print("Iniciando com perceptron")
        last_score = 0
        while True:
            # Certifique-se que o jogo esteja rodando
            if hasattr(self.flappy, "player") and hasattr(self.flappy, "pipes"):
                midpoint = self._get_midpoint_between_pipes()
                features = self._get_distance_to_midpoint(midpoint)

                if self.trained:
                    decision = self.model.predict([features])[0]
                else:
                    decision = int(features[1] > 0)

                if decision:
                    self._flap()

                self.last_features = features
                self.last_decision = decision

                # Se o jogo acabar, treina e reinicia automaticamente
                if self.flappy.player.collided(
                    self.flappy.pipes, self.flappy.floor
                ):
                    correct_decision = int(not self.last_decision)
                    self.update_model(self.last_features, correct_decision)

                    # Aguarda a reinicialização do jogo automaticamente
                    await asyncio.sleep(1.5)
                    self._flap()
                elif last_score < self.flappy.score.score:
                    if self.train:
                        correct_decision = int(self.last_decision)
                        self.update_model(self.last_features, correct_decision)
                    last_score = self.flappy.score.score

            await asyncio.sleep(0.001)

    def update_model(self, features, correct_decision):
        X = np.array([features])
        y = np.array([correct_decision])

        if not self.trained:
            # Na primeira vez, treine com as duas classes artificialmente
            X_init = np.array(
                [
                    [0, -10],  # Exemplo fictício para classe 1 (pular)
                    [0, 10],  # Exemplo fictício para classe 0 (não pular)
                ]
            )
            y_init = np.array([1, 0])

            # Adiciona o exemplo real obtido no jogo
            X_init = np.vstack([X_init, X])
            y_init = np.append(y_init, y)

            self.model.fit(X_init, y_init)
            self.trained = True
            print("Modelo treinado inicialmente com classes artificiais.")
        else:
            self.model.partial_fit(X, y)

        self.save_model()

    def save_model(self):
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)
        print("Modelo salvo automaticamente.")

    def load_model(self):
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)
