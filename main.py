import pygame
import random
import config
import os

pygame.init()

screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("강아지 닌자 횡스크롤")

clock = pygame.time.Clock()

# 한글 폰트 설정
try:
    # macOS에서 기본 한글 폰트 사용
    font = pygame.font.SysFont("AppleGothic", 24)
    font_large = pygame.font.SysFont("AppleGothic", 36)
    font_title = pygame.font.SysFont("AppleGothic", 48)  # 게임 제목용 큰 폰트
    font_small = pygame.font.SysFont("AppleGothic", 18)
except:
    try:
        # Windows에서 기본 한글 폰트 사용
        font = pygame.font.SysFont("malgun gothic", 24)
        font_large = pygame.font.SysFont("malgun gothic", 36)
        font_title = pygame.font.SysFont("malgun gothic", 48)  # 게임 제목용 큰 폰트
        font_small = pygame.font.SysFont("malgun gothic", 18)
    except:
        # 폴백 폰트
        font = pygame.font.SysFont("arial", 24)
        font_large = pygame.font.SysFont("arial", 36)
        font_title = pygame.font.SysFont("arial", 48)  # 게임 제목용 큰 폰트
        font_small = pygame.font.SysFont("arial", 18)

# --- 클래스들 ---

# ============================================================================
# 🐕 플레이어 클래스 (Player Class)
# ============================================================================
# 플레이어는 게임의 주인공인 강아지 닌자입니다.
# 이 클래스는 플레이어의 모든 동작과 상태를 관리합니다.

