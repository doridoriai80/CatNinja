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

# 플레이어 충돌 판정 마진 (픽셀 단위, 값이 클수록 판정이 느슨해짐)
PLAYER_TOUCH_MARGIN = 20

SHURIKEN_SPEED = 15
SHURIKEN_WIDTH = 30
SHURIKEN_HEIGHT = 30

# 고양이 색상별 크기 설정
ENEMY_CAT_SIZE = {
    "yellow": (40, 50),  # 노란 고양이: 작음 (빠름)
    "black": (50, 60),   # 검은 고양이: 보통 (보통)
    "white": (50, 60),   # 흰 고양이: 큼 (느림)
}

# 고양이 색상별 속도 설정
ENEMY_CAT_SPEED = {
    "yellow": 9,  # 노란 고양이: 빠름
    "black": 6,   # 검은 고양이: 보통
    "white": 2,   # 흰 고양이: 느림
}

# 흰색 고양이 점프 설정
WHITE_CAT_JUMP_INTERVAL = 1000  # 점프 간격 (밀리초)
WHITE_CAT_JUMP_VELOCITY = -8    # 점프 속도 (음수 = 위로)
WHITE_CAT_GRAVITY = 0.4         # 중력 효과

BOSS_CAT_WIDTH = 120
BOSS_CAT_HEIGHT = 100
BOSS_STONE_COOLDOWN = 2000

# 보스 HP 표시 설정
BOSS_HP_BAR_WIDTH = 200
BOSS_HP_BAR_HEIGHT = 20
BOSS_HP_BAR_MARGIN = 10  # 오른쪽 여백

SNACK_SIZE = 60
SNACK_DURATION = 10000

# Puppy 아이템 설정
PUPPY_SIZE = 50
PUPPY_DEFENSE_COUNT = 1  # 플레이어를 방어할 횟수 (1번만)
PUPPY_SPAWN_INTERVAL = 5000  # 15초마다 스폰 (간식보다 더 자주)
PUPPY_DISPLAY_SIZE = 30  # 플레이어와 함께 표시될 때의 크기

# Puppy 랜덤 스폰 설정
PUPPY_SPAWN_MIN_INTERVAL = 3000   # 최소 스폰 간격 (3초)
PUPPY_SPAWN_MAX_INTERVAL = 8000   # 최대 스폰 간격 (8초)

# Puppy 충돌 영역 설정
PUPPY_LESS_COLLISION_MARGIN = 30  # puppy가 없을 때 충돌 영역 여백 (픽셀)

STONE_RADIUS = 40
STONE_SPEED_MIN = 5   # 돌의 최소 속도
STONE_SPEED_MAX = 15  # 돌의 최대 속도
STONE_GRAVITY = 0  # 중력 효과 (자연스러운 포물선 궤도)

# Stone 위치 설정
STONE_SPAWN_OFFSET_X = 0    # 보스 중심에서 X축 오프셋 (음수 = 왼쪽, 양수 = 오른쪽)
STONE_SPAWN_OFFSET_Y = -20    # 보스 바닥에서 Y축 오프셋 (음수 = 위쪽, 양수 = 아래쪽)

ENEMY_SPAWN_INTERVAL = 2000
SNACK_SPAWN_INTERVAL = 10000

# 고양이 적 발생 설정
TOTAL_CATS_TO_SPAWN = 10  # 발생할 고양이의 총 마리 수

# 스테이지 설정
MAX_STAGE = 10  # 최대 스테이지 수
BASE_CAT_HP = {  # 기본 고양이 HP (스테이지 1 기준)
    "yellow": 2,
    "black": 3,
    "white": 8,
}
BASE_BOSS_HP = 50  # 기본 보스 HP (스테이지 1 기준)

BACKGROUND_COLOR = (50, 150, 255)
GROUND_COLOR = (50, 200, 50)
