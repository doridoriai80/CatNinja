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
    font_small = pygame.font.SysFont("AppleGothic", 18)
except:
    try:
        # Windows에서 기본 한글 폰트 사용
        font = pygame.font.SysFont("malgun gothic", 24)
        font_large = pygame.font.SysFont("malgun gothic", 36)
        font_small = pygame.font.SysFont("malgun gothic", 18)
    except:
        # 폴백 폰트
        font = pygame.font.SysFont("arial", 24)
        font_large = pygame.font.SysFont("arial", 36)
        font_small = pygame.font.SysFont("arial", 18)

# --- 클래스들 ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 이미지 로드
        try:
            self.original_image = pygame.image.load("assets/player.png").convert_alpha()
            # 이미지 크기 조정
            self.image = pygame.transform.scale(self.original_image, (config.PLAYER_WIDTH, config.PLAYER_HEIGHT))
        except:
            # 이미지 로드 실패 시 기본 사각형 사용
            self.image = pygame.Surface((config.PLAYER_WIDTH, config.PLAYER_HEIGHT))
            self.image.fill((200, 150, 100))
        
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (50, config.HEIGHT - 50)
        self.vel_y = 0
        self.speed = config.PLAYER_SPEED
        self.on_ground = True
        self.alive = True
        self.shuriken_double = False
        self.double_end_time = 0

    def update(self, keys):
        if not self.alive:
            return
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            if self.rect.left < 0:
                self.rect.left = 0
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            if self.rect.right > config.WIDTH:
                self.rect.right = config.WIDTH

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = config.PLAYER_JUMP_VELOCITY
            self.on_ground = False

        self.vel_y += config.GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom >= config.HEIGHT - 50:
            self.rect.bottom = config.HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True

        if self.shuriken_double and pygame.time.get_ticks() > self.double_end_time:
            self.shuriken_double = False

    def eat_snack(self):
        self.shuriken_double = True
        self.double_end_time = pygame.time.get_ticks() + config.SNACK_DURATION


