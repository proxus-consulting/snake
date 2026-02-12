import pygame
import random
import sys
import math
import json
import os
import struct
import asyncio

# --- Konstanter ---
CELL_SIZE = 20
GRID_W = 50
GRID_H = 30
SCOREBOARD_H = 50
WINDOW_W = GRID_W * CELL_SIZE
WINDOW_H = GRID_H * CELL_SIZE + SCOREBOARD_H

HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")
MAX_HIGHSCORES = 5
MAX_NAME_LEN = 12

# Sværhedsgrader: (label, start_fps, max_fps, fps_increase_every)
DIFFICULTIES = [
    ("Let", 5, 20, 8),
    ("Normal", 8, 26, 5),
    ("Svær", 12, 32, 3),
    ("Vanvid", 16, 48, 2),
]

# Farver
BLACK = (0, 0, 0)
DARK_GRAY = (25, 25, 25)
GRAY = (40, 40, 40)
LIGHT_GRAY = (120, 120, 120)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (80, 200, 80)
GREEN_DARK = (50, 150, 50)
GREEN_BELLY = (100, 220, 100)
BLUE = (80, 130, 220)
BLUE_DARK = (50, 90, 170)
BLUE_BELLY = (110, 160, 240)
YELLOW = (240, 220, 60)
GOLD = (255, 200, 0)
PURPLE = (180, 60, 220)
CYAN = (60, 220, 220)

# Ruin-farver
# === MAP TEMAER pr. sværhedsgrad ===
# 0=Let(skov), 1=Normal(vildmark), 2=Svær(vulkan), 3=Vanvid(militærbase)
MAP_THEMES = {
    0: {  # SKOV (Let)
        "floor1": (28, 45, 22), "floor2": (34, 52, 26), "floor3": (24, 38, 18),
        "dirt1": (50, 38, 24), "dirt2": (42, 32, 20),
        "detail_col": [(70, 50, 20), (80, 60, 15), (55, 75, 25), (90, 70, 30)],
        "detail_chance": 0.08, "moss_chance": 0.15,
        "moss_r": (40, 25), "moss_g": (70, 30), "moss_b": (30, 15),
        "trunk": (90, 60, 35), "trunk_dark": (65, 42, 22), "trunk_light": (115, 80, 50),
        "canopy": (35, 90, 30), "canopy_light": (55, 120, 45),
        "canopy_dark": (22, 60, 18), "canopy_shadow": (15, 35, 12),
        "ruin_dark": (75, 60, 45), "ruin_med": (95, 78, 58),
        "ruin_light": (115, 95, 72), "ruin_moss": (60, 90, 45),
        "scoreboard": (30, 45, 28),
    },
    1: {  # VILDMARK (Normal)
        "floor1": (55, 48, 30), "floor2": (62, 55, 35), "floor3": (48, 40, 25),
        "dirt1": (70, 55, 32), "dirt2": (58, 45, 28),
        "detail_col": [(80, 70, 40), (65, 55, 30), (90, 80, 50), (50, 60, 30)],
        "detail_chance": 0.10, "moss_chance": 0.10,
        "moss_r": (55, 20), "moss_g": (60, 25), "moss_b": (25, 15),
        "trunk": (70, 50, 30), "trunk_dark": (50, 35, 18), "trunk_light": (95, 70, 45),
        "canopy": (60, 75, 25), "canopy_light": (80, 100, 40),
        "canopy_dark": (40, 50, 15), "canopy_shadow": (25, 35, 10),
        "ruin_dark": (65, 55, 38), "ruin_med": (85, 72, 50),
        "ruin_light": (105, 90, 65), "ruin_moss": (50, 70, 35),
        "scoreboard": (40, 35, 22),
    },
    2: {  # VULKAN (Svær)
        "floor1": (40, 22, 18), "floor2": (50, 28, 20), "floor3": (32, 18, 14),
        "dirt1": (60, 30, 15), "dirt2": (45, 20, 10),
        "detail_col": [(180, 60, 20), (200, 80, 10), (150, 40, 15), (220, 100, 30)],
        "detail_chance": 0.12, "moss_chance": 0.08,
        "moss_r": (80, 40), "moss_g": (25, 15), "moss_b": (10, 10),
        "trunk": (55, 35, 30), "trunk_dark": (35, 20, 18), "trunk_light": (75, 50, 40),
        "canopy": (160, 50, 20), "canopy_light": (220, 100, 30),
        "canopy_dark": (100, 30, 10), "canopy_shadow": (60, 15, 5),
        "ruin_dark": (45, 25, 20), "ruin_med": (65, 35, 25),
        "ruin_light": (85, 50, 35), "ruin_moss": (120, 50, 15),
        "scoreboard": (50, 20, 15),
    },
    3: {  # MILITÆRBASE (Vanvid)
        "floor1": (48, 50, 48), "floor2": (55, 58, 55), "floor3": (40, 42, 40),
        "dirt1": (60, 62, 58), "dirt2": (50, 52, 48),
        "detail_col": [(70, 72, 68), (55, 58, 52), (80, 82, 78), (45, 48, 42)],
        "detail_chance": 0.06, "moss_chance": 0.05,
        "moss_r": (50, 15), "moss_g": (52, 15), "moss_b": (48, 15),
        "trunk": (80, 82, 78), "trunk_dark": (55, 58, 52), "trunk_light": (110, 112, 108),
        "canopy": (60, 75, 55), "canopy_light": (80, 95, 70),
        "canopy_dark": (40, 52, 35), "canopy_shadow": (30, 40, 25),
        "ruin_dark": (55, 58, 52), "ruin_med": (75, 78, 72),
        "ruin_light": (95, 98, 92), "ruin_moss": (50, 65, 45),
        "scoreboard": (35, 40, 35),
    },
}

# Standardfarver (bruges som fallback)
RUIN_DARK = (75, 60, 45)
RUIN_MED = (95, 78, 58)
RUIN_LIGHT = (115, 95, 72)
RUIN_MOSS = (60, 90, 45)

# Skov-farver (fallback)
FOREST_FLOOR_1 = (28, 45, 22)
FOREST_FLOOR_2 = (34, 52, 26)
FOREST_FLOOR_3 = (24, 38, 18)
FOREST_DIRT_1 = (50, 38, 24)
FOREST_DIRT_2 = (42, 32, 20)
TREE_TRUNK = (90, 60, 35)
TREE_TRUNK_DARK = (65, 42, 22)
TREE_TRUNK_LIGHT = (115, 80, 50)
TREE_CANOPY = (35, 90, 30)
TREE_CANOPY_LIGHT = (55, 120, 45)
TREE_CANOPY_DARK = (22, 60, 18)
TREE_CANOPY_SHADOW = (15, 35, 12)

# Retninger
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

FOOD_NORMAL = "normal"
FOOD_BONUS = "bonus"
FOOD_INVINCIBLE = "invincible"
FOOD_MEGA = "mega"          # 100 point - spawner 20 per 10 min
MEGA_FOOD_INTERVAL = 30     # sekunder mellem mega-food spawns (10 min / 20 = 30s)

# Coin / Bullet / Gun
COIN_COLOR = (255, 215, 0)
COIN_COLOR_DARK = (200, 160, 0)
MONEY_BILL_COLOR = (85, 200, 85)  # Grøn pengeseddel
MONEY_BILL_DARK = (60, 140, 60)
MONEY_BILL_VALUE = 10  # Pengesedler giver 10 coins
BULLET_COLOR = (255, 100, 50)
BULLET_SPEED = 2  # celler per game-tick
AMMO_PRICE = 1      # 1 coin = 5 skud
AMMO_AMOUNT = 5     # skud per køb
GUN_BARREL_COLOR = (100, 100, 110)
GUN_BODY_COLOR = (70, 70, 80)

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "savedata.json")

# Kanon-typer: (id, navn, pris, farve)
GUN_NONE = None
GUN_BASIC = "basic"       # Manuel skydning, 1 skud
GUN_AUTO = "auto"         # Automatisk skydning
GUN_QUAD = "quad"         # 4 skud ad gangen
GUN_VACUUM = "vacuum"     # Støvsuger - suger mad til sig
GUN_TYPES = [
    (GUN_BASIC, "Kanon", 10, GUN_BARREL_COLOR),
    (GUN_AUTO, "Auto-Kanon", 15, (120, 180, 120)),
    (GUN_QUAD, "Quad-Kanon", 25, (180, 100, 100)),
    (GUN_VACUUM, "Støvsuger", 50, (100, 60, 180)),
]
GUN_INFO = {g[0]: g for g in GUN_TYPES}
AUTO_SHOOT_INTERVAL = 4  # auto-kanon skyder hvert N. tick
VACUUM_INTERVAL = 12      # støvsuger suger hvert N. tick (langsom forbrug)
VACUUM_RANGE = 10         # rækkevidde i celler
POWER_PRICE = 5           # 5 coins for 7 strøm
POWER_AMOUNT = 7

# Slange-typer (20 stk)
SNAKE_NORMAL = "normal"
SNAKE_DOG = "dog"
SNAKE_TANK = "tank"
SNAKE_CAT = "cat"
SNAKE_DRAGON = "dragon"
SNAKE_ROBOT = "robot"
SNAKE_SHARK = "shark"
SNAKE_FIRE = "fire"
SNAKE_ICE = "ice"
SNAKE_RAINBOW = "rainbow"
SNAKE_ZOMBIE = "zombie"
SNAKE_NINJA = "ninja"
SNAKE_PIRATE = "pirate"
SNAKE_ALIEN = "alien"
SNAKE_CANDY = "candy"
SNAKE_GOLD = "gold"
SNAKE_SKELETON = "skeleton"
SNAKE_LAVA = "lava"
SNAKE_ELECTRIC = "electric"
SNAKE_DIAMOND = "diamond"

SNAKE_TYPES_LIST = [
    SNAKE_NORMAL, SNAKE_DOG, SNAKE_TANK, SNAKE_CAT, SNAKE_DRAGON,
    SNAKE_ROBOT, SNAKE_SHARK, SNAKE_FIRE, SNAKE_ICE, SNAKE_RAINBOW,
    SNAKE_ZOMBIE, SNAKE_NINJA, SNAKE_PIRATE, SNAKE_ALIEN, SNAKE_CANDY,
    SNAKE_GOLD, SNAKE_SKELETON, SNAKE_LAVA, SNAKE_ELECTRIC, SNAKE_DIAMOND,
]
SNAKE_TYPE_NAMES = {
    SNAKE_NORMAL: "Normal", SNAKE_DOG: "Hund", SNAKE_TANK: "Tank",
    SNAKE_CAT: "Kat", SNAKE_DRAGON: "Drage", SNAKE_ROBOT: "Robot",
    SNAKE_SHARK: "Hai", SNAKE_FIRE: "Ild", SNAKE_ICE: "Is",
    SNAKE_RAINBOW: "Regnbue", SNAKE_ZOMBIE: "Zombie", SNAKE_NINJA: "Ninja",
    SNAKE_PIRATE: "Pirat", SNAKE_ALIEN: "Alien", SNAKE_CANDY: "Slik",
    SNAKE_GOLD: "Guld", SNAKE_SKELETON: "Skelet", SNAKE_LAVA: "Lava",
    SNAKE_ELECTRIC: "Elektrisk", SNAKE_DIAMOND: "Diamant",
}

# Square-head types
SQUARE_HEAD_TYPES = (SNAKE_TANK, SNAKE_ROBOT)

# Farver per (slange-type, spiller-idx): (main, dark, belly)
SNAKE_TYPE_COLORS = {
    SNAKE_NORMAL: {
        0: ((80, 200, 80), (50, 150, 50), (100, 220, 100)),
        1: ((80, 130, 220), (50, 90, 170), (110, 160, 240)),
    },
    SNAKE_DOG: {
        0: ((180, 130, 70), (140, 95, 45), (210, 170, 100)),
        1: ((200, 150, 90), (160, 110, 55), (230, 180, 120)),
    },
    SNAKE_TANK: {
        0: ((100, 120, 80), (70, 85, 55), (130, 150, 110)),
        1: ((90, 100, 120), (65, 75, 95), (120, 130, 150)),
    },
    SNAKE_CAT: {
        0: ((180, 140, 180), (140, 100, 140), (210, 175, 210)),
        1: ((200, 170, 130), (160, 130, 90), (230, 200, 165)),
    },
    SNAKE_DRAGON: {
        0: ((180, 50, 50), (130, 30, 30), (210, 80, 60)),
        1: ((50, 100, 180), (30, 70, 130), (80, 130, 210)),
    },
    SNAKE_ROBOT: {
        0: ((160, 165, 175), (110, 115, 125), (190, 195, 205)),
        1: ((175, 160, 140), (125, 110, 95), (205, 190, 175)),
    },
    SNAKE_SHARK: {
        0: ((100, 115, 135), (70, 80, 100), (145, 160, 180)),
        1: ((120, 105, 135), (85, 70, 100), (155, 140, 175)),
    },
    SNAKE_FIRE: {
        0: ((230, 120, 30), (180, 80, 15), (255, 170, 60)),
        1: ((230, 50, 30), (180, 30, 15), (255, 90, 60)),
    },
    SNAKE_ICE: {
        0: ((140, 195, 235), (95, 155, 205), (185, 220, 250)),
        1: ((175, 215, 235), (135, 180, 205), (210, 238, 250)),
    },
    SNAKE_RAINBOW: {
        0: ((255, 100, 100), (200, 60, 60), (255, 150, 150)),
        1: ((100, 100, 255), (60, 60, 200), (150, 150, 255)),
    },
    SNAKE_ZOMBIE: {
        0: ((115, 140, 85), (78, 100, 55), (148, 170, 112)),
        1: ((130, 115, 140), (90, 78, 100), (162, 148, 170)),
    },
    SNAKE_NINJA: {
        0: ((50, 40, 65), (30, 22, 42), (78, 65, 90)),
        1: ((40, 50, 65), (22, 30, 42), (65, 78, 90)),
    },
    SNAKE_PIRATE: {
        0: ((140, 80, 48), (100, 52, 28), (178, 112, 75)),
        1: ((150, 58, 48), (108, 35, 28), (188, 88, 75)),
    },
    SNAKE_ALIEN: {
        0: ((70, 220, 95), (42, 170, 62), (110, 248, 135)),
        1: ((95, 175, 220), (62, 135, 170), (135, 208, 248)),
    },
    SNAKE_CANDY: {
        0: ((238, 135, 178), (198, 98, 138), (255, 178, 208)),
        1: ((135, 198, 238), (98, 158, 198), (178, 228, 255)),
    },
    SNAKE_GOLD: {
        0: ((218, 178, 48), (178, 138, 28), (248, 208, 78)),
        1: ((198, 198, 208), (158, 158, 168), (228, 228, 238)),
    },
    SNAKE_SKELETON: {
        0: ((218, 212, 198), (168, 162, 148), (238, 232, 222)),
        1: ((198, 208, 218), (148, 158, 168), (222, 232, 238)),
    },
    SNAKE_LAVA: {
        0: ((78, 38, 28), (48, 22, 14), (118, 58, 38)),
        1: ((58, 38, 48), (34, 22, 28), (88, 58, 68)),
    },
    SNAKE_ELECTRIC: {
        0: ((238, 218, 58), (198, 178, 38), (255, 238, 98)),
        1: ((58, 178, 238), (38, 138, 198), (98, 208, 255)),
    },
    SNAKE_DIAMOND: {
        0: ((158, 218, 238), (118, 178, 208), (198, 238, 252)),
        1: ((218, 158, 218), (178, 118, 178), (238, 198, 238)),
    },
}

# --- Ruin-layouts (relative positioner fra anker) ---
RUIN_TEMPLATES = [
    # L-form
    [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2)],
    # Omvendt L
    [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
    # Lille kvadrat
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    # Vandret mur
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    # Lodret mur
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    # T-form
    [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],
    # Kryds
    [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
    # S-form
    [(1, 0), (2, 0), (0, 1), (1, 1), (0, 2)],
    # Lille prik-klump
    [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)],
]

# Antal ruiner per sværhedsgrad (mere skov = flere ruiner)
RUIN_COUNTS = [4, 6, 9, 13]

# Antal dekorative træer per sværhedsgrad
TREE_COUNTS = [8, 12, 16, 20]


def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_highscores(data):
    with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_highscore_list(data, difficulty_idx, num_players):
    key = f"{num_players}p_{difficulty_idx}"
    return data.get(key, [])


def add_highscore(data, difficulty_idx, num_players, name, score):
    key = f"{num_players}p_{difficulty_idx}"
    entries = data.get(key, [])
    entries.append({"name": name, "score": score})
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:MAX_HIGHSCORES]
    data[key] = entries
    save_highscores(data)
    for i, e in enumerate(entries):
        if e["name"] == name and e["score"] == score:
            return i
    return None


def is_highscore(data, difficulty_idx, num_players, score):
    if score <= 0:
        return False
    entries = get_highscore_list(data, difficulty_idx, num_players)
    if len(entries) < MAX_HIGHSCORES:
        return True
    return score > entries[-1]["score"]


