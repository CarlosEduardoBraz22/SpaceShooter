import pygame, random, sys, time

pygame.init()
win = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
pygame.display.set_caption("🚀 Space Shooter 80s")
try:
    pygame.display.toggle_fullscreen()  # Mantém atalhos do SO
except Exception:
    pass
WIDTH, HEIGHT = win.get_size()
clock = pygame.time.Clock()
FPS = 60

# --- VISUAIS ---

# Nave jogador: forma estilo nave clássica (corpo + cockpit + asas)
player_img = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.rect(player_img, (0, 255, 255), (15, 15, 20, 30))
pygame.draw.circle(player_img, (100, 200, 255), (25, 20), 8)
pygame.draw.polygon(player_img, (0, 200, 200), [(15, 15), (5, 35), (15, 35)])
pygame.draw.polygon(player_img, (0, 200, 200), [(35, 15), (45, 35), (35, 35)])

# Nave inimiga: nave clássica pixelada (polígonos)
def create_enemy_ship():
    surf = pygame.Surface((48, 40), pygame.SRCALPHA)
    # Corpo central
    pygame.draw.polygon(surf, (255, 0, 0), [(24, 5), (8, 35), (40, 35)])
    # Cockpit
    pygame.draw.polygon(surf, (255, 255, 255), [(24, 10), (18, 28), (30, 28)])
    # Asas
    pygame.draw.polygon(surf, (200, 0, 0), [(8, 35), (0, 39), (8, 39)])
    pygame.draw.polygon(surf, (200, 0, 0), [(40, 35), (48, 39), (40, 39)])
    # Detalhe central
    pygame.draw.rect(surf, (255, 255, 0), (22, 20, 4, 10))
    return surf

enemy_img = create_enemy_ship()

# Chefão: retângulos roxo, branco e vermelho
boss_img = pygame.Surface((100, 100), pygame.SRCALPHA)
pygame.draw.rect(boss_img, (128, 0, 128), (10, 30, 80, 40))
pygame.draw.rect(boss_img, (255, 255, 255), (20, 20, 60, 20))
pygame.draw.rect(boss_img, (255, 0, 0), (40, 10, 20, 10))

# Tiros jogador: azul
bullet_img = pygame.Surface((5, 15), pygame.SRCALPHA)
bullet_img.fill((0, 100, 255))

# Tiros inimigos: vermelho
enemy_bullet_img = pygame.Surface((5, 15), pygame.SRCALPHA)
enemy_bullet_img.fill((255, 0, 0))

# Power-ups com “bolha” de destaque
def create_powerup_bubble(kind):
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(surf, (150, 150, 255, 120), (15, 15), 15)
    pygame.draw.circle(surf, (50, 50, 255, 180), (15, 15), 13)
    if kind == "fast":
        pygame.draw.polygon(surf, (0, 255, 255), [(15, 4), (20, 15), (16, 15), (25, 26), (21, 16), (24, 16)])
    elif kind == "double":
        pygame.draw.rect(surf, (255, 0, 255), (14, 5, 2, 20))
        pygame.draw.rect(surf, (255, 0, 255), (5, 14, 20, 2))
    return surf

power_imgs = {
    "fast": create_powerup_bubble("fast"),
    "double": create_powerup_bubble("double")
}

font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 48)
biggest_font = pygame.font.SysFont("arial", 60, bold=True)
WHITE = (255, 255, 255)
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]

# --- CLASSES ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.speed = 5
        self.last_shot = 0
        self.shot_delay = 300
        self.lives = 3
        self.double_shot = False
        self.powerup_end_time = 0
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if time.time() > self.powerup_end_time:
            self.shot_delay = 300
            self.double_shot = False
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_delay:
            if self.double_shot:
                for offset in [-10, 10]:
                    bullet = Bullet(self.rect.centerx + offset, self.rect.top)
                    bullets.add(bullet)
                    all_sprites.add(bullet)
            else:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                bullets.add(bullet)
                all_sprites.add(bullet)
            self.last_shot = now

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(topleft=(x, y))
    def update(self):
        if random.random() < 0.005:
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            enemy_bullets.add(bullet)
            all_sprites.add(bullet)

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = boss_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, -100))
        self.health = 50
        self.speed = 2
        self.direction = 1
        self.last_shot = pygame.time.get_ticks()
    def update(self):
        if self.rect.top < 50:
            self.rect.y += self.speed
        else:
            self.rect.x += self.direction * self.speed
            if self.rect.left < 0 or self.rect.right > WIDTH:
                self.direction *= -1
        now = pygame.time.get_ticks()
        if now - self.last_shot > 800:
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            enemy_bullets.add(bullet)
            all_sprites.add(bullet)
            self.last_shot = now
    def draw_health(self):
        pygame.draw.rect(win, (255, 0, 0), (self.rect.x, self.rect.y - 10, self.rect.width, 5))
        pygame.draw.rect(win, (0, 255, 0), (self.rect.x, self.rect.y - 10, self.rect.width * (self.health / 50), 5))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
    def update(self):
        self.rect.y -= 10
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_bullet_img
        self.rect = self.image.get_rect(center=(x, y))
    def update(self):
        self.rect.y += 5
        if self.rect.top > HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, kind):
        super().__init__()
        self.kind = kind
        self.image = power_imgs[kind]
        self.rect = self.image.get_rect(center=(random.randint(20, WIDTH - 20), -20))
    def update(self):
        self.rect.y += 3
        if self.rect.top > HEIGHT:
            self.kill()

