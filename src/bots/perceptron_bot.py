import asyncio
import os
import pickle

import numpy as np
import pygame
from sklearn.linear_model import Perceptron

from src.flappy import Flappy


class PerceptronBot:
    def __init__(self, flappy: Flappy):
        self.flappy = flappy
        self.model = Perceptron(max_iter=1000, tol=1e-3, warm_start=True)
        self.last_features = None
        self.last_decision = None
        self.countInitialErrors = 0

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

    def initializeModel(self):
        # usa o primeiro par de features para inicializar classes
        if not self.trained:
            midpoint = self._get_midpoint_between_pipes()
            features = self._get_distance_to_midpoint(midpoint)
            self.model.partial_fit([features], [0], classes=np.array([0, 1]))
            self.trained = True
            print("Perceptron inicializado com treinamento zero.")

    def verifyInitialErrors(self, features):
        if self.countInitialErrors > 5:
            self.model.partial_fit([features], [0], classes=np.array([0, 1]))
            self.countInitialErrors = 0
            print("Perceptron RESETADO")

    async def start(self):
        print("Iniciando com perceptron")
        last_score = 0

        self.initializeModel()

        while True:
            # Certifique-se que o jogo esteja rodando
            if hasattr(self.flappy, "player") and hasattr(self.flappy, "pipes"):
                midpoint = self._get_midpoint_between_pipes()
                features = self._get_distance_to_midpoint(midpoint)

                self.verifyInitialErrors(features)

                decision = self.model.predict([features])[0]

                if decision:
                    self._flap()

                self.last_features = features
                self.last_decision = decision

                # Se o jogo acabar, treina e reinicia automaticamente
                if (
                    self.flappy.player.collided(
                        self.flappy.pipes, self.flappy.floor
                    )
                    and self.flappy.score.score == 0
                ):
                    self.countInitialErrors += 1
                    if self.flappy.isTraining():
                        correct = int(not self.last_decision)
                        self.update_model(self.last_features, correct)
                    # Reinicia o jogo
                    if self.flappy.isTraining():
                        await asyncio.sleep(0.1)
                    else:
                        await asyncio.sleep(2)
                    self._flap()
                elif last_score < self.flappy.score.score:
                    if self.flappy.isTraining():
                        print("Aprendendo da última ação bem-sucedida")
                        self.update_model(
                            self.last_features, self.last_decision
                        )
                    last_score = self.flappy.score.score

            await asyncio.sleep(0.001)

    def update_model(self, features, correct_decision):
        X = np.array([features])
        y = np.array([correct_decision])

        if not hasattr(self.model, "classes_"):
            self.model.partial_fit(X, y, classes=np.array([0, 1]))
        else:
            self.model.partial_fit(X, y)

        print(self.model.coef_, self.model.intercept_)
        self.save_model()

    def save_model(self):
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)

    def load_model(self):
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)
