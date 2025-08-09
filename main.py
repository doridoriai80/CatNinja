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
    COLOR_HP = {
        "yellow": (config.YELLOW, config.ENEMY_CAT_HP["yellow"]),
        "black": (config.BLACK, config.ENEMY_CAT_HP["black"]),
        "white": (config.WHITE, config.ENEMY_CAT_HP["white"]),
    }
    def __init__(self, x, y, color_name):
        super().__init__()
        self.color_name = color_name
        self.color, self.hp = EnemyCat.COLOR_HP[color_name]
        self.width = config.ENEMY_CAT_WIDTH
        self.height = config.ENEMY_CAT_HEIGHT
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = config.ENEMY_CAT_SPEED

    def update(self, keys=None):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class BossCat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = config.BOSS_CAT_WIDTH
        self.height = config.BOSS_CAT_HEIGHT
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((150, 0, 150))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.hp = config.BOSS_CAT_HP
        self.stone_cooldown = config.BOSS_STONE_COOLDOWN
        self.last_stone_time = pygame.time.get_ticks()

    def update(self, keys=None):
        now = pygame.time.get_ticks()
        if now - self.last_stone_time > self.stone_cooldown:
            self.last_stone_time = now
            stone = Stone(self.rect.centerx, self.rect.bottom)
            stones.add(stone)
            all_sprites.add(stone)

class Snack(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = config.SNACK_SIZE
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
        self.vel_x = config.STONE_VEL_X
        self.vel_y = config.STONE_VEL_Y
        self.gravity = config.STONE_GRAVITY

    def update(self, keys=None):
        self.vel_y += self.gravity
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.rect.top > config.HEIGHT:
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

def draw_text(text, x, y, color=config.WHITE, font_type=font):
    img = font_type.render(text, True, color)
    screen.blit(img, (x, y))

def draw_centered_text(text, y, color=config.WHITE, font_type=font):
    img = font_type.render(text, True, color)
    x = (config.WIDTH - img.get_width()) // 2
    screen.blit(img, (x, y))

def draw_menu():
    screen.fill(config.BACKGROUND_COLOR)
    pygame.draw.rect(screen, config.GROUND_COLOR, (0, config.HEIGHT-50, config.WIDTH, 50))
    
    # 게임 제목
    draw_centered_text("강아지 닌자 횡스크롤", 100, config.BLUE, font_large)
    
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
    global game_over, game_clear, spawn_timer, snack_spawn_timer, boss_spawned, cats_spawned, total_cats
    game_over = False
    game_clear = False
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
    total_cats = 20  # 총 20마리의 고양이 생성


# 게임 상태 변수
game_state = "menu"  # "menu", "playing", "game_over", "game_clear"
cats_spawned = 0
total_cats = 20

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
                cat = EnemyCat(config.WIDTH + 50, config.HEIGHT - 50, cat_type)
                enemies.add(cat)
                all_sprites.add(cat)
                cats_spawned += 1

        # 간식 스폰 로직
        snack_spawn_timer += dt
        if snack_spawn_timer > config.SNACK_SPAWN_INTERVAL:
            snack_spawn_timer = 0
            snack = Snack(config.WIDTH + 30, config.HEIGHT - 80)
            items.add(snack)
            all_sprites.add(snack)

        # 모든 고양이를 처치했을 때 보스 스폰
        if cats_spawned >= total_cats and not boss_spawned and len(enemies) == 0:
            boss = BossCat(config.WIDTH - 150, config.HEIGHT - 50)
            enemies.add(boss)
            all_sprites.add(boss)
            boss_spawned = True

        for shuriken in shurikens:
            hit_cats = pygame.sprite.spritecollide(shuriken, enemies, False)
            for cat in hit_cats:
                if isinstance(cat, BossCat):
                    cat.hp -= 1
                    if cat.hp <= 0:
                        cat.kill()
                        game_state = "game_clear"
                    shuriken.kill()
                else:
                    cat.hp -= 1
                    if cat.hp <= 0:
                        cat.kill()
                    shuriken.kill()

        if pygame.sprite.spritecollide(player, enemies, False):
            player.alive = False
            game_state = "game_over"

        hit_snack = pygame.sprite.spritecollide(player, items, True)
        if hit_snack:
            player.eat_snack()

        if pygame.sprite.spritecollide(player, stones, False):
            player.alive = False
            game_state = "game_over"

        # 게임 화면 그리기
        screen.fill(config.BACKGROUND_COLOR)
        pygame.draw.rect(screen, config.GROUND_COLOR, (0, config.HEIGHT-50, config.WIDTH, 50))
        all_sprites.draw(screen)

        # UI 정보 표시
        if player.shuriken_double:
            time_left = (player.double_end_time - pygame.time.get_ticks()) // 1000
            draw_text(f"간식 효과: {time_left}초", 10, 10, config.GREEN)
        
        # 남은 고양이 수 표시
        if not boss_spawned:
            remaining_cats = total_cats - cats_spawned + len([e for e in enemies if not isinstance(e, BossCat)])
            draw_text(f"남은 고양이: {remaining_cats}마리", 10, 40, config.WHITE)
        else:
            draw_text("보스 고양이 출현!", 10, 40, config.RED, font_large)

        pygame.display.flip()
    
    elif game_state == "game_over":
        screen.fill(config.BACKGROUND_COLOR)
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
        pygame.draw.rect(screen, config.GROUND_COLOR, (0, config.HEIGHT-50, config.WIDTH, 50))
        all_sprites.draw(screen)
        
        # 반투명 오버레이
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        draw_centered_text("게임 클리어!", config.HEIGHT//2 - 60, config.BLUE, font_large)
        draw_centered_text("축하합니다!", config.HEIGHT//2 - 20, config.GREEN, font)
        draw_centered_text("R 키: 재시작", config.HEIGHT//2 + 20, config.WHITE, font)
        draw_centered_text("M 키: 메뉴로 돌아가기", config.HEIGHT//2 + 50, config.WHITE, font)
        
        pygame.display.flip()

pygame.quit()
