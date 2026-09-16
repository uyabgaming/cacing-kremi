import pygame
import sys
import random
import math
import array

# Inisialisasi Pygame & Audio
pygame.init()
pygame.font.init()

try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    HAS_AUDIO = True
except Exception:
    HAS_AUDIO = False

# ---------------------------------------------------------
# FUNGSIONALITAS GENERATOR EFEK SUARA
# ---------------------------------------------------------
def play_sound(sound_type):
    if not HAS_AUDIO:
        return
    
    sample_rate = 44100
    samples = array.array('h')
    
    if sound_type == "eat":
        duration = 0.08
        freq = 880.0
        n_samples = int(sample_rate * duration)
        for i in range(n_samples):
            t = i / sample_rate
            value = int(16000 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))
            samples.append(value)
            
    elif sound_type == "star":
        duration = 0.15
        n_samples = int(sample_rate * duration)
        for i in range(n_samples):
            t = i / sample_rate
            freq = 600.0 + (t / duration) * 600.0
            value = int(18000 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))
            samples.append(value)
            
    elif sound_type == "bomb":
        duration = 0.25
        n_samples = int(sample_rate * duration)
        for i in range(n_samples):
            t = i / sample_rate
            noise = random.uniform(-1, 1)
            value = int(22000 * noise * (1 - t / duration))
            samples.append(value)
            
    elif sound_type == "click":
        duration = 0.03
        n_samples = int(sample_rate * duration)
        for i in range(n_samples):
            t = i / sample_rate
            value = int(10000 * math.sin(2 * math.pi * 400.0 * t))
            samples.append(value)

    try:
        snd = pygame.mixer.Sound(buffer=samples)
        snd.set_volume(0.3)
        snd.play()
    except Exception:
        pass

# ---------------------------------------------------------
# KONFIGURASI GAME & LAYAR
# ---------------------------------------------------------
WIDTH = 512
HEIGHT = 512
CONTROL_PANEL_HEIGHT = 160
SCREEN_HEIGHT = HEIGHT + CONTROL_PANEL_HEIGHT

FPS = 60

COLOR_PANEL_BG = (44, 62, 80)

COLOR_SNAKE_HEAD = (88, 214, 141)
COLOR_SNAKE_BODY = (46, 139, 87)
COLOR_BLUSH = (255, 140, 157)
COLOR_TONGUE = (255, 99, 71)

COLOR_APPLE = (255, 107, 107)
COLOR_LEAF = (78, 205, 196)
COLOR_STAR = (255, 215, 0)

COLOR_BOMB = (45, 52, 54)
COLOR_BOMB_GLOW = (231, 76, 60)
COLOR_FUSE = (225, 112, 85)

COLOR_TEXT = (44, 62, 80)
COLOR_TEXT_WHITE = (255, 255, 255)

COLOR_BTN = (52, 152, 219)
COLOR_BTN_HOVER = (41, 128, 185)
COLOR_BTN_PRESS = (21, 67, 96)