class Shuriken(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((config.SHURIKEN_WIDTH, config.SHURIKEN_HEIGHT))
        self.image.fill(config.BLACK)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = config.SHURIKEN_SPEED

    def update(self, keys=None):
        self.rect.x += self.speed
        if self.rect.left > config.WIDTH:
            self.kill()

class EnemyCat(pygame.sprite.Sprite):
    def __init__(self, x, y, color_name, stage=1):
        super().__init__()
        self.color_name = color_name
        self.color = self.get_color(color_name)
        self.hp = self.get_hp(color_name, stage)
        
    def get_color(self, color_name):
        """색상 이름에 따른 색상 반환"""
        colors = {
            "yellow": config.YELLOW,
            "black": config.BLACK,
            "white": config.WHITE,
        }
        return colors.get(color_name, config.WHITE)
    
    def get_hp(self, color_name, stage):
        """스테이지에 따른 HP 계산 (2배씩 증가)"""
        base_hp = config.BASE_CAT_HP[color_name]
        return base_hp * (2 ** (stage - 1))
    
    def __init__(self, x, y, color_name, stage=1):
        super().__init__()
        self.color_name = color_name
        self.color = self.get_color(color_name)
        self.hp = self.get_hp(color_name, stage)
        self.width, self.height = config.ENEMY_CAT_SIZE[color_name]
        
        # 고양이 이미지 로드 및 좌우 반전
        try:
            image_path = f"assets/cat_{color_name}.png"
            self.original_image = pygame.image.load(image_path).convert_alpha()
            # 이미지 크기 조정
            self.original_image = pygame.transform.scale(self.original_image, (self.width, self.height))
            # 좌우 반전 (왼쪽으로 이동하므로 반전 필요)
            self.image = pygame.transform.flip(self.original_image, True, False)
        except:
            # 이미지 로드 실패 시 기존 색상 사각형 사용
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(self.color)
        
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = config.ENEMY_CAT_SPEED[color_name]

    def update(self, keys=None):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class BossCat(pygame.sprite.Sprite):
    def __init__(self, x, y, stage=1):
        super().__init__()
        self.width = config.BOSS_CAT_WIDTH
        self.height = config.BOSS_CAT_HEIGHT
        
        # 보스 고양이 이미지 로드 및 좌우 반전
        try:
            self.original_image = pygame.image.load("assets/cat_boss.png").convert_alpha()
            # 이미지 크기 조정
            self.original_image = pygame.transform.scale(self.original_image, (self.width, self.height))
            # 좌우 반전 (왼쪽으로 이동하므로 반전 필요)
            self.image = pygame.transform.flip(self.original_image, True, False)
        except:
            # 이미지 로드 실패 시 기존 색상 사각형 사용
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((150, 0, 150))
        
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.hp = self.get_hp(stage)
        self.stone_cooldown = config.BOSS_STONE_COOLDOWN
        self.last_stone_time = pygame.time.get_ticks()
        
    def get_hp(self, stage):
        """스테이지에 따른 HP 계산 (2배씩 증가)"""
        return config.BASE_BOSS_HP * (2 ** (stage - 1))

    def update(self, keys=None):
        now = pygame.time.get_ticks()
        if now - self.last_stone_time > self.stone_cooldown:
            self.last_stone_time = now
            # 앞쪽(왼쪽)으로 돌 던지기
            stone = Stone(self.rect.centerx, self.rect.bottom)
            stones.add(stone)
            all_sprites.add(stone)

class Snack(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = config.SNACK_SIZE
        
        # 간식 이미지 로드
        try:
            self.original_image = pygame.image.load("assets/snack.png").convert_alpha()
            # 이미지 크기 조정
            self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        except:
            # 이미지 로드 실패 시 기존 색상 사각형 사용
            self.image = pygame.Surface((self.size, self.size))
            self.image.fill(config.GREEN)
        
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, keys=None):
        self.rect.x -= 3
        if self.rect.right < 0:
            self.kill()

class Stone(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.radius = config.STONE_RADIUS
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, config.GRAY, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))
        
        # 왼쪽으로만 던지기 (랜덤 속도)
        random_speed = random.randint(config.STONE_SPEED_MIN, config.STONE_SPEED_MAX)
        self.vel_x = -random_speed  # 왼쪽으로 이동 (랜덤 속도)
        self.vel_y = 0  # 수평으로만 발사 (위아래 움직임 없음)
        
        self.gravity = config.STONE_GRAVITY

    def update(self, keys=None):
        self.vel_y += self.gravity
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.rect.top > config.HEIGHT or self.rect.left < 0 or self.rect.right > config.WIDTH:
            self.kill()


# --- 그룹 ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
shurikens = pygame.sprite.Group()
items = pygame.sprite.Group()
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
    draw_centered_text("개 닌자 횡스크롤", 100, config.BLUE, font_large)
    
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
    global game_over, game_clear, spawn_timer, snack_spawn_timer, boss_spawned, cats_spawned, total_cats, current_stage
    game_over = False
    game_clear = False
    current_stage = 1  # 스테이지 1부터 시작
    player.alive = True
    player.rect.bottomleft = (50, config.HEIGHT - 50)
    player.shuriken_double = False
    player.double_end_time = 0
    for group in [enemies, shurikens, items, stones]:
        group.empty()
    all_sprites.empty()
    all_sprites.add(player)
    spawn_timer = 0
    snack_spawn_timer = 0
    boss_spawned = False
    cats_spawned = 0
    total_cats = config.TOTAL_CATS_TO_SPAWN  # config에서 설정된 고양이 수만큼 생성
    reset_game.snack_spawned = False  # 간식 스폰 플래그 초기화