class Player(pygame.sprite.Sprite):
    """
    플레이어(강아지 닌자) 클래스
    
    주요 기능:
    - 좌우 이동 (← → 키)
    - 점프 (스페이스바)
    - 수리검 발사 (Z 키)
    - puppy 방어 효과 사용
    - 간식 효과 (더블 수리검)
    
    pygame.sprite.Sprite를 상속받아 Pygame의 스프라이트 시스템을 사용합니다.
    """
    
    def __init__(self):
        """
        플레이어 초기화 - 플레이어 객체가 생성될 때 한 번만 실행됩니다.
        
        이 메서드에서:
        - 플레이어의 이미지를 로드하고 크기를 조정합니다
        - 플레이어의 초기 위치를 설정합니다
        - 플레이어의 물리 속성(속도, 중력 등)을 초기화합니다
        - 게임 상태 변수들을 초기화합니다
        """
        super().__init__()  # pygame.sprite.Sprite 초기화 (반드시 필요)
        
        # ===== 이미지 로드 및 설정 =====
        try:
            # assets/player.png 파일을 로드하여 플레이어 이미지로 사용
            # convert_alpha()는 투명도를 지원하는 이미지 형식으로 변환합니다
            self.original_image = pygame.image.load("assets/player.png").convert_alpha()
            
            # config.py에 정의된 크기로 이미지 조정
            # transform.scale(이미지, (너비, 높이))로 크기를 변경합니다
            self.image = pygame.transform.scale(self.original_image, (config.PLAYER_WIDTH, config.PLAYER_HEIGHT))
        except:
            # 이미지 로드 실패 시 기본 사각형으로 대체
            # Surface(너비, 높이)로 빈 이미지를 만들고 fill(색상)로 채웁니다
            self.image = pygame.Surface((config.PLAYER_WIDTH, config.PLAYER_HEIGHT))
            self.image.fill((200, 150, 100))  # 갈색 사각형
            print("⚠️ 플레이어 이미지 로드 실패 - 기본 사각형 사용")
        
        # ===== 충돌 영역 설정 =====
        # rect는 플레이어의 충돌 영역을 나타냅니다
        # get_rect()로 이미지 크기에 맞는 사각형을 생성합니다
        self.rect = self.image.get_rect()
        
        # 플레이어의 초기 위치 설정
        # bottomleft는 사각형의 왼쪽 하단 모서리를 의미합니다
        # (50, config.HEIGHT - 50)은 화면 왼쪽 하단에서 약간 떨어진 위치입니다
        self.rect.bottomleft = (50, config.HEIGHT - 50)
        
        # ===== 물리 속성 초기화 =====
        self.vel_y = 0        # Y축 속도 (점프, 낙하할 때 사용)
        self.speed = config.PLAYER_SPEED  # 좌우 이동 속도 (config.py에서 가져옴)
        self.on_ground = True # 지면 접촉 여부 (점프 가능 여부 판단용)
        
        # ===== 게임 상태 변수 초기화 =====
        self.alive = True           # 생존 여부 (True = 살아있음, False = 죽음)
        self.shuriken_double = False # 더블 수리검 효과 활성화 여부
        self.double_end_time = 0    # 더블 수리검 효과 종료 시간
        
        # ===== puppy 방어 시스템 변수 =====
        self.defense_count = 0      # 남은 방어 횟수 (0 = 방어 불가, 1 이상 = 방어 가능)
        self.defense_active = False # 방어 효과 활성화 여부

    def update(self, keys):
        """
        플레이어 상태 업데이트 - 매 프레임마다 호출됩니다.
        
        Args:
            keys: pygame.key.get_pressed()로 얻은 키 입력 상태
                  키를 누르고 있으면 True, 누르지 않으면 False
        
        이 메서드에서:
        - 키 입력에 따른 플레이어 이동을 처리합니다
        - 점프와 낙하를 처리합니다
        - 화면 경계를 벗어나지 않도록 제한합니다
        - 더블 수리검 효과 시간을 체크합니다
        """
        # 플레이어가 죽어있으면 업데이트하지 않음
        if not self.alive:
            return
        
        # ===== 좌우 이동 처리 =====
        if keys[pygame.K_LEFT]:  # 왼쪽 화살표 키를 누르고 있으면
            self.rect.x -= self.speed  # 왼쪽으로 이동 (X좌표 감소)
            # 화면 왼쪽 경계 체크 - 화면 밖으로 나가지 않도록 제한
            if self.rect.left < 0:
                self.rect.left = 0  # 왼쪽 경계에 고정
                
        if keys[pygame.K_RIGHT]:  # 오른쪽 화살표 키를 누르고 있으면
            self.rect.x += self.speed  # 오른쪽으로 이동 (X좌표 증가)
            # 화면 오른쪽 경계 체크 - 화면 밖으로 나가지 않도록 제한
            if self.rect.right > config.WIDTH:
                self.rect.right = config.WIDTH  # 오른쪽 경계에 고정

        # ===== 점프 처리 =====
        if keys[pygame.K_SPACE] and self.on_ground:  # 스페이스바 + 지면 접촉 시
            self.vel_y = config.PLAYER_JUMP_VELOCITY  # 점프 속도 설정 (음수 = 위로)
            self.on_ground = False  # 점프 중이므로 지면에서 떨어짐

        # ===== 중력 적용 =====
        self.vel_y += config.GRAVITY  # 중력으로 인해 아래로 가속
        self.rect.y += self.vel_y     # Y축 위치 업데이트

        # ===== 지면 처리 =====
        if self.rect.bottom >= config.HEIGHT - 50:  # 바닥에 닿으면
            self.rect.bottom = config.HEIGHT - 50   # 바닥에 고정
            self.vel_y = 0                          # 낙하 속도 초기화
            self.on_ground = True                   # 지면 접촉 상태로 변경

        # ===== 더블 수리검 효과 시간 체크 =====
        if self.shuriken_double and pygame.time.get_ticks() > self.double_end_time:
            # 효과 시간이 지나면 더블 수리검 효과 비활성화
            self.shuriken_double = False

    def eat_snack(self):
        """
        간식을 먹었을 때 더블 수리검 효과를 활성화합니다.
        
        이 메서드는 간식과 충돌했을 때 자동으로 호출됩니다.
        """
        self.shuriken_double = True  # 더블 수리검 효과 활성화
        # 현재 시간 + 지속 시간으로 효과 종료 시간 계산
        self.double_end_time = pygame.time.get_ticks() + config.SNACK_DURATION

    def get_puppy(self):
        """
        puppy 아이템을 획득하여 방어 효과를 활성화합니다.
        
        Returns:
            bool: puppy 획득 성공 여부
                  True = 획득 성공, False = 이미 보유 중
        
        이 메서드는 puppy와 충돌했을 때 자동으로 호출됩니다.
        """
        print(f"get_puppy 호출: 현재 defense_count={self.defense_count}")
        
        if self.defense_count == 0:  # puppy가 없을 때만 획득 가능
            self.defense_count = config.PUPPY_DEFENSE_COUNT  # config에서 방어 횟수 가져오기
            self.defense_active = True  # 방어 효과 활성화
            print(f"puppy 획득 성공: defense_count={self.defense_count}")
            return True  # puppy 획득 성공
            
        print(f"이미 puppy 보유 중: defense_count={self.defense_count}")
        return False  # 이미 puppy를 가지고 있음

    def use_defense(self):
        """
        방어 효과 사용 (충돌 시 자동 호출) - 현재는 사용되지 않음
        
        Returns:
            bool: 방어 효과 사용 성공 여부
                  True = 방어 성공, False = 방어 실패
        
        이 메서드는 이전 버전에서 사용되었지만, 현재는 remove_puppy_defense()로 대체되었습니다.
        """
        if self.defense_count > 0:
            self.defense_count -= 1  # 방어 횟수 1회 감소
            if self.defense_count <= 0:
                self.defense_active = False  # 방어 횟수가 0이 되면 비활성화
            return True  # 방어 성공
        return False  # 방어 실패

    def has_defense(self):
        """
        현재 방어 효과 보유 여부를 확인합니다.
        
        Returns:
            bool: 방어 효과 보유 여부
                  True = 방어 효과 있음, False = 방어 효과 없음
        
        이 메서드는 충돌 감지 시 플레이어가 방어 효과를 가지고 있는지 확인하는 데 사용됩니다.
        """
        has_defense = self.defense_count > 0
        print(f"has_defense 호출: defense_count={self.defense_count}, has_defense={has_defense}")
        return has_defense

    def remove_puppy_defense(self):
        """
        puppy 방어 효과를 소모합니다 (충돌 시 자동 호출).
        
        Returns:
            bool: 방어 효과 소모 성공 여부
                  True = 소모 성공, False = 소모 실패
        
        이 메서드는 플레이어가 적이나 돌과 충돌했을 때 자동으로 호출됩니다.
        방어 횟수가 1회 감소하고, 0이 되면 방어 효과가 비활성화됩니다.
        """
        if self.defense_count > 0:
            self.defense_count -= 1  # 방어 횟수 1회 감소
            if self.defense_count <= 0:
                self.defense_active = False  # 방어 횟수가 0이 되면 비활성화
                print(f"🐕 puppy 방어 효과 완전 소모됨")
            else:
                print(f"🐕 puppy 방어 효과 1회 소모, 남은 횟수: {self.defense_count}")
            return True
        return False

    def draw_puppy(self, screen):
        """
        플레이어 오른쪽에 puppy를 표시합니다 (방어 효과 활성화 시).
        
        Args:
            screen: pygame 화면 객체 (그리기 대상)
        
        이 메서드는 플레이어가 puppy 방어 효과를 가지고 있을 때만 호출됩니다.
        puppy 이미지를 플레이어 오른쪽에 작은 크기로 표시합니다.
        """
        if self.defense_count > 0:  # puppy가 있을 때만 표시
            try:
                # puppy 이미지 로드 (원본 이미지, 좌우 반전 없음)
                puppy_image = pygame.image.load("assets/puppy.png").convert_alpha()
                
                # 이미지 크기 조정 (플레이어보다 작게)
                puppy_size = config.PUPPY_DISPLAY_SIZE
                puppy_image = pygame.transform.scale(puppy_image, (puppy_size, puppy_size))
                
                # 플레이어 오른쪽에 표시할 위치 계산
                puppy_x = self.rect.right + 10  # 플레이어 오른쪽에서 10픽셀 떨어진 위치
                puppy_y = self.rect.centery     # 플레이어 중앙 높이
                
                # puppy 이미지를 화면에 그리기
                # blit(이미지, (x, y))로 이미지를 지정된 위치에 그립니다
                # puppy_size//2를 빼는 이유는 이미지의 중심을 기준으로 위치를 맞추기 위함입니다
                screen.blit(puppy_image, (puppy_x - puppy_size//2, puppy_y - puppy_size//2))
                
            except:
                # 이미지 로드 실패 시 주황색 원으로 대체
                puppy_x = self.rect.right + 10
                puppy_y = self.rect.centery
                # draw_circle(화면, 색상, (x, y), 반지름)으로 원을 그립니다
                pygame.draw.circle(screen, (255, 200, 100), (puppy_x, puppy_y), config.PUPPY_DISPLAY_SIZE//2)


# ============================================================================
# 🥷 수리검 클래스 (Shuriken Class)
# ============================================================================
# 수리검은 플레이어가 발사하는 무기입니다.
# Z 키를 누르면 발사되며, 적을 공격할 수 있습니다.

class Shuriken(pygame.sprite.Sprite):
    """
    수리검 클래스
    
    주요 기능:
    - 플레이어가 발사하는 투척 무기
    - 오른쪽으로 직선 이동
    - 적과 충돌 시 데미지
    - 화면 밖으로 나가면 자동 제거
    
    pygame.sprite.Sprite를 상속받아 Pygame의 스프라이트 시스템을 사용합니다.
    """
    
    def __init__(self, x, y):
        """
        수리검 초기화 - 수리검 객체가 생성될 때 한 번만 실행됩니다.
        
        Args:
            x: 수리검 시작 X 좌표 (보통 플레이어의 오른쪽 위치)
            y: 수리검 시작 Y 좌표 (보통 플레이어의 중앙 높이)
        
        이 메서드에서:
        - 수리검의 이미지를 로드하고 크기를 조정합니다
        - 수리검의 초기 위치를 설정합니다
        - 수리검의 이동 속도를 설정합니다
        """
        super().__init__()  # pygame.sprite.Sprite 초기화 (반드시 필요)
        
        # ===== 이미지 로드 및 설정 =====
        try:
            # assets/shuriken.png 파일을 로드하여 수리검 이미지로 사용
            # convert_alpha()는 투명도를 지원하는 이미지 형식으로 변환합니다
            self.original_image = pygame.image.load("assets/shuriken.png").convert_alpha()
            
            # config.py에 정의된 크기로 이미지 조정
            # transform.scale(이미지, (너비, 높이))로 크기를 변경합니다
            self.image = pygame.transform.scale(self.original_image, (config.SHURIKEN_WIDTH, config.SHURIKEN_HEIGHT))
        except:
            # 이미지 로드 실패 시 검은색 사각형으로 대체
            # Surface(너비, 높이)로 빈 이미지를 만들고 fill(색상)로 채웁니다
            self.image = pygame.Surface((config.SHURIKEN_WIDTH, config.SHURIKEN_HEIGHT))
            self.image.fill(config.BLACK)  # 검은색 사각형
            print("⚠️ 수리검 이미지 로드 실패 - 기본 사각형 사용")
        
        # ===== 충돌 영역 설정 =====
        # rect는 수리검의 충돌 영역을 나타냅니다
        # get_rect(center=(x, y))로 이미지 중심을 기준으로 사각형을 생성합니다
        self.rect = self.image.get_rect(center=(x, y))
        
        # ===== 이동 속도 설정 =====
        # 수리검 이동 속도 (config.py에서 가져옴)
        # 양수 값이므로 오른쪽으로 이동합니다
        self.speed = config.SHURIKEN_SPEED
    
    def update(self, keys=None):
        """
        수리검 상태 업데이트 - 매 프레임마다 호출됩니다.
        
        Args:
            keys: 키 입력 (수리검은 자동 이동하므로 사용하지 않음)
        
        이 메서드에서:
        - 수리검을 오른쪽으로 이동시킵니다
        - 화면 밖으로 나가면 자동으로 제거합니다
        """
        # ===== 수리검 이동 =====
        # 수리검을 오른쪽으로 이동 (X좌표 증가)
        self.rect.x += self.speed
        
        # ===== 화면 경계 체크 =====
        # 화면 왼쪽 밖으로 나가면 자동 제거 (메모리 절약)
        # 화면 왼쪽 경계는 0보다 작은 값입니다
        if self.rect.left > config.WIDTH:
            self.kill()  # 스프라이트를 제거하고 메모리에서 해제

# ============================================================================
# 🐱 적 고양이 클래스 (EnemyCat Class)
# ============================================================================
# 적 고양이는 플레이어를 공격하는 적입니다.
# 노란색, 검은색, 흰색의 세 가지 타입이 있으며, 각각 다른 특성을 가집니다.

class EnemyCat(pygame.sprite.Sprite):
    """
    적 고양이 클래스
    
    고양이 타입별 특성:
    - 노란색: 기본 고양이 (보통 체력, 보통 속도)
    - 검은색: 강한 고양이 (높은 체력, 느린 속도)
    - 흰색: 빠른 고양이 (낮은 체력, 빠른 속도, 점프 능력)
    
    주요 기능:
    - 왼쪽으로 자동 이동
    - 플레이어와 충돌 시 게임오버
    - 수리검에 맞으면 체력 감소
    - 흰색 고양이는 점프하면서 이동
    
    pygame.sprite.Sprite를 상속받아 Pygame의 스프라이트 시스템을 사용합니다.
    """
    
    def __init__(self, x, y, color_name, stage=1):
        """
        적 고양이 초기화 - 고양이 객체가 생성될 때 한 번만 실행됩니다.
        
        Args:
            x: 고양이 시작 X 좌표 (보통 화면 오른쪽에서 시작)
            y: 고양이 시작 Y 좌표 (보통 지면 높이)
            color_name: 고양이 색상 ("yellow", "black", "white")
            stage: 현재 스테이지 (체력 계산에 사용, 기본값: 1)
        
        이 메서드에서:
        - 고양이의 색상과 체력을 설정합니다
        - 고양이의 크기와 이미지를 설정합니다
        - 고양이의 이동 속도를 설정합니다
        - 점프 관련 변수들을 초기화합니다 (흰색 고양이용)
        """
        super().__init__()  # pygame.sprite.Sprite 초기화 (반드시 필요)
        
        # ===== 고양이 속성 설정 =====
        self.color_name = color_name  # 색상 이름 저장 (예: "yellow", "black", "white")
        self.color = self.get_color(color_name)  # 실제 색상 값 가져오기 (RGB)
        self.hp = self.get_hp(color_name, stage)  # 체력 설정 (스테이지에 따라 증가)
        
        # ===== 고양이 크기 설정 =====
        # 색상별로 다른 크기 설정 (config.py에서 가져옴)
        self.width, self.height = config.ENEMY_CAT_SIZE[color_name]
        
        # ===== 점프 관련 변수 (흰색 고양이용) =====
        self.vel_y = 0        # Y축 속도 (점프, 낙하할 때 사용)
        self.on_ground = False # 지면 접촉 여부 (점프 가능 여부 판단용)
        self.jump_timer = 0   # 점프 타이머 (점프 간격 조절용)
        self.jump_interval = config.WHITE_CAT_JUMP_INTERVAL  # 점프 간격 (config에서 가져옴)
        
        # ===== 고양이 이미지 로드 및 크기 조정 =====
        try:
            # assets/ 폴더에서 해당 색상의 고양이 이미지 로드
            # f-string을 사용하여 동적으로 파일 경로 생성
            image_path = f"assets/cat_{color_name}.png"
            self.original_image = pygame.image.load(image_path).convert_alpha()
            
            # config.py에 정의된 크기로 이미지 조정
            self.image = pygame.transform.scale(self.original_image, (self.width, self.height))
        except:
            # 이미지 로드 실패 시 색상 사각형으로 대체
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(self.color)  # 고양이 색상으로 채움
            print(f"⚠️ {color_name} 고양이 이미지 로드 실패 - 기본 사각형 사용")
        
        # ===== 고양이의 충돌 영역 설정 =====
        # rect는 고양이의 충돌 영역을 나타냅니다
        # midbottom=(x, y)는 사각형의 하단 중앙을 기준으로 위치를 설정합니다
        self.rect = self.image.get_rect(midbottom=(x, y))
        
        # ===== 고양이 이동 속도 설정 =====
        # 색상별로 다른 이동 속도 (config.py에서 가져옴)
        self.speed = config.ENEMY_CAT_SPEED[color_name]
    
    def get_color(self, color_name):
        """
        색상 이름에 따른 실제 색상 값(RGB)을 반환합니다.
        
        Args:
            color_name: 색상 이름 ("yellow", "black", "white")
            
        Returns:
            tuple: RGB 색상 값 (예: (255, 255, 0) = 노란색)
        """
        # 색상 이름과 실제 색상 값을 매핑하는 딕셔너리
        color_map = {
            "yellow": config.YELLOW,  # 노란색 (255, 255, 0)
            "black": config.BLACK,    # 검은색 (0, 0, 0)
            "white": config.WHITE     # 흰색 (255, 255, 255)
        }
        # get() 메서드로 색상을 가져오고, 없으면 기본값(흰색) 반환
        return color_map.get(color_name, config.WHITE)
    
    def get_hp(self, color_name, stage):
        """
        색상과 스테이지에 따른 체력을 계산합니다.
        
        Args:
            color_name: 색상 이름 ("yellow", "black", "white")
            stage: 현재 스테이지 (1부터 시작)
            
        Returns:
            int: 계산된 체력 값
            
        체력 계산 공식:
        - 기본 체력은 색상별로 다름
        - 스테이지가 올라갈수록 체력이 증가 (난이도 조절)
        """
        # 기본 체력 (색상별로 다름)
        base_hp = {
            "yellow": 1,  # 노란색: 기본 체력 (1)
            "black": 2,   # 검은색: 높은 체력 (2)
            "white": 1    # 흰색: 낮은 체력 (1)
        }
        
        # 스테이지가 올라갈수록 체력 증가 (난이도 조절)
        # stage_multiplier = 1 + (stage - 1) * 0.5
        # 예: 스테이지 1 = 1.0, 스테이지 2 = 1.5, 스테이지 3 = 2.0
        stage_multiplier = 1 + (stage - 1) * 0.5
        
        # 기본 체력 × 스테이지 배율로 최종 체력 계산
        return int(base_hp.get(color_name, 1) * stage_multiplier)
    
    def update(self, keys=None):
        """
        적 고양이 상태 업데이트 - 매 프레임마다 호출됩니다.
        
        Args:
            keys: 키 입력 (적은 자동 동작하므로 사용하지 않음)
        
        이 메서드에서:
        - 흰색 고양이의 점프를 처리합니다
        - 고양이를 왼쪽으로 이동시킵니다
        - 화면 밖으로 나가면 자동으로 제거합니다
        """
        # ===== 흰색 고양이 점프 로직 =====
        if self.color_name == "white":  # 흰색 고양이일 때만 점프
            # 점프 타이머 증가 (약 60FPS 기준으로 16ms씩 증가)
            self.jump_timer += 16
            
            # 점프 간격에 도달하면 점프
            if self.jump_timer >= self.jump_interval:
                self.vel_y = config.WHITE_CAT_JUMP_VELOCITY  # 점프 속도 설정 (음수 = 위로)
                self.jump_timer = 0  # 타이머 리셋
            
            # 중력 적용 (점프 후 낙하)
            self.vel_y += config.WHITE_CAT_GRAVITY
            
            # Y축 위치 업데이트
            self.rect.y += self.vel_y
            
            # ===== 지면 처리 =====
            # 바닥에 닿으면 점프 속도 초기화
            if self.rect.bottom >= config.HEIGHT - 50:
                self.rect.bottom = config.HEIGHT - 50  # 바닥에 고정
                self.vel_y = 0  # 낙하 속도 초기화
        
        # ===== 고양이 이동 =====
        # 고양이를 왼쪽으로 이동 (X좌표 감소)
        self.rect.x -= self.speed
        
        # ===== 화면 경계 체크 =====
        # 화면 왼쪽 밖으로 나가면 자동 제거 (메모리 절약)
        if self.rect.right < 0:
            self.kill()  # 스프라이트를 제거하고 메모리에서 해제

# ============================================================================
# 👑 보스 고양이 클래스 (BossCat Class)
# ============================================================================
# 보스 고양이는 각 스테이지의 최종 보스입니다.
# 일반 고양이보다 훨씬 강하며, 돌을 던져서 공격합니다.

class BossCat(pygame.sprite.Sprite):
    """
    보스 고양이 클래스
    
    주요 기능:
    - 높은 체력과 공격력
    - 주기적으로 돌을 던져서 공격
    - 수리검에 맞으면 체력 감소
    - 체력이 0이 되면 다음 스테이지로 진행
    - 스테이지가 올라갈수록 체력 증가
    
    pygame.sprite.Sprite를 상속받아 Pygame의 스프라이트 시스템을 사용합니다.
    """
    
    def __init__(self, x, y, stage=1):
        """
        보스 고양이 초기화 - 보스 객체가 생성될 때 한 번만 실행됩니다.
        
        Args:
            x: 보스 시작 X 좌표 (보통 화면 오른쪽에서 시작)
            y: 보스 시작 Y 좌표 (보통 지면 높이)
            stage: 현재 스테이지 (체력 계산에 사용, 기본값: 1)
        
        이 메서드에서:
        - 보스의 크기와 이미지를 설정합니다
        - 보스의 체력을 설정합니다 (스테이지에 따라 증가)
        - 보스의 공격 관련 변수들을 초기화합니다
        """
        super().__init__()  # pygame.sprite.Sprite 초기화 (반드시 필요)
        
        # ===== 보스 크기 설정 =====
        self.width = config.BOSS_CAT_WIDTH   # 보스 너비 (config.py에서 가져옴)
        self.height = config.BOSS_CAT_HEIGHT # 보스 높이 (config.py에서 가져옴)
        
        # ===== 보스 이미지 로드 및 크기 조정 =====
        try:
            # assets/cat_boss.png 파일을 로드하여 보스 이미지로 사용
            self.original_image = pygame.image.load("assets/cat_boss.png").convert_alpha()
            
            # config.py에 정의된 크기로 이미지 조정
            self.image = pygame.transform.scale(self.original_image, (self.width, self.height))
        except:
            # 이미지 로드 실패 시 빨간색 사각형으로 대체
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(config.RED)  # 빨간색 사각형
            print("⚠️ 보스 고양이 이미지 로드 실패 - 기본 사각형 사용")
        
        # ===== 보스의 충돌 영역 설정 =====
        # rect는 보스의 충돌 영역을 나타냅니다
        # midbottom=(x, y)는 사각형의 하단 중앙을 기준으로 위치를 설정합니다
        self.rect = self.image.get_rect(midbottom=(x, y))
        
        # ===== 보스 체력 설정 =====
        # 스테이지에 따라 체력이 증가합니다
        # 기본 체력 * 2^(스테이지-1) 공식으로 계산
        # 예: 스테이지 1 = 50, 스테이지 2 = 100, 스테이지 3 = 200
        self.hp = config.BASE_BOSS_HP * (2 ** (stage - 1))
        
        # ===== 보스 공격 관련 변수 =====
        self.attack_timer = 0        # 공격 타이머 (공격 간격 조절용)
        self.attack_interval = config.BOSS_ATTACK_INTERVAL  # 공격 간격 (config에서 가져옴)
        
        # 보스 스폰 시 콘솔에 정보 출력 (디버깅용)
        print(f"👑 보스 고양이 스폰! 체력: {self.hp}, 스테이지: {stage}")
    
    def update(self, keys=None):
        """
        보스 고양이 상태 업데이트 - 매 프레임마다 호출됩니다.
        
        Args:
            keys: 키 입력 (보스는 자동 동작하므로 사용하지 않음)
        
        이 메서드에서:
        - 보스의 공격 타이머를 관리합니다
        - 공격 간격에 도달하면 돌을 던집니다
        - 돌을 적절한 스프라이트 그룹에 추가합니다
        """
        # ===== 공격 타이머 관리 =====
        # 공격 타이머 증가 (약 60FPS 기준으로 16ms씩 증가)
        self.attack_timer += 16
        
        # ===== 공격 실행 =====
        # 공격 간격에 도달하면 돌 던지기
        if self.attack_timer >= self.attack_interval:
            self.attack_timer = 0  # 타이머 리셋
            
            # ===== 돌 생성 및 던지기 =====
            # 보스 위치에서 약간 오프셋된 위치에 돌 생성
            # config.py에서 설정된 오프셋 값 사용
            stone_x = self.rect.centerx + config.STONE_SPAWN_OFFSET_X  # X축 오프셋
            stone_y = self.rect.bottom + config.STONE_SPAWN_OFFSET_Y   # Y축 오프셋
            
            # Stone 객체 생성 (새로운 돌 공격)
            stone = Stone(stone_x, stone_y)
            
            # 돌을 적절한 스프라이트 그룹에 추가
            stones.add(stone)        # stones 그룹에 추가 (돌 관리용)
            all_sprites.add(stone)   # 전체 스프라이트 그룹에 추가 (화면 표시용)
            
            # 돌 던지기 로그 출력 (디버깅용)
            print(f"🪨 보스가 돌을 던졌습니다! 위치: ({stone_x}, {stone_y})")
        
        # ===== 보스 동작 =====
        # 보스는 제자리에 고정 (이동하지 않음)
        # 필요시 여기에 보스 이동 로직 추가 가능
        # 예: 플레이어를 향해 이동, 패턴별 움직임 등

# ============================================================================
# 🍪 간식 클래스 (Snack Class)
# ============================================================================
# 간식은 플레이어가 획득하면 더블 수리검 효과를 주는 아이템입니다.
# 각 스테이지마다 한 번만 스폰되며, 플레이어가 먹으면 효과가 적용됩니다.

class Snack(pygame.sprite.Sprite):
    """
    간식 클래스
    
    주요 기능:
    - 플레이어가 획득하면 더블 수리검 효과 활성화
    - 효과 지속 시간 동안 두 개의 수리검을 동시에 발사
    - 왼쪽으로 자동 이동
    - 화면 밖으로 나가면 자동 제거
    
    pygame.sprite.Sprite를 상속받아 Pygame의 스프라이트 시스템을 사용합니다.
    """
    
    def __init__(self, x, y):
        """
        간식 초기화 - 간식 객체가 생성될 때 한 번만 실행됩니다.
        
        Args:
            x: 간식 시작 X 좌표 (보통 화면 오른쪽에서 시작)
            y: 간식 시작 Y 좌표 (보통 지면 위쪽)
        
        이 메서드에서:
        - 간식의 크기와 이미지를 설정합니다
        - 간식의 초기 위치를 설정합니다
        - 간식의 이동 속도를 설정합니다
        """
        super().__init__()  # pygame.sprite.Sprite 초기화 (반드시 필요)
        
        # ===== 간식 크기 설정 =====
        self.size = config.SNACK_SIZE  # 간식 크기 (config.py에서 가져옴)
        
        # ===== 간식 이미지 로드 및 크기 조정 =====
        try:
            # assets/snack.png 파일을 로드하여 간식 이미지로 사용
            self.original_image = pygame.image.load("assets/snack.png").convert_alpha()
            
            # config.py에 정의된 크기로 이미지 조정
            self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        except:
            # 이미지 로드 실패 시 초록색 사각형으로 대체
            self.image = pygame.Surface((self.size, self.size))
            self.image.fill(config.GREEN)  # 초록색 사각형
            print("⚠️ 간식 이미지 로드 실패 - 기본 사각형 사용")
        
        # ===== 간식의 충돌 영역 설정 =====
        # rect는 간식의 충돌 영역을 나타냅니다
        # center=(x, y)는 사각형의 중심을 기준으로 위치를 설정합니다
        self.rect = self.image.get_rect(center=(x, y))
        
        # ===== 간식 이동 속도 설정 =====
        # 간식 이동 속도 (config.py에서 가져옴)
        # 양수 값이므로 오른쪽에서 왼쪽으로 이동합니다
        self.speed = config.SNACK_SPEED
    
    def update(self, keys=None):
        """
        간식 상태 업데이트 - 매 프레임마다 호출됩니다.
        
        Args:
            keys: 키 입력 (간식은 자동 이동하므로 사용하지 않음)
        
        이 메서드에서:
        - 간식을 왼쪽으로 이동시킵니다
        - 화면 밖으로 나가면 자동으로 제거합니다
        """
        # ===== 간식 이동 =====
        # 간식을 왼쪽으로 이동 (X좌표 감소)
        self.rect.x -= self.speed
        
        # ===== 화면 경계 체크 =====
        # 화면 왼쪽 밖으로 나가면 자동 제거 (메모리 절약)
        if self.rect.right < 0:
            self.kill()  # 스프라이트를 제거하고 메모리에서 해제

# ============================================================================
# 🐕 강아지 방어 아이템 클래스 (Puppy Class)
# ============================================================================
# Puppy는 플레이어가 획득하면 방어 효과를 주는 특별한 아이템입니다.
# 플레이어가 고양이, 보스, 돌과 충돌해도 게임오버되지 않게 해줍니다.

class Puppy(pygame.sprite.Sprite):
    """
    강아지 방어 아이템 클래스
    
    주요 기능:
    - 플레이어가 획득하면 방어 효과 활성화
    - 충돌 시 자동으로 방어 효과 소모
    - 방어 횟수만큼 충돌을 막아줌
    - 왼쪽으로 자동 이동
    - 화면 밖으로 나가면 자동 제거
    
    pygame.sprite.Sprite를 상속받아 Pygame의 스프라이트 시스템을 사용합니다.
    """
    
    def __init__(self, x, y):
        """
        강아지 방어 아이템 초기화 - puppy 객체가 생성될 때 한 번만 실행됩니다.
        
        Args:
            x: puppy 시작 X 좌표 (보통 화면 오른쪽에서 시작)
            y: puppy 시작 Y 좌표 (보통 지면 위쪽)
        
        이 메서드에서:
        - puppy의 크기와 이미지를 설정합니다
        - puppy의 초기 위치를 설정합니다
        - puppy의 이동 속도를 설정합니다
        """
        super().__init__()  # pygame.sprite.Sprite 초기화 (반드시 필요)
        
        # ===== puppy 크기 설정 =====
        self.size = config.PUPPY_SIZE  # puppy 크기 (config.py에서 가져옴)
        
        # ===== puppy 이미지 로드 및 크기 조정 =====
        try:
            # assets/puppy.png 파일을 로드하여 puppy 이미지로 사용
            self.original_image = pygame.image.load("assets/puppy.png").convert_alpha()
            
            # 이미지 크기 조정
            self.original_image = pygame.transform.scale(self.original_image, (self.size, self.size))
            
            # 좌우 반전된 이미지 (왼쪽에서 오른쪽으로 이동하므로 반전 필요)
            # transform.flip(이미지, 가로반전, 세로반전)
            # True = 가로 반전, False = 세로 반전 안함
            self.image = pygame.transform.flip(self.original_image, True, False)
        except:
            # 이미지 로드 실패 시 연한 주황색 사각형으로 대체
            self.image = pygame.Surface((self.size, self.size))
            self.image.fill((255, 200, 100))  # 연한 주황색
            print("⚠️ 강아지 이미지 로드 실패 - 기본 사각형 사용")
        
        # ===== puppy의 충돌 영역 설정 =====
        # rect는 puppy의 충돌 영역을 나타냅니다
        # center=(x, y)는 사각형의 중심을 기준으로 위치를 설정합니다
        self.rect = self.image.get_rect(center=(x, y))
        
        # ===== puppy 이동 속도 설정 =====
        # puppy 이동 속도 (고정값, config에서 가져오지 않음)
        # 양수 값이므로 오른쪽에서 왼쪽으로 이동합니다
        self.speed = 3
    
    def update(self, keys=None):
        """
        강아지 방어 아이템 상태 업데이트 - 매 프레임마다 호출됩니다.
        
        Args:
            keys: 키 입력 (puppy는 자동 이동하므로 사용하지 않음)
        
        이 메서드에서:
        - puppy를 왼쪽으로 이동시킵니다
        - 화면 밖으로 나가면 자동으로 제거합니다
        """
        # ===== puppy 이동 =====
        # puppy를 왼쪽으로 이동 (X좌표 감소)
        self.rect.x -= self.speed
        
        # ===== 화면 경계 체크 =====
        # 화면 왼쪽 밖으로 나가면 자동 제거 (메모리 절약)
        if self.rect.right < 0:
            self.kill()  # 스프라이트를 제거하고 메모리에서 해제

# ============================================================================
# 🪨 돌 공격 클래스 (Stone Class)
# ============================================================================
# Stone은 보스 고양이가 던지는 공격 무기입니다.
# 플레이어와 충돌하면 게임오버가 되며, 중력의 영향을 받아 포물선을 그리며 이동합니다.

class Stone(pygame.sprite.Sprite):
    """
    돌 공격 클래스
    
    주요 기능:
    - 보스 고양이가 주기적으로 던지는 공격
    - 중력의 영향을 받아 포물선 궤도로 이동
    - 플레이어와 충돌 시 게임오버
    - 화면 밖으로 나가면 자동 제거
    
    pygame.sprite.Sprite를 상속받아 Pygame의 스프라이트 시스템을 사용합니다.
    """
    
    def __init__(self, x, y):
        """
        돌 공격 초기화 - 돌 객체가 생성될 때 한 번만 실행됩니다.
        
        Args:
            x: 돌 시작 X 좌표 (보통 보스 고양이 위치에서 시작)
            y: 돌 시작 Y 좌표 (보통 보스 고양이 아래쪽)
        
        이 메서드에서:
        - 돌의 크기와 이미지를 설정합니다
        - 돌의 초기 위치를 설정합니다
        - 돌의 물리 속성(속도, 중력 등)을 설정합니다
        """
        super().__init__()  # pygame.sprite.Sprite 초기화 (반드시 필요)
        
        # ===== 돌 크기 설정 =====
        self.radius = config.STONE_RADIUS  # 돌 반지름 (config.py에서 가져옴)
        
        # ===== 돌 이미지 로드 및 크기 조정 =====
        try:
            # assets/stone.png 파일을 로드하여 돌 이미지로 사용
            self.original_image = pygame.image.load("assets/stone.png").convert_alpha()
            
            # 이미지 크기 조정 (radius*2 x radius*2)
            # 돌의 지름은 반지름의 2배이므로 (radius*2, radius*2) 크기로 설정
            self.image = pygame.transform.scale(self.original_image, (self.radius*2, self.radius*2))
        except:
            # 이미지 로드 실패 시 회색 원으로 대체
            # SRCALPHA는 투명도를 지원하는 Surface를 생성합니다
            self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            
            # draw_circle(이미지, 색상, (x, y), 반지름)으로 원을 그립니다
            # (radius, radius)는 Surface의 중심점입니다
            pygame.draw.circle(self.image, config.GRAY, (self.radius, self.radius), self.radius)
            print("⚠️ 돌 이미지 로드 실패 - 기본 원형 사용")
        
        # ===== 돌의 충돌 영역 설정 =====
        # rect는 돌의 충돌 영역을 나타냅니다
        # center=(x, y)는 사각형의 중심을 기준으로 위치를 설정합니다
        self.rect = self.image.get_rect(center=(x, y))
        
        # ===== 돌의 물리 속성 설정 =====
        # 왼쪽으로만 던지기 (랜덤 속도)
        # random.randint(최소값, 최대값)으로 랜덤한 속도 생성
        random_speed = random.randint(config.STONE_SPEED_MIN, config.STONE_SPEED_MAX)
        self.vel_x = -random_speed  # 왼쪽으로 이동 (음수 = 왼쪽, 랜덤 속도)
        self.vel_y = 0              # 수평으로만 발사 (위아래 움직임 없음, 초기값)
        
        # ===== 중력 설정 =====
        # 중력 설정 (config.py에서 가져옴)
        # 양수 값이므로 아래쪽으로 가속됩니다
        self.gravity = config.STONE_GRAVITY
    
    def update(self, keys=None):
        """
        돌 공격 상태 업데이트 - 매 프레임마다 호출됩니다.
        
        Args:
            keys: 키 입력 (돌은 자동 이동하므로 사용하지 않음)
        
        이 메서드에서:
        - 중력을 적용하여 돌을 아래쪽으로 가속시킵니다
        - 돌의 위치를 업데이트합니다
        - 화면 밖으로 나가면 자동으로 제거합니다
        """
        # ===== 중력 적용 =====
        # 중력으로 인해 아래쪽으로 가속 (Y축 속도 증가)
        self.vel_y += self.gravity
        
        # ===== 위치 업데이트 =====
        self.rect.x += self.vel_x  # X축 이동 (왼쪽으로 일정한 속도)
        self.rect.y += self.vel_y  # Y축 이동 (중력의 영향을 받아 가속)
        
        # ===== 화면 경계 체크 및 제거 =====
        # 위쪽 경계: 화면 위로 나가면 제거
        if self.rect.top > config.HEIGHT:
            self.kill()
        # 왼쪽 경계: 화면 왼쪽으로 나가면 제거
        if self.rect.left < 0:
            self.kill()
        # 오른쪽 경계: 화면 오른쪽으로 나가면 제거
        if self.rect.right > config.WIDTH:
            self.kill()


# --- 그룹 ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
shurikens = pygame.sprite.Group()
items = pygame.sprite.Group()
puppies = pygame.sprite.Group()  # 강아지 아이템 그룹
stones = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

game_over = False
game_clear = False
spawn_timer = 0
snack_spawn_timer = 0
boss_spawned = False

def get_touch_rect(sprite, margin):
    rect = sprite.rect.copy()
    rect.inflate_ip(-margin*2, -margin*2)
    return rect

def draw_text(text, x, y, color=config.WHITE, font_type=font):
    img = font_type.render(text, True, color)
    screen.blit(img, (x, y))

def draw_centered_text(text, y, color=config.WHITE, font_type=font):
    img = font_type.render(text, True, color)
    x = (config.WIDTH - img.get_width()) // 2
    screen.blit(img, (x, y))

def draw_clouds():
    """배경에 구름을 그리는 함수"""
    cloud_color = (255, 255, 255)  # 흰색 구름
    
    # 구름 1 (왼쪽 위)
    pygame.draw.ellipse(screen, cloud_color, (50, 80, 120, 60))
    pygame.draw.ellipse(screen, cloud_color, (80, 70, 80, 50))
    pygame.draw.ellipse(screen, cloud_color, (110, 90, 60, 40))
    
    # 구름 2 (오른쪽 위)
    pygame.draw.ellipse(screen, cloud_color, (600, 60, 100, 50))
    pygame.draw.ellipse(screen, cloud_color, (630, 50, 70, 40))
    pygame.draw.ellipse(screen, cloud_color, (660, 70, 50, 30))
    
    # 구름 3 (중앙 위)
    pygame.draw.ellipse(screen, cloud_color, (350, 100, 90, 45))
    pygame.draw.ellipse(screen, cloud_color, (380, 90, 60, 35))
    pygame.draw.ellipse(screen, cloud_color, (410, 105, 40, 25))

def draw_background_elements():
    # 산 그리기 (멀리, 큰 삼각형)
    mountain_color = (120, 180, 120)
    pygame.draw.polygon(screen, mountain_color, [(100, config.HEIGHT-50), (300, 200), (500, config.HEIGHT-50)])
    pygame.draw.polygon(screen, mountain_color, [(400, config.HEIGHT-50), (600, 250), (800, config.HEIGHT-50)])
    pygame.draw.polygon(screen, (100, 150, 100), [(0, config.HEIGHT-50), (120, 300), (250, config.HEIGHT-50)])

    # 나무 그리기 (여러 개)
    for x in [150, 250, 600, 700]:
        # 나무 기둥
        pygame.draw.rect(screen, (100, 60, 20), (x, config.HEIGHT-120, 20, 70))
        # 나뭇잎 (원)
        pygame.draw.ellipse(screen, (30, 120, 30), (x-20, config.HEIGHT-150, 60, 50))

def draw_menu():
    screen.fill(config.BACKGROUND_COLOR)
    pygame.draw.rect(screen, config.GROUND_COLOR, (0, config.HEIGHT-50, config.WIDTH, 50))
    
    # 게임 제목
    draw_centered_text("개 닌자 대모험", 100, config.BLUE, font_title)
    
    # 조작법
    draw_text("조작법:", 50, 200, config.WHITE, font)
    draw_text("← → : 이동", 70, 230, config.WHITE, font_small)
    draw_text("스페이스바 : 점프", 70, 250, config.WHITE, font_small)
    draw_text("Z : 수리검 발사", 70, 270, config.WHITE, font_small)
    draw_text("R : 게임 재시작", 70, 290, config.WHITE, font_small)
    
    # 게임 시작 안내
    draw_centered_text("스페이스바를 눌러 게임 시작", 350, config.GREEN, font)
    
    pygame.display.flip()

def reset_game():
    global game_over, game_clear, spawn_timer, snack_spawn_timer, puppy_spawn_timer, boss_spawned, cats_spawned, total_cats, current_stage, stage_start_time
    game_over = False
    game_clear = False
    current_stage = 1  # 스테이지 1부터 시작
    stage_start_time = pygame.time.get_ticks()  # 스테이지 시작 시간 기록
    player.alive = True
    player.rect.bottomleft = (50, config.HEIGHT - 50)
    player.shuriken_double = False
    player.double_end_time = 0
    player.defense_count = 0  # 방어 횟수 초기화
    player.defense_active = False  # 방어 효과 초기화
    
    # 스프라이트 그룹 초기화
    for group in [enemies, shurikens, items, puppies, stones]:
        group.empty()
    all_sprites.empty()
    all_sprites.add(player)
    
    # 게임 상태 변수 초기화
    spawn_timer = 0
    snack_spawn_timer = 0
    puppy_spawn_timer = 0  # puppy 전용 타이머 추가
    cats_spawned = 0  # 고양이 스폰 개수 초기화 (중요!)
    boss_spawned = False  # 보스 스폰 상태 초기화
    reset_game.next_puppy_interval = random.randint(config.PUPPY_SPAWN_MIN_INTERVAL, config.PUPPY_SPAWN_MAX_INTERVAL)  # 다음 puppy 스폰 간격
    reset_game.snack_spawned = False  # 간식 스폰 플래그 초기화
    
    print(f"🎮 게임 리셋 완료 - cats_spawned: {cats_spawned}, boss_spawned: {boss_spawned}")
    print(f"🎮 puppy_spawn_timer: {puppy_spawn_timer}, next_interval: {reset_game.next_puppy_interval}ms")


# 게임 상태 변수
game_state = "menu"  # "menu", "playing", "game_over", "game_clear"
current_stage = 1  # 현재 스테이지
cats_spawned = 0
total_cats = config.TOTAL_CATS_TO_SPAWN
stage_start_time = 0  # 스테이지 시작 시간

running = True
while running:
    dt = clock.tick(config.FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_SPACE:
                    print(f"🎮 메뉴에서 게임 시작 - game_state: {game_state} -> playing")
                    game_state = "playing"
                    reset_game()
            
            elif game_state == "playing":
                if event.key == pygame.K_z and player.alive:
                    if player.shuriken_double:
                        sh1 = Shuriken(player.rect.right, player.rect.centery - 10)
                        sh2 = Shuriken(player.rect.right, player.rect.centery + 10)
                        shurikens.add(sh1, sh2)
                        all_sprites.add(sh1, sh2)
                    else:
                        sh = Shuriken(player.rect.right, player.rect.centery)
                        shurikens.add(sh)
                        all_sprites.add(sh)
            
            elif game_state in ["game_over", "game_clear"]:
                if event.key == pygame.K_r:
                    print(f"🎮 게임 재시작 - game_state: {game_state} -> playing")
                    game_state = "playing"
                    reset_game()
                elif event.key == pygame.K_m:
                    print(f"🎮 메뉴로 돌아가기 - game_state: {game_state} -> menu")
                    game_state = "menu"

    if game_state == "menu":
        draw_menu()
    
    elif game_state == "playing":
        all_sprites.update(keys)

        # 고양이 스폰 로직
        if cats_spawned < total_cats and not boss_spawned:
            spawn_timer += dt
            if spawn_timer > config.ENEMY_SPAWN_INTERVAL:
                spawn_timer = 0
                cat_type = random.choice(["yellow", "black", "white"])
                cat = EnemyCat(config.WIDTH + 50, config.HEIGHT - 50, cat_type, current_stage)
                enemies.add(cat)
                all_sprites.add(cat)
                cats_spawned += 1
                print(f"🐱 고양이 스폰됨 (타입: {cat_type}, 스폰된 수: {cats_spawned}/{total_cats})")
                print(f"🐱 현재 enemies 그룹 크기: {len(enemies)}")
        else:
            # 고양이 스폰이 멈춘 이유 로깅
            if cats_spawned >= total_cats:
                print(f"🐱 고양이 스폰 완료: {cats_spawned}/{total_cats}")
            if boss_spawned:
                print(f"🐱 보스 스폰됨 - 고양이 스폰 중단")
            if len(enemies) > 0:
                print(f"🐱 현재 enemies 그룹 크기: {len(enemies)}")

        # 간식 스폰 로직 (한 번만)
        if not hasattr(reset_game, 'snack_spawned') or not reset_game.snack_spawned:
            snack_spawn_timer += dt
            if snack_spawn_timer > config.SNACK_SPAWN_INTERVAL:
                snack_spawn_timer = 0
                snack = Snack(config.WIDTH + 30, config.HEIGHT - 80)
                items.add(snack)
                all_sprites.add(snack)
                reset_game.snack_spawned = True

        # 강아지 스폰 로직 (랜덤 간격으로 스폰)
        # next_puppy_interval이 정의되지 않았을 때 기본값 설정
        if not hasattr(reset_game, 'next_puppy_interval'):
            reset_game.next_puppy_interval = random.randint(config.PUPPY_SPAWN_MIN_INTERVAL, config.PUPPY_SPAWN_MAX_INTERVAL)
            print(f"🐕 next_puppy_interval 초기화: {reset_game.next_puppy_interval}ms")
        
        puppy_spawn_timer += dt
        # 매 1000ms마다만 로그 출력 (너무 많이 출력되지 않도록)
        if puppy_spawn_timer % 1000 < dt:
            print(f"🐕 puppy_spawn_timer: {puppy_spawn_timer}ms, next_interval: {reset_game.next_puppy_interval}ms")
        if puppy_spawn_timer > reset_game.next_puppy_interval:
            puppy_spawn_timer = 0
            puppy = Puppy(config.WIDTH + 30, config.HEIGHT - 80)
            puppies.add(puppy)
            all_sprites.add(puppy)
            print(f"🐕 puppy 스폰됨 (위치: {puppy.rect.x}, {puppy.rect.y}, 이미지: 좌우 반전)")
            print(f"🐕 현재 puppies 그룹 크기: {len(puppies)}")
            reset_game.next_puppy_interval = random.randint(config.PUPPY_SPAWN_MIN_INTERVAL, config.PUPPY_SPAWN_MAX_INTERVAL) # 다음 puppy 스폰 간격 업데이트
            print(f"🐕 다음 puppy 스폰 간격: {reset_game.next_puppy_interval}ms")

        # 모든 고양이를 처치했을 때 보스 스폰
        if cats_spawned >= total_cats and not boss_spawned and len(enemies) == 0:
            boss = BossCat(config.WIDTH - 150, config.HEIGHT - 50, current_stage)
            enemies.add(boss)
            all_sprites.add(boss)
            boss_spawned = True

        for shuriken in shurikens:
            if len(enemies) > 0:
                hit_cats = pygame.sprite.spritecollide(shuriken, enemies, False)
            else:
                hit_cats = []
            for cat in hit_cats:
                if isinstance(cat, BossCat):
                    cat.hp -= 1
                    if cat.hp <= 0:
                        cat.kill()
                        # 다음 스테이지로 진행
                        if current_stage < config.MAX_STAGE:
                            current_stage += 1
                            stage_start_time = pygame.time.get_ticks()  # 새 스테이지 시작 시간 기록
                            # 다음 스테이지 준비
                            cats_spawned = 0
                            boss_spawned = False
                            spawn_timer = 0
                            snack_spawn_timer = 0
                            puppy_spawn_timer = 0  # puppy 타이머 초기화
                            reset_game.next_puppy_interval = random.randint(config.PUPPY_SPAWN_MIN_INTERVAL, config.PUPPY_SPAWN_MAX_INTERVAL)  # 다음 puppy 스폰 간격 초기화
                            reset_game.snack_spawned = False
                            # 모든 스프라이트 제거 (플레이어 제외)
                            for group in [enemies, shurikens, items, puppies, stones]:
                                group.empty()
                            all_sprites.empty()
                            all_sprites.add(player)
                        else:
                            # 모든 스테이지 클리어
                            game_state = "game_clear"
                    shuriken.kill()
                else:
                    cat.hp -= 1
                    if cat.hp <= 0:
                        cat.kill()
                    shuriken.kill()

        # 충돌 체크 부분(playing 상태)
        # player_touch_rect = get_touch_rect(player, config.PLAYER_TOUCH_MARGIN)
        if len(items) > 0:
            hit_snack = pygame.sprite.spritecollide(player, items, True)
        else:
            hit_snack = []
        if hit_snack:
            player.eat_snack()

        # 강아지 충돌 감지
        if len(puppies) > 0:
            hit_puppy = pygame.sprite.spritecollide(player, puppies, True)
        else:
            hit_puppy = []
        if hit_puppy:
            print(f"🐕 puppy 충돌 감지! hit_puppy 개수: {len(hit_puppy)}")
            if player.get_puppy():
                # puppy 획득 성공
                print(f"🐕 puppy 획득 성공! (플레이어와 함께 표시: 원래 이미지)")
            else:
                # 이미 puppy를 가지고 있음 - hit_puppy를 다시 추가
                print(f"🐕 이미 puppy 보유 중 - puppy 반환")
                for puppy in hit_puppy:
                    puppies.add(puppy)
                    all_sprites.add(puppy)

        # 적과의 충돌 시 방어 효과 적용
        if len(enemies) > 0:
            enemy_touched = False
            touched_enemy = None
            # puppy가 있으면 정상 충돌 영역, 없으면 작은 충돌 영역 사용
            if player.has_defense():
                collision_rect = player.rect
                print(f"🐕 puppy 있음 - 정상 충돌 영역 사용")
            else:
                # puppy가 없을 때는 더 작은 충돌 영역 사용
                collision_rect = get_touch_rect(player, config.PUPPY_LESS_COLLISION_MARGIN)  # config에서 설정된 여백
                print(f"❌ puppy 없음 - 작은 충돌 영역 사용 (여유: {config.PUPPY_LESS_COLLISION_MARGIN}픽셀)")
            
            for enemy in enemies:
                if collision_rect.colliderect(enemy.rect):
                    enemy_touched = True
                    touched_enemy = enemy
                    break
            if enemy_touched:
                if player.has_defense():
                    # puppy가 있으면 방어 효과 적용
                    print(f"🐕 방어 효과 적용! 현재 방어 횟수: {player.defense_count}")
                    # 충돌한 적 제거
                    if touched_enemy:
                        touched_enemy.kill()
                        print(f"🐕 방어 효과로 적 제거됨")
                    # puppy 방어 효과 1회 소모
                    player.remove_puppy_defense()
                    # 방어 성공 - 게임 오버되지 않음
                else:
                    # puppy가 없으면 게임 오버
                    print("❌ 방어 효과 없음 - 게임 오버")
                    player.alive = False
                    game_state = "game_over"

        # 돌 충돌도 동일하게
        stone_touched = False
        touched_stone = None
        # puppy가 있으면 정상 충돌 영역, 없으면 작은 충돌 영역 사용
        if player.has_defense():
            collision_rect = player.rect
            print(f"🪨 puppy 있음 - 정상 충돌 영역 사용")
        else:
            # puppy가 없을 때는 더 작은 충돌 영역 사용
            collision_rect = get_touch_rect(player, config.PUPPY_LESS_COLLISION_MARGIN)  # config에서 설정된 여백
            print(f"🪨 puppy 없음 - 작은 충돌 영역 사용 (여유: {config.PUPPY_LESS_COLLISION_MARGIN}픽셀)")
        
        for stone in stones:
            if collision_rect.colliderect(stone.rect):
                stone_touched = True
                touched_stone = stone
                break
        if stone_touched:
            if player.has_defense():
                # puppy가 있으면 방어 효과 적용
                print(f"🪨 돌 충돌 방어 효과 적용! 현재 방어 횟수: {player.defense_count}")
                # 충돌한 stone 제거
                if touched_stone:
                    touched_stone.kill()
                    print(f"🪨 방어 효과로 stone 제거됨")
                # puppy 방어 효과 1회 소모
                player.remove_puppy_defense()
                # 방어 성공 - 게임 오버되지 않음
            else:
                # puppy가 없으면 게임 오버
                print("🪨 돌 충돌 방어 효과 없음 - 게임 오버")
                player.alive = False
                game_state = "game_over"

        # 게임 화면 그리기
        screen.fill(config.BACKGROUND_COLOR)
        draw_background_elements() # 배경 요소 그리기
        draw_clouds()  # 구름 그리기
        pygame.draw.rect(screen, config.GROUND_COLOR, (0, config.HEIGHT-50, config.WIDTH, 50))
        all_sprites.draw(screen)
        
        # 플레이어와 함께 puppy 표시
        player.draw_puppy(screen)

        # UI 정보 표시
        # 현재 스테이지 표시
        draw_text(f"스테이지 {current_stage}", 10, 10, config.WHITE, font_large)
        
        # 스테이지 시작 메시지 표시 (3초간)
        if pygame.time.get_ticks() - stage_start_time < 3000:
            stage_message = f"Stage {current_stage} 시작!"
            draw_centered_text(stage_message, 150, config.YELLOW, font_large)
        
        if player.shuriken_double:
            time_left = (player.double_end_time - pygame.time.get_ticks()) // 1000
            draw_text(f"간식 효과: {time_left}초", 10, 70, config.GREEN)
        
        # 방어 횟수 표시
        if player.defense_count > 0:
            draw_text(f"방어 효과: 활성화 ({player.defense_count}회)", 10, 100, config.YELLOW)
        else:
            draw_text("방어 효과: 비활성화", 10, 100, config.GRAY)
        
        # 남은 고양이 수 표시
        if not boss_spawned:
            remaining_cats = total_cats - cats_spawned + len([e for e in enemies if not isinstance(e, BossCat)])
            draw_text(f"남은 고양이: {remaining_cats}마리", 10, 50, config.WHITE)
            # 디버깅 정보 추가
            draw_text(f"스폰된 고양이: {cats_spawned}/{total_cats}", 10, 130, config.WHITE, font_small)
            draw_text(f"현재 enemies: {len(enemies)}", 10, 150, config.WHITE, font_small)
        else:
            # 보스 체력 표시
            boss = None
            for enemy in enemies:
                if isinstance(enemy, BossCat):
                    boss = enemy
                    break
            
            if boss:
                # 보스 HP를 오른쪽 상단에 표시
                draw_text("보스 고양이 출현!", config.WIDTH - 200, 10, config.RED, font_large)
                
                # 보스 체력 바 표시 (오른쪽 상단)
                health_bar_width = config.BOSS_HP_BAR_WIDTH
                health_bar_height = config.BOSS_HP_BAR_HEIGHT
                health_ratio = boss.hp / (config.BASE_BOSS_HP * (2 ** (current_stage - 1)))
                health_bar_x = config.WIDTH - health_bar_width - config.BOSS_HP_BAR_MARGIN  # 오른쪽에서 여백
                health_bar_y = 50
                
                # 배경 체력 바
                pygame.draw.rect(screen, (100, 100, 100), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
                # 현재 체력 바
                current_health_width = int(health_bar_width * health_ratio)
                health_color = (255, 0, 0) if health_ratio > 0.5 else (255, 255, 0) if health_ratio > 0.2 else (255, 0, 0)
                pygame.draw.rect(screen, health_color, (health_bar_x, health_bar_y, current_health_width, health_bar_height))
                # 체력 바 테두리
                pygame.draw.rect(screen, config.WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
                
                # 체력 수치 표시 (오른쪽 상단)
                max_boss_hp = config.BASE_BOSS_HP * (2 ** (current_stage - 1))
                draw_text(f"보스 체력: {boss.hp}/{max_boss_hp}", config.WIDTH - config.BOSS_HP_BAR_WIDTH - config.BOSS_HP_BAR_MARGIN, 80, config.WHITE)

        pygame.display.flip()
    
    elif game_state == "game_over":
        screen.fill(config.BACKGROUND_COLOR)
        draw_clouds()  # 구름 그리기
        pygame.draw.rect(screen, config.GROUND_COLOR, (0, config.HEIGHT-50, config.WIDTH, 50))
        all_sprites.draw(screen)
        
        # 플레이어와 함께 puppy 표시
        player.draw_puppy(screen)
        
        # 반투명 오버레이
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        draw_centered_text("게임 오버!", config.HEIGHT//2 - 60, config.RED, font_large)
        draw_centered_text("R 키: 재시작", config.HEIGHT//2 - 20, config.WHITE, font)
        draw_centered_text("M 키: 메뉴로 돌아가기", config.HEIGHT//2 + 10, config.WHITE, font)
        
        pygame.display.flip()
    
    elif game_state == "game_clear":
        screen.fill(config.BACKGROUND_COLOR)
        draw_clouds()  # 구름 그리기
        pygame.draw.rect(screen, config.GROUND_COLOR, (0, config.HEIGHT-50, config.WIDTH, 50))
        all_sprites.draw(screen)
        
        # 플레이어와 함께 puppy 표시
        player.draw_puppy(screen)
        
        # 반투명 오버레이
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        if current_stage >= config.MAX_STAGE:
            draw_centered_text("게임 클리어!", config.HEIGHT//2 - 60, config.BLUE, font_large)
            draw_centered_text("모든 스테이지 완주!", config.HEIGHT//2 - 20, config.GREEN, font)
        else:
            draw_centered_text("스테이지 클리어!", config.HEIGHT//2 - 60, config.BLUE, font_large)
            draw_centered_text(f"스테이지 {current_stage} 완주!", config.HEIGHT//2 - 20, config.GREEN, font)
        draw_centered_text("R 키: 재시작", config.HEIGHT//2 + 20, config.WHITE, font)
        draw_centered_text("M 키: 메뉴로 돌아가기", config.HEIGHT//2 + 50, config.WHITE, font)
        
        pygame.display.flip()

pygame.quit()