def load_savedata():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_savedata(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_ruins(count, safe_zones):
    """Generer tilfældige ruiner på banen. safe_zones er et set af positioner der skal holdes fri."""
    ruin_cells = set()
    attempts = 0
    placed = 0
    while placed < count and attempts < count * 20:
        attempts += 1
        template = random.choice(RUIN_TEMPLATES)
        # Tilfældig rotation (0, 90, 180, 270)
        rot = random.randint(0, 3)
        rotated = template
        for _ in range(rot):
            rotated = [(-y, x) for x, y in rotated]
        # Tilfældig offset
        min_x = min(x for x, y in rotated)
        min_y = min(y for x, y in rotated)
        max_x = max(x for x, y in rotated)
        max_y = max(y for x, y in rotated)
        ox = random.randint(2 - min_x, GRID_W - 3 - max_x)
        oy = random.randint(2 - min_y, GRID_H - 3 - max_y)
        cells = [(x + ox, y + oy) for x, y in rotated]
        # Tjek at alle celler er ledige
        valid = True
        for cx, cy in cells:
            if cx < 1 or cx >= GRID_W - 1 or cy < 1 or cy >= GRID_H - 1:
                valid = False
                break
            if (cx, cy) in ruin_cells or (cx, cy) in safe_zones:
                valid = False
                break
            # Hold afstand til andre ruiner
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if (cx + dx, cy + dy) in ruin_cells:
                        valid = False
                        break
                if not valid:
                    break
        if valid:
            for c in cells:
                ruin_cells.add(c)
            placed += 1
    return ruin_cells


def generate_trees(count, occupied):
    """Generer tilfældige dekorative træ-positioner (grid-celler). Undgår occuperede celler."""
    trees = []
    attempts = 0
    while len(trees) < count and attempts < count * 30:
        attempts += 1
        tx = random.randint(1, GRID_W - 2)
        ty = random.randint(1, GRID_H - 2)
        if (tx, ty) in occupied:
            continue
        # Hold afstand til andre træer (min 2 celler)
        too_close = False
        for ex, ey in trees:
            if abs(tx - ex) <= 2 and abs(ty - ey) <= 2:
                too_close = True
                break
        if not too_close:
            trees.append((tx, ty))
            occupied.add((tx, ty))
    return trees


def draw_map_floor(surface, difficulty=0):
    """Tegn gulv baseret på map-tema (skov/vildmark/vulkan/militærbase)."""
    theme = MAP_THEMES.get(difficulty, MAP_THEMES[0])
    rng = random.Random(123)
    f1, f2, f3 = theme["floor1"], theme["floor2"], theme["floor3"]
    d1, d2 = theme["dirt1"], theme["dirt2"]
    for gx in range(GRID_W):
        for gy in range(GRID_H):
            px = gx * CELL_SIZE
            py = gy * CELL_SIZE + SCOREBOARD_H
            roll = rng.random()
            if roll < 0.55:
                base = f1
            elif roll < 0.85:
                base = f2
            else:
                base = f3
            draw_3d_tile(surface, px, py, CELL_SIZE, base)
            # Jord/detalje-pletter
            if rng.random() < 0.12:
                dx = rng.randint(2, CELL_SIZE - 6)
                dy = rng.randint(2, CELL_SIZE - 6)
                dr = rng.randint(2, 4)
                dirt = d1 if rng.random() > 0.5 else d2
                pygame.draw.circle(surface, dirt, (px + dx, py + dy), dr)
            # Mos/tekstur-klumper
            if rng.random() < theme["moss_chance"]:
                mx = rng.randint(1, CELL_SIZE - 3)
                my = rng.randint(1, CELL_SIZE - 3)
                mr, mg, mb = theme["moss_r"], theme["moss_g"], theme["moss_b"]
                moss_col = (mr[0] + rng.randint(0, mr[1]), mg[0] + rng.randint(0, mg[1]), mb[0] + rng.randint(0, mb[1]))
                pygame.draw.circle(surface, moss_col, (px + mx, py + my), rng.randint(1, 3))
            # Detaljer (blade/sten/aske/skruer)
            if rng.random() < theme["detail_chance"]:
                lx = px + rng.randint(3, CELL_SIZE - 5)
                ly = py + rng.randint(3, CELL_SIZE - 5)
                leaf_col = rng.choice(theme["detail_col"])
                pygame.draw.ellipse(surface, leaf_col, (lx, ly, rng.randint(3, 6), rng.randint(2, 4)))
            # Vulkan: lava-revner
            if difficulty == 2 and rng.random() < 0.04:
                cx = px + rng.randint(2, CELL_SIZE - 2)
                cy = py + rng.randint(2, CELL_SIZE - 2)
                ex = cx + rng.randint(-8, 8)
                ey = cy + rng.randint(-8, 8)
                pygame.draw.line(surface, (200, 60, 10), (cx, cy), (ex, ey), 1)
                pygame.draw.line(surface, (255, 120, 20), (cx, cy), ((cx + ex) // 2, (cy + ey) // 2), 1)
            # Militærbase: gulv-markeringer
            if difficulty == 3 and rng.random() < 0.03:
                mx = px + rng.randint(0, CELL_SIZE - 1)
                my = py + rng.randint(0, CELL_SIZE - 1)
                pygame.draw.line(surface, (80, 85, 60), (mx, my), (mx + rng.randint(4, 10), my), 1)


def draw_decorations(surface, trees, difficulty=0):
    """Tegn dekorationer baseret på tema: træer/buske/vulkan-klipper/militær-strukturer."""
    theme = MAP_THEMES.get(difficulty, MAP_THEMES[0])
    rng = random.Random(77)
    cs = CELL_SIZE
    trunk_col = theme["trunk"]
    trunk_dk = theme["trunk_dark"]
    trunk_lt = theme["trunk_light"]
    canopy_col = theme["canopy"]
    canopy_lt = theme["canopy_light"]
    canopy_dk = theme["canopy_dark"]

    for (tx, ty) in trees:
        px = tx * cs
        py = ty * cs + SCOREBOARD_H
        cx = px + cs // 2
        cy = py + cs // 2

        if difficulty == 2:
            # --- VULKAN: lava-klipper og ryggende sten ---
            rock_h = rng.randint(10, 16)
            # Skygge
            shadow_surf = pygame.Surface((rock_h * 2, rock_h), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 50), (0, 0, rock_h * 2, rock_h))
            surface.blit(shadow_surf, (cx - rock_h, cy + 2))
            # Klippeform (uregelmæssig polygon)
            pts = []
            for a in range(6):
                ang = a * math.pi / 3 - math.pi / 2
                r = rock_h + rng.randint(-4, 4)
                pts.append((int(cx + r * math.cos(ang)), int(cy - r * 0.6 * math.sin(ang))))
            pygame.draw.polygon(surface, (50, 30, 25), [(p[0] + 2, p[1] + 2) for p in pts])
            pygame.draw.polygon(surface, trunk_col, pts)
            pygame.draw.polygon(surface, trunk_lt, pts, 1)
            # Glødende revner
            for _ in range(rng.randint(1, 3)):
                rx = cx + rng.randint(-rock_h // 2, rock_h // 2)
                ry = cy + rng.randint(-rock_h // 3, rock_h // 3)
                pygame.draw.line(surface, (220, 80, 10), (rx, ry), (rx + rng.randint(-5, 5), ry + rng.randint(-5, 5)), 1)
            # Røg/damp
            for _ in range(rng.randint(1, 2)):
                sx = cx + rng.randint(-3, 3)
                sy = cy - rock_h // 2 - rng.randint(2, 8)
                smoke_r = rng.randint(2, 5)
                smoke_surf = pygame.Surface((smoke_r * 2, smoke_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surf, (120, 110, 100, 60), (smoke_r, smoke_r), smoke_r)
                surface.blit(smoke_surf, (sx - smoke_r, sy - smoke_r))

        elif difficulty == 3:
            # --- MILITÆRBASE: sandsække, barrikader, tårne ---
            struct_type = rng.randint(0, 2)
            if struct_type == 0:
                # Sandsæk-bunke
                for row in range(3):
                    for col in range(2 - row):
                        bx = cx - 8 + col * 10 + row * 5
                        by = cy + 4 - row * 6
                        draw_3d_rect(surface, (90, 85, 60), (bx, by, 10, 6), depth=2)
                        pygame.draw.rect(surface, (75, 70, 48), (bx + 1, by + 1, 8, 4), 1)
            elif struct_type == 1:
                # Vagttårn
                base_w, base_h = 14, 8
                draw_3d_rect(surface, (70, 72, 65), (cx - base_w // 2, cy, base_w, base_h), depth=3)
                # Stolpe
                pygame.draw.line(surface, (80, 82, 75), (cx, cy), (cx, cy - 18), 3)
                pygame.draw.line(surface, (100, 102, 95), (cx - 1, cy), (cx - 1, cy - 18), 1)
                # Platform
                draw_3d_rect(surface, (75, 78, 70), (cx - 8, cy - 22, 16, 6), depth=2)
                # Gelænder
                pygame.draw.rect(surface, (90, 92, 85), (cx - 7, cy - 26, 14, 4), 1)
            else:
                # Pigtrådshegn
                y1 = cy - 6
                y2 = cy + 6
                pygame.draw.line(surface, (90, 88, 80), (cx - 10, cy), (cx + 10, cy), 2)
                pygame.draw.line(surface, (70, 68, 60), (cx - 10, y1), (cx - 10, y2), 2)
                pygame.draw.line(surface, (70, 68, 60), (cx + 10, y1), (cx + 10, y2), 2)
                # Pigtråd
                for wx in range(cx - 9, cx + 9, 3):
                    pygame.draw.line(surface, (110, 108, 100), (wx, cy - 1), (wx + 2, cy + 1), 1)
                    pygame.draw.line(surface, (110, 108, 100), (wx + 2, cy + 1), (wx + 1, cy - 1), 1)

        elif difficulty == 1:
            # --- VILDMARK: buske og klipper ---
            is_bush = rng.random() < 0.6
            if is_bush:
                bush_r = rng.randint(8, 14)
                shadow_surf = pygame.Surface((bush_r * 2, bush_r), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow_surf, (0, 0, 0, 45), (0, 0, bush_r * 2, bush_r))
                surface.blit(shadow_surf, (cx - bush_r, cy + 2))
                # Busk-klumper
                for _ in range(rng.randint(3, 5)):
                    bx = cx + rng.randint(-bush_r // 2, bush_r // 2)
                    by = cy + rng.randint(-bush_r // 2, bush_r // 3)
                    br = rng.randint(bush_r // 3, bush_r // 2 + 2)
                    pygame.draw.circle(surface, canopy_dk, (bx + 1, by + 1), br)
                    pygame.draw.circle(surface, canopy_col, (bx, by), br)
                # Highlight
                for _ in range(rng.randint(1, 3)):
                    hx = cx + rng.randint(-bush_r // 3, bush_r // 3)
                    hy = cy + rng.randint(-bush_r // 2, -bush_r // 4)
                    pygame.draw.circle(surface, canopy_lt, (hx, hy), rng.randint(2, 4))
            else:
                # Klippe
                rock_r = rng.randint(6, 10)
                pygame.draw.circle(surface, (40, 38, 32), (cx + 1, cy + 1), rock_r)
                pygame.draw.circle(surface, (75, 70, 58), (cx, cy), rock_r)
                pygame.draw.circle(surface, (95, 90, 75), (cx - 2, cy - 2), rock_r // 2)
                pygame.draw.circle(surface, canopy_dk, (cx, cy), rock_r, 1)

        else:
            # --- SKOV: standard træer ---
            tree_h = rng.randint(14, 22)
            trunk_w = rng.randint(3, 5)
            shadow_r = tree_h + 2
            shadow_surf = pygame.Surface((shadow_r * 2, shadow_r), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 50), (0, 0, shadow_r * 2, shadow_r))
            surface.blit(shadow_surf, (cx - shadow_r, cy + 2))
            trunk_top = cy - tree_h // 2
            trunk_bot = cy + 4
            pygame.draw.line(surface, trunk_dk, (cx + 2, trunk_top + 2), (cx + 2, trunk_bot + 2), trunk_w + 2)
            pygame.draw.line(surface, trunk_col, (cx, trunk_top), (cx, trunk_bot), trunk_w)
            pygame.draw.line(surface, trunk_lt, (cx - trunk_w // 2 + 1, trunk_top), (cx - trunk_w // 2 + 1, trunk_bot), 1)
            for bark_y in range(trunk_top + 3, trunk_bot, 4):
                pygame.draw.line(surface, trunk_dk, (cx - trunk_w // 2, bark_y), (cx + trunk_w // 2, bark_y), 1)
            crown_cx = cx + rng.randint(-2, 2)
            crown_cy = trunk_top - tree_h // 3
            draw_3d_circle(surface, canopy_dk, (crown_cx + 3, crown_cy + 3), tree_h, depth=0)
            pygame.draw.circle(surface, canopy_col, (crown_cx, crown_cy), tree_h)
            for _ in range(rng.randint(3, 5)):
                bx = crown_cx + rng.randint(-tree_h // 2, tree_h // 2)
                by = crown_cy + rng.randint(-tree_h // 2, tree_h // 2)
                br = rng.randint(tree_h // 3, tree_h // 2)
                pygame.draw.circle(surface, canopy_col, (bx, by), br)
            for _ in range(rng.randint(2, 4)):
                hx = crown_cx + rng.randint(-tree_h // 3, tree_h // 3)
                hy = crown_cy + rng.randint(-tree_h // 2, -tree_h // 4)
                hr = rng.randint(tree_h // 4, tree_h // 3)
                pygame.draw.circle(surface, canopy_lt, (hx, hy), hr)
            for _ in range(rng.randint(2, 3)):
                sx = crown_cx + rng.randint(-tree_h // 3, tree_h // 3)
                sy = crown_cy + rng.randint(0, tree_h // 3)
                sr = rng.randint(tree_h // 4, tree_h // 3)
                pygame.draw.circle(surface, canopy_dk, (sx, sy), sr)
            spec_x = crown_cx - tree_h // 4
            spec_y = crown_cy - tree_h // 3
            pygame.draw.circle(surface, _lighten(canopy_lt, 30), (spec_x, spec_y), tree_h // 5)
            pygame.draw.circle(surface, canopy_dk, (crown_cx, crown_cy), tree_h, 1)


def _seg_direction(prev, curr):
    """Retning fra prev til curr."""
    return (curr[0] - prev[0], curr[1] - prev[1])


# --- 3D tegne-hjælpere ---
def _clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def _lighten(color, amount=40):
    return tuple(_clamp(c + amount) for c in color)


def _hsv_to_rgb(h, s, v):
    """HSV -> RGB. h,s,v in [0,1]. Returns (r,g,b) in [0,255]."""
    if s == 0:
        val = int(v * 255)
        return (val, val, val)
    h6 = h * 6.0
    i = int(h6) % 6
    f = h6 - int(h6)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q
    return (int(r * 255), int(g * 255), int(b * 255))


def _darken(color, amount=40):
    return tuple(_clamp(c - amount) for c in color)


def _blend(c1, c2, t):
    """Bland to farver. t=0 giver c1, t=1 giver c2."""
    return tuple(_clamp(int(a + (b - a) * t)) for a, b in zip(c1, c2))


def draw_3d_rect(surface, color, rect, depth=3):
    """Tegn et realistisk ophøjet rektangel med bløde skygger og gradient."""
    x, y, w, h = rect if isinstance(rect, tuple) else (rect.x, rect.y, rect.w, rect.h)
    # Blød skygge (flere lag med alpha)
    for d in range(depth, 0, -1):
        alpha = 30 + (depth - d) * 15
        sh = pygame.Surface((w, h), pygame.SRCALPHA)
        sh.fill((0, 0, 0, min(alpha, 100)))
        surface.blit(sh, (x + d, y + d))
    # Hovedflade med subtle vertikal gradient
    for row in range(h):
        frac = row / max(1, h - 1)
        rc = _blend(_lighten(color, 20), _darken(color, 15), frac)
        pygame.draw.line(surface, rc, (x, y + row), (x + w - 1, y + row), 1)
    # Bevelled kanter
    highlight = _lighten(color, 55)
    pygame.draw.line(surface, highlight, (x, y), (x + w - 1, y), 1)
    pygame.draw.line(surface, highlight, (x, y), (x, y + h - 1), 1)
    dark = _darken(color, 40)
    pygame.draw.line(surface, dark, (x, y + h - 1), (x + w - 1, y + h - 1), 1)
    pygame.draw.line(surface, dark, (x + w - 1, y), (x + w - 1, y + h - 1), 1)
    # Inner glow (subtil lys ramme)
    inner_hl = _lighten(color, 25)
    if w > 4 and h > 4:
        pygame.draw.line(surface, inner_hl, (x + 1, y + 1), (x + w - 2, y + 1), 1)
        pygame.draw.line(surface, inner_hl, (x + 1, y + 1), (x + 1, y + h - 2), 1)


def draw_3d_circle(surface, color, center, radius, depth=2):
    """Tegn en realistisk 3D-sfære med gradient, ambient occlusion og specular."""
    cx, cy = center
    if radius < 1:
        return
    # Blød skygge
    for d in range(depth, 0, -1):
        alpha = 25 + (depth - d) * 20
        sh = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(sh, (0, 0, 0, min(alpha, 80)), (radius + 2, radius + 2), radius)
        surface.blit(sh, (cx - radius - 2 + d, cy - radius - 2 + d))
    # Basis cirkel
    pygame.draw.circle(surface, color, (cx, cy), radius)
    # Radial gradient (mørkere kant = ambient occlusion)
    if radius >= 4:
        dark_rim = _darken(color, 35)
        pygame.draw.circle(surface, dark_rim, (cx, cy), radius, 2)
        mid_rim = _darken(color, 18)
        pygame.draw.circle(surface, mid_rim, (cx, cy), max(1, radius - 1), 1)
    elif radius >= 2:
        dark_rim = _darken(color, 30)
        pygame.draw.circle(surface, dark_rim, (cx, cy), radius, 1)
    # Specular highlights (realistisk lysrefleks)
    if radius >= 3:
        hl = _lighten(color, 90)
        hr = max(1, radius // 3)
        hx = cx - radius // 3
        hy = cy - radius // 3
        pygame.draw.circle(surface, hl, (hx, hy), hr)
        # Sekundær diffus highlight
        hl2 = _lighten(color, 40)
        pygame.draw.circle(surface, hl2, (cx - radius // 5, cy - radius // 4), max(1, radius // 2))


def draw_3d_panel(surface, rect, base_color, depth=3):
    """Tegn et realistisk ophøjet panel med gradient og bløde kanter."""
    x, y, w, h = rect if isinstance(rect, tuple) else (rect.x, rect.y, rect.w, rect.h)
    # Blød skygge
    for d in range(depth, 0, -1):
        alpha = 20 + (depth - d) * 15
        sh = pygame.Surface((w, h), pygame.SRCALPHA)
        sh.fill((0, 0, 0, min(alpha, 80)))
        surface.blit(sh, (x + d, y + d))
    # Vertikal gradient panel
    for row in range(h):
        frac = row / max(1, h - 1)
        rc = _blend(_lighten(base_color, 15), _darken(base_color, 10), frac)
        pygame.draw.line(surface, rc, (x, y + row), (x + w - 1, y + row), 1)
    # Bevelled kanter
    highlight = _lighten(base_color, 45)
    dark = _darken(base_color, 40)
    pygame.draw.line(surface, highlight, (x, y), (x + w, y), 2)
    pygame.draw.line(surface, highlight, (x, y), (x, y + h), 1)
    pygame.draw.line(surface, dark, (x, y + h), (x + w, y + h), 2)
    pygame.draw.line(surface, dark, (x + w, y), (x + w, y + h), 1)


def draw_3d_tile(surface, x, y, size, base_color, light_dir=(1, 1)):
    """Tegn en realistisk gulv-flise med subtil gradient og ambient occlusion."""
    # Vertikal micro-gradient for dybde
    for row in range(size):
        frac = row / max(1, size - 1)
        # Subtle gradient fra lys til mørkere
        rc = _blend(_lighten(base_color, 6), _darken(base_color, 6), frac)
        pygame.draw.line(surface, rc, (x, y + row), (x + size - 1, y + row), 1)
    # Ambient occlusion (mørkere kanter)
    ao = _darken(base_color, 18)
    pygame.draw.line(surface, ao, (x + size - 1, y), (x + size - 1, y + size - 1), 1)
    pygame.draw.line(surface, ao, (x, y + size - 1), (x + size - 1, y + size - 1), 1)
    # Highlight kanter
    hl = _lighten(base_color, 12)
    pygame.draw.line(surface, hl, (x, y), (x + size - 1, y), 1)
    pygame.draw.line(surface, hl, (x, y), (x, y + size - 1), 1)


class Snake:
    def __init__(self, start_pos, direction, color, color_dark, color_belly):
        self.color = color
        self.color_dark = color_dark
        self.color_belly = color_belly
        self.direction = direction
        self.next_direction = direction
        self.body = []
        self.alive = True
        self.grow_pending = 0
        self.invincible_timer = 0
        x, y = start_pos
        for i in range(3):
            dx, dy = direction
            self.body.append((x - dx * i, y - dy * i))

    def reset(self, start_pos, direction):
        self.direction = direction
        self.next_direction = direction
        self.body = []
        self.alive = True
        self.grow_pending = 0
        self.invincible_timer = 0
        x, y = start_pos
        for i in range(3):
            dx, dy = direction
            self.body.append((x - dx * i, y - dy * i))

    @property
    def is_invincible(self):
        return self.invincible_timer > 0

    def set_direction(self, new_dir):
        if new_dir != OPPOSITES.get(self.direction):
            self.next_direction = new_dir

    def move(self):
        if not self.alive:
            return
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def grow(self, amount=1):
        self.grow_pending += amount

    def head(self):
        return self.body[0]

    def check_wall_collision(self):
        x, y = self.head()
        if x < 0 or x >= GRID_W or y < 0 or y >= GRID_H:
            if not self.is_invincible:
                self.alive = False

    def check_self_collision(self):
        if self.head() in self.body[1:]:
            if not self.is_invincible:
                self.alive = False

    def check_ruin_collision(self, ruins):
        if self.head() in ruins:
            if not self.is_invincible:
                self.alive = False

    def draw(self, surface, tick, gun_type=GUN_NONE, snake_type=SNAKE_NORMAL):
        if not self.body:
            return

        n = len(self.body)
        cs = CELL_SIZE
        off_y = SCOREBOARD_H
        sd = 2

        for i in range(n):
            x, y = self.body[i]
            px = x * cs
            py = y * cs + off_y
            cx = px + cs // 2
            cy = py + cs // 2

            if self.is_invincible:
                pulse = (math.sin(tick * 0.5) + 1) / 2
                bright = int(180 + 75 * pulse)
                body_col = (bright, bright, bright)
                dark_col = (max(0, bright - 50),) * 3
                belly_col = (min(255, bright + 20),) * 3
            elif snake_type == SNAKE_RAINBOW:
                hue = ((i * 18 + tick * 2) % 360) / 360.0
                body_col = _hsv_to_rgb(hue, 0.75, 0.88)
                dark_col = _darken(body_col, 40)
                belly_col = _lighten(body_col, 30)
            else:
                body_col = self.color
                dark_col = self.color_dark
                belly_col = self.color_belly

            if i == 0:
                # ============ HOVED ============
                dx, dy = self.direction
                if snake_type in SQUARE_HEAD_TYPES:
                    # --- Firkantet hoved (Tank, Robot) ---
                    draw_3d_rect(surface, body_col, (px + 1, py + 1, cs - 2, cs - 2), depth=sd)
                    pygame.draw.rect(surface, dark_col, (px + 1, py + 1, cs - 2, cs - 2), 2, border_radius=3)
                    eo = cs // 4
                    e1 = (cx - eo, cy) if dx == 0 else (cx, cy - eo)
                    e2 = (cx + eo, cy) if dx == 0 else (cx, cy + eo)
                    if snake_type == SNAKE_TANK:
                        if dx != 0:
                            pygame.draw.line(surface, dark_col, (cx, py + 3), (cx, py + cs - 3), 1)
                        else:
                            pygame.draw.line(surface, dark_col, (px + 3, cy), (px + cs - 3, cy), 1)
                        draw_3d_rect(surface, (200, 200, 80), (e1[0] - 2, e1[1] - 1, 4, 2), depth=1)
                        draw_3d_rect(surface, (200, 200, 80), (e2[0] - 2, e2[1] - 1, 4, 2), depth=1)
                        ant_x = cx - dx * (cs // 3)
                        ant_y = cy - dy * (cs // 3)
                        pygame.draw.line(surface, (180, 180, 180), (ant_x, ant_y), (ant_x, ant_y - 9), 1)
                        pr = 2 if tick % 10 < 5 else 3
                        draw_3d_circle(surface, RED, (ant_x, ant_y - 9), pr, depth=1)
                    else:  # ROBOT
                        # LED øjne
                        led_col = (50, 255, 50) if tick % 8 < 4 else (20, 180, 20)
                        draw_3d_rect(surface, led_col, (e1[0] - 2, e1[1] - 2, 4, 4), depth=1)
                        draw_3d_rect(surface, led_col, (e2[0] - 2, e2[1] - 2, 4, 4), depth=1)
                        # Antenne med roterende top
                        ant_x = cx - dx * (cs // 3)
                        ant_y = cy - dy * (cs // 3)
                        pygame.draw.line(surface, (180, 180, 190), (ant_x, ant_y), (ant_x, ant_y - 8), 2)
                        ang = tick * 0.4
                        rx = int(ant_x + 3 * math.cos(ang))
                        ry = int(ant_y - 8 + 2 * math.sin(ang))
                        draw_3d_circle(surface, (100, 200, 255), (rx, ry), 2, depth=1)
                        # Mund-gitter
                        mx = cx + dx * (cs // 3)
                        my = cy + dy * (cs // 3)
                        for off in (-2, 0, 2):
                            if dx != 0:
                                pygame.draw.line(surface, (120, 120, 130), (mx, my + off - 1), (mx + dx * 2, my + off - 1), 1)
                            else:
                                pygame.draw.line(surface, (120, 120, 130), (mx + off - 1, my), (mx + off - 1, my + dy * 2), 1)
                else:
                    # --- Rund hoved (alle andre 18 typer) ---
                    draw_3d_circle(surface, body_col, (cx, cy), cs // 2, depth=sd)
                    eo = cs // 4
                    if dx == 0:
                        e1, e2 = (cx - eo, cy), (cx + eo, cy)
                        poff = (0, dy * 2)
                    else:
                        e1, e2 = (cx, cy - eo), (cx, cy + eo)
                        poff = (dx * 2, 0)

                    # --- Øjne per type ---
                    if snake_type == SNAKE_DOG:
                        draw_3d_circle(surface, WHITE, e1, 4, depth=1)
                        draw_3d_circle(surface, WHITE, e2, 4, depth=1)
                        pygame.draw.circle(surface, (60, 30, 10), (e1[0] + poff[0], e1[1] + poff[1]), 2)
                        pygame.draw.circle(surface, (60, 30, 10), (e2[0] + poff[0], e2[1] + poff[1]), 2)
                    elif snake_type == SNAKE_CAT:
                        draw_3d_circle(surface, (220, 200, 50), e1, 3, depth=1)
                        draw_3d_circle(surface, (220, 200, 50), e2, 3, depth=1)
                        # Slit-pupiller
                        if dx == 0:
                            pygame.draw.line(surface, BLACK, (e1[0] + poff[0], e1[1] - 2), (e1[0] + poff[0], e1[1] + 2), 1)
                            pygame.draw.line(surface, BLACK, (e2[0] + poff[0], e2[1] - 2), (e2[0] + poff[0], e2[1] + 2), 1)
                        else:
                            pygame.draw.line(surface, BLACK, (e1[0] - 2, e1[1] + poff[1]), (e1[0] + 2, e1[1] + poff[1]), 1)
                            pygame.draw.line(surface, BLACK, (e2[0] - 2, e2[1] + poff[1]), (e2[0] + 2, e2[1] + poff[1]), 1)
                    elif snake_type == SNAKE_ALIEN:
                        draw_3d_circle(surface, (20, 20, 20), e1, 5, depth=1)
                        draw_3d_circle(surface, (20, 20, 20), e2, 5, depth=1)
                        draw_3d_circle(surface, (0, 255, 100), e1, 3, depth=0)
                        draw_3d_circle(surface, (0, 255, 100), e2, 3, depth=0)
                    elif snake_type == SNAKE_ZOMBIE:
                        draw_3d_circle(surface, (200, 200, 50), e1, 3, depth=1)
                        pygame.draw.circle(surface, (120, 20, 20), (e1[0] + poff[0], e1[1] + poff[1]), 2)
                        # X-øje
                        pygame.draw.line(surface, RED, (e2[0] - 2, e2[1] - 2), (e2[0] + 2, e2[1] + 2), 2)
                        pygame.draw.line(surface, RED, (e2[0] + 2, e2[1] - 2), (e2[0] - 2, e2[1] + 2), 2)
                    elif snake_type == SNAKE_SKELETON:
                        # Tomme øjenhuler
                        pygame.draw.circle(surface, (20, 15, 10), e1, 4)
                        pygame.draw.circle(surface, (20, 15, 10), e2, 4)
                        pygame.draw.circle(surface, (50, 40, 30), e1, 2)
                        pygame.draw.circle(surface, (50, 40, 30), e2, 2)
                    elif snake_type == SNAKE_LAVA:
                        # Glødende øjne
                        glow = (255, 100 + int(50 * math.sin(tick * 0.3)), 20)
                        draw_3d_circle(surface, glow, e1, 3, depth=1)
                        draw_3d_circle(surface, glow, e2, 3, depth=1)
                    elif snake_type == SNAKE_PIRATE:
                        # Normalt øje + klap
                        draw_3d_circle(surface, WHITE, e1, 3, depth=1)
                        pygame.draw.circle(surface, BLACK, (e1[0] + poff[0], e1[1] + poff[1]), 2)
                        pygame.draw.circle(surface, (30, 30, 30), e2, 4)
                        pygame.draw.line(surface, (60, 40, 20), (e2[0] - 4, e2[1] - 5), (e2[0] + 4, e2[1] - 5), 2)
                    elif snake_type == SNAKE_NINJA:
                        # Smalle øjne (maske)
                        pygame.draw.rect(surface, WHITE, (e1[0] - 3, e1[1] - 1, 6, 2))
                        pygame.draw.rect(surface, WHITE, (e2[0] - 3, e2[1] - 1, 6, 2))
                    else:
                        # Standard øjne (Normal, Dragon, Shark, Fire, Ice, Rainbow, Candy, Gold, Electric, Diamond)
                        draw_3d_circle(surface, WHITE, e1, 3, depth=1)
                        draw_3d_circle(surface, WHITE, e2, 3, depth=1)
                        pygame.draw.circle(surface, BLACK, (e1[0] + poff[0], e1[1] + poff[1]), 2)
                        pygame.draw.circle(surface, BLACK, (e2[0] + poff[0], e2[1] + poff[1]), 2)

                    # --- Dekorationer per type ---
                    if snake_type == SNAKE_DOG:
                        ear_s = 6
                        if dx != 0:
                            ea1, ea2 = (cx - dx * 3, cy - cs // 3 - 2), (cx - dx * 3, cy + cs // 3 + 2)
                        else:
                            ea1, ea2 = (cx - cs // 3 - 2, cy - dy * 3), (cx + cs // 3 + 2, cy - dy * 3)
                        draw_3d_circle(surface, dark_col, ea1, ear_s, depth=sd)
                        draw_3d_circle(surface, dark_col, ea2, ear_s, depth=sd)
                        draw_3d_circle(surface, (20, 20, 20), (cx + dx * (cs // 2), cy + dy * (cs // 2)), 3, depth=1)
                        pink = (255, 130, 150)
                        tmx, tmy = cx + dx * (cs // 2 + 1), cy + dy * (cs // 2 + 1)
                        ttx, tty = cx + dx * (cs // 2 + 4), cy + dy * (cs // 2 + 4)
                        if dx != 0:
                            pygame.draw.line(surface, pink, (tmx, tmy), (ttx, tty + 3), 3)
                            draw_3d_circle(surface, pink, (ttx, tty + 4), 2, depth=1)
                        else:
                            pygame.draw.line(surface, pink, (tmx, tmy), (ttx + 3, tty), 3)
                            draw_3d_circle(surface, pink, (ttx + 4, tty), 2, depth=1)
                    elif snake_type == SNAKE_CAT:
                        # Spidse ører
                        if dx != 0:
                            ea1 = [(cx - dx * 4, cy - cs // 2 - 4), (cx - dx * 4 - 3, cy - cs // 4), (cx - dx * 4 + 3, cy - cs // 4)]
                            ea2 = [(cx - dx * 4, cy + cs // 2 + 4), (cx - dx * 4 - 3, cy + cs // 4), (cx - dx * 4 + 3, cy + cs // 4)]
                        else:
                            ea1 = [(cx - cs // 2 - 4, cy - dy * 4), (cx - cs // 4, cy - dy * 4 - 3), (cx - cs // 4, cy - dy * 4 + 3)]
                            ea2 = [(cx + cs // 2 + 4, cy - dy * 4), (cx + cs // 4, cy - dy * 4 - 3), (cx + cs // 4, cy - dy * 4 + 3)]
                        pygame.draw.polygon(surface, dark_col, ea1)
                        pygame.draw.polygon(surface, dark_col, ea2)
                        pygame.draw.polygon(surface, (255, 180, 180), [(p[0], p[1]) for p in ea1[:1]] + [(ea1[1][0] + 1, ea1[1][1]), (ea1[2][0] - 1, ea1[2][1])])
                        # Knurhår
                        nx, ny = cx + dx * (cs // 2), cy + dy * (cs // 2)
                        draw_3d_circle(surface, (255, 150, 170), (nx, ny), 2, depth=1)
                        if dx != 0:
                            for wy in (-3, 0, 3):
                                pygame.draw.line(surface, (180, 160, 140), (nx, ny + wy), (nx + dx * 6, ny + wy + (1 if wy > 0 else -1 if wy < 0 else 0)), 1)
                        else:
                            for wx in (-3, 0, 3):
                                pygame.draw.line(surface, (180, 160, 140), (nx + wx, ny), (nx + wx + (1 if wx > 0 else -1 if wx < 0 else 0), ny + dy * 6), 1)
                    elif snake_type == SNAKE_DRAGON:
                        # Horn
                        if dx != 0:
                            draw_3d_circle(surface, (180, 140, 40), (cx - dx * 2, cy - cs // 3 - 3), 3, depth=1)
                            draw_3d_circle(surface, (180, 140, 40), (cx - dx * 2, cy + cs // 3 + 3), 3, depth=1)
                        else:
                            draw_3d_circle(surface, (180, 140, 40), (cx - cs // 3 - 3, cy - dy * 2), 3, depth=1)
                            draw_3d_circle(surface, (180, 140, 40), (cx + cs // 3 + 3, cy - dy * 2), 3, depth=1)
                        # Ild-ånde
                        fx, fy = cx + dx * (cs // 2 + 4), cy + dy * (cs // 2 + 4)
                        draw_3d_circle(surface, (255, 180, 30), (fx, fy), 3, depth=0)
                        draw_3d_circle(surface, (255, 80, 20), (fx + dx * 2, fy + dy * 2), 2, depth=0)
                    elif snake_type == SNAKE_SHARK:
                        # Rygfinne
                        if dx != 0:
                            fin_pts = [(cx, cy - cs // 2 - 5), (cx - 4, cy - cs // 4), (cx + 4, cy - cs // 4)]
                        else:
                            fin_pts = [(cx - cs // 2 - 5, cy), (cx - cs // 4, cy - 4), (cx - cs // 4, cy + 4)]
                        pygame.draw.polygon(surface, _darken(body_col, 20), fin_pts)
                        pygame.draw.polygon(surface, _lighten(body_col, 15), fin_pts, 1)
                        # Tænder
                        mx, my = cx + dx * (cs // 2), cy + dy * (cs // 2)
                        for tt in (-3, -1, 1, 3):
                            if dx != 0:
                                pygame.draw.polygon(surface, WHITE, [(mx, my + tt), (mx + dx * 2, my + tt - 1), (mx + dx * 2, my + tt + 1)])
                            else:
                                pygame.draw.polygon(surface, WHITE, [(mx + tt, my), (mx + tt - 1, my + dy * 2), (mx + tt + 1, my + dy * 2)])
                    elif snake_type == SNAKE_FIRE:
                        # Flamme-aura
                        for _ in range(3):
                            fa = tick * 0.3 + _ * 2.1
                            fr = cs // 2 + 2 + int(2 * math.sin(fa))
                            fax = cx + int(fr * 0.7 * math.cos(fa))
                            fay = cy + int(fr * 0.7 * math.sin(fa))
                            draw_3d_circle(surface, (255, 160 + int(40 * math.sin(fa)), 20), (fax, fay), 2, depth=0)
                        # Ild-tunge
                        pygame.draw.line(surface, (255, 200, 40), (cx + dx * (cs // 2), cy + dy * (cs // 2)),
                                         (cx + dx * (cs // 2 + 4), cy + dy * (cs // 2 + 4)), 2)
                    elif snake_type == SNAKE_ICE:
                        # Iskrystaller på toppen
                        for off in (-3, 0, 3):
                            ix = cx - dx * 3 + (off if dx != 0 else 0)
                            iy = cy - dy * 3 + (off if dy != 0 else 0)
                            pygame.draw.polygon(surface, (200, 230, 255), [(ix, iy - 5), (ix - 2, iy), (ix + 2, iy)])
                    elif snake_type == SNAKE_ZOMBIE:
                        # Sting over hovedet
                        pygame.draw.line(surface, (80, 60, 50), (cx - 4, cy - 2), (cx + 4, cy - 2), 1)
                        for sx in range(-3, 4, 2):
                            pygame.draw.line(surface, (80, 60, 50), (cx + sx, cy - 3), (cx + sx, cy - 1), 1)
                    elif snake_type == SNAKE_NINJA:
                        # Pandebånd
                        if dx != 0:
                            pygame.draw.line(surface, RED, (cx - dx * 2, cy - cs // 2 + 1), (cx - dx * 2, cy + cs // 2 - 1), 2)
                            # Bånd-ender
                            pygame.draw.line(surface, RED, (cx - dx * 3, cy - cs // 2), (cx - dx * 6, cy - cs // 2 - 3), 1)
                            pygame.draw.line(surface, RED, (cx - dx * 3, cy + cs // 2), (cx - dx * 6, cy + cs // 2 + 3), 1)
                        else:
                            pygame.draw.line(surface, RED, (cx - cs // 2 + 1, cy - dy * 2), (cx + cs // 2 - 1, cy - dy * 2), 2)
                    elif snake_type == SNAKE_PIRATE:
                        # Bandana
                        if dx != 0:
                            pygame.draw.line(surface, (180, 30, 30), (cx - dx * 3, cy - cs // 2), (cx - dx * 3, cy + cs // 2), 2)
                        else:
                            pygame.draw.line(surface, (180, 30, 30), (cx - cs // 2, cy - dy * 3), (cx + cs // 2, cy - dy * 3), 2)
                    elif snake_type == SNAKE_ALIEN:
                        # Antenner
                        for side in (-1, 1):
                            if dx != 0:
                                ax, ay = cx - dx * 4, cy + side * (cs // 3)
                                pygame.draw.line(surface, (100, 255, 100), (ax, ay), (ax - dx * 3, ay + side * 5), 1)
                                draw_3d_circle(surface, (150, 255, 150), (ax - dx * 3, ay + side * 5), 2, depth=0)
                            else:
                                ax, ay = cx + side * (cs // 3), cy - dy * 4
                                pygame.draw.line(surface, (100, 255, 100), (ax, ay), (ax + side * 5, ay - dy * 3), 1)
                                draw_3d_circle(surface, (150, 255, 150), (ax + side * 5, ay - dy * 3), 2, depth=0)
                    elif snake_type == SNAKE_CANDY:
                        # Lille sløjfe
                        bx, by = cx - dx * 3, cy - dy * 3 - 3
                        pygame.draw.circle(surface, (255, 80, 120), (bx - 2, by), 2)
                        pygame.draw.circle(surface, (255, 80, 120), (bx + 2, by), 2)
                        pygame.draw.circle(surface, (255, 200, 220), (bx, by), 1)
                    elif snake_type == SNAKE_GOLD:
                        # Krone (3 trekanter)
                        crown_y = cy - cs // 2 - 2
                        for coff in (-3, 0, 3):
                            pygame.draw.polygon(surface, GOLD, [
                                (cx + coff, crown_y - 4), (cx + coff - 2, crown_y + 1), (cx + coff + 2, crown_y + 1)])
                        pygame.draw.rect(surface, (200, 160, 0), (cx - 5, crown_y, 10, 2))
                    elif snake_type == SNAKE_SKELETON:
                        # Næse-hul + revner
                        nx, ny = cx + dx * 2, cy + dy * 2
                        pygame.draw.polygon(surface, (40, 35, 30), [(nx, ny), (nx - 1, ny + 2), (nx + 1, ny + 2)])
                        pygame.draw.line(surface, (140, 130, 120), (cx - 3, cy - 4), (cx + 1, cy - 2), 1)
                    elif snake_type == SNAKE_LAVA:
                        # Glødende revner
                        for loff in (-3, 3):
                            pygame.draw.line(surface, (255, 120, 20), (cx + loff, cy - 3), (cx + loff + 1, cy + 3), 1)
                    elif snake_type == SNAKE_ELECTRIC:
                        # Gnister
                        for _ in range(2):
                            sa = tick * 0.5 + _ * 3.14
                            sr = cs // 2 + 2
                            sx = cx + int(sr * math.cos(sa))
                            sy = cy + int(sr * math.sin(sa))
                            pygame.draw.line(surface, (255, 255, 100), (sx, sy), (sx + 2, sy - 2), 2)
                    elif snake_type == SNAKE_DIAMOND:
                        # Glans-facetter
                        pygame.draw.line(surface, (255, 255, 255), (cx - 4, cy - 3), (cx, cy - 6), 1)
                        pygame.draw.line(surface, (255, 255, 255), (cx + 2, cy - 4), (cx + 5, cy - 1), 1)
                        draw_3d_circle(surface, (255, 255, 240), (cx - 2, cy - 3), 1, depth=0)
                    elif snake_type == SNAKE_NORMAL:
                        # Splittet tunge
                        tmx, tmy = cx + dx * (cs // 2), cy + dy * (cs // 2)
                        ttx, tty = cx + dx * (cs // 2 + 3), cy + dy * (cs // 2 + 3)
                        pygame.draw.line(surface, RED, (tmx, tmy), (ttx, tty), 2)
                        if dx != 0:
                            pygame.draw.line(surface, RED, (ttx, tty), (ttx + dx * 2, tty - 2), 1)
                            pygame.draw.line(surface, RED, (ttx, tty), (ttx + dx * 2, tty + 2), 1)
                        else:
                            pygame.draw.line(surface, RED, (ttx, tty), (ttx - 2, tty + dy * 2), 1)
                            pygame.draw.line(surface, RED, (ttx, tty), (ttx + 2, tty + dy * 2), 1)

                # --- MASKINKANON (3D, uændret) ---
                if gun_type is not GUN_NONE:
                    gun_cx = cx + dx * 2
                    gun_cy = cy + dy * 2
                    barrel_len = cs // 2 + 4
                    if gun_type == GUN_BASIC:
                        bx1 = gun_cx + dx * barrel_len
                        by1 = gun_cy + dy * barrel_len
                        pygame.draw.line(surface, _darken(GUN_BARREL_COLOR, 40), (gun_cx + 1, gun_cy + 1), (bx1 + 1, by1 + 1), 4)
                        pygame.draw.line(surface, GUN_BARREL_COLOR, (gun_cx, gun_cy), (bx1, by1), 3)
                        pygame.draw.line(surface, _lighten(GUN_BARREL_COLOR, 40), (gun_cx, gun_cy), (bx1, by1), 1)
                        draw_3d_circle(surface, YELLOW, (bx1, by1), 2, depth=1)
                        draw_3d_rect(surface, GUN_BODY_COLOR, (gun_cx - 3, gun_cy - 3, 6, 6), depth=2)
                    elif gun_type == GUN_AUTO:
                        auto_col = (100, 200, 100)
                        bx1 = gun_cx + dx * (barrel_len + 2)
                        by1 = gun_cy + dy * (barrel_len + 2)
                        if dx != 0:
                            pygame.draw.line(surface, _darken(auto_col, 40), (gun_cx + 1, gun_cy - 1), (bx1 + 1, by1 - 1), 3)
                            pygame.draw.line(surface, auto_col, (gun_cx, gun_cy - 2), (bx1, by1 - 2), 2)
                            pygame.draw.line(surface, _darken(auto_col, 40), (gun_cx + 1, gun_cy + 3), (bx1 + 1, by1 + 3), 3)
                            pygame.draw.line(surface, auto_col, (gun_cx, gun_cy + 2), (bx1, by1 + 2), 2)
                        else:
                            pygame.draw.line(surface, _darken(auto_col, 40), (gun_cx - 1, gun_cy + 1), (bx1 - 1, by1 + 1), 3)
                            pygame.draw.line(surface, auto_col, (gun_cx - 2, gun_cy), (bx1 - 2, by1), 2)
                            pygame.draw.line(surface, _darken(auto_col, 40), (gun_cx + 3, gun_cy + 1), (bx1 + 3, by1 + 1), 3)
                            pygame.draw.line(surface, auto_col, (gun_cx + 2, gun_cy), (bx1 + 2, by1), 2)
                        draw_3d_circle(surface, (150, 255, 150), (bx1, by1), 2, depth=1)
                        draw_3d_circle(surface, (40, 60, 40), (gun_cx, gun_cy), 5, depth=2)
                        pygame.draw.circle(surface, auto_col, (gun_cx, gun_cy), 4, 1)
                        pulse = int(3 + 2 * math.sin(tick * 0.4))
                        pygame.draw.circle(surface, (80, 220, 80), (gun_cx, gun_cy), pulse, 1)
                        ang = tick * 0.3
                        pygame.draw.circle(surface, (180, 255, 180), (int(gun_cx + 3 * math.cos(ang)), int(gun_cy + 3 * math.sin(ang))), 1)
                    elif gun_type == GUN_QUAD:
                        quad_col, quad_tip, bl = (200, 80, 80), (255, 120, 60), barrel_len + 2
                        for dd in (UP, DOWN, LEFT, RIGHT):
                            bx, by = gun_cx + dd[0] * bl, gun_cy + dd[1] * bl
                            pygame.draw.line(surface, _darken(quad_col, 40), (gun_cx + 1, gun_cy + 1), (bx + 1, by + 1), 5)
                            pygame.draw.line(surface, quad_col, (gun_cx, gun_cy), (bx, by), 4)
                            pygame.draw.line(surface, _lighten(quad_col, 30), (gun_cx, gun_cy), (bx, by), 1)
                            draw_3d_circle(surface, quad_tip, (bx, by), 3, depth=1)
                            pygame.draw.circle(surface, YELLOW, (bx, by), 1)
                        draw_3d_circle(surface, (80, 30, 30), (gun_cx, gun_cy), 6, depth=2)
                        pygame.draw.circle(surface, quad_col, (gun_cx, gun_cy), 5, 1)
                        pygame.draw.line(surface, YELLOW, (gun_cx - 2, gun_cy), (gun_cx + 2, gun_cy), 1)
                        pygame.draw.line(surface, YELLOW, (gun_cx, gun_cy - 2), (gun_cx, gun_cy + 2), 1)
                    elif gun_type == GUN_VACUUM:
                        # Støvsuger: bred tragt foran hovedet
                        vac_col = (100, 60, 180)
                        vac_light = (140, 100, 220)
                        vac_dark = (60, 30, 120)
                        # Motorhus bag hovedet
                        draw_3d_circle(surface, vac_dark, (gun_cx, gun_cy), 5, depth=2)
                        pygame.draw.circle(surface, vac_col, (gun_cx, gun_cy), 4, 1)
                        # Sugerør
                        end_x = gun_cx + dx * (barrel_len + 4)
                        end_y = gun_cy + dy * (barrel_len + 4)
                        pygame.draw.line(surface, vac_dark, (gun_cx + 1, gun_cy + 1), (end_x + 1, end_y + 1), 5)
                        pygame.draw.line(surface, vac_col, (gun_cx, gun_cy), (end_x, end_y), 4)
                        pygame.draw.line(surface, vac_light, (gun_cx, gun_cy), (end_x, end_y), 1)
                        # Tragt/mundstykke (bred åbning)
                        perp_x, perp_y = -dy, dx  # vinkelret retning
                        t1 = (end_x + perp_x * 5, end_y + perp_y * 5)
                        t2 = (end_x - perp_x * 5, end_y - perp_y * 5)
                        t3 = (end_x + dx * 4, end_y + dy * 4)
                        pygame.draw.polygon(surface, vac_col, [t1, t2, t3])
                        pygame.draw.polygon(surface, vac_light, [t1, t2, t3], 1)
                        # Suge-effekt (pulserende cirkler når aktiv)
                        pulse = int(2 + 2 * math.sin(tick * 0.5))
                        pygame.draw.circle(surface, (180, 140, 255), (end_x + dx * 2, end_y + dy * 2), pulse, 1)

            elif i == n - 1:
                # ============ HALE ============
                prev = self.body[i - 1]
                d = _seg_direction(self.body[i], prev)
                if snake_type in SQUARE_HEAD_TYPES:
                    # Flad hale (Tank, Robot)
                    draw_3d_rect(surface, dark_col, (px + 2, py + 2, cs - 4, cs - 4), depth=sd)
                    draw_3d_rect(surface, body_col, (px + 3, py + 3, cs - 6, cs - 6), depth=1)
                    ex_x = cx - d[0] * (cs // 2 - 1)
                    ex_y = cy - d[1] * (cs // 2 - 1)
                    if snake_type == SNAKE_TANK:
                        draw_3d_circle(surface, (50, 50, 50), (ex_x, ex_y), 3, depth=1)
                        draw_3d_circle(surface, (80, 80, 80), (ex_x, ex_y), 2, depth=1)
                    else:  # Robot: lille lys
                        led = (255, 50, 50) if tick % 6 < 3 else (100, 20, 20)
                        draw_3d_circle(surface, led, (ex_x, ex_y), 2, depth=1)
                elif snake_type in (SNAKE_DOG, SNAKE_CAT, SNAKE_CANDY, SNAKE_ALIEN):
                    # Rund/fluffy hale
                    wag = int(3 * math.sin(tick * 0.6))
                    tip_x = cx - d[0] * (cs // 2) + (wag if d[0] == 0 else 0)
                    tip_y = cy - d[1] * (cs // 2) + (wag if d[1] == 0 else 0)
                    base_x = cx + d[0] * (cs // 4)
                    base_y = cy + d[1] * (cs // 4)
                    pygame.draw.line(surface, _darken(dark_col, 30), (base_x + 1, base_y + 1), (tip_x + 1, tip_y + 1), 5)
                    pygame.draw.line(surface, dark_col, (base_x, base_y), (tip_x, tip_y), 4)
                    pygame.draw.line(surface, _lighten(body_col, 30), (base_x, base_y), (tip_x, tip_y), 1)
                    r = 4 if snake_type == SNAKE_CAT else 3
                    draw_3d_circle(surface, body_col, (tip_x, tip_y), r, depth=1)
                else:
                    # Spids trekant (alle andre)
                    tip_x = cx - d[0] * (cs // 2)
                    tip_y = cy - d[1] * (cs // 2)
                    if d[0] != 0:
                        p1 = (cx + d[0] * (cs // 2), cy - cs // 3)
                        p2 = (cx + d[0] * (cs // 2), cy + cs // 3)
                    else:
                        p1 = (cx - cs // 3, cy + d[1] * (cs // 2))
                        p2 = (cx + cs // 3, cy + d[1] * (cs // 2))
                    shadow_pts = [(tip_x + sd, tip_y + sd), (p1[0] + sd, p1[1] + sd), (p2[0] + sd, p2[1] + sd)]
                    pygame.draw.polygon(surface, _darken(dark_col, 50), shadow_pts)
                    pygame.draw.polygon(surface, dark_col, [(tip_x, tip_y), p1, p2])
                    pygame.draw.line(surface, _lighten(dark_col, 30), (tip_x, tip_y), p1, 1)
                    # Type-specifik hale-dekoration
                    if snake_type == SNAKE_FIRE:
                        draw_3d_circle(surface, (255, 180, 30), (tip_x, tip_y), 3, depth=0)
                        draw_3d_circle(surface, (255, 100, 20), (tip_x - d[0] * 2, tip_y - d[1] * 2), 2, depth=0)
                    elif snake_type == SNAKE_DRAGON:
                        for side in (-1, 1):
                            if d[0] != 0:
                                pygame.draw.polygon(surface, _darken(body_col, 20), [(tip_x, tip_y), (tip_x - d[0] * 3, tip_y + side * 4), (tip_x - d[0] * 1, tip_y + side * 2)])
                            else:
                                pygame.draw.polygon(surface, _darken(body_col, 20), [(tip_x, tip_y), (tip_x + side * 4, tip_y - d[1] * 3), (tip_x + side * 2, tip_y - d[1] * 1)])
                    elif snake_type == SNAKE_ELECTRIC:
                        pygame.draw.line(surface, (255, 255, 100), (tip_x, tip_y), (tip_x - d[0] * 4, tip_y - d[1] * 4), 2)
                    elif snake_type == SNAKE_SKELETON:
                        draw_3d_circle(surface, belly_col, (tip_x, tip_y), 2, depth=1)

            else:
                # ============ KROP ============
                prev = self.body[i - 1]
                nxt = self.body[i + 1] if i + 1 < n else self.body[i]
                d_prev = _seg_direction(prev, self.body[i])
                d_next = _seg_direction(self.body[i], nxt)
                is_h = (d_prev[0] != 0 or d_next[0] != 0)

                if snake_type in SQUARE_HEAD_TYPES:
                    # --- Firkantet krop (Tank, Robot) ---
                    draw_3d_rect(surface, body_col, (px + 1, py + 1, cs - 2, cs - 2), depth=sd)
                    shine = _lighten(body_col, 35)
                    pygame.draw.rect(surface, shine, (px + cs // 3, py + 2, cs // 3, cs - 4), border_radius=1)
                    if snake_type == SNAKE_TANK:
                        if d_prev[0] != 0:
                            for ty in [py + 2, py + cs - 3]:
                                for tx in range(px + 2, px + cs - 2, 4):
                                    pygame.draw.line(surface, dark_col, (tx, ty), (tx + 2, ty), 1)
                        else:
                            for tx in [px + 2, px + cs - 3]:
                                for ty in range(py + 2, py + cs - 2, 4):
                                    pygame.draw.line(surface, dark_col, (tx, ty), (tx, ty + 2), 1)
                        if i % 3 == 0:
                            pygame.draw.rect(surface, belly_col, (px + 4, py + 4, cs - 8, cs - 8), 1)
                        if i % 2 == 0:
                            draw_3d_circle(surface, _lighten(dark_col, 20), (px + 3, py + 3), 1, depth=1)
                            draw_3d_circle(surface, _lighten(dark_col, 20), (px + cs - 4, py + cs - 4), 1, depth=1)
                    else:  # Robot
                        # Grid-mønster
                        if i % 2 == 0:
                            pygame.draw.line(surface, dark_col, (px + 3, cy), (px + cs - 3, cy), 1)
                            pygame.draw.line(surface, dark_col, (cx, py + 3), (cx, py + cs - 3), 1)
                        # Bolte i hjørner
                        for bx, by in [(px + 3, py + 3), (px + cs - 4, py + cs - 4)]:
                            draw_3d_circle(surface, _lighten(dark_col, 30), (bx, by), 1, depth=1)
                else:
                    # --- Rund krop (18 typer) ---
                    br = 8 if snake_type == SNAKE_DOG else 6
                    pygame.draw.rect(surface, _darken(dark_col, 60), (px + 1 + sd, py + 1 + sd, cs - 2, cs - 2), border_radius=br)
                    pygame.draw.rect(surface, dark_col, (px + 1, py + 1, cs - 2, cs - 2), border_radius=br)
                    # Cylindrisk highlight
                    hl = _lighten(body_col, 45)
                    if is_h:
                        pygame.draw.rect(surface, hl, (px + 2, cy - 3, cs - 4, 3), border_radius=2)
                    else:
                        pygame.draw.rect(surface, hl, (cx - 3, py + 2, 3, cs - 4), border_radius=2)
                    pygame.draw.circle(surface, _lighten(body_col, 65), (cx - 2, cy - 3), 2)
                    # Bug
                    if is_h:
                        pygame.draw.rect(surface, belly_col, (px + 2, cy + 2, cs - 4, 4), border_radius=2)
                    else:
                        pygame.draw.rect(surface, belly_col, (cx + 2, py + 2, 4, cs - 4), border_radius=2)
                    pygame.draw.rect(surface, _darken(dark_col, 25), (px + 1, py + 1, cs - 2, cs - 2), 1, border_radius=br)

                    # --- Type-specifik krop-mønster ---
                    if snake_type == SNAKE_NORMAL and i % 2 == 0:
                        sc = tuple(max(0, c - 25) for c in dark_col)
                        pygame.draw.arc(surface, sc, (px + 2, py + 2, cs // 2 - 2, cs // 2 - 2), 0, math.pi, 1)
                        pygame.draw.arc(surface, sc, (px + cs // 2, py + cs // 2, cs // 2 - 2, cs // 2 - 2), math.pi, 2 * math.pi, 1)
                    elif snake_type == SNAKE_DOG and i % 3 == 0:
                        draw_3d_circle(surface, dark_col, (cx + (3 if i % 2 == 0 else -3), cy + (2 if i % 4 == 0 else -2)), 3, depth=1)
                    elif snake_type == SNAKE_CAT and i % 2 == 0:
                        # Tiger-striber
                        pygame.draw.line(surface, dark_col, (px + 3, py + 2), (px + cs - 5, py + cs // 2), 1)
                        pygame.draw.line(surface, dark_col, (px + 3, py + cs - 3), (px + cs - 5, cy), 1)
                    elif snake_type == SNAKE_DRAGON and i % 2 == 0:
                        # Rygspigge
                        if is_h:
                            pygame.draw.polygon(surface, _darken(body_col, 15), [(cx, py), (cx - 2, py + 3), (cx + 2, py + 3)])
                        else:
                            pygame.draw.polygon(surface, _darken(body_col, 15), [(px, cy), (px + 3, cy - 2), (px + 3, cy + 2)])
                    elif snake_type == SNAKE_SHARK and i % 2 == 0:
                        # Gælle-streger
                        if is_h:
                            for gy in range(py + 4, py + cs - 3, 3):
                                pygame.draw.line(surface, _darken(dark_col, 15), (cx - 2, gy), (cx + 2, gy), 1)
                        else:
                            for gx in range(px + 4, px + cs - 3, 3):
                                pygame.draw.line(surface, _darken(dark_col, 15), (gx, cy - 2), (gx, cy + 2), 1)
                    elif snake_type == SNAKE_FIRE:
                        if i % 2 == 0:
                            off = int(2 * math.sin(tick * 0.4 + i))
                            draw_3d_circle(surface, (255, 180, 40), (px + 2, cy + off), 2, depth=0)
                    elif snake_type == SNAKE_ICE and i % 3 == 0:
                        pygame.draw.polygon(surface, (200, 230, 255), [(cx, py + 2), (cx - 2, cy), (cx + 2, cy)])
                    elif snake_type == SNAKE_ZOMBIE and i % 2 == 0:
                        # Sting
                        pygame.draw.line(surface, (80, 60, 50), (px + 3, cy - 2), (px + cs - 4, cy - 2), 1)
                        for sx in range(px + 4, px + cs - 3, 3):
                            pygame.draw.line(surface, (80, 60, 50), (sx, cy - 3), (sx, cy - 1), 1)
                    elif snake_type == SNAKE_PIRATE and i % 3 == 0:
                        # Kryds-mærke
                        pygame.draw.line(surface, dark_col, (cx - 2, cy - 2), (cx + 2, cy + 2), 1)
                        pygame.draw.line(surface, dark_col, (cx + 2, cy - 2), (cx - 2, cy + 2), 1)
                    elif snake_type == SNAKE_ALIEN and i % 2 == 0:
                        draw_3d_circle(surface, _lighten(body_col, 30), (cx - 2, cy - 2), 1, depth=0)
                        draw_3d_circle(surface, _lighten(body_col, 30), (cx + 2, cy + 2), 1, depth=0)
                    elif snake_type == SNAKE_CANDY and i % 2 == 0:
                        # Spiralstriber
                        pygame.draw.line(surface, _lighten(body_col, 40), (px + 2, py + 2), (px + cs - 3, py + cs - 3), 2)
                    elif snake_type == SNAKE_GOLD and i % 3 == 0:
                        # Diamant-glimt
                        pygame.draw.polygon(surface, _lighten(body_col, 40), [(cx, cy - 3), (cx + 2, cy), (cx, cy + 3), (cx - 2, cy)])
                    elif snake_type == SNAKE_SKELETON:
                        # Ribben-knogler
                        if is_h:
                            pygame.draw.line(surface, belly_col, (cx, py + 3), (cx, py + cs - 3), 1)
                            if i % 2 == 0:
                                pygame.draw.line(surface, belly_col, (cx - 3, cy), (cx + 3, cy), 1)
                        else:
                            pygame.draw.line(surface, belly_col, (px + 3, cy), (px + cs - 3, cy), 1)
                            if i % 2 == 0:
                                pygame.draw.line(surface, belly_col, (cx, cy - 3), (cx, cy + 3), 1)
                    elif snake_type == SNAKE_LAVA and i % 2 == 0:
                        # Glødende revner
                        glow = (255, 120 + int(40 * math.sin(tick * 0.3 + i)), 20)
                        pygame.draw.line(surface, glow, (px + 3, py + 3), (px + cs - 4, py + cs - 4), 1)
                        pygame.draw.line(surface, glow, (px + cs - 4, py + 3), (px + 3, py + cs - 4), 1)
                    elif snake_type == SNAKE_ELECTRIC and i % 2 == 0:
                        # Lyn-zigzag
                        bolt_col = (255, 255, 100)
                        if is_h:
                            pygame.draw.lines(surface, bolt_col, False, [(px + 2, cy - 3), (cx, cy), (px + cs - 3, cy - 3)], 1)
                        else:
                            pygame.draw.lines(surface, bolt_col, False, [(cx - 3, py + 2), (cx, cy), (cx - 3, py + cs - 3)], 1)
                    elif snake_type == SNAKE_DIAMOND and i % 2 == 0:
                        # Facet-linjer
                        pygame.draw.line(surface, _lighten(body_col, 35), (px + 3, py + 3), (px + cs - 4, py + cs - 4), 1)
                        pygame.draw.line(surface, _lighten(body_col, 25), (px + cs - 4, py + 3), (px + 3, py + cs - 4), 1)


class FoodItem:
    def __init__(self, food_type, pos):
        self.food_type = food_type
        self.pos = pos
        self.lifetime = None
        self.age = 0
        if food_type == FOOD_BONUS:
            self.color = GOLD
            self.points = 3
            self.lifetime = 80
        elif food_type == FOOD_INVINCIBLE:
            self.color = PURPLE
            self.points = 0
            self.lifetime = 60
        elif food_type == FOOD_MEGA:
            self.color = (255, 50, 255)  # hot pink/magenta
            self.points = 100
            self.lifetime = 120  # forsvinder efter 120 ticks
        else:
            self.color = RED
            self.points = 1
            self.lifetime = None

    @property
    def expired(self):
        return self.lifetime is not None and self.age >= self.lifetime

    def tick(self):
        self.age += 1

    def draw(self, surface, game_tick):
        x, y = self.pos
        base_x = x * CELL_SIZE
        base_y = y * CELL_SIZE + SCOREBOARD_H

        if self.food_type == FOOD_NORMAL:
            # 3D Æble-look
            cx = base_x + CELL_SIZE // 2
            cy = base_y + CELL_SIZE // 2
            r = CELL_SIZE // 2 - 3
            draw_3d_circle(surface, self.color, (cx, cy + 1), r, depth=2)
            # Lys plet for glans
            draw_3d_circle(surface, (180, 30, 30), (cx - 2, cy - 1), r - 2, depth=1)
            # 3D Blad
            pygame.draw.ellipse(surface, _darken((50, 160, 50), 30), (cx + 1, cy - CELL_SIZE // 2 + 2, 6, 4))
            pygame.draw.ellipse(surface, (50, 160, 50), (cx, cy - CELL_SIZE // 2 + 1, 6, 4))
            pygame.draw.ellipse(surface, _lighten((50, 160, 50), 30), (cx + 1, cy - CELL_SIZE // 2 + 1, 3, 2))

        elif self.food_type == FOOD_BONUS:
            pulse = (math.sin(game_tick * 0.15) + 1) / 2
            size_offset = int(2 * pulse)
            rect = pygame.Rect(
                base_x + 2 - size_offset, base_y + 2 - size_offset,
                CELL_SIZE - 4 + size_offset * 2, CELL_SIZE - 4 + size_offset * 2
            )
            draw_3d_rect(surface, self.color, rect, depth=3)
            font = pygame.font.SysFont("Consolas", 12, bold=True)
            txt = font.render("3", True, BLACK)
            surface.blit(txt, txt.get_rect(center=rect.center))

        elif self.food_type == FOOD_INVINCIBLE:
            blink = (math.sin(game_tick * 0.3) + 1) / 2
            alpha = int(100 + 155 * blink)
            r, g, b = self.color
            blended = (
                min(255, int(r * alpha / 255)),
                min(255, int(g * alpha / 255)),
                min(255, int(b * alpha / 255)),
            )
            cx = base_x + CELL_SIZE // 2
            cy = base_y + CELL_SIZE // 2
            s = CELL_SIZE // 2 - 2
            # 3D diamant med skygge
            shadow_pts = [(cx + 2, cy - s + 2), (cx + s + 2, cy + 2), (cx + 2, cy + s + 2), (cx - s + 2, cy + 2)]
            pygame.draw.polygon(surface, _darken(blended, 60), shadow_pts)
            points = [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]
            pygame.draw.polygon(surface, blended, points)
            # Highlight top-facet
            pygame.draw.line(surface, _lighten(blended, 60), (cx, cy - s), (cx + s, cy), 1)
            pygame.draw.line(surface, _lighten(blended, 60), (cx - s, cy), (cx, cy - s), 1)
            draw_3d_circle(surface, WHITE, (cx, cy), 2, depth=1)

        elif self.food_type == FOOD_MEGA:
            # Mega-mad: glødende stjerne, 100 point
            cx = base_x + CELL_SIZE // 2
            cy = base_y + CELL_SIZE // 2
            pulse = (math.sin(game_tick * 0.2) + 1) / 2
            glow_r = int(CELL_SIZE // 2 + 3 * pulse)
            # Ydre glow
            glow_col = (
                min(255, int(180 + 75 * pulse)),
                min(255, int(30 + 50 * pulse)),
                min(255, int(200 + 55 * pulse)),
            )
            pygame.draw.circle(surface, _darken(glow_col, 60), (cx, cy), glow_r, 1)
            pygame.draw.circle(surface, _darken(glow_col, 30), (cx, cy), glow_r - 1, 1)
            # Stjerne (6 spidser)
            s = CELL_SIZE // 2 - 1
            inner = s // 2
            pts = []
            for j in range(12):
                ang = math.pi / 2 + j * math.pi / 6
                r = s if j % 2 == 0 else inner
                pts.append((int(cx + r * math.cos(ang)), int(cy - r * math.sin(ang))))
            # Skygge
            shadow_pts = [(p[0] + 1, p[1] + 1) for p in pts]
            pygame.draw.polygon(surface, _darken(self.color, 60), shadow_pts)
            # Hovedform
            pygame.draw.polygon(surface, self.color, pts)
            # Highlight
            pygame.draw.polygon(surface, _lighten(self.color, 40), pts, 1)
            # "100" tekst
            font = pygame.font.SysFont("Consolas", 8, bold=True)
            txt = font.render("100", True, WHITE)
            surface.blit(txt, txt.get_rect(center=(cx, cy)))
            # Glans-prik
            draw_3d_circle(surface, WHITE, (cx - 2, cy - 3), 2, depth=1)


class Coin:
    _font = None

    def __init__(self, pos):
        self.pos = pos
        self.age = 0
        self.lifetime = 120  # forsvinder efter 120 ticks

    @property
    def expired(self):
        return self.age >= self.lifetime

    def tick(self):
        self.age += 1

    def draw(self, surface, game_tick):
        x, y = self.pos
        px = x * CELL_SIZE
        py = y * CELL_SIZE + SCOREBOARD_H
        cx = px + CELL_SIZE // 2
        cy = py + CELL_SIZE // 2
        # 3D spinnende mønt-effekt
        phase = math.sin(game_tick * 0.15)
        w = max(2, int((CELL_SIZE // 2 - 2) * abs(phase)))
        h = CELL_SIZE // 2 - 2
        rect = pygame.Rect(cx - w, cy - h, w * 2, h * 2)
        col = COIN_COLOR if phase > 0 else COIN_COLOR_DARK
        # Skygge
        shadow_rect = pygame.Rect(cx - w + 2, cy - h + 2, w * 2, h * 2)
        pygame.draw.ellipse(surface, _darken(col, 70), shadow_rect)
        # Mønt
        pygame.draw.ellipse(surface, col, rect)
        # Highlight bue øverst
        if w > 3:
            hl_rect = pygame.Rect(cx - w + 2, cy - h + 1, w * 2 - 4, h)
            pygame.draw.ellipse(surface, _lighten(col, 50), hl_rect)
        # Kant
        pygame.draw.ellipse(surface, _darken(col, 30), rect, 1)
        # "$" symbol
        if abs(phase) > 0.3:
            if Coin._font is None:
                Coin._font = pygame.font.SysFont("Consolas", 11, bold=True)
            txt = Coin._font.render("$", True, (100, 70, 0))
            surface.blit(txt, txt.get_rect(center=(cx, cy)))


class MoneyBill:
    """Pengeseddel der giver 10 coins når den samles op."""
    _font = None

    def __init__(self, pos):
        self.pos = pos
        self.age = 0
        self.lifetime = 180  # forsvinder efter 180 ticks (lidt længere end coins)

    @property
    def expired(self):
        return self.age >= self.lifetime

    def tick(self):
        self.age += 1

    def draw(self, surface, game_tick):
        x, y = self.pos
        px = x * CELL_SIZE
        py = y * CELL_SIZE + SCOREBOARD_H
        cx = px + CELL_SIZE // 2
        cy = py + CELL_SIZE // 2

        # Svævende/vibrerende effekt
        float_offset = int(math.sin(game_tick * 0.1) * 2)
        cy += float_offset

        # Pengeseddel størrelse (rektangulær)
        bill_w = CELL_SIZE - 4
        bill_h = int(CELL_SIZE * 0.6)

        # Skygge
        shadow_rect = pygame.Rect(cx - bill_w // 2 + 2, cy - bill_h // 2 + 2, bill_w, bill_h)
        pygame.draw.rect(surface, _darken(MONEY_BILL_COLOR, 100), shadow_rect, border_radius=2)

        # Pengeseddel baggrund
        bill_rect = pygame.Rect(cx - bill_w // 2, cy - bill_h // 2, bill_w, bill_h)
        pygame.draw.rect(surface, MONEY_BILL_COLOR, bill_rect, border_radius=2)

        # Mørk kant
        pygame.draw.rect(surface, MONEY_BILL_DARK, bill_rect, 2, border_radius=2)

        # Dekorativ kant indeni
        inner_rect = pygame.Rect(cx - bill_w // 2 + 3, cy - bill_h // 2 + 2, bill_w - 6, bill_h - 4)
        pygame.draw.rect(surface, _darken(MONEY_BILL_COLOR, 30), inner_rect, 1, border_radius=1)

        # "10" tekst i midten
        if MoneyBill._font is None:
            MoneyBill._font = pygame.font.SysFont("Consolas", 10, bold=True)
        txt = MoneyBill._font.render("10", True, (30, 80, 30))
        surface.blit(txt, txt.get_rect(center=(cx, cy)))


class EnemyDog:
    """Fjendtlig hund der jager slangen og dræber ved kontakt."""
    DOG_MOVE_INTERVAL = 3  # bevæger sig hvert N. game-tick (langsommere end slangen)
    DOG_BODY = (140, 90, 45)
    DOG_BODY_DARK = (100, 65, 30)
    DOG_EAR = (110, 70, 35)
    DOG_EYE = (30, 30, 30)
    DOG_NOSE = (20, 15, 15)
    DOG_TONGUE = (220, 80, 80)

    def __init__(self, pos):
        self.x, self.y = pos
        self.alive = True
        self.move_cd = 0
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def pos(self):
        return (self.x, self.y)

    def update(self, target_pos, ruins, occupied):
        """Bevæg hunden mod target (slangens hoved)."""
        self.move_cd -= 1
        if self.move_cd > 0:
            return
        self.move_cd = self.DOG_MOVE_INTERVAL
        tx, ty = target_pos
        # Simpel AI: bevæg mod target, undgå ruiner
        dx = (1 if tx > self.x else -1) if tx != self.x else 0
        dy = (1 if ty > self.y else -1) if ty != self.y else 0
        # Prøv primær retning (største afstand først)
        moves = []
        if abs(tx - self.x) >= abs(ty - self.y):
            moves = [(dx, 0), (0, dy), (-dx, 0), (0, -dy)]
        else:
            moves = [(0, dy), (dx, 0), (0, -dy), (-dx, 0)]
        for mx, my in moves:
            if mx == 0 and my == 0:
                continue
            nx, ny = self.x + mx, self.y + my
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H and (nx, ny) not in ruins and (nx, ny) not in occupied:
                self.x, self.y = nx, ny
                self.direction = (mx, my)
                return
        # Sidst: tilfældig retning
        random.shuffle(moves)
        for mx, my in moves:
            if mx == 0 and my == 0:
                continue
            nx, ny = self.x + mx, self.y + my
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H and (nx, ny) not in ruins:
                self.x, self.y = nx, ny
                self.direction = (mx, my)
                return

    def draw(self, surface, game_tick):
        """Tegn realistisk 3D-hund med pels-tekstur og animerede detaljer."""
        px = self.x * CELL_SIZE
        py = self.y * CELL_SIZE + SCOREBOARD_H
        cs = CELL_SIZE
        cx = px + cs // 2
        cy = py + cs // 2
        dx, dy = self.direction
        body_r = cs // 2 - 1
        # Blød skygge på jorden
        sh = pygame.Surface((body_r * 2 + 4, body_r + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 45), (0, 0, body_r * 2 + 4, body_r + 2))
        surface.blit(sh, (cx - body_r - 2, cy + body_r // 2))
        # Bagben (animerede - bag kroppen)
        leg_anim = math.sin(game_tick * 0.6) * 2
        for side in [-1, 1]:
            lx = cx + side * 3 - dx * 3
            ly = cy - dy * 3 + side * (1 if dx != 0 else 0)
            lo = int(leg_anim * side)
            pygame.draw.line(surface, self.DOG_BODY_DARK, (lx, ly), (lx + lo, ly + 3), 2)
            pygame.draw.circle(surface, _darken(self.DOG_BODY_DARK, 15), (lx + lo, ly + 3), 1)
        # Krop (oval med pels-gradient)
        draw_3d_circle(surface, self.DOG_BODY, (cx, cy), body_r, depth=2)
        # Pels-tekstur (subtile streger)
        rng_fur = random.Random(self.x * 100 + self.y)
        for _ in range(5):
            fx = cx + rng_fur.randint(-body_r + 2, body_r - 2)
            fy = cy + rng_fur.randint(-body_r + 2, body_r - 2)
            pygame.draw.line(surface, _darken(self.DOG_BODY, 12), (fx, fy), (fx + rng_fur.randint(-2, 2), fy + rng_fur.randint(-2, 2)), 1)
        # Mave (lysere underside)
        belly_s = pygame.Surface((body_r, body_r // 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(belly_s, (*_lighten(self.DOG_BODY, 25), 100), (0, 0, body_r, body_r // 2 + 2))
        surface.blit(belly_s, (cx - body_r // 2, cy))
        # Forben (foran kroppen)
        for side in [-1, 1]:
            lx = cx + side * 3 + dx * 2
            ly = cy + dy * 2 + side * (1 if dx != 0 else 0)
            lo = int(-leg_anim * side)
            pygame.draw.line(surface, self.DOG_BODY_DARK, (lx, ly), (lx + lo, ly + 3), 2)
            pygame.draw.circle(surface, _darken(self.DOG_BODY_DARK, 15), (lx + lo, ly + 3), 1)
        # Hale (vipper)
        tail_wag = math.sin(game_tick * 0.8) * 3
        tail_x = cx - dx * (body_r - 1)
        tail_y = cy - dy * (body_r - 1)
        tail_end_x = tail_x - dx * 4 + int(tail_wag * (-dy if dy == 0 else 0))
        tail_end_y = tail_y - dy * 4 + int(tail_wag * (-dx if dx == 0 else 0))
        pygame.draw.line(surface, self.DOG_BODY_DARK, (tail_x, tail_y), (tail_end_x, tail_end_y), 2)
        # Ører (triangulære, realistiske)
        ear_off = 4
        for side in [-1, 1]:
            ex = cx + side * ear_off - dx * 3
            ey = cy + side * (0 if dx != 0 else ear_off) - dy * 3
            pts = [(ex, ey - 3), (ex + side * 2, ey - 5), (ex + side * 3, ey)]
            pygame.draw.polygon(surface, self.DOG_EAR, pts)
            pygame.draw.polygon(surface, _darken(self.DOG_EAR, 20), pts, 1)
            # Indre øre
            pygame.draw.polygon(surface, _lighten(self.DOG_EAR, 30), [(ex, ey - 2), (ex + side * 1, ey - 4), (ex + side * 2, ey)])
        # Snude (lidt frem fra hovedet)
        snout_x = cx + dx * 4
        snout_y = cy + dy * 4
        draw_3d_circle(surface, _lighten(self.DOG_BODY, 15), (snout_x, snout_y), 3, depth=1)
        # Øjne (røde, glødende - fjendtlige!)
        for side in [-1, 1]:
            eye_x = cx + dx * 3 + side * (-dy) * 2
            eye_y = cy + dy * 3 + side * dx * 2
            # Øjenhule
            pygame.draw.circle(surface, (30, 10, 10), (eye_x, eye_y), 3)
            # Rød iris
            pygame.draw.circle(surface, (200, 30, 30), (eye_x, eye_y), 2)
            # Lysende pupil
            glow = int(200 + 55 * math.sin(game_tick * 0.3))
            pygame.draw.circle(surface, (glow, 60, 60), (eye_x, eye_y), 1)
        # Næse (blank, realistisk)
        nose_x = cx + dx * 6
        nose_y = cy + dy * 6
        pygame.draw.circle(surface, (15, 10, 10), (nose_x, nose_y), 2)
        pygame.draw.circle(surface, (40, 30, 30), (nose_x - 1, nose_y - 1), 1)
        # Tunge (animeret, blødt)
        if game_tick % 10 < 5:
            tongue_len = 2 + int(math.sin(game_tick * 0.4) * 1)
            tongue_x = nose_x + dx * tongue_len
            tongue_y = nose_y + dy * tongue_len + 1
            pygame.draw.line(surface, self.DOG_TONGUE, (nose_x, nose_y + 1), (tongue_x, tongue_y), 2)
            pygame.draw.circle(surface, _lighten(self.DOG_TONGUE, 30), (tongue_x, tongue_y), 1)


class Bullet:
    def __init__(self, pos, direction, owner_idx, gun_type=GUN_BASIC):
        self.x, self.y = pos
        self.direction = direction
        self.owner_idx = owner_idx  # 0 = spiller 1, 1 = spiller 2
        self.gun_type = gun_type
        self.alive = True
        self.age = 0

    def move(self):
        dx, dy = self.direction
        self.x += dx
        self.y += dy
        self.age += 1

    def pos(self):
        return (self.x, self.y)

    def is_out_of_bounds(self):
        return self.x < 0 or self.x >= GRID_W or self.y < 0 or self.y >= GRID_H

    def draw(self, surface):
        px = self.x * CELL_SIZE + CELL_SIZE // 2
        py = self.y * CELL_SIZE + SCOREBOARD_H + CELL_SIZE // 2
        if self.gun_type == GUN_AUTO:
            # Auto: 3D grøn energi-kugle med hale
            draw_3d_circle(surface, (80, 220, 80), (px, py), 4, depth=2)
            draw_3d_circle(surface, (150, 255, 150), (px, py), 2, depth=1)
            dx, dy = self.direction
            draw_3d_circle(surface, (60, 160, 60), (px - dx * 4, py - dy * 4), 2, depth=1)
        elif self.gun_type == GUN_QUAD:
            # Quad: 3D rød plasma med glow
            draw_3d_circle(surface, (220, 60, 60), (px, py), 5, depth=2)
            draw_3d_circle(surface, (255, 150, 80), (px, py), 3, depth=1)
            pygame.draw.circle(surface, YELLOW, (px, py), 1)
        else:
            # Basic: 3D orange kugle
            draw_3d_circle(surface, BULLET_COLOR, (px, py), 4, depth=2)
            draw_3d_circle(surface, YELLOW, (px, py), 2, depth=1)


def draw_ruins(surface, ruins, difficulty=0):
    """Tegn realistiske 3D-ruiner med sten-tekstur, revner, mos og forvitring."""
    theme = MAP_THEMES.get(difficulty, MAP_THEMES[0])
    r_med = theme["ruin_med"]
    r_dark = theme["ruin_dark"]
    r_light = theme.get("ruin_light", _lighten(r_med, 20))  # bruges i sten-fuger
    r_moss = theme["ruin_moss"]
    rng = random.Random(42)
    depth = 3
    for (x, y) in ruins:
        px = x * CELL_SIZE
        py = y * CELL_SIZE + SCOREBOARD_H
        cs = CELL_SIZE
        draw_3d_rect(surface, r_med, (px, py, cs, cs), depth=depth)
        # Sten-tekstur (vandrette og lodrette fuger med highlight)
        for fy in range(py + 3, py + cs - 2, 5):
            offset = rng.randint(0, 4)
            pygame.draw.line(surface, r_dark, (px + 2 + offset, fy), (px + cs - 3, fy), 1)
            pygame.draw.line(surface, r_light, (px + 2 + offset, fy + 1), (px + cs - 3, fy + 1), 1)
        for fx in range(px + 4, px + cs - 2, 6):
            fy_start = py + rng.randint(2, 5)
            pygame.draw.line(surface, r_dark, (fx, fy_start), (fx, fy_start + rng.randint(3, 6)), 1)
        # Revner (realistiske uregelmæssige)
        if rng.random() < 0.5:
            cx = px + rng.randint(4, cs - 4)
            cy = py + rng.randint(4, cs - 4)
            for _ in range(rng.randint(2, 4)):
                nx = cx + rng.randint(-4, 4)
                ny = cy + rng.randint(-4, 4)
                pygame.draw.line(surface, _darken(r_dark, 15), (cx, cy), (nx, ny), 1)
                cx, cy = nx, ny
        # Forvitring (mørke pletter)
        for _ in range(rng.randint(1, 3)):
            wx = px + rng.randint(3, cs - 4)
            wy = py + rng.randint(3, cs - 4)
            wr = rng.randint(1, 2)
            ws = pygame.Surface((wr * 2, wr * 2), pygame.SRCALPHA)
            pygame.draw.circle(ws, (*_darken(r_med, 25), 80), (wr, wr), wr)
            surface.blit(ws, (wx - wr, wy - wr))
        # Mos med alpha-blending
        if rng.random() < 0.4:
            mx = px + rng.randint(2, cs - 6)
            my = py + rng.randint(2, cs - 6)
            mr = rng.randint(2, 4)
            ms = pygame.Surface((mr * 2 + 2, mr * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(ms, (*r_moss, 160), (mr + 1, mr + 1), mr)
            pygame.draw.circle(ms, (*_lighten(r_moss, 20), 100), (mr, mr), max(1, mr - 1))
            surface.blit(ms, (mx - mr - 1, my - mr - 1))


def _make_sound(sample_rate=22050):
    """Generer lyd-effekter som pygame Sound-objekter."""
    sounds = {}

    # --- BASIC skud: SHOTGUN BLAST - massiv eksplosion ---
    dur = 0.35
    n = int(sample_rate * dur)
    buf = bytearray(n * 2)
    rng_s = random.Random(99)
    for i in range(n):
        t = i / sample_rate
        frac = i / n
        # Massiv noise-eksplosion de første 60ms
        noise_env = max(0.0, 1.0 - frac * 5) if frac < 0.18 else max(0.0, 0.3 * (1.0 - frac * 2))
        noise = noise_env * (rng_s.random() * 2 - 1)
        # Dyb tone-sweep 1500->60Hz
        freq = 1500 * (1.0 - frac) ** 2 + 60
        tone_env = max(0.0, 1.0 - frac * 2.0)
        tone = tone_env * math.sin(2 * math.pi * freq * t)
        # Distorted bass-punch 55Hz
        bass_env = max(0.0, 1.0 - frac * 3) if frac < 0.35 else 0.0
        bass_raw = math.sin(2 * math.pi * 55 * t)
        bass = bass_env * 0.8 * max(-1.0, min(1.0, bass_raw * 3.0))
        # Mid-crunch 300Hz
        crunch_env = max(0.0, 1.0 - frac * 4) if frac < 0.25 else 0.0
        crunch = crunch_env * 0.4 * math.sin(2 * math.pi * 300 * t)
        s = (0.40 * noise + 0.30 * tone + 0.20 * bass + 0.10 * crunch) * 1.3
        val = int(s * 32767)
        struct.pack_into('<h', buf, i * 2, max(-32768, min(32767, val)))
    sounds["shoot_basic"] = pygame.mixer.Sound(buffer=bytes(buf))

    # --- AUTO skud: EXPLOSIVE BURST - distorted laser-eksplosion ---
    dur = 0.18
    n = int(sample_rate * dur)
    buf = bytearray(n * 2)
    rng_a = random.Random(55)
    for i in range(n):
        t = i / sample_rate
        frac = i / n
        # Noise-blast
        noise_env = max(0.0, 1.0 - frac * 6) if frac < 0.15 else 0.0
        noise = noise_env * (rng_a.random() * 2 - 1)
        # Dobbelt distorted laser-sweep
        f1 = 2800 - 2400 * frac
        f2 = 1800 - 1500 * frac
        env = max(0.0, 1.0 - frac * 2.5)
        raw1 = math.sin(2 * math.pi * f1 * t)
        raw2 = math.sin(2 * math.pi * f2 * t)
        zap = env * (0.35 * max(-1.0, min(1.0, raw1 * 2.5)) + 0.25 * max(-1.0, min(1.0, raw2 * 2.0)))
        # Bass-thump
        bass_env = max(0.0, 1.0 - frac * 5) if frac < 0.2 else 0.0
        bass = bass_env * 0.5 * math.sin(2 * math.pi * 90 * t)
        s = (0.35 * noise + 0.45 * zap + 0.20 * bass) * 1.2
        val = int(s * 32767)
        struct.pack_into('<h', buf, i * 2, max(-32768, min(32767, val)))
    sounds["shoot_auto"] = pygame.mixer.Sound(buffer=bytes(buf))

    # --- QUAD skud: MEGA-BOOM - massiv eksplosion med sub-bass og ekko ---
    dur = 0.55
    n = int(sample_rate * dur)
    buf = bytearray(n * 2)
    rng_q = random.Random(77)
    for i in range(n):
        t = i / sample_rate
        frac = i / n
        # Full-clip noise-eksplosion
        noise_env = max(0.0, 1.0 - frac * 4) if frac < 0.25 else max(0.0, 0.2 * (1.0 - frac * 1.5))
        noise = noise_env * (rng_q.random() * 2 - 1)
        # Cubic sweep 800->25Hz for ekstra tyngde
        sweep_frac = min(1.0, frac * 1.5)
        freq = 800 * (1.0 - sweep_frac) ** 3 + 25
        tone_env = max(0.0, 1.0 - frac * 1.5)
        tone = tone_env * math.sin(2 * math.pi * freq * t)
        # Sub-bass vibrato 35Hz med tremolo
        sub_env = max(0.0, 1.0 - frac * 1.8)
        sub = sub_env * 0.7 * math.sin(2 * math.pi * 35 * t) * (1.0 + 0.5 * math.sin(2 * math.pi * 8 * t))
        # Distorted mid-crunch
        crunch_env = max(0.0, 1.0 - frac * 3) if frac < 0.3 else 0.0
        crunch_raw = math.sin(2 * math.pi * 200 * t) + 0.5 * math.sin(2 * math.pi * 150 * t)
        crunch = crunch_env * 0.4 * max(-1.0, min(1.0, crunch_raw * 3.0))
        # Ekko-bølge efter 120ms
        echo = 0.0
        if t > 0.12:
            te = t - 0.12
            echo_frac = te / (dur - 0.12)
            echo_env = max(0.0, 0.5 * (1.0 - echo_frac * 2))
            echo = echo_env * math.sin(2 * math.pi * (300 - 250 * echo_frac) * te)
        s = (0.30 * noise + 0.25 * tone + 0.20 * sub + 0.15 * crunch + 0.10 * echo) * 1.5
        val = int(s * 32767)
        struct.pack_into('<h', buf, i * 2, max(-32768, min(32767, val)))
    sounds["shoot_quad"] = pygame.mixer.Sound(buffer=bytes(buf))

    # --- VACUUM skud: STØVSUGER-HVINEN - stigende sug med luft-woosh ---
    dur = 0.25
    n = int(sample_rate * dur)
    buf = bytearray(n * 2)
    rng_v = random.Random(33)
    for i in range(n):
        t = i / sample_rate
        frac = i / n
        # Luftstrøm-noise (konstant sugelyd)
        air_env = 0.6 * (0.8 + 0.2 * math.sin(2 * math.pi * 12 * t))
        air = air_env * (rng_v.random() * 2 - 1)
        # Stigende hvine-tone 200->800Hz (sugelyd)
        whine_freq = 200 + 600 * frac
        whine_env = 0.5 + 0.3 * frac
        whine = whine_env * math.sin(2 * math.pi * whine_freq * t)
        # Dyb motor-brummen 60Hz
        motor = 0.3 * math.sin(2 * math.pi * 60 * t) * (1.0 + 0.4 * math.sin(2 * math.pi * 6 * t))
        # Fade in/out
        fade = min(1.0, frac * 8) * min(1.0, (1.0 - frac) * 5)
        s = fade * (0.35 * air + 0.40 * whine + 0.25 * motor)
        val = int(s * 32767)
        struct.pack_into('<h', buf, i * 2, max(-32768, min(32767, val)))
    sounds["shoot_vacuum"] = pygame.mixer.Sound(buffer=bytes(buf))

    # Død-lyd: faldende tone (0.4s, 500->80Hz)
    dur = 0.4
    n = int(sample_rate * dur)
    buf = bytearray(n * 2)
    for i in range(n):
        t = i / sample_rate
        frac = i / n
        freq = 500 - 420 * frac
        vol = 0.3 * (1 - frac * 0.7)
        val = int(vol * 32767 * math.sin(2 * math.pi * freq * t))
        struct.pack_into('<h', buf, i * 2, max(-32768, min(32767, val)))
    sounds["death"] = pygame.mixer.Sound(buffer=bytes(buf))

    # --- Coin pling: kort krystalklart pling ---
    dur = 0.15
    n = int(sample_rate * dur)
    buf = bytearray(n * 2)
    for i in range(n):
        t = i / sample_rate
        frac = i / n
        env = max(0.0, 1.0 - frac * 3) if frac < 0.33 else max(0.0, (1.0 - frac) * 1.5)
        # Høj klar tone 1200Hz + overtone 2400Hz
        s = env * (0.5 * math.sin(2 * math.pi * 1200 * t) +
                   0.3 * math.sin(2 * math.pi * 2400 * t) +
                   0.2 * math.sin(2 * math.pi * 3600 * t))
        val = int(s * 0.4 * 32767)
        struct.pack_into('<h', buf, i * 2, max(-32768, min(32767, val)))
    sounds["coin_pling"] = pygame.mixer.Sound(buffer=bytes(buf))

    # --- Æble nam-nam: to korte bløde "nam" lyde ---
    dur = 0.3
    n = int(sample_rate * dur)
    buf = bytearray(n * 2)
    rng_nom = random.Random(42)
    for i in range(n):
        t = i / sample_rate
        frac = i / n
        # To "nam" bumps ved 0.0-0.12s og 0.15-0.27s
        if frac < 0.4:
            bite_t = frac / 0.4
            env = math.sin(math.pi * bite_t) * 0.8
        elif frac < 0.5:
            env = 0.0
        else:
            bite_t = (frac - 0.5) / 0.4
            env = math.sin(math.pi * min(1.0, bite_t)) * 0.6
        # Blød crunch-lyd (lav tone + lidt noise)
        tone = math.sin(2 * math.pi * 180 * t) + 0.5 * math.sin(2 * math.pi * 300 * t)
        noise = (rng_nom.random() * 2 - 1) * 0.3
        s = env * (0.6 * tone + 0.4 * noise)
        val = int(s * 0.35 * 32767)
        struct.pack_into('<h', buf, i * 2, max(-32768, min(32767, val)))
    sounds["eat_apple"] = pygame.mixer.Sound(buffer=bytes(buf))

    # --- Mega food spawn fanfare: majestætisk stigende akkord ---
    dur = 1.2
    n = int(sample_rate * dur)
    buf = bytearray(n * 2)
    for i in range(n):
        t = i / sample_rate
        frac = i / n
        # Fade in hurtigt, hold, fade ud blødt
        if frac < 0.05:
            env = frac / 0.05
        elif frac < 0.7:
            env = 1.0
        else:
            env = max(0.0, (1.0 - frac) / 0.3)
        # Tre toner der kommer ind forskudt: C5, E5, G5 (dur-akkord)
        c5 = 523.25
        e5 = 659.25
        g5 = 783.99
        c6 = 1046.50
        t1 = math.sin(2 * math.pi * c5 * t) * min(1.0, t * 8)
        t2 = math.sin(2 * math.pi * e5 * t) * min(1.0, max(0.0, (t - 0.1) * 6))
        t3 = math.sin(2 * math.pi * g5 * t) * min(1.0, max(0.0, (t - 0.2) * 5))
        t4 = math.sin(2 * math.pi * c6 * t) * min(1.0, max(0.0, (t - 0.35) * 4))
        # Shimmer
        shimmer = 0.15 * math.sin(2 * math.pi * 12 * t) * math.sin(2 * math.pi * g5 * 2 * t)
        s = env * (0.25 * t1 + 0.25 * t2 + 0.25 * t3 + 0.15 * t4 + 0.10 * shimmer)
        val = int(s * 0.5 * 32767)
        struct.pack_into('<h', buf, i * 2, max(-32768, min(32767, val)))
    sounds["mega_spawn"] = pygame.mixer.Sound(buffer=bytes(buf))

    # --- Fjendtlig hund: aggressivt gø ---
    dur = 0.2
    n = int(sample_rate * dur)
    buf = bytearray(n * 2)
    rng_bark = random.Random(66)
    for i in range(n):
        t = i / sample_rate
        frac = i / n
        # To hurtige "vov"-bumps
        if frac < 0.4:
            env = math.sin(math.pi * frac / 0.4) * 0.9
        elif frac < 0.5:
            env = 0.0
        else:
            env = math.sin(math.pi * (frac - 0.5) / 0.4) * 0.7 if frac < 0.9 else 0.0
        # Rå tone 150Hz + noise for gø-lyd
        tone = math.sin(2 * math.pi * 150 * t) + 0.6 * math.sin(2 * math.pi * 250 * t)
        noise = (rng_bark.random() * 2 - 1) * 0.4
        s = env * (0.55 * tone + 0.45 * noise)
        val = int(s * 0.45 * 32767)
        struct.pack_into('<h', buf, i * 2, max(-32768, min(32767, val)))
    sounds["enemy_bark"] = pygame.mixer.Sound(buffer=bytes(buf))

    # --- Hjælper: generer melodi-samples fra nodeliste ---
    def _melody_samples(notes, vol, attack=0.08, release=0.15):
        """notes: [(freq, dur_sek), ...]. Returnerer list of float samples."""
        out = []
        for freq, dur in notes:
            ns = int(sample_rate * dur)
            att_s = int(sample_rate * attack)
            rel_s = int(sample_rate * release)
            for j in range(ns):
                t = j / sample_rate
                # Envelope: attack + sustain + release
                if j < att_s:
                    env = j / att_s
                elif j > ns - rel_s:
                    env = (ns - j) / rel_s
                else:
                    env = 1.0
                if freq > 0:
                    s = vol * env * math.sin(2 * math.pi * freq * t)
                else:
                    s = 0.0
                out.append(s)
        return out

    # --- MENU-MUSIK: rolig C-dur melodi med pad (ca. 10 sek loop) ---
    # Noder: (frekvens, varighed)
    _C4, _D4, _E4, _F4, _G4 = 261.63, 293.66, 329.63, 349.23, 392.00
    _A4, _B4, _C5, _D5 = 440.00, 493.88, 523.25, 587.33
    _C3, _G3 = 130.81, 196.00
    _R = 0  # pause
    menu_notes = [
        (_E4, 0.45), (_G4, 0.45), (_C5, 0.6), (_B4, 0.3), (_G4, 0.45),
        (_E4, 0.45), (_F4, 0.45), (_A4, 0.6), (_G4, 0.3), (_E4, 0.45),
        (_C4, 0.45), (_D4, 0.45), (_F4, 0.45), (_E4, 0.6), (_R, 0.2),
        (_C4, 0.45), (_D4, 0.45), (_E4, 0.45), (_G4, 0.45), (_C5, 0.6),
        (_A4, 0.3), (_G4, 0.45), (_E4, 0.45), (_D4, 0.45), (_C4, 0.6),
        (_R, 0.3),
    ]
    mel = _melody_samples(menu_notes, 0.10, attack=0.06, release=0.12)
    total_n = len(mel)
    buf = bytearray(total_n * 2)
    for i in range(total_n):
        t = i / sample_rate
        frac = i / total_n
        # Blød pad underneden
        pad_env = math.sin(math.pi * frac)
        pad = 0.025 * pad_env * (
            math.sin(2 * math.pi * _C3 * t)
            + 0.7 * math.sin(2 * math.pi * _G3 * t)
            + 0.4 * math.sin(2 * math.pi * _E4 * t * 0.5)
        )
        # Melodi fader lidt ind/ud ved loop-grænsen
        mel_env = min(1.0, frac * 8, (1.0 - frac) * 8)
        s = mel[i] * mel_env + pad
        val = int(s * 32767)
        struct.pack_into('<h', buf, i * 2, max(-32768, min(32767, val)))
    sounds["menu_music"] = pygame.mixer.Sound(buffer=bytes(buf))

    # --- SPIL-MUSIK: intens A-mol melodi med pulserende bas (ca. 5 sek loop) ---
    _A3, _C4g, _D4g, _E4g, _F4g, _G4g = 220.00, 261.63, 293.66, 329.63, 349.23, 392.00
    _E3, _G3g, _B3 = 164.81, 196.00, 246.94
    _A4g = 440.00
    game_notes = [
        (_A3, 0.16), (_C4g, 0.16), (_E4g, 0.16), (_A4g, 0.12), (_E4g, 0.12),
        (_C4g, 0.16), (_D4g, 0.16), (_F4g, 0.16), (_D4g, 0.12), (_A3, 0.12),
        (_E3, 0.16), (_G3g, 0.16), (_B3, 0.16), (_E4g, 0.12), (_B3, 0.12),
        (_A3, 0.22), (_R, 0.06), (_G3g, 0.16), (_E3, 0.16), (_A3, 0.22),
        (_R, 0.08),
        (_A3, 0.12), (_E4g, 0.12), (_C4g, 0.16), (_A3, 0.12), (_E3, 0.16),
        (_G3g, 0.16), (_A3, 0.22), (_R, 0.06),
    ]
    mel = _melody_samples(game_notes, 0.12, attack=0.02, release=0.05)
    total_n = len(mel)
    buf = bytearray(total_n * 2)
    bpm = 140
    beat_samples = int(sample_rate * 60.0 / bpm)
    rng_hat = random.Random(42)
    for i in range(total_n):
        t = i / sample_rate
        # Pulserende bas (A2 = 110 Hz)
        bp = i % beat_samples
        bf = bp / beat_samples
        bass_env = max(0.0, 1.0 - bf * 2.5)
        bass = 0.10 * bass_env * math.sin(2 * math.pi * 110 * t)
        # Hi-hat
        bp3 = i % (beat_samples // 2)
        bf3 = bp3 / (beat_samples // 2)
        hat_env = max(0.0, 1.0 - bf3 * 8)
        hat = 0.018 * hat_env * (rng_hat.random() * 2 - 1)
        s = mel[i] + bass + hat
        val = int(s * 32767)
        struct.pack_into('<h', buf, i * 2, max(-32768, min(32767, val)))
    sounds["game_music"] = pygame.mixer.Sound(buffer=bytes(buf))

    return sounds


class Game:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.sfx = _make_sound()
        self.font_big = pygame.font.SysFont("Consolas", 36, bold=True)
        self.font_med = pygame.font.SysFont("Consolas", 22)
        self.font_small = pygame.font.SysFont("Consolas", 16)

        self.scores = [0, 0]
        self.coins = [0, 0]
        self.ammo = [0, 0]
        self.power = [0, 0]  # strøm til støvsuger
        self.gun_type = [GUN_NONE, GUN_NONE]  # None, "basic", "auto", "quad", "vacuum"
        self.auto_shoot_cd = [0, 0]
        self.vacuum_cd = [0, 0]
        self.vacuum_active = [False, False]  # om støvsugeren kører lige nu
        self.snake_type = [SNAKE_NORMAL, SNAKE_NORMAL]
        self.state = "MENU"
        self.current_music = None
        self.num_players = 2
        self.difficulty = 1
        self.menu_row = 0
        self.snake1 = Snake((3, 3), RIGHT, GREEN, GREEN_DARK, GREEN_BELLY)
        self.snake2 = Snake((GRID_W - 4, GRID_H - 4), LEFT, BLUE, BLUE_DARK, BLUE_BELLY)
        self.foods = []
        self.coin_items = []
        self.money_bills = []
        self.bullets = []
        self.enemies = []
        self.enemy_spawn_cd = 0
        self.ruins = set()
        self.trees = []
        self.fps = DIFFICULTIES[self.difficulty][1]
        self.round_message = ""
        self.game_tick = 0
        self.special_food_cooldown = 0
        self.coin_spawn_cooldown = 0

        # Highscore
        self.highscore_data = load_highscores()
        self.name_input = ""
        self.name_player_idx = 0
        self.pending_highscores = []

        # Load saved wallet data
        self._load_wallet()
        # Start menu-musik
        self._play_music("menu_music")

    def _load_wallet(self):
        data = load_savedata()
        self.coins[0] = data.get("p1_coins", 0)
        self.coins[1] = data.get("p2_coins", 0)
        self.ammo[0] = data.get("p1_ammo", 0)
        self.ammo[1] = data.get("p2_ammo", 0)
        self.power[0] = data.get("p1_power", 0)
        self.power[1] = data.get("p2_power", 0)
        self.gun_type[0] = data.get("p1_gun", GUN_NONE)
        self.gun_type[1] = data.get("p2_gun", GUN_NONE)
        st0 = data.get("p1_snake_type", SNAKE_NORMAL)
        st1 = data.get("p2_snake_type", SNAKE_NORMAL)
        self.snake_type[0] = st0 if st0 in SNAKE_TYPES_LIST else SNAKE_NORMAL
        self.snake_type[1] = st1 if st1 in SNAKE_TYPES_LIST else SNAKE_NORMAL

    def _save_wallet(self):
        data = {
            "p1_coins": self.coins[0],
            "p2_coins": self.coins[1],
            "p1_ammo": self.ammo[0],
            "p2_ammo": self.ammo[1],
            "p1_power": self.power[0],
            "p2_power": self.power[1],
            "p1_gun": self.gun_type[0],
            "p2_gun": self.gun_type[1],
            "p1_snake_type": self.snake_type[0],
            "p2_snake_type": self.snake_type[1],
        }
        save_savedata(data)

    @property
    def _two_player(self):
        return self.num_players == 2

    def _play_music(self, track_name):
        """Skift baggrundsmusik. Stopper nuværende og starter ny."""
        if self.current_music == track_name:
            return
        # Stop gammel musik
        if self.current_music and self.current_music in self.sfx:
            self.sfx[self.current_music].stop()
        self.current_music = track_name
        if track_name and track_name in self.sfx:
            self.sfx[track_name].play(loops=-1)

    def _stop_music(self):
        if self.current_music and self.current_music in self.sfx:
            self.sfx[self.current_music].stop()
        self.current_music = None

    def _occupied(self):
        positions = set(self.snake1.body)
        if self._two_player:
            positions.update(self.snake2.body)
        positions.update(self.ruins)
        for f in self.foods:
            positions.add(f.pos)
        for c in self.coin_items:
            positions.add(c.pos)
        for b in self.money_bills:
            positions.add(b.pos)
        return positions

    def _spawn_food(self, food_type):
        occupied = self._occupied()
        free = [
            (x, y) for x in range(GRID_W) for y in range(GRID_H)
            if (x, y) not in occupied
        ]
        if free:
            pos = random.choice(free)
            self.foods.append(FoodItem(food_type, pos))

    def _spawn_coin(self):
        occupied = self._occupied()
        free = [
            (x, y) for x in range(GRID_W) for y in range(GRID_H)
            if (x, y) not in occupied
        ]
        if free:
            pos = random.choice(free)
            self.coin_items.append(Coin(pos))

    def _spawn_money_bill(self):
        """Spawn en pengeseddel (10 coins) - sjældnere end normale coins."""
        occupied = self._occupied()
        free = [
            (x, y) for x in range(GRID_W) for y in range(GRID_H)
            if (x, y) not in occupied
        ]
        if free:
            pos = random.choice(free)
            self.money_bills.append(MoneyBill(pos))

    def _shoot(self, player_idx):
        """Spiller skyder. Kræver kanon + ammo."""
        gt = self.gun_type[player_idx]
        if gt is GUN_NONE:
            return
        if gt == GUN_VACUUM:
            return  # støvsuger håndteres separat
        if self.ammo[player_idx] <= 0:
            return
        snake = self.snake1 if player_idx == 0 else self.snake2
        if not snake.alive:
            return
        self.ammo[player_idx] -= 1
        hx, hy = snake.head()
        dx, dy = snake.direction
        if gt == GUN_QUAD:
            # 4 skud i alle retninger
            for d in (UP, DOWN, LEFT, RIGHT):
                self.bullets.append(Bullet((hx + d[0], hy + d[1]), d, player_idx, gt))
        else:
            # 1 skud fremad (basic + auto)
            self.bullets.append(Bullet((hx + dx, hy + dy), snake.direction, player_idx, gt))
        sfx_key = f"shoot_{gt}"
        self.sfx.get(sfx_key, self.sfx["shoot_basic"]).play()

    def _buy_ammo(self, player_idx):
        """Køb ammo: AMMO_PRICE coins for AMMO_AMOUNT skud."""
        if self.coins[player_idx] >= AMMO_PRICE:
            self.coins[player_idx] -= AMMO_PRICE
            self.ammo[player_idx] += AMMO_AMOUNT
            self._save_wallet()

    def _buy_gun(self, player_idx, gun_id):
        """Køb en kanon-type."""
        info = GUN_INFO.get(gun_id)
        if not info:
            return
        price = info[2]
        if self.gun_type[player_idx] == gun_id:
            return  # Har allerede denne type
        if self.coins[player_idx] >= price:
            self.coins[player_idx] -= price
            self.gun_type[player_idx] = gun_id
            self._save_wallet()

    def _buy_power(self, player_idx):
        """Køb strøm: POWER_PRICE coins for POWER_AMOUNT strøm."""
        if self.coins[player_idx] >= POWER_PRICE:
            self.coins[player_idx] -= POWER_PRICE
            self.power[player_idx] += POWER_AMOUNT
            self._save_wallet()

    def _vacuum_suck(self, player_idx):
        """Støvsuger: ryk al mad og coins 1 felt tættere på slangens hoved."""
        snake = self.snake1 if player_idx == 0 else self.snake2
        if not snake.alive:
            return
        hx, hy = snake.head()
        occupied = set()
        if self.snake1.alive:
            occupied.update(self.snake1.body)
        if self._two_player and self.snake2.alive:
            occupied.update(self.snake2.body)
        occupied.update(self.ruins)
        # Ryk mad tættere
        for food in self.foods:
            fx, fy = food.pos
            dist = abs(fx - hx) + abs(fy - hy)
            if dist <= VACUUM_RANGE and dist > 0:
                # Flyt 1 celle mod hovedet
                dx = (1 if hx > fx else -1) if hx != fx else 0
                dy = (1 if hy > fy else -1) if hy != fy else 0
                nx, ny = fx + dx, fy + dy
                # Tjek bounds og ikke blokeret
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H and (nx, ny) not in occupied and (nx, ny) not in self.ruins:
                    food.pos = (nx, ny)
        # Ryk coins tættere
        for coin in self.coin_items:
            cx_c, cy_c = coin.pos
            dist = abs(cx_c - hx) + abs(cy_c - hy)
            if dist <= VACUUM_RANGE and dist > 0:
                dx = (1 if hx > cx_c else -1) if hx != cx_c else 0
                dy = (1 if hy > cy_c else -1) if hy != cy_c else 0
                nx, ny = cx_c + dx, cy_c + dy
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H and (nx, ny) not in occupied and (nx, ny) not in self.ruins:
                    coin.pos = (nx, ny)
        # Ryk pengesedler tættere
        for bill in self.money_bills:
            bx, by = bill.pos
            dist = abs(bx - hx) + abs(by - hy)
            if dist <= VACUUM_RANGE and dist > 0:
                dx = (1 if hx > bx else -1) if hx != bx else 0
                dy = (1 if hy > by else -1) if hy != by else 0
                nx, ny = bx + dx, by + dy
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H and (nx, ny) not in occupied and (nx, ny) not in self.ruins:
                    bill.pos = (nx, ny)

    def _generate_safe_zones(self):
        """Positioner der skal holdes fri for ruiner (spawn-områder)."""
        safe = set()
        # Spiller 1 spawn-zone (øverst venstre)
        for x in range(0, 8):
            for y in range(0, 8):
                safe.add((x, y))
        # Spiller 2 spawn-zone (nederst højre)
        for x in range(GRID_W - 8, GRID_W):
            for y in range(GRID_H - 8, GRID_H):
                safe.add((x, y))
        # Center (for 1-spiller spawn)
        cx, cy = GRID_W // 2, GRID_H // 2
        for x in range(cx - 4, cx + 5):
            for y in range(cy - 4, cy + 5):
                safe.add((x, y))
        return safe

    def new_round(self):
        self.scores = [0, 0]
        # Anvend slange-type farver
        c1 = SNAKE_TYPE_COLORS[self.snake_type[0]][0]
        self.snake1.color, self.snake1.color_dark, self.snake1.color_belly = c1
        c2 = SNAKE_TYPE_COLORS[self.snake_type[1]][1]
        self.snake2.color, self.snake2.color_dark, self.snake2.color_belly = c2
        if self._two_player:
            self.snake1.reset((3, 3), RIGHT)
            self.snake2.reset((GRID_W - 4, GRID_H - 4), LEFT)
        else:
            self.snake1.reset((GRID_W // 2, GRID_H // 2), RIGHT)
            self.snake2.body = []
            self.snake2.alive = False
        # Generer ruiner og træer
        safe = self._generate_safe_zones()
        ruin_count = RUIN_COUNTS[self.difficulty]
        self.ruins = generate_ruins(ruin_count, safe)
        # Træer (dekorative - undgå ruiner og safe zones)
        tree_occupied = set(self.ruins) | safe
        tree_count = TREE_COUNTS[self.difficulty]
        self.trees = generate_trees(tree_count, tree_occupied)
        self.foods = []
        self.coin_items = []
        self.money_bills = []
        self.bullets = []
        self.enemies = []
        self.enemy_spawn_cd = 0
        self._spawn_food(FOOD_NORMAL)
        diff = DIFFICULTIES[self.difficulty]
        self.fps = diff[1]
        self.state = "PLAYING"
        self.game_tick = 0
        self.special_food_cooldown = 0
        self.coin_spawn_cooldown = 0
        self.mega_food_timer = 0.0       # sekund-tæller for mega-food
        self.mega_food_spawned = 0       # antal mega-food spawnet denne runde
        self._play_music("game_music")

    def _start_name_input(self):
        self.pending_highscores = []
        if self._two_player:
            for idx in range(2):
                if is_highscore(self.highscore_data, self.difficulty, self.num_players, self.scores[idx]):
                    self.pending_highscores.append((idx, self.scores[idx]))
        else:
            if is_highscore(self.highscore_data, self.difficulty, self.num_players, self.scores[0]):
                self.pending_highscores.append((0, self.scores[0]))
        if self.pending_highscores:
            self._next_name_input()
        else:
            self.state = "ROUND_OVER"

    def _next_name_input(self):
        if self.pending_highscores:
            self.name_player_idx, _ = self.pending_highscores[0]
            self.name_input = ""
            self.state = "ENTER_NAME"
        else:
            self.state = "ROUND_OVER"

    def _submit_name(self):
        name = self.name_input.strip() or "???"
        _, score = self.pending_highscores.pop(0)
        add_highscore(self.highscore_data, self.difficulty, self.num_players, name, score)
        self._next_name_input()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in ("PLAYING", "ROUND_OVER", "ENTER_NAME"):
                        self.state = "MENU"
                        self._play_music("menu_music")
                        continue
                    else:
                        return False

                if self.state == "MENU":
                    max_row = 8
                    if event.key == pygame.K_SPACE:
                        self.new_round()
                    elif event.key in (pygame.K_w, pygame.K_UP):
                        self.menu_row = max(0, self.menu_row - 1)
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        self.menu_row = min(max_row, self.menu_row + 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if self.menu_row == 0:
                            self.num_players = max(1, self.num_players - 1)
                        elif self.menu_row == 1:
                            self.difficulty = max(0, self.difficulty - 1)
                        elif self.menu_row == 2:
                            # Skift P1 slange-type
                            idx = SNAKE_TYPES_LIST.index(self.snake_type[0])
                            self.snake_type[0] = SNAKE_TYPES_LIST[(idx - 1) % len(SNAKE_TYPES_LIST)]
                            self._save_wallet()
                        elif self.menu_row == 3:
                            self._buy_ammo(0)
                        elif self.menu_row == 4:
                            self._buy_power(0)
                        elif self.menu_row == 5:
                            self._buy_gun(0, GUN_BASIC)
                        elif self.menu_row == 6:
                            self._buy_gun(0, GUN_AUTO)
                        elif self.menu_row == 7:
                            self._buy_gun(0, GUN_QUAD)
                        elif self.menu_row == 8:
                            self._buy_gun(0, GUN_VACUUM)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        p2 = 1 if self._two_player else 0
                        if self.menu_row == 0:
                            self.num_players = min(2, self.num_players + 1)
                        elif self.menu_row == 1:
                            self.difficulty = min(len(DIFFICULTIES) - 1, self.difficulty + 1)
                        elif self.menu_row == 2:
                            # Skift P2 (eller P1 i 1-spiller) slange-type
                            idx = SNAKE_TYPES_LIST.index(self.snake_type[p2])
                            self.snake_type[p2] = SNAKE_TYPES_LIST[(idx + 1) % len(SNAKE_TYPES_LIST)]
                            self._save_wallet()
                        elif self.menu_row == 3:
                            self._buy_ammo(p2)
                        elif self.menu_row == 4:
                            self._buy_power(p2)
                        elif self.menu_row == 5:
                            self._buy_gun(p2, GUN_BASIC)
                        elif self.menu_row == 6:
                            self._buy_gun(p2, GUN_AUTO)
                        elif self.menu_row == 7:
                            self._buy_gun(p2, GUN_QUAD)
                        elif self.menu_row == 8:
                            self._buy_gun(p2, GUN_VACUUM)

                elif self.state == "PLAYING":
                    if event.key == pygame.K_w:
                        self.snake1.set_direction(UP)
                    elif event.key == pygame.K_s:
                        self.snake1.set_direction(DOWN)
                    elif event.key == pygame.K_a:
                        self.snake1.set_direction(LEFT)
                    elif event.key == pygame.K_d:
                        self.snake1.set_direction(RIGHT)
                    elif event.key == pygame.K_e:
                        if self.gun_type[0] != GUN_AUTO:
                            self._shoot(0)
                    elif event.key == pygame.K_UP:
                        (self.snake2 if self._two_player else self.snake1).set_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        (self.snake2 if self._two_player else self.snake1).set_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        (self.snake2 if self._two_player else self.snake1).set_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        (self.snake2 if self._two_player else self.snake1).set_direction(RIGHT)
                    elif event.key == pygame.K_RSHIFT:
                        if self._two_player:
                            if self.gun_type[1] != GUN_AUTO:
                                self._shoot(1)
                        else:
                            if self.gun_type[0] != GUN_AUTO:
                                self._shoot(0)

                elif self.state == "ENTER_NAME":
                    if event.key == pygame.K_RETURN:
                        self._submit_name()
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_input = self.name_input[:-1]
                    elif event.unicode and event.unicode.isprintable() and len(self.name_input) < MAX_NAME_LEN:
                        self.name_input += event.unicode

                elif self.state == "ROUND_OVER":
                    if event.key == pygame.K_SPACE:
                        self.new_round()
                    elif event.key == pygame.K_m:
                        self.state = "MENU"
                        self._play_music("menu_music")

        return True

    def update(self):
        if self.state != "PLAYING":
            return

        self.game_tick += 1

        self.snake1.move()
        if self._two_player:
            self.snake2.move()

        self.snake1.check_wall_collision()
        if self._two_player:
            self.snake2.check_wall_collision()

        self.snake1.check_self_collision()
        if self._two_player:
            self.snake2.check_self_collision()

        # Ruin-kollision
        self.snake1.check_ruin_collision(self.ruins)
        if self._two_player:
            self.snake2.check_ruin_collision(self.ruins)

        if self._two_player and self.snake1.alive and self.snake2.alive:
            s1_hit_s2 = self.snake1.head() in self.snake2.body
            s2_hit_s1 = self.snake2.head() in self.snake1.body
            head_on = self.snake1.head() == self.snake2.head()

            if head_on:
                if not self.snake1.is_invincible:
                    self.snake1.alive = False
                if not self.snake2.is_invincible:
                    self.snake2.alive = False
            else:
                if s1_hit_s2 and not self.snake1.is_invincible:
                    self.snake1.alive = False
                    if not self.snake2.is_invincible:
                        self.snake2.alive = False
                if s2_hit_s1 and not self.snake2.is_invincible:
                    self.snake2.alive = False
                    if not self.snake1.is_invincible:
                        self.snake1.alive = False

        eaten = []
        for food in self.foods:
            if self.snake1.alive and self.snake1.head() == food.pos:
                self.scores[0] += food.points
                self.snake1.grow()
                if food.food_type == FOOD_INVINCIBLE:
                    self.snake1.invincible_timer = 50
                eaten.append(food)
            elif self._two_player and self.snake2.alive and self.snake2.head() == food.pos:
                self.scores[1] += food.points
                self.snake2.grow()
                if food.food_type == FOOD_INVINCIBLE:
                    self.snake2.invincible_timer = 50
                eaten.append(food)

        for food in eaten:
            if food.food_type == FOOD_NORMAL:
                self.sfx["eat_apple"].play()
            elif food.food_type == FOOD_MEGA:
                self.sfx["mega_spawn"].play()  # episk lyd når man spiser den også
            else:
                self.sfx["eat_apple"].play()

        for food in self.foods:
            food.tick()
        self.foods = [
            f for f in self.foods
            if f not in eaten and not f.expired
        ]

        has_normal = any(f.food_type == FOOD_NORMAL for f in self.foods)
        if not has_normal:
            self._spawn_food(FOOD_NORMAL)

        self.special_food_cooldown -= 1
        if self.special_food_cooldown <= 0:
            roll = random.random()
            if roll < 0.03:
                self._spawn_food(FOOD_BONUS)
                self.special_food_cooldown = 30
            elif roll < 0.04:
                self._spawn_food(FOOD_INVINCIBLE)
                self.special_food_cooldown = 60

        # --- Mega-food (100 point, 20 per 10 minutter) ---
        if self.mega_food_spawned < 20:
            self.mega_food_timer += 1.0 / self.fps
            if self.mega_food_timer >= MEGA_FOOD_INTERVAL:
                self.mega_food_timer = 0.0
                self.mega_food_spawned += 1
                self._spawn_food(FOOD_MEGA)
                self.sfx["mega_spawn"].play()

        # --- Coins ---
        self.coin_spawn_cooldown -= 1
        if self.coin_spawn_cooldown <= 0:
            if random.random() < 0.15:
                self._spawn_coin()
                self.coin_spawn_cooldown = 8
            else:
                self.coin_spawn_cooldown = 3

        # --- Money Bills (pengesedler) - sjældnere end coins ---
        if random.random() < 0.003:  # ~0.3% chance per tick
            self._spawn_money_bill()

        # Coin opsamling
        coin_eaten = []
        for coin in self.coin_items:
            if self.snake1.alive and self.snake1.head() == coin.pos:
                self.coins[0] += 1
                coin_eaten.append(coin)
            elif self._two_player and self.snake2.alive and self.snake2.head() == coin.pos:
                self.coins[1] += 1
                coin_eaten.append(coin)
        if coin_eaten:
            self.sfx["coin_pling"].play()
            self._save_wallet()
        for coin in self.coin_items:
            coin.tick()
        self.coin_items = [c for c in self.coin_items if c not in coin_eaten and not c.expired]

        # Money Bill opsamling (10 coins!)
        bills_eaten = []
        for bill in self.money_bills:
            if self.snake1.alive and self.snake1.head() == bill.pos:
                self.coins[0] += MONEY_BILL_VALUE
                bills_eaten.append(bill)
            elif self._two_player and self.snake2.alive and self.snake2.head() == bill.pos:
                self.coins[1] += MONEY_BILL_VALUE
                bills_eaten.append(bill)
        if bills_eaten:
            self.sfx["coin_pling"].play()  # Brug samme lyd (eller lav ny senere)
            self._save_wallet()
        for bill in self.money_bills:
            bill.tick()
        self.money_bills = [b for b in self.money_bills if b not in bills_eaten and not b.expired]

        # --- Auto-kanon (hold-to-fire) ---
        keys = pygame.key.get_pressed()
        for pidx in range(2 if self._two_player else 1):
            if self.gun_type[pidx] == GUN_AUTO:
                held = False
                if pidx == 0 and keys[pygame.K_e]:
                    held = True
                elif pidx == 1 and keys[pygame.K_RSHIFT]:
                    held = True
                elif not self._two_player and (keys[pygame.K_e] or keys[pygame.K_RSHIFT]):
                    held = True
                if held:
                    self.auto_shoot_cd[pidx] -= 1
                    if self.auto_shoot_cd[pidx] <= 0:
                        self._shoot(pidx)
                        self.auto_shoot_cd[pidx] = AUTO_SHOOT_INTERVAL
                else:
                    self.auto_shoot_cd[pidx] = 0  # klar til at skyde med det samme

        # --- Støvsuger (hold-to-suck) ---
        for pidx in range(2 if self._two_player else 1):
            if self.gun_type[pidx] == GUN_VACUUM:
                held = False
                if pidx == 0 and keys[pygame.K_e]:
                    held = True
                elif pidx == 1 and keys[pygame.K_RSHIFT]:
                    held = True
                elif not self._two_player and (keys[pygame.K_e] or keys[pygame.K_RSHIFT]):
                    held = True
                if held and self.power[pidx] > 0:
                    self.vacuum_active[pidx] = True
                    self.vacuum_cd[pidx] -= 1
                    if self.vacuum_cd[pidx] <= 0:
                        self.power[pidx] -= 1
                        self._vacuum_suck(pidx)
                        self.sfx.get("shoot_vacuum", self.sfx["shoot_basic"]).play()
                        self.vacuum_cd[pidx] = VACUUM_INTERVAL
                        self._save_wallet()
                else:
                    self.vacuum_active[pidx] = False
                    self.vacuum_cd[pidx] = 0
            else:
                self.vacuum_active[pidx] = False

        # --- Bullets ---
        for bullet in self.bullets:
            for _ in range(BULLET_SPEED):
                bullet.move()
                if bullet.is_out_of_bounds():
                    bullet.alive = False
                    break
                bp = bullet.pos()
                # Ruin-kollision: ødelæg ruin-blokken
                if bp in self.ruins:
                    self.ruins.discard(bp)
                    bullet.alive = False
                    break
                # Slange-kollision (rammer modstanderen)
                if bullet.owner_idx != 0 and self.snake1.alive and bp in self.snake1.body:
                    if not self.snake1.is_invincible:
                        self.snake1.alive = False
                    bullet.alive = False
                    break
                if bullet.owner_idx != 1 and self._two_player and self.snake2.alive and bp in self.snake2.body:
                    if not self.snake2.is_invincible:
                        self.snake2.alive = False
                    bullet.alive = False
                    break
        self.bullets = [b for b in self.bullets if b.alive]

        # --- Fjendtlige hunde (Svær + Vanvid) ---
        if self.difficulty >= 2:
            # Spawn nye hunde med jævne mellemrum
            self.enemy_spawn_cd -= 1
            if self.enemy_spawn_cd <= 0:
                # Svær: hvert ~60 ticks, Vanvid: hvert ~35 ticks
                interval = 60 if self.difficulty == 2 else 35
                self.enemy_spawn_cd = interval
                # Max antal hunde: Svær=3, Vanvid=6
                max_enemies = 3 if self.difficulty == 2 else 6
                if len(self.enemies) < max_enemies:
                    occupied = self._occupied()
                    for edog in self.enemies:
                        occupied.add(edog.pos())
                    # Spawn ved kant
                    edge_cells = (
                        [(0, y) for y in range(GRID_H)] +
                        [(GRID_W - 1, y) for y in range(GRID_H)] +
                        [(x, 0) for x in range(GRID_W)] +
                        [(x, GRID_H - 1) for x in range(GRID_W)]
                    )
                    free_edges = [p for p in edge_cells if p not in occupied]
                    if free_edges:
                        pos = random.choice(free_edges)
                        self.enemies.append(EnemyDog(pos))
                        self.sfx.get("enemy_bark", self.sfx["death"]).play()

            # Opdater hunde-AI (jag nærmeste slange)
            enemy_occ = set()
            for edog in self.enemies:
                enemy_occ.add(edog.pos())
            for edog in self.enemies:
                if not edog.alive:
                    continue
                # Find nærmeste levende slange
                targets = []
                if self.snake1.alive:
                    targets.append(self.snake1.head())
                if self._two_player and self.snake2.alive:
                    targets.append(self.snake2.head())
                if targets:
                    best = min(targets, key=lambda t: abs(t[0] - edog.x) + abs(t[1] - edog.y))
                    other_dogs = enemy_occ - {edog.pos()}
                    edog.update(best, self.ruins, other_dogs)

            # Hund ramt af kugle = dø
            for edog in self.enemies:
                if not edog.alive:
                    continue
                for bullet in self.bullets:
                    if bullet.alive and bullet.pos() == edog.pos():
                        edog.alive = False
                        bullet.alive = False
                        break
            self.bullets = [b for b in self.bullets if b.alive]

            # Hund rammer slange = dræb slangen
            for edog in self.enemies:
                if not edog.alive:
                    continue
                ep = edog.pos()
                if self.snake1.alive and ep == self.snake1.head():
                    if not self.snake1.is_invincible:
                        self.snake1.alive = False
                    edog.alive = False
                if self._two_player and self.snake2.alive and ep == self.snake2.head():
                    if not self.snake2.is_invincible:
                        self.snake2.alive = False
                    edog.alive = False

            self.enemies = [e for e in self.enemies if e.alive]

        self._update_speed()

        if not self.snake1.alive:
            self._end_round()
        elif self._two_player and not self.snake2.alive:
            self._end_round()

    def _update_speed(self):
        diff = DIFFICULTIES[self.difficulty]
        _, start_fps, max_fps, increase_every = diff
        total = self.scores[0] + self.scores[1]
        self.fps = min(start_fps + total // increase_every, max_fps)

    def _end_round(self):
        self.sfx["death"].play()
        self._save_wallet()
        if not self._two_player:
            self.round_message = f"Game Over!  Score: {self.scores[0]}"
        else:
            s1_alive = self.snake1.alive
            s2_alive = self.snake2.alive
            if not s1_alive and not s2_alive:
                self.round_message = "Begge døde! Uafgjort!"
            elif not s1_alive:
                self.round_message = "Spiller 2 (Blå) vinder runden!"
            else:
                self.round_message = "Spiller 1 (Grøn) vinder runden!"
        self._start_name_input()

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == "MENU":
            self._draw_menu()
        elif self.state == "PLAYING":
            self._draw_game()
        elif self.state in ("ROUND_OVER", "ENTER_NAME"):
            self._draw_game()
            if self.state == "ENTER_NAME":
                self._draw_enter_name()
            else:
                self._draw_round_over()

        pygame.display.flip()

    def _draw_menu_selector(self, cx, y, label, value_text, value_color, is_selected, can_left, can_right):
        sel_color = WHITE if is_selected else LIGHT_GRAY

        # 3D baggrundspanel for valgt række
        if is_selected:
            draw_3d_panel(self.screen, (cx - 160, y - 32, 320, 68), (40, 40, 50), depth=3)

        lbl = self.font_med.render(label, True, sel_color)
        self.screen.blit(lbl, lbl.get_rect(center=(cx, y - 22)))

        arrow_l_color = (WHITE if can_left else GRAY) if is_selected else GRAY
        arrow_r_color = (WHITE if can_right else GRAY) if is_selected else GRAY
        arrow_left = self.font_med.render("<", True, arrow_l_color)
        arrow_right = self.font_med.render(">", True, arrow_r_color)
        val = self.font_big.render(value_text, True, value_color)

        self.screen.blit(arrow_left, arrow_left.get_rect(center=(cx - 140, y + 10)))
        self.screen.blit(val, val.get_rect(center=(cx, y + 10)))
        self.screen.blit(arrow_right, arrow_right.get_rect(center=(cx + 140, y + 10)))

        if is_selected:
            underline_w = 300
            pygame.draw.line(
                self.screen, sel_color,
                (cx - underline_w // 2, y + 32), (cx + underline_w // 2, y + 32), 1
            )

    def _draw_gun_preview(self, cx, cy, gun_id, tick):
        """Tegn et mini-billede af en kanon-type."""
        if gun_id == GUN_BASIC:
            # Kanon: simpel tønde med mundingsflamme
            draw_3d_rect(self.screen, GUN_BODY_COLOR, (cx - 8, cy - 6, 16, 12), depth=2)
            pygame.draw.rect(self.screen, _lighten(GUN_BODY_COLOR, 30), (cx - 6, cy - 4, 12, 8), 1)
            # Tønde
            pygame.draw.line(self.screen, GUN_BARREL_COLOR, (cx + 8, cy), (cx + 22, cy), 4)
            pygame.draw.line(self.screen, _lighten(GUN_BARREL_COLOR, 40), (cx + 8, cy - 1), (cx + 22, cy - 1), 1)
            # Mundingsflamme
            draw_3d_circle(self.screen, YELLOW, (cx + 24, cy), 3, depth=1)
            draw_3d_circle(self.screen, (255, 160, 50), (cx + 26, cy), 2, depth=1)
        elif gun_id == GUN_AUTO:
            # Auto-kanon: dobbeltløbet med roterende energi-ring
            auto_col = (100, 200, 100)
            draw_3d_circle(self.screen, (40, 60, 40), (cx, cy), 7, depth=2)
            pygame.draw.circle(self.screen, auto_col, (cx, cy), 6, 1)
            # Dobbelt tønder
            pygame.draw.line(self.screen, auto_col, (cx + 6, cy - 3), (cx + 22, cy - 3), 3)
            pygame.draw.line(self.screen, auto_col, (cx + 6, cy + 3), (cx + 22, cy + 3), 3)
            pygame.draw.line(self.screen, _lighten(auto_col, 40), (cx + 6, cy - 4), (cx + 22, cy - 4), 1)
            pygame.draw.line(self.screen, _lighten(auto_col, 40), (cx + 6, cy + 2), (cx + 22, cy + 2), 1)
            # Energi-kugler
            draw_3d_circle(self.screen, (150, 255, 150), (cx + 24, cy - 3), 2, depth=1)
            draw_3d_circle(self.screen, (150, 255, 150), (cx + 24, cy + 3), 2, depth=1)
            # Pulserende ring
            pulse = int(4 + 2 * math.sin(tick * 0.3))
            pygame.draw.circle(self.screen, (80, 220, 80), (cx, cy), pulse, 1)
        elif gun_id == GUN_QUAD:
            # Quad-kanon: 4 tønder i kryds med centralt kammer
            quad_col = (200, 80, 80)
            quad_tip = (255, 120, 60)
            draw_3d_circle(self.screen, (80, 30, 30), (cx, cy), 6, depth=2)
            pygame.draw.circle(self.screen, quad_col, (cx, cy), 5, 1)
            # 4 tønder
            for ddx, ddy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                bx, by = cx + ddx * 12, cy + ddy * 12
                pygame.draw.line(self.screen, quad_col, (cx + ddx * 5, cy + ddy * 5), (bx, by), 3)
                pygame.draw.line(self.screen, _lighten(quad_col, 30), (cx + ddx * 5, cy + ddy * 5), (bx, by), 1)
                draw_3d_circle(self.screen, quad_tip, (bx, by), 2, depth=1)
                pygame.draw.circle(self.screen, YELLOW, (bx, by), 1)
            # Centralt sigtekorn
            pygame.draw.line(self.screen, YELLOW, (cx - 2, cy), (cx + 2, cy), 1)
            pygame.draw.line(self.screen, YELLOW, (cx, cy - 2), (cx, cy + 2), 1)
        elif gun_id == GUN_VACUUM:
            # Støvsuger: lilla motor med sugetragt
            vac_col = (100, 60, 180)
            vac_light = (140, 100, 220)
            vac_dark = (60, 30, 120)
            # Motor
            draw_3d_circle(self.screen, vac_dark, (cx, cy), 7, depth=2)
            pygame.draw.circle(self.screen, vac_col, (cx, cy), 6, 1)
            # Sugerør
            pygame.draw.line(self.screen, vac_dark, (cx + 6, cy + 1), (cx + 20, cy + 1), 5)
            pygame.draw.line(self.screen, vac_col, (cx + 6, cy), (cx + 20, cy), 4)
            pygame.draw.line(self.screen, vac_light, (cx + 6, cy - 1), (cx + 20, cy - 1), 1)
            # Tragt
            pygame.draw.polygon(self.screen, vac_col, [
                (cx + 20, cy - 6), (cx + 20, cy + 6), (cx + 28, cy)])
            pygame.draw.polygon(self.screen, vac_light, [
                (cx + 20, cy - 6), (cx + 20, cy + 6), (cx + 28, cy)], 1)
            # Suge-effekt
            pulse = int(2 + 2 * math.sin(tick * 0.4))
            pygame.draw.circle(self.screen, (180, 140, 255), (cx + 28, cy), pulse, 1)
            # Strøm-ikon (lyn)
            pygame.draw.lines(self.screen, YELLOW, False, [
                (cx - 2, cy - 5), (cx + 1, cy - 1), (cx - 1, cy + 1), (cx + 2, cy + 5)], 1)

    def _draw_snake_preview(self, sx, sy, stype, pidx, selected, tick):
        """Tegn et mini-slange-preview (5 segmenter, vandret mod højre)."""
        cs = 12
        col, col_dark, col_belly = SNAKE_TYPE_COLORS[stype][pidx]
        is_sq = stype in SQUARE_HEAD_TYPES
        # Rainbow dynamisk farve i preview
        if stype == SNAKE_RAINBOW:
            col = _hsv_to_rgb(((tick * 2) % 360) / 360.0, 0.75, 0.88)
            col_dark = _darken(col, 40)
            col_belly = _lighten(col, 30)

        # 3D baggrundsboks
        box = pygame.Rect(sx - 8, sy - cs - 6, 5 * cs + 16, cs * 2 + 12)
        if selected:
            draw_3d_panel(self.screen, box, (45, 45, 55), depth=3)
            pygame.draw.rect(self.screen, WHITE, box, 2, border_radius=4)
        else:
            draw_3d_panel(self.screen, box, (30, 30, 38), depth=2)
            pygame.draw.rect(self.screen, GRAY, box, 1, border_radius=4)

        segs = [(sx + i * cs, sy) for i in range(5)]

        # --- HALE ---
        tx, ty = segs[0]
        if is_sq:
            pygame.draw.rect(self.screen, col_dark, (tx, ty - cs // 2, cs - 2, cs), border_radius=1)
        elif stype in (SNAKE_DOG, SNAKE_CAT, SNAKE_CANDY, SNAKE_ALIEN):
            wag = int(2 * math.sin(tick * 0.6))
            pygame.draw.line(self.screen, col_dark, (tx + cs // 2, ty), (tx, ty + wag), 3)
            pygame.draw.circle(self.screen, col, (tx, ty + wag), 2)
        else:
            pygame.draw.polygon(self.screen, col_dark, [(tx, ty), (tx + cs // 2, ty - cs // 3), (tx + cs // 2, ty + cs // 3)])

        # --- KROP ---
        for i in range(1, 4):
            bx, by = segs[i]
            # Rainbow per-segment
            if stype == SNAKE_RAINBOW:
                hue = ((i * 30 + tick * 2) % 360) / 360.0
                seg_col = _hsv_to_rgb(hue, 0.75, 0.88)
                seg_dark = _darken(seg_col, 40)
                seg_belly = _lighten(seg_col, 30)
            else:
                seg_col, seg_dark, seg_belly = col, col_dark, col_belly
            if is_sq:
                pygame.draw.rect(self.screen, seg_col, (bx, by - cs // 2, cs - 1, cs))
                pygame.draw.rect(self.screen, seg_dark, (bx, by - cs // 2, cs - 1, cs), 1)
            else:
                br = 5 if stype == SNAKE_DOG else 4
                pygame.draw.rect(self.screen, seg_dark, (bx, by - cs // 2, cs - 1, cs), border_radius=br)
                pygame.draw.rect(self.screen, seg_belly, (bx + 2, by - 1, cs - 5, 2), border_radius=1)

        # --- HOVED ---
        hx, hy = segs[4][0] + cs // 2, segs[4][1]
        if is_sq:
            hr = pygame.Rect(hx - cs // 2, hy - cs // 2, cs, cs)
            pygame.draw.rect(self.screen, col, hr, border_radius=2)
            pygame.draw.rect(self.screen, col_dark, hr, 1, border_radius=2)
            if stype == SNAKE_TANK:
                pygame.draw.rect(self.screen, (200, 200, 80), (hx + 1, hy - 3, 3, 2))
                pygame.draw.rect(self.screen, (200, 200, 80), (hx + 1, hy + 1, 3, 2))
            else:  # Robot
                led = (50, 255, 50) if tick % 8 < 4 else (20, 180, 20)
                pygame.draw.rect(self.screen, led, (hx, hy - 3, 3, 3))
                pygame.draw.rect(self.screen, led, (hx, hy + 1, 3, 3))
        else:
            pygame.draw.circle(self.screen, col, (hx, hy), cs // 2 + 1)
            # Øjne
            if stype == SNAKE_ALIEN:
                pygame.draw.circle(self.screen, (20, 20, 20), (hx + 1, hy - 3), 3)
                pygame.draw.circle(self.screen, (20, 20, 20), (hx + 1, hy + 3), 3)
                pygame.draw.circle(self.screen, (0, 255, 100), (hx + 1, hy - 3), 2)
                pygame.draw.circle(self.screen, (0, 255, 100), (hx + 1, hy + 3), 2)
            elif stype == SNAKE_ZOMBIE:
                pygame.draw.circle(self.screen, (200, 200, 50), (hx + 1, hy - 3), 2)
                pygame.draw.line(self.screen, RED, (hx - 1, hy + 1), (hx + 3, hy + 5), 1)
                pygame.draw.line(self.screen, RED, (hx + 3, hy + 1), (hx - 1, hy + 5), 1)
            elif stype == SNAKE_SKELETON:
                pygame.draw.circle(self.screen, (30, 25, 20), (hx + 1, hy - 3), 2)
                pygame.draw.circle(self.screen, (30, 25, 20), (hx + 1, hy + 3), 2)
            elif stype == SNAKE_NINJA:
                pygame.draw.rect(self.screen, WHITE, (hx - 1, hy - 4, 4, 2))
                pygame.draw.rect(self.screen, WHITE, (hx - 1, hy + 2, 4, 2))
            elif stype == SNAKE_CAT:
                pygame.draw.circle(self.screen, (220, 200, 50), (hx + 1, hy - 3), 2)
                pygame.draw.circle(self.screen, (220, 200, 50), (hx + 1, hy + 3), 2)
            elif stype == SNAKE_LAVA:
                glow = (255, 130, 20)
                pygame.draw.circle(self.screen, glow, (hx + 1, hy - 3), 2)
                pygame.draw.circle(self.screen, glow, (hx + 1, hy + 3), 2)
            else:
                pygame.draw.circle(self.screen, WHITE, (hx + 1, hy - 3), 2)
                pygame.draw.circle(self.screen, WHITE, (hx + 1, hy + 3), 2)
                pygame.draw.circle(self.screen, BLACK, (hx + 2, hy - 3), 1)
                pygame.draw.circle(self.screen, BLACK, (hx + 2, hy + 3), 1)
            # Type-specifik head deko
            if stype == SNAKE_DOG:
                pygame.draw.circle(self.screen, col_dark, (hx - 3, hy - cs // 2 - 2), 4)
                pygame.draw.circle(self.screen, col_dark, (hx - 3, hy + cs // 2 + 2), 4)
                pygame.draw.circle(self.screen, BLACK, (hx + cs // 2 + 1, hy), 2)
            elif stype == SNAKE_CAT:
                pygame.draw.polygon(self.screen, col_dark, [(hx - 3, hy - cs // 2 - 3), (hx - 5, hy - 2), (hx - 1, hy - 2)])
                pygame.draw.polygon(self.screen, col_dark, [(hx - 3, hy + cs // 2 + 3), (hx - 5, hy + 2), (hx - 1, hy + 2)])
            elif stype == SNAKE_DRAGON:
                pygame.draw.circle(self.screen, (180, 140, 40), (hx - 2, hy - cs // 2 - 2), 2)
                pygame.draw.circle(self.screen, (180, 140, 40), (hx - 2, hy + cs // 2 + 2), 2)
            elif stype == SNAKE_SHARK:
                pygame.draw.polygon(self.screen, col_dark, [(hx, hy - cs // 2 - 3), (hx - 2, hy - 2), (hx + 2, hy - 2)])
            elif stype == SNAKE_GOLD:
                for co in (-2, 0, 2):
                    pygame.draw.polygon(self.screen, GOLD, [(hx + co, hy - cs // 2 - 3), (hx + co - 1, hy - cs // 2), (hx + co + 1, hy - cs // 2)])
            elif stype == SNAKE_PIRATE:
                pygame.draw.circle(self.screen, (30, 30, 30), (hx + 1, hy + 3), 3)
            elif stype == SNAKE_FIRE:
                pygame.draw.circle(self.screen, (255, 180, 30), (hx + cs // 2 + 2, hy), 2)
            elif stype == SNAKE_ICE:
                pygame.draw.polygon(self.screen, (200, 230, 255), [(hx, hy - cs // 2 - 3), (hx - 1, hy - cs // 2), (hx + 1, hy - cs // 2)])
            elif stype == SNAKE_ELECTRIC:
                pygame.draw.line(self.screen, (255, 255, 100), (hx + cs // 2, hy - 2), (hx + cs // 2 + 3, hy), 1)
            elif stype == SNAKE_DIAMOND:
                pygame.draw.circle(self.screen, (255, 255, 240), (hx - 1, hy - 3), 1)
            elif stype == SNAKE_CANDY:
                pygame.draw.circle(self.screen, (255, 80, 120), (hx - 1, hy - cs // 2 - 1), 1)
                pygame.draw.circle(self.screen, (255, 80, 120), (hx + 1, hy - cs // 2 - 1), 1)
            elif stype == SNAKE_ALIEN:
                pygame.draw.line(self.screen, (100, 255, 100), (hx - 2, hy - cs // 2), (hx - 4, hy - cs // 2 - 3), 1)
                pygame.draw.line(self.screen, (100, 255, 100), (hx - 2, hy + cs // 2), (hx - 4, hy + cs // 2 + 3), 1)

    def _draw_menu(self):
        cx = WINDOW_W // 2
        tick = pygame.time.get_ticks() // 50

        # --- Titel ---
        title = self.font_big.render("SNAKE", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(cx, 32)))

        # --- Spillere (row 0) ---
        player_names = {1: "1 Spiller", 2: "2 Spillere"}
        player_colors = {1: GREEN, 2: CYAN}
        self._draw_menu_selector(
            cx, 78,
            "Spillere:", player_names[self.num_players], player_colors[self.num_players],
            is_selected=(self.menu_row == 0),
            can_left=(self.num_players > 1), can_right=(self.num_players < 2),
        )

        # --- Sværhedsgrad (row 1) ---
        diff_name = DIFFICULTIES[self.difficulty][0]
        diff_colors = [GREEN, YELLOW, (255, 140, 40), RED]
        self._draw_menu_selector(
            cx, 148,
            "Sværhedsgrad:", diff_name, diff_colors[self.difficulty],
            is_selected=(self.menu_row == 1),
            can_left=(self.difficulty > 0), can_right=(self.difficulty < len(DIFFICULTIES) - 1),
        )

        # === SLANGER section (row 2) ===
        snake_y = 200
        sel_st = self.menu_row == 2
        st_col = WHITE if sel_st else LIGHT_GRAY
        slanger_title = self.font_med.render("SLANGER", True, st_col)
        self.screen.blit(slanger_title, slanger_title.get_rect(center=(cx, snake_y)))
        if sel_st:
            tw = slanger_title.get_width() // 2 + 10
            pygame.draw.line(self.screen, st_col, (cx - tw, snake_y + 12), (cx + tw, snake_y + 12), 1)

        # P1 og P2 slange-previews side om side med scroll
        preview_y = snake_y + 32
        n_types = len(SNAKE_TYPES_LIST)
        p1_type = self.snake_type[0]
        p2_type = self.snake_type[1]
        p1_idx = SNAKE_TYPES_LIST.index(p1_type) if p1_type in SNAKE_TYPES_LIST else 0
        p2_idx = SNAKE_TYPES_LIST.index(p2_type) if p2_type in SNAKE_TYPES_LIST else 0

        # --- Spiller 1 (venstre side) ---
        p1_cx = cx - 120
        p1_col = SNAKE_TYPE_COLORS[p1_type][0][0]
        p1_label = self.font_small.render("P1", True, p1_col if sel_st else LIGHT_GRAY)
        self.screen.blit(p1_label, p1_label.get_rect(center=(p1_cx, preview_y - 10)))
        # Pil venstre
        if sel_st:
            arrow_col = (180, 180, 180)
            pygame.draw.polygon(self.screen, arrow_col, [
                (p1_cx - 60, preview_y + 8), (p1_cx - 48, preview_y), (p1_cx - 48, preview_y + 16)])
            pygame.draw.polygon(self.screen, arrow_col, [
                (p1_cx + 60, preview_y + 8), (p1_cx + 48, preview_y), (p1_cx + 48, preview_y + 16)])
        self._draw_snake_preview(p1_cx - 28, preview_y, p1_type, 0, sel_st, tick)
        name1 = self.font_small.render(SNAKE_TYPE_NAMES[p1_type], True, WHITE if sel_st else LIGHT_GRAY)
        self.screen.blit(name1, name1.get_rect(center=(p1_cx + 2, preview_y + 24)))
        idx_txt1 = self.font_small.render(f"{p1_idx + 1}/{n_types}", True, LIGHT_GRAY)
        self.screen.blit(idx_txt1, idx_txt1.get_rect(center=(p1_cx + 2, preview_y + 38)))

        # --- Spiller 2 (højre side) ---
        if self._two_player:
            p2_cx = cx + 120
            p2_col = SNAKE_TYPE_COLORS[p2_type][1][0]
            p2_label = self.font_small.render("P2", True, p2_col if sel_st else LIGHT_GRAY)
            self.screen.blit(p2_label, p2_label.get_rect(center=(p2_cx, preview_y - 10)))
            if sel_st:
                pygame.draw.polygon(self.screen, arrow_col, [
                    (p2_cx - 60, preview_y + 8), (p2_cx - 48, preview_y), (p2_cx - 48, preview_y + 16)])
                pygame.draw.polygon(self.screen, arrow_col, [
                    (p2_cx + 60, preview_y + 8), (p2_cx + 48, preview_y), (p2_cx + 48, preview_y + 16)])
            self._draw_snake_preview(p2_cx - 28, preview_y, p2_type, 1, sel_st, tick)
            name2 = self.font_small.render(SNAKE_TYPE_NAMES[p2_type], True, WHITE if sel_st else LIGHT_GRAY)
            self.screen.blit(name2, name2.get_rect(center=(p2_cx + 2, preview_y + 24)))
            idx_txt2 = self.font_small.render(f"{p2_idx + 1}/{n_types}", True, LIGHT_GRAY)
            self.screen.blit(idx_txt2, idx_txt2.get_rect(center=(p2_cx + 2, preview_y + 38)))

        # Navigations-hint
        if sel_st:
            hint_txt = "A = P1 skift  |  D = P2 skift" if self._two_player else "A/D = skift slange"
            hint_st = self.font_small.render(hint_txt, True, LIGHT_GRAY)
            self.screen.blit(hint_st, hint_st.get_rect(center=(cx, preview_y + 52)))

        # --- Hint ---
        hint_y = preview_y + 68
        hint = self.font_small.render("W/S = skift række  |  A/D = skift værdi / køb", True, LIGHT_GRAY)
        self.screen.blit(hint, hint.get_rect(center=(cx, hint_y)))

        # === BUTIK section ===
        shop_y = hint_y + 22
        shop_title = self.font_med.render("BUTIK", True, COIN_COLOR)
        self.screen.blit(shop_title, shop_title.get_rect(center=(cx, shop_y)))

        # Wallet display
        wallet_y = shop_y + 20
        def _gun_label(pidx):
            g = self.gun_type[pidx]
            if g is GUN_NONE:
                return ""
            return GUN_INFO[g][1]
        if self._two_player:
            w_txt = self.font_small.render(
                f"P1: ${self.coins[0]} Ammo:{self.ammo[0]} Strøm:{self.power[0]} {_gun_label(0)}"
                f"  |  P2: ${self.coins[1]} Ammo:{self.ammo[1]} Strøm:{self.power[1]} {_gun_label(1)}",
                True, COIN_COLOR
            )
        else:
            gl = _gun_label(0)
            w_txt = self.font_small.render(
                f"Coins: ${self.coins[0]}  Ammo: {self.ammo[0]}  Strøm: {self.power[0]}  {gl}",
                True, COIN_COLOR
            )
        self.screen.blit(w_txt, w_txt.get_rect(center=(cx, wallet_y)))

        # Shop row helper
        def _draw_shop_row(y, row_idx, label, price, owned_check=None):
            sel = self.menu_row == row_idx
            col = WHITE if sel else LIGHT_GRAY
            prefix = "< " if sel else "  "
            suffix = " >" if sel else "  "
            owned = ""
            if owned_check:
                parts = []
                if owned_check(0):
                    parts.append("P1:OK" if self._two_player else "EJET")
                if self._two_player and owned_check(1):
                    parts.append("P2:OK")
                if parts:
                    owned = "  " + " ".join(parts)
            txt = f"{prefix}{label} (${price}){suffix}{owned}"
            rendered = self.font_small.render(txt, True, col)
            self.screen.blit(rendered, rendered.get_rect(center=(cx, y)))
            if sel:
                pygame.draw.line(self.screen, col, (cx - 220, y + 10), (cx + 220, y + 10), 1)

        # Ammo (row 3)
        row_y = wallet_y + 20
        sel3 = self.menu_row == 3
        ammo_col = WHITE if sel3 else LIGHT_GRAY
        ammo_txt = f"Ammo (${AMMO_PRICE} = {AMMO_AMOUNT} skud)"
        if sel3:
            ammo_txt = "< " + ammo_txt + " >"
        ammo_r = self.font_small.render(ammo_txt, True, ammo_col)
        self.screen.blit(ammo_r, ammo_r.get_rect(center=(cx, row_y)))
        if sel3:
            pygame.draw.line(self.screen, ammo_col, (cx - 220, row_y + 10), (cx + 220, row_y + 10), 1)

        # Strøm (row 4)
        power_y = row_y + 18
        sel4 = self.menu_row == 4
        pow_col = WHITE if sel4 else LIGHT_GRAY
        pow_txt = f"Strøm (${POWER_PRICE} = {POWER_AMOUNT} strøm)"
        if sel4:
            pow_txt = "< " + pow_txt + " >"
        pow_r = self.font_small.render(pow_txt, True, pow_col)
        self.screen.blit(pow_r, pow_r.get_rect(center=(cx, power_y)))
        if sel4:
            pygame.draw.line(self.screen, pow_col, (cx - 220, power_y + 10), (cx + 220, power_y + 10), 1)
        # Lyn-ikon ved strøm
        bolt_x = cx - 120
        pygame.draw.lines(self.screen, YELLOW, False, [
            (bolt_x, power_y - 5), (bolt_x + 3, power_y - 1),
            (bolt_x + 1, power_y + 1), (bolt_x + 4, power_y + 5)], 1)

        # 4 kanon-typer (rows 5-8) med preview-billeder
        for i, (gid, gname, gprice, gcol) in enumerate(GUN_TYPES):
            gy = power_y + 22 * (i + 1)
            _draw_shop_row(gy, 5 + i, gname, gprice,
                           owned_check=lambda pidx, g=gid: self.gun_type[pidx] == g)
            # Tegn kanon-preview til venstre for teksten
            self._draw_gun_preview(cx - 180, gy, gid, tick)

        # Kontroller
        last_gun_y = power_y + 22 * len(GUN_TYPES)
        ctrl_y = last_gun_y + 20
        if self.num_players == 1:
            sub1 = self.font_small.render("WASD/pile = styr  |  E/Shift = skyd", True, GREEN)
            self.screen.blit(sub1, sub1.get_rect(center=(cx, ctrl_y)))
        else:
            sub1 = self.font_small.render("P1: WASD + E=skyd  |  P2: Pile + RShift=skyd", True, LIGHT_GRAY)
            self.screen.blit(sub1, sub1.get_rect(center=(cx, ctrl_y)))

        hs_list = get_highscore_list(self.highscore_data, self.difficulty, self.num_players)
        if hs_list:
            hs_y = ctrl_y + 18
            hs_title = self.font_small.render("-- Highscores --", True, GOLD)
            self.screen.blit(hs_title, hs_title.get_rect(center=(cx, hs_y)))
            hs_y += 16
            for i, entry in enumerate(hs_list[:3]):
                color = GOLD if i == 0 else WHITE
                txt = self.font_small.render(
                    f"{i + 1}. {entry['name']:<{MAX_NAME_LEN}} {entry['score']:>4}", True, color
                )
                self.screen.blit(txt, txt.get_rect(center=(cx, hs_y)))
                hs_y += 15
            bottom_y = hs_y + 4
        else:
            bottom_y = ctrl_y + 24

        start = self.font_med.render("Tryk SPACE for at starte", True, YELLOW)
        esc = self.font_small.render("ESC for at afslutte", True, GRAY)
        self.screen.blit(start, start.get_rect(center=(cx, bottom_y)))
        self.screen.blit(esc, esc.get_rect(center=(cx, bottom_y + 20)))

    def _draw_game(self):
        diff = self.difficulty
        theme = MAP_THEMES.get(diff, MAP_THEMES[0])
        # Map-gulv (tema-baseret)
        draw_map_floor(self.screen, diff)

        # Ruiner (3D blokke, tema-farver)
        draw_ruins(self.screen, self.ruins, diff)

        # 3D Scoreboard panel (tema-farve)
        draw_3d_panel(self.screen, (0, 0, WINDOW_W, SCOREBOARD_H), theme["scoreboard"], depth=4)

        s1_inv = " [INVINCIBLE]" if self.snake1.is_invincible else ""
        s1_color = CYAN if self.snake1.is_invincible else GREEN

        def _hud_gun(pidx):
            g = self.gun_type[pidx]
            if g is GUN_NONE:
                return ""
            name = GUN_INFO[g][1]
            return f"  {name} x{self.ammo[pidx]}"

        if self._two_player:
            s2_inv = " [INVINCIBLE]" if self.snake2.is_invincible else ""
            s2_color = CYAN if self.snake2.is_invincible else BLUE
            s1_text = self.font_med.render(f"P1: {self.scores[0]}{s1_inv}", True, s1_color)
            s1_sub = self.font_small.render(f"${self.coins[0]}{_hud_gun(0)}", True, COIN_COLOR)
            s2_text = self.font_med.render(f"P2: {self.scores[1]}{s2_inv}", True, s2_color)
            s2_sub = self.font_small.render(f"${self.coins[1]}{_hud_gun(1)}", True, COIN_COLOR)
            self.screen.blit(s1_text, (20, 4))
            self.screen.blit(s1_sub, (20, 28))
            self.screen.blit(s2_text, (WINDOW_W - s2_text.get_width() - 20, 4))
            self.screen.blit(s2_sub, (WINDOW_W - s2_sub.get_width() - 20, 28))
        else:
            hs_list = get_highscore_list(self.highscore_data, self.difficulty, self.num_players)
            best = hs_list[0]["score"] if hs_list else 0
            s1_text = self.font_med.render(f"Score: {self.scores[0]}{s1_inv}", True, s1_color)
            s1_sub = self.font_small.render(f"${self.coins[0]}{_hud_gun(0)}", True, COIN_COLOR)
            hs_text = self.font_med.render(f"Bedste: {best}", True, GOLD)
            self.screen.blit(s1_text, (20, 4))
            self.screen.blit(s1_sub, (20, 28))
            self.screen.blit(hs_text, (WINDOW_W - hs_text.get_width() - 20, 12))

        # Coins
        for coin in self.coin_items:
            coin.draw(self.screen, self.game_tick)
        # Money Bills (pengesedler)
        for bill in self.money_bills:
            bill.draw(self.screen, self.game_tick)
        for food in self.foods:
            food.draw(self.screen, self.game_tick)
        # Bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        # Fjendtlige hunde
        for edog in self.enemies:
            edog.draw(self.screen, self.game_tick)
        self.snake1.draw(self.screen, self.game_tick, self.gun_type[0], self.snake_type[0])
        if self._two_player:
            self.snake2.draw(self.screen, self.game_tick, self.gun_type[1], self.snake_type[1])

        # 3D Dekorationer (træer/buske/klipper/strukturer - tegnes ovenpå)
        draw_decorations(self.screen, self.trees, self.difficulty)

    def _draw_enter_name(self):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        cx = WINDOW_W // 2
        cy = WINDOW_H // 2

        # 3D dialog-panel
        panel_w, panel_h = 500, 220
        draw_3d_panel(self.screen, (cx - panel_w // 2, cy - panel_h // 2, panel_w, panel_h), (35, 35, 45), depth=5)

        new_hs = self.font_big.render("NY HIGHSCORE!", True, GOLD)
        self.screen.blit(new_hs, new_hs.get_rect(center=(cx, cy - 70)))

        if self._two_player:
            player_label = f"Spiller {self.name_player_idx + 1}"
            player_color = GREEN if self.name_player_idx == 0 else BLUE
        else:
            player_label = "Din score"
            player_color = GREEN

        _, score = self.pending_highscores[0]
        score_txt = self.font_med.render(f"{player_label}: {score} point", True, player_color)
        self.screen.blit(score_txt, score_txt.get_rect(center=(cx, cy - 30)))

        prompt = self.font_med.render("Indtast dit navn:", True, WHITE)
        self.screen.blit(prompt, prompt.get_rect(center=(cx, cy + 10)))

        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        name_display = self.name_input + cursor
        # 3D input-felt
        input_w = 300
        draw_3d_panel(self.screen, (cx - input_w // 2, cy + 32, input_w, 38), (25, 25, 30), depth=2)
        name_txt = self.font_big.render(name_display, True, YELLOW)
        self.screen.blit(name_txt, name_txt.get_rect(center=(cx, cy + 50)))

        hint = self.font_small.render("Tryk ENTER for at bekræfte  |  ESC = spring over", True, LIGHT_GRAY)
        self.screen.blit(hint, hint.get_rect(center=(cx, cy + 90)))

    def _draw_round_over(self):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        cx = WINDOW_W // 2
        cy = WINDOW_H // 2

        # 3D resultat-panel
        panel_w, panel_h = 600, 160
        draw_3d_panel(self.screen, (cx - panel_w // 2, cy - panel_h // 2, panel_w, panel_h), (35, 35, 45), depth=5)

        msg = self.font_big.render(self.round_message, True, YELLOW)
        if self._two_player:
            score_text = self.font_med.render(
                f"Score:  {self.scores[0]}  -  {self.scores[1]}", True, WHITE
            )
        else:
            score_text = self.font_med.render(
                f"Score:  {self.scores[0]}", True, WHITE
            )
        hint = self.font_small.render("SPACE = ny runde  |  M = menu  |  ESC = menu", True, WHITE)

        self.screen.blit(msg, msg.get_rect(center=(cx, cy - 30)))
        self.screen.blit(score_text, score_text.get_rect(center=(cx, cy + 15)))
        self.screen.blit(hint, hint.get_rect(center=(cx, cy + 55)))

    async def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps if self.state == "PLAYING" else 30)
            await asyncio.sleep(0)  # Yield control to browser

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    asyncio.run(Game().run())