# --- FUNÇÕES DE DISPLAY ---
def draw_stars():
    for x, y in stars:
        if random.random() < 0.02:
            pygame.draw.circle(win, WHITE, (x, y), random.randint(1, 2))

def show_text(text, y, size=48, colors=None):
    if not colors:
        colors = [WHITE]
    font_show = pygame.font.SysFont("arial", size, bold=True)
    for i, color in enumerate(colors):
        surf = font_show.render(text, True, color)
        rect = surf.get_rect(center=(WIDTH // 2 + i*2, y + i*2))
        win.blit(surf, rect)

def show_start():
    while True:
        win.fill((0, 0, 0))
        draw_stars()
        show_text("SPACE SHOOTER 80s", HEIGHT // 3, 60, colors=[(255,0,255), (0,255,255), (255,255,0), WHITE])
        if pygame.time.get_ticks() % 1000 < 500:
            show_text("Press SPACE", HEIGHT // 2, 30, colors=[(0,255,255)])
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                return
        clock.tick(60)

def show_game_over():
    while True:
        win.fill((0, 0, 0))
        draw_stars()
        show_text("GAME OVER", HEIGHT // 3, 60, colors=[(255, 0, 0), (255, 255, 255)])
        show_text("Press SPACE to Restart", HEIGHT // 2, 30, colors=[(255, 255, 255)])
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                return

# --- LOOP PRINCIPAL ---
while True:
    show_start()
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    # Centralizar inimigos
    n_cols = 8
    n_rows = 3
    enemy_w = enemy_img.get_width()
    total_w = n_cols * enemy_w + (n_cols - 1) * 22
    start_x = (WIDTH - total_w) // 2
    for row in range(n_rows):
        for col in range(n_cols):
            x = start_x + col * (enemy_w + 22)
            y = 50 + row * 60
            e = Enemy(x, y)
            all_sprites.add(e)
            enemies.add(e)
    score = 0
    boss_spawned = False
    power_timer = pygame.time.get_ticks()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                player.shoot()
        now = pygame.time.get_ticks()
        if now - power_timer > 10000:
            kind = random.choice(["fast", "double"])
            pu = PowerUp(kind)
            all_sprites.add(pu)
            powerups.add(pu)
            power_timer = now
        all_sprites.update()
        for hit in pygame.sprite.groupcollide(enemies, bullets, True, True):
            score += 10
        for hit in pygame.sprite.spritecollide(player, powerups, True):
            if hit.kind == "fast":
                player.shot_delay = 100
            elif hit.kind == "double":
                player.double_shot = True
            player.powerup_end_time = time.time() + 5
        if not enemies and not boss_spawned:
            boss = Boss()
            all_sprites.add(boss)
            boss_group.add(boss)
            boss_spawned = True
        if boss_spawned:
            if pygame.sprite.spritecollide(boss, bullets, True):
                boss.health -= 1
                if boss.health <= 0:
                    boss.kill()
                    score += 100
                    running = False
        if pygame.sprite.spritecollide(player, enemies, True) or pygame.sprite.spritecollide(player, enemy_bullets, True):
            player.lives -= 1
            if player.lives <= 0:
                running = False
        win.fill((0, 0, 20))
        draw_stars()
        all_sprites.draw(win)
        if boss_spawned and boss.alive():
            boss.draw_health()
        win.blit(font.render(f"Pontos: {score}", True, WHITE), (10, 10))
        win.blit(font.render(f"Vidas: {player.lives}", True, WHITE), (WIDTH - 140, 10))
        pygame.display.flip()
        clock.tick(FPS)
    show_game_over()
