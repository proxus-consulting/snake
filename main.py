import asyncio
import platform

# Pygbag requires main.py as the entry point
if __name__ == "__main__":
    # Import and run the game
    from snake import Game
    asyncio.run(Game().run())