screen = pygame.display.set_mode((WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cacing Kremi 🪱✨")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("Comic Sans MS", 15, bold=True)
font_ui = pygame.font.SysFont("Comic Sans MS", 22, bold=True)
font_title = pygame.font.SysFont("Comic Sans MS", 40, bold=True)

game_state = "HOME"
high_score = 0

# ---------------------------------------------------------
# KELAS TOMBOL
# ---------------------------------------------------------
class Button:
    def __init__(self, x, y, width, height, text, target_angle=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.target_angle = target_angle
        self.is_pressed = False

    def draw(self, surface, mouse_pos):
        color = COLOR_BTN
        offset_y = 0
        
        if self.rect.collidepoint(mouse_pos):
            if self.is_pressed:
                color = COLOR_BTN_PRESS
                offset_y = 2
            else:
                color = COLOR_BTN_HOVER
        
        shadow_rect = pygame.Rect(self.rect.x, self.rect.y + 4, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, (20, 30, 40), shadow_rect, border_radius=12)
        
        btn_draw_rect = pygame.Rect(self.rect.x, self.rect.y + offset_y, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, color, btn_draw_rect, border_radius=12)
        
        txt_surf = font_ui.render(self.text, True, COLOR_TEXT_WHITE)
        surface.blit(txt_surf, (btn_draw_rect.centerx - txt_surf.get_width() // 2, btn_draw_rect.centery - txt_surf.get_height() // 2))

# ---------------------------------------------------------
# KELAS PARTIKEL
# ---------------------------------------------------------
class Particle:
    def __init__(self, x, y, is_explosion=False, is_star=False):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(3.0, 8.0) if is_explosion else random.uniform(2.0, 6.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = random.uniform(3, 8)
        
        if is_explosion:
            self.color = random.choice([(255, 71, 87), (255, 165, 2), (255, 242, 0), (87, 101, 116)])
            self.lifetime = random.randint(30, 50)
        elif is_star:
            self.color = random.choice([(255, 242, 0), (255, 215, 0), (255, 255, 255)])
            self.lifetime = random.randint(25, 40)
        else:
            self.color = random.choice([(255, 230, 109), (255, 107, 107), (78, 205, 196), (255, 159, 243)])
            self.lifetime = random.randint(20, 35)
            
        self.max_life = self.lifetime

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.vy += 0.1
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_life))
            r = max(1, int(self.radius * (self.lifetime / self.max_life)))
            p_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*self.color, alpha), (r + 1, r + 1), r)
            surface.blit(p_surf, (self.x - r - 1, self.y - r - 1))

# ---------------------------------------------------------
# KELAS BOMB & BINTANG
# ---------------------------------------------------------
class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12

    def draw(self, surface, time_counter):
        glow = math.sin(time_counter * 0.2) > 0
        pygame.draw.arc(surface, COLOR_FUSE, (self.x - 4, self.y - 18, 12, 12), 0, math.pi / 2, 2)
        spark_color = (255, 242, 0) if glow else (255, 71, 87)
        pygame.draw.circle(surface, spark_color, (int(self.x + 8), int(self.y - 14)), 3)
        pygame.draw.circle(surface, COLOR_BOMB, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (120, 120, 120), (int(self.x - 3), int(self.y - 3)), 3)

        if glow:
            pygame.draw.circle(surface, COLOR_BOMB_GLOW, (int(self.x), int(self.y)), self.radius, 2)

class BonusStar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 300

    def draw(self, surface, time_counter):
        if self.timer <= 0:
            return
        if self.timer < 90 and (self.timer // 10) % 2 == 0:
            return

        scale = 1.0 + math.sin(time_counter * 0.2) * 0.15
        r = int(12 * scale)
        points = []
        for i in range(5):
            angle_outer = i * math.pi * 2 / 5 - math.pi / 2
            angle_inner = angle_outer + math.pi / 5
            points.append((self.x + math.cos(angle_outer) * r, self.y + math.sin(angle_outer) * r))
            points.append((self.x + math.cos(angle_inner) * (r * 0.5), self.y + math.sin(angle_inner) * (r * 0.5)))
            
        pygame.draw.polygon(surface, COLOR_STAR, points)
        pygame.draw.polygon(surface, (255, 255, 255), points, 1)

# ---------------------------------------------------------
# KELAS GAME ULAR / CACING
# ---------------------------------------------------------
class SnakeGameSmooth:
    def __init__(self):
        self.btn_start = Button(WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 50, "MULAI MAIN")
        
        btn_size = 46
        cx = WIDTH // 2
        cy = HEIGHT + (CONTROL_PANEL_HEIGHT // 2)

        self.btn_up = Button(cx - btn_size // 2, cy - btn_size - 4, btn_size, btn_size, "▲", target_angle=-math.pi / 2)
        self.btn_down = Button(cx - btn_size // 2, cy + 4, btn_size, btn_size, "▼", target_angle=math.pi / 2)
        self.btn_left = Button(cx - btn_size - btn_size // 2 - 4, cy - btn_size // 2, btn_size, btn_size, "◄", target_angle=math.pi)
        self.btn_right = Button(cx + btn_size // 2 + 4, cy - btn_size // 2, btn_size, btn_size, "►", target_angle=0.0)

        self.dpad_buttons = [self.btn_up, self.btn_down, self.btn_left, self.btn_right]
        self.shake_amount = 0
        self.reset()

    def reset(self):
        self.head_x = WIDTH / 2
        self.head_y = HEIGHT / 2 + 50
        self.current_angle = 0.0
        self.target_angle = 0.0
        self.speed = 3.2
        self.turn_speed = 0.12

        self.segment_distance = 14
        self.body_radius = 14
        self.body = []

        for i in range(12):
            self.body.append([self.head_x - i * self.segment_distance, self.head_y])

        self.score = 0
        self.particles = []
        self.bombs = []
        self.bonus_star = None
        self.time_counter = 0
        self.shake_amount = 0
        self.spawn_food()
        self.update_bombs()

    def spawn_food(self):
        margin = 40
        while True:
            fx = random.randint(margin, WIDTH - margin)
            fy = random.randint(margin, HEIGHT - margin)
            
            too_close = False
            for bomb in self.bombs:
                if math.hypot(fx - bomb.x, fy - bomb.y) < 40:
                    too_close = True
                    break
            if not too_close:
                self.food_x = fx
                self.food_y = fy
                break

    def spawn_bonus_star(self):
        if self.bonus_star is None and random.random() < 0.35:
            margin = 50
            bx = random.randint(margin, WIDTH - margin)
            by = random.randint(margin, HEIGHT - margin)
            self.bonus_star = BonusStar(bx, by)

    def update_bombs(self):
        target_bomb_count = min(1 + self.score // 30, 6)
        
        while len(self.bombs) < target_bomb_count:
            margin = 50
            bx = random.randint(margin, WIDTH - margin)
            by = random.randint(margin, HEIGHT - margin)
            
            if math.hypot(bx - self.head_x, by - self.head_y) > 100 and \
               math.hypot(bx - self.food_x, by - self.food_y) > 50:
                self.bombs.append(Bomb(bx, by))

    def set_target_angle(self, angle):
        diff = (angle - self.current_angle + math.pi) % (math.pi * 2) - math.pi
        self.target_angle = self.current_angle + diff

    def handle_input(self):
        global game_state, high_score
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "HOME":
                    if self.btn_start.rect.collidepoint(mouse_pos):
                        self.btn_start.is_pressed = True
                        play_sound("click")

                elif game_state == "PLAYING":
                    for btn in self.dpad_buttons:
                        if btn.rect.collidepoint(mouse_pos):
                            btn.is_pressed = True
                            self.set_target_angle(btn.target_angle)
                            play_sound("click")

                elif game_state == "GAMEOVER":
                    self.reset()
                    game_state = "PLAYING"
                    play_sound("click")

            elif event.type == pygame.MOUSEBUTTONUP:
                if game_state == "HOME":
                    if self.btn_start.is_pressed and self.btn_start.rect.collidepoint(mouse_pos):
                        self.reset()
                        game_state = "PLAYING"
                        play_sound("click")
                    self.btn_start.is_pressed = False

                elif game_state == "PLAYING":
                    for btn in self.dpad_buttons:
                        btn.is_pressed = False

            elif event.type == pygame.KEYDOWN:
                if game_state in ("HOME", "GAMEOVER"):
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.reset()
                        game_state = "PLAYING"
                        play_sound("click")

        if game_state == "PLAYING":
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.set_target_angle(-math.pi / 2)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.set_target_angle(math.pi / 2)
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.set_target_angle(math.pi)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.set_target_angle(0.0)

    def trigger_game_over(self):
        global game_state, high_score
        game_state = "GAMEOVER"
        self.shake_amount = 15
        play_sound("bomb")
        if self.score > high_score:
            high_score = self.score

    def update(self):
        self.time_counter += 1

        if self.shake_amount > 0:
            self.shake_amount -= 1

        if game_state != "PLAYING":
            return

        angle_diff = self.target_angle - self.current_angle
        if abs(angle_diff) > 0.01:
            self.current_angle += angle_diff * self.turn_speed

        self.head_x += math.cos(self.current_angle) * self.speed
        self.head_y += math.sin(self.current_angle) * self.speed

        if not (self.body_radius <= self.head_x <= WIDTH - self.body_radius) or \
           not (self.body_radius <= self.head_y <= HEIGHT - self.body_radius):
            self.trigger_game_over()
            return

        self.body[0] = [self.head_x, self.head_y]

        for i in range(1, len(self.body)):
            prev_x, prev_y = self.body[i - 1]
            curr_x, curr_y = self.body[i]

            dx = prev_x - curr_x
            dy = prev_y - curr_y
            dist = math.hypot(dx, dy)

            if dist > 0:
                target_x = prev_x - (dx / dist) * self.segment_distance
                target_y = prev_y - (dy / dist) * self.segment_distance
                self.body[i] = [target_x, target_y]

        for seg in self.body[8:]:
            if math.hypot(self.head_x - seg[0], self.head_y - seg[1]) < self.body_radius:
                self.trigger_game_over()
                return

        for bomb in self.bombs:
            if math.hypot(self.head_x - bomb.x, self.head_y - bomb.y) < self.body_radius + bomb.radius:
                for _ in range(40):
                    self.particles.append(Particle(bomb.x, bomb.y, is_explosion=True))
                self.trigger_game_over()
                return

        dist_to_food = math.hypot(self.head_x - self.food_x, self.head_y - self.food_y)
        if dist_to_food < self.body_radius + 12:
            self.score += 10
            play_sound("eat")
            
            for _ in range(30):
                self.particles.append(Particle(self.food_x, self.food_y))
            
            last_x, last_y = self.body[-1]
            for _ in range(3):
                self.body.append([last_x, last_y])
                
            self.update_bombs()
            self.spawn_food()
            self.spawn_bonus_star()

        if self.bonus_star:
            self.bonus_star.timer -= 1
            if self.bonus_star.timer <= 0:
                self.bonus_star = None
            else:
                dist_to_star = math.hypot(self.head_x - self.bonus_star.x, self.head_y - self.bonus_star.y)
                if dist_to_star < self.body_radius + 12:
                    self.score += 30
                    play_sound("star")
                    for _ in range(30):
                        self.particles.append(Particle(self.bonus_star.x, self.bonus_star.y, is_star=True))
                    self.bonus_star = None

        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

    def draw_board(self, surface):
        grid_size = 32
        COLOR_GRASS_LIGHT = (186, 237, 145)
        COLOR_GRASS_DARK = (171, 224, 130)

        for row in range(HEIGHT // grid_size):
            for col in range(WIDTH // grid_size):
                color = COLOR_GRASS_LIGHT if (row + col) % 2 == 0 else COLOR_GRASS_DARK
                pygame.draw.rect(surface, color, (col * grid_size, row * grid_size, grid_size, grid_size))

    def draw_food(self, surface):
        bounce = math.sin(self.time_counter * 0.12) * 3
        fy = self.food_y + bounce
        radius = 12

        pygame.draw.circle(surface, COLOR_APPLE, (int(self.food_x), int(fy)), radius)
        pygame.draw.circle(surface, (255, 180, 180), (int(self.food_x - 3), int(fy - 3)), 4)
        pygame.draw.ellipse(surface, COLOR_LEAF, (int(self.food_x - 1), int(fy - radius - 3), 7, 5))

    def draw_snake(self, surface):
        num_segments = len(self.body)

        for i in range(num_segments - 1, -1, -1):
            bx, by = self.body[i]
            factor = 1.0 - (i / num_segments) * 0.4
            r = int(self.body_radius * factor)

            if i == 0:
                pygame.draw.circle(surface, COLOR_SNAKE_HEAD, (int(bx), int(by)), self.body_radius + 2)
                
                tongue_len = abs(math.sin(self.time_counter * 0.25)) * 8 + 4
                tx = bx + math.cos(self.current_angle) * (self.body_radius + tongue_len)
                ty = by + math.sin(self.current_angle) * (self.body_radius + tongue_len)
                pygame.draw.line(surface, COLOR_TONGUE, (bx, by), (tx, ty), 3)

                eye_offset_angle = 0.5
                e1_x = bx + math.cos(self.current_angle - eye_offset_angle) * 9
                e1_y = by + math.sin(self.current_angle - eye_offset_angle) * 9
                e2_x = bx + math.cos(self.current_angle + eye_offset_angle) * 9
                e2_y = by + math.sin(self.current_angle + eye_offset_angle) * 9

                pygame.draw.circle(surface, COLOR_BLUSH, (int(e1_x - 2), int(e1_y + 3)), 3)
                pygame.draw.circle(surface, COLOR_BLUSH, (int(e2_x + 2), int(e2_y + 3)), 3)

                pygame.draw.circle(surface, (20, 20, 20), (int(e1_x), int(e1_y)), 4)
                pygame.draw.circle(surface, (20, 20, 20), (int(e2_x), int(e2_y)), 4)
                pygame.draw.circle(surface, (255, 255, 255), (int(e1_x - 1), int(e1_y - 1)), 1.5)
                pygame.draw.circle(surface, (255, 255, 255), (int(e2_x - 1), int(e2_y - 1)), 1.5)
            else:
                pygame.draw.circle(surface, COLOR_SNAKE_BODY, (int(bx), int(by)), max(r, 4))

    def draw_hud(self, surface):
        score_txt = font_ui.render(f"🍎 Skor: {self.score}", True, COLOR_TEXT)
        high_txt = font_ui.render(f"🏆 Terbaik: {high_score}", True, COLOR_TEXT)

        surface.blit(score_txt, (15, 8))
        surface.blit(high_txt, (WIDTH - high_txt.get_width() - 15, 8))

    def draw_home_screen(self, surface):
        self.draw_board(surface)
        self.time_counter += 1
        mouse_pos = pygame.mouse.get_pos()

        bounce = math.sin(self.time_counter * 0.08) * 5
        title_surf = font_title.render("Cacing Kremi 🪱", True, COLOR_TEXT)
        surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 4 + bounce))

        cx, cy = WIDTH // 2, HEIGHT // 2 - 20
        pygame.draw.circle(surface, COLOR_SNAKE_HEAD, (cx, cy), 32)
        pygame.draw.circle(surface, COLOR_BLUSH, (cx - 16, cy + 6), 6)
        pygame.draw.circle(surface, COLOR_BLUSH, (cx + 16, cy + 6), 6)
        pygame.draw.circle(surface, (20, 20, 20), (cx - 10, cy - 6), 5)
        pygame.draw.circle(surface, (20, 20, 20), (cx + 10, cy - 6), 5)

        self.btn_start.draw(surface, mouse_pos)

    def draw_gameover_screen(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        title = font_title.render("Kena Bom / Nabrak! 💥", True, (255, 107, 107))
        score_info = font_ui.render(f"Skor Kamu: {self.score}", True, COLOR_TEXT_WHITE)
        best_info = font_ui.render(f"Skor Terbaik: {high_score}", True, (255, 230, 109))
        restart_txt = font_small.render("Klik Layar untuk Main Lagi", True, COLOR_TEXT_WHITE)

        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3 - 20))
        surface.blit(score_info, (WIDTH // 2 - score_info.get_width() // 2, HEIGHT // 2 - 20))
        surface.blit(best_info, (WIDTH // 2 - best_info.get_width() // 2, HEIGHT // 2 + 20))
        surface.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 70))

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        game_surface = pygame.Surface((WIDTH, HEIGHT))

        if game_state == "HOME":
            self.draw_home_screen(game_surface)
        else:
            self.draw_board(game_surface)
            
            for bomb in self.bombs:
                bomb.draw(game_surface, self.time_counter)
                
            self.draw_food(game_surface)

            if self.bonus_star:
                self.bonus_star.draw(game_surface, self.time_counter)

            self.draw_snake(game_surface)

            for p in self.particles:
                p.draw(game_surface)

            self.draw_hud(game_surface)

            if game_state == "GAMEOVER":
                self.draw_gameover_screen(game_surface)

        offset_x = random.randint(-self.shake_amount, self.shake_amount) if self.shake_amount > 0 else 0
        offset_y = random.randint(-self.shake_amount, self.shake_amount) if self.shake_amount > 0 else 0

        screen.blit(game_surface, (offset_x, offset_y))

        pygame.draw.rect(screen, COLOR_PANEL_BG, (0, HEIGHT, WIDTH, CONTROL_PANEL_HEIGHT))
        pygame.draw.line(screen, (255, 255, 255, 50), (0, HEIGHT), (WIDTH, HEIGHT), 2)
        
        if game_state == "HOME":
            hint_txt = font_small.render("Gunakan D-Pad atau Keyboard (W-A-S-D)", True, COLOR_TEXT_WHITE)
            screen.blit(hint_txt, (WIDTH // 2 - hint_txt.get_width() // 2, HEIGHT + 65))
        else:
            for btn in self.dpad_buttons:
                btn.draw(screen, mouse_pos)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            clock.tick(FPS)

if __name__ == "__main__":
    game = SnakeGameSmooth()
    game.run()