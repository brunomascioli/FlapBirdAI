import asyncio

from src.bots.perceptron_bot import PerceptronBot
from src.flappy import Flappy


async def main():
    flappy = Flappy(train=True)

    await asyncio.gather(flappy.start(), PerceptronBot(flappy).start())


if __name__ == "__main__":
    asyncio.run(main())
