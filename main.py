import asyncio

from src.flappy import Flappy
from src.bots.bot import Bot  

async def main():
    flappy = Flappy()
    
    await asyncio.gather(
        flappy.start(), 
        Bot(flappy).start()
    )

if __name__ == "__main__":
    asyncio.run(main())