# 게임 상태 변수
game_state = "menu"  # "menu", "playing", "game_over", "game_clear"
current_stage = 1  # 현재 스테이지
cats_spawned = 0
total_cats = config.TOTAL_CATS_TO_SPAWN

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
                    game_state = "playing"
                    reset_game()
                elif event.key == pygame.K_m:
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

        # 간식 스폰 로직 (한 번만)
        if not hasattr(reset_game, 'snack_spawned') or not reset_game.snack_spawned:
            snack_spawn_timer += dt
            if snack_spawn_timer > config.SNACK_SPAWN_INTERVAL:
                snack_spawn_timer = 0
                snack = Snack(config.WIDTH + 30, config.HEIGHT - 80)
                items.add(snack)
                all_sprites.add(snack)
                reset_game.snack_spawned = True

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
                            # 다음 스테이지 준비
                            cats_spawned = 0
                            boss_spawned = False
                            spawn_timer = 0
                            snack_spawn_timer = 0
                            reset_game.snack_spawned = False
                            # 모든 스프라이트 제거 (플레이어 제외)
                            for group in [enemies, shurikens, items, stones]:
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
        player_touch_rect = get_touch_rect(player, config.PLAYER_TOUCH_MARGIN)
        enemy_touched = False
        for enemy in enemies:
            if player_touch_rect.colliderect(get_touch_rect(enemy, 0)):
                enemy_touched = True
                break
        if enemy_touched:
            player.alive = False
            game_state = "game_over"

        # 돌 충돌도 동일하게
        stone_touched = False
        for stone in stones:
            if player_touch_rect.colliderect(get_touch_rect(stone, 0)):
                stone_touched = True
                break
        if stone_touched:
            player.alive = False
            game_state = "game_over"

        if len(items) > 0:
            hit_snack = pygame.sprite.spritecollide(player, items, True)
        else:
            hit_snack = []
        if hit_snack:
            player.eat_snack()

        # 게임 화면 그리기
        screen.fill(config.BACKGROUND_COLOR)
        draw_background_elements() # 배경 요소 그리기
        draw_clouds()  # 구름 그리기
        pygame.draw.rect(screen, config.GROUND_COLOR, (0, config.HEIGHT-50, config.WIDTH, 50))
        all_sprites.draw(screen)

        # UI 정보 표시
        # 현재 스테이지 표시
        draw_text(f"스테이지 {current_stage}", 10, 10, config.WHITE, font_large)
        
        if player.shuriken_double:
            time_left = (player.double_end_time - pygame.time.get_ticks()) // 1000
            draw_text(f"간식 효과: {time_left}초", 10, 70, config.GREEN)
        
        # 남은 고양이 수 표시
        if not boss_spawned:
            remaining_cats = total_cats - cats_spawned + len([e for e in enemies if not isinstance(e, BossCat)])
            draw_text(f"남은 고양이: {remaining_cats}마리", 10, 50, config.WHITE)
        else:
            # 보스 체력 표시
            boss = None
            for enemy in enemies:
                if isinstance(enemy, BossCat):
                    boss = enemy
                    break
            
            if boss:
                draw_text("보스 고양이 출현!", 10, 40, config.RED, font_large)
                # 보스 체력 바 표시
                health_bar_width = 200
                health_bar_height = 20
                health_ratio = boss.hp / (config.BASE_BOSS_HP * (2 ** (current_stage - 1)))
                health_bar_x = 10
                health_bar_y = 80
                
                # 배경 체력 바
                pygame.draw.rect(screen, (100, 100, 100), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
                # 현재 체력 바
                current_health_width = int(health_bar_width * health_ratio)
                health_color = (255, 0, 0) if health_ratio > 0.5 else (255, 255, 0) if health_ratio > 0.2 else (255, 0, 0)
                pygame.draw.rect(screen, health_color, (health_bar_x, health_bar_y, current_health_width, health_bar_height))
                # 체력 바 테두리
                pygame.draw.rect(screen, config.WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
                
                # 체력 수치 표시
                max_boss_hp = config.BASE_BOSS_HP * (2 ** (current_stage - 1))
                draw_text(f"보스 체력: {boss.hp}/{max_boss_hp}", 10, 110, config.WHITE)

        pygame.display.flip()
    
    elif game_state == "game_over":
        screen.fill(config.BACKGROUND_COLOR)
        draw_clouds()  # 구름 그리기
        pygame.draw.rect(screen, config.GROUND_COLOR, (0, config.HEIGHT-50, config.WIDTH, 50))
        all_sprites.draw(screen)
        
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
