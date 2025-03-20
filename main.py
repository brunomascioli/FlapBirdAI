import asyncio

from src.bots.perceptron_bot import PerceptronBot
from src.flappy import Flappy


async def main():
    flappy = Flappy()

    await asyncio.gather(
        flappy.start(), PerceptronBot(flappy, train=True).start()
    )


if __name__ == "__main__":
    asyncio.run(main())
