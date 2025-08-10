# config.py

WIDTH = 800
HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

FPS = 60

GRAVITY = 0.6

PLAYER_WIDTH = 70
PLAYER_HEIGHT = 80
PLAYER_SPEED = 5
PLAYER_JUMP_VELOCITY = -12

SHURIKEN_SPEED = 15
SHURIKEN_WIDTH = 20
SHURIKEN_HEIGHT = 10

# 고양이 색상별 크기 설정
ENEMY_CAT_SIZE = {
    "yellow": (40, 50),  # 노란 고양이: 작음 (빠름)
    "black": (50, 60),   # 검은 고양이: 보통 (보통)
    "white": (60, 70),   # 흰 고양이: 큼 (느림)
}

# 고양이 색상별 속도 설정
ENEMY_CAT_SPEED = {
    "yellow": 9,  # 노란 고양이: 빠름
    "black": 6,   # 검은 고양이: 보통
    "white": 2,   # 흰 고양이: 느림
}

BOSS_CAT_WIDTH = 120
BOSS_CAT_HEIGHT = 100
BOSS_STONE_COOLDOWN = 2000

SNACK_SIZE = 60
SNACK_DURATION = 10000

STONE_RADIUS = 30
STONE_SPEED_MIN = 5   # 돌의 최소 속도
STONE_SPEED_MAX = 15  # 돌의 최대 속도
STONE_GRAVITY = 0  # 중력 효과 (자연스러운 포물선 궤도)

ENEMY_SPAWN_INTERVAL = 2000
SNACK_SPAWN_INTERVAL = 10000

# 고양이 적 발생 설정
TOTAL_CATS_TO_SPAWN = 10  # 발생할 고양이의 총 마리 수

# 스테이지 설정
MAX_STAGE = 10  # 최대 스테이지 수
BASE_CAT_HP = {  # 기본 고양이 HP (스테이지 1 기준)
    "yellow": 4,
    "black": 8,
    "white": 12,
}
BASE_BOSS_HP = 100  # 기본 보스 HP (스테이지 1 기준)

BACKGROUND_COLOR = (50, 150, 255)
GROUND_COLOR = (50, 200, 50)
