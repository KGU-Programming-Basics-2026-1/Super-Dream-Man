import math
import random
import pygame

SCREEN_W = 960
SCREEN_H = 540
FPS = 60

SKY_TOP = (116, 196, 255)
SKY_BOTTOM = (206, 238, 255)
WHITE = (248, 252, 255)
INK = (39, 45, 61)
GOLD = (255, 196, 75)
BLUE = (54, 112, 214)
GREEN = (80, 170, 96)
RED = (218, 83, 83)
PURPLE = (126, 94, 197)
DARK_STONE = (73, 82, 96)

def nspeed(value, low, high):
    return max(low, min(high, value))

def approach(current, target, amount):
    if current < target:
        return min(target, current + amount)
    return max(target, current - amount)

def draw_text(surface, font, text, pos, color=INK, center=False):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(rendered, rect)
    return rect

def draw_outlined_text(surface, font, text, pos, color=WHITE, outline=INK, center=False, thickness=2, shadow=True):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    if shadow:
        shadow_rendered = font.render(text, True, (24, 31, 48))
        surface.blit(shadow_rendered, rect.move(3, 4))
    outline_rendered = font.render(text, True, outline)
    for ox, oy in ((-thickness, 0), (thickness, 0), (0, -thickness), (0, thickness),
                   (-thickness, -thickness), (-thickness, thickness),
                   (thickness, -thickness), (thickness, thickness)):
        surface.blit(outline_rendered, rect.move(ox, oy))
    surface.blit(rendered, rect)
    return rect

def blend_color(a, b, amount):
    amount = nspeed(amount, 0.0, 1.0)
    return tuple(round(a[i] * (1 - amount) + b[i] * amount) for i in range(3))

def draw_centered_lines(surface, font, lines, center_x, first_y, color=INK, gap=3, outline=None):
    y = first_y
    for line in lines:
        rendered = font.render(line, True, color)
        line_center = (center_x, y + rendered.get_height() // 2)
        if outline is None:
            rect = rendered.get_rect(center=line_center)
            surface.blit(rendered, rect)
        else:
            draw_outlined_text(surface, font, line, line_center, color=color, outline=outline, center=True, thickness=1)
        y += rendered.get_height() + gap

def draw_star(surface, center, outer_radius=11, inner_radius=5, color=GOLD, border=INK):
    cx, cy = center
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = outer_radius if i % 2 == 0 else inner_radius
        points.append(
            (
                round(cx + math.cos(angle) * radius),
                round(cy + math.sin(angle) * radius),
            )
        )
    pygame.draw.polygon(surface, color, points)
    pygame.draw.lines(surface, border, True, points, 2)

class Platform:
    def __init__(self, rect, color, trim, label="", one_way=False):
        self.rect = rect
        self.color = color
        self.trim = trim
        self.label = label
        self.one_way = one_way

    def draw(self, surface, camera_x, world_name=""):
        r = self.rect.move(-camera_x, 0)
        if r.right < -80 or r.left > SCREEN_W + 80:
            return

        if world_name == "인문대학":
            self.draw_library_platform(surface, r)
            return
        if world_name == "자연과학 대학":
            self.draw_laboratory_platform(surface, r)
            return
        if world_name == "예술 대학":
            self.draw_art_platform(surface, r)
            return
        if world_name == "소프트웨어경영 대학":
            self.draw_software_platform(surface, r)
            return
        if world_name == "창의공과 대학":
            self.draw_factory_platform(surface, r)
            return

        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, self.trim, (r.x, r.y, r.w, 6))
        pygame.draw.rect(surface, DARK_STONE, r, 2)
        for x in range(r.left + 8, r.right, 24):
            pygame.draw.rect(surface, self.trim, (x, r.y + 12, 10, 3))

    def draw_library_platform(self, surface, r):
        cover = (120, 66, 58)
        page = (232, 212, 166)
        spine = (86, 46, 45)
        edge = (52, 39, 42)
        shadow = (48, 31, 33)

        if r.h >= 70:
            pygame.draw.rect(surface, shadow, (r.x + 4, r.y + 7, r.w, r.h - 7))
            pygame.draw.rect(surface, cover, (r.x, r.y, r.w, r.h))
            pygame.draw.rect(surface, spine, (r.x, r.y + 9, r.w, 9))
            pygame.draw.rect(surface, page, (r.x, r.y + 20, r.w, max(8, r.h - 25)))
            pygame.draw.rect(surface, cover, (r.x, r.bottom - 9, r.w, 9))
            pygame.draw.line(surface, (255, 239, 194), (r.x, r.y + 21), (r.right, r.y + 21), 2)
            for x in range(r.left + 22, r.right, 64):
                pygame.draw.line(surface, (192, 170, 132), (x, r.y + 25), (x + 18, r.y + 25), 1)
            pygame.draw.rect(surface, edge, r, 2)
            return

        pygame.draw.rect(surface, shadow, (r.x + 4, r.y + 5, r.w, r.h))
        pygame.draw.rect(surface, cover, r)
        page_rect = pygame.Rect(r.x + 5, r.y + 5, max(4, r.w - 10), max(5, r.h - 10))
        pygame.draw.rect(surface, page, page_rect)
        pygame.draw.line(surface, (255, 242, 202), (page_rect.x, page_rect.y + 2), (page_rect.right, page_rect.y + 2), 1)
        pygame.draw.rect(surface, spine, (r.x, r.y, min(9, r.w), r.h))
        pygame.draw.rect(surface, edge, r, 2)

    def draw_laboratory_platform(self, surface, r):
        shadow = r.move(4, 5)
        pygame.draw.rect(surface, (88, 126, 132), shadow, border_radius=3)
        pygame.draw.rect(surface, (212, 235, 233), r, border_radius=3)
        pygame.draw.rect(surface, (126, 179, 183), (r.x, r.y, r.w, min(7, r.h)), border_radius=3)
        pygame.draw.rect(surface, (76, 118, 126), r, 2, border_radius=3)
        for x in range(r.left + 22, r.right, 42):
            pygame.draw.line(surface, (169, 207, 207), (x, r.y + 8), (x, r.bottom - 3), 1)

    def draw_art_platform(self, surface, r):
        shadow = r.move(4, 5)
        pygame.draw.rect(surface, (112, 94, 104), shadow, border_radius=4)
        pygame.draw.rect(surface, (245, 242, 232), r, border_radius=4)
        pygame.draw.rect(surface, (152, 136, 142), r, 2, border_radius=4)

        colors = ((234, 92, 111), (244, 181, 73), (97, 162, 218), (119, 191, 131), (177, 112, 203), (255, 255, 250))
        step = 58
        start_x = r.x + 8
        for index, x in enumerate(range(start_x, r.right - 4, step)):
            color = colors[(index + r.x // 37) % len(colors)]
            blob_w = min(24, r.right - x - 2)
            blob_h = 6 + (index % 3) * 2
            y = r.y + 5 + (index % 2) * 5
            pygame.draw.ellipse(surface, color, (x, y, max(8, blob_w), blob_h))
            if index % 2 == 0:
                pygame.draw.circle(surface, color, (x + 5, min(r.bottom - 4, y + blob_h + 4)), 3)

        if r.h >= 70:
            for y in range(r.y + 22, r.bottom, 22):
                pygame.draw.line(surface, (225, 218, 207), (r.x + 3, y), (r.right - 3, y), 1)

    def draw_software_platform(self, surface, r):
        pygame.draw.rect(surface, (6, 14, 18), r.move(3, 4), border_radius=3)
        pygame.draw.rect(surface, (12, 29, 34), r, border_radius=3)
        pygame.draw.rect(surface, (42, 217, 120), (r.x, r.y, r.w, min(5, r.h)), border_radius=2)
        pygame.draw.rect(surface, (55, 106, 99), r, 2, border_radius=3)
        for x in range(r.left + 10, r.right, 34):
            pygame.draw.line(surface, (54, 182, 111), (x, r.y + 9), (x + 13, r.y + 9), 1)

    def draw_factory_platform(self, surface, r):
        pygame.draw.rect(surface, (45, 45, 48), r.move(4, 5))
        pygame.draw.rect(surface, (92, 96, 100), r)
        pygame.draw.rect(surface, (188, 140, 63), (r.x, r.y, r.w, min(6, r.h)))
        pygame.draw.rect(surface, (39, 42, 45), r, 2)
        for x in range(r.left + 12, r.right, 38):
            pygame.draw.circle(surface, (57, 60, 63), (x, r.y + 13), 3)

class Cloud:
    def __init__(self, x, y, speed, size):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size

    def update(self, dt):
        self.x += self.speed * dt
        if self.x > SCREEN_W + 160:
            self.x = -180
            self.y = random.randint(42, 210)

    def draw(self, surface):
        s = self.size
        color = (250, 253, 255)

        base_rect = pygame.Rect(
            int(self.x),
            int(self.y + s * 0.45),
            int(s * 3.2),
            max(8, int(s * 0.62)),
        )
        pygame.draw.rect(surface, color, base_rect, border_radius=base_rect.height // 2)

        pygame.draw.circle(surface, color, (int(self.x + s * 0.7), int(self.y + s * 0.55)), int(s * 0.65))
        pygame.draw.circle(surface, color, (int(self.x + s * 1.55), int(self.y + s * 0.35)), int(s * 0.85))
        pygame.draw.circle(surface, color, (int(self.x + s * 2.35), int(self.y + s * 0.58)), int(s * 0.62))

class Bird:
    def __init__(self):
        self.reset(random.randint(0, SCREEN_W))

    def reset(self, x=None):
        self.x = SCREEN_W + random.randint(20, 320) if x is None else x
        self.y = random.randint(65, 190)
        self.speed = random.uniform(60, 110)
        self.phase = random.uniform(0, math.tau)
        self.cooldown = random.uniform(0.0, 10.0)

    def update(self, dt):
        self.cooldown -= dt
        if self.cooldown > 0:
            return
        self.x -= self.speed * dt
        self.phase += dt * 8
        if self.x < -40:
            self.reset()
            self.cooldown = random.uniform(2.0, 8.0)

    def draw(self, surface):
        if self.cooldown > 0:
            return
        wing = math.sin(self.phase) * 5
        p1 = (int(self.x), int(self.y))
        pygame.draw.line(surface, INK, p1, (int(self.x - 9), int(self.y + wing)), 2)
        pygame.draw.line(surface, INK, p1, (int(self.x + 9), int(self.y + wing)), 2)

class PencilProjectile:

    def __init__(self, x, y, speed):
        self.x = float(x)
        self.y = float(y)
        self.speed = float(speed)
        self.width = 76
        self.height = 9
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    @property
    def danger_rect(self):
        r = self.rect
        return pygame.Rect(r.left - 2, r.top + 1, 17, max(3, r.height - 2))

    def update(self, dt, player):
        old_rect = self.rect
        standing_on_top = (
            abs(player.rect.bottom - old_rect.top) <= 3
            and player.rect.right > old_rect.left
            and player.rect.left < old_rect.right
        )
        distance = self.speed * dt
        self.x -= distance
        if standing_on_top:
            player.pos.x -= distance
        if self.rect.right < -180:
            self.alive = False

    def hits_player_from_front(self, player):
        r = self.rect
        safe_on_top = (
            player.rect.bottom <= r.top + 4
            and player.rect.right > r.left
            and player.rect.left < r.right
        )
        return not safe_on_top and self.danger_rect.colliderect(player.rect)

    def draw(self, surface, camera_x):
        r = self.rect.move(-camera_x, 0)
        if r.right < -100 or r.left > SCREEN_W + 120:
            return
        body = pygame.Rect(r.x + 14, r.y, r.w - 24, r.h)
        pygame.draw.rect(surface, (247, 196, 73), body)
        pygame.draw.line(surface, (255, 231, 132), (body.x, body.y + 2), (body.right, body.y + 2), 2)
        pygame.draw.line(surface, (179, 123, 50), (body.x, body.bottom - 2), (body.right, body.bottom - 2), 2)
        pygame.draw.rect(surface, INK, body, 1)

        wood = [(r.x + 14, r.y), (r.x, r.centery), (r.x + 14, r.bottom)]
        pygame.draw.polygon(surface, (226, 176, 118), wood)
        pygame.draw.polygon(surface, INK, wood, 1)
        graphite = [(r.x, r.centery), (r.x + 6, r.centery - 3), (r.x + 6, r.centery + 3)]
        pygame.draw.polygon(surface, (54, 58, 69), graphite)

        pygame.draw.rect(surface, (205, 143, 92), (r.right - 10, r.y, 5, r.h))
        pygame.draw.rect(surface, (240, 142, 157), (r.right - 5, r.y, 8, r.h), border_radius=2)
        pygame.draw.rect(surface, INK, (r.right - 10, r.y, 13, r.h), 1)

class TrapBook:

    def __init__(self, x, floor_y, width=84):
        self.x = x
        self.floor_y = floor_y
        self.width = width
        self.timer = 0.45
        self.default_timer = 0.45
        self.destroyed = False
        self.closed_flash = 0.0

    @property
    def zone(self):
        return pygame.Rect(self.x, self.floor_y - 15, self.width, 20)

    def reset_contact(self):
        if self.closed_flash <= 0:
            self.timer = self.default_timer

    def destroy(self):
        self.destroyed = True
        self.closed_flash = 0.0

    def update_contact(self, dt, player, stomp_landed):
        if self.destroyed:
            return False
        overlap = player.rect.right > self.x and player.rect.left < self.x + self.width
        on_floor = player.on_ground and abs(player.rect.bottom - self.floor_y) <= 3

        if stomp_landed and overlap and on_floor:
            self.destroy()
            return False

        if overlap and on_floor and player.hitbox_height < player.height:
            self.reset_contact()
            return False
        if overlap and on_floor:
            self.timer -= dt
            if self.timer <= 0:
                self.closed_flash = 0.20
                return True
        else:
            self.reset_contact()
        return False

    def update_visual(self, dt):
        self.closed_flash = max(0.0, self.closed_flash - dt)

    def draw(self, surface, camera_x):
        if self.destroyed:
            return
        x = round(self.x - camera_x)
        y = self.floor_y
        if x > SCREEN_W + 120 or x + self.width < -120:
            return
        warning = self.timer < self.default_timer
        shake = round(math.sin(pygame.time.get_ticks() * 0.035) * 3) if warning else 0
        x += shake

        if self.closed_flash > 0:
            pygame.draw.rect(surface, (112, 56, 52), (x, y - 16, self.width, 16), border_radius=4)
            pygame.draw.rect(surface, (245, 217, 164), (x + 5, y - 12, self.width - 10, 7))
            pygame.draw.rect(surface, INK, (x, y - 16, self.width, 16), 2, border_radius=4)
            return

        cx = x + self.width // 2
        left_page = [(cx, y - 2), (x + 3, y - 14), (x + 6, y - 25), (cx - 2, y - 12)]
        right_page = [(cx, y - 2), (x + self.width - 3, y - 14), (x + self.width - 6, y - 25), (cx + 2, y - 12)]
        pygame.draw.polygon(surface, (242, 220, 174), left_page)
        pygame.draw.polygon(surface, (250, 230, 185), right_page)
        pygame.draw.lines(surface, INK, True, left_page, 2)
        pygame.draw.lines(surface, INK, True, right_page, 2)
        pygame.draw.line(surface, (132, 93, 73), (cx, y - 2), (cx, y - 18), 2)
        for line_y in (y - 18, y - 14, y - 10):
            pygame.draw.line(surface, (183, 153, 119), (x + 11, line_y), (cx - 7, line_y + 3), 1)
            pygame.draw.line(surface, (183, 153, 119), (cx + 7, line_y + 3), (x + self.width - 11, line_y), 1)

class PaperPlatform:

    def __init__(self, x, y, width=86, height=13):
        self.base_rect = pygame.Rect(x, y, width, height)
        self.state = "idle"
        self.timer = 0.0
        self.fall_offset = 0.0
        self.fall_speed = 0.0
        self.respawn_timer = 0.0

        self.armed_delay = 0.78
        self.shake_delay = 0.24
        self.respawn_delay = 3.0

    @property
    def active(self):
        return self.state != "gone"

    @property
    def rect(self):
        shake_x = 0
        if self.state == "shaking":
            shake_x = round(math.sin(pygame.time.get_ticks() * 0.045) * 4)
        return self.base_rect.move(shake_x, round(self.fall_offset))

    def update(self, dt):
        if self.state == "armed":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "shaking"
                self.timer = self.shake_delay
        elif self.state == "shaking":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "falling"
                self.fall_speed = 46.0
        elif self.state == "falling":
            self.fall_speed += 520 * dt
            self.fall_offset += self.fall_speed * dt
            if self.rect.top > SCREEN_H + 150:
                self.state = "gone"
                self.respawn_timer = self.respawn_delay
        elif self.state == "gone":
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.state = "idle"
                self.fall_offset = 0.0
                self.fall_speed = 0.0

    def register_player(self, player):
        if not self.active or self.state not in ("idle", "armed"):
            return
        r = self.rect
        standing = (
            player.on_ground
            and abs(player.rect.bottom - r.top) <= 3
            and player.rect.right > r.left
            and player.rect.left < r.right
        )
        if standing and self.state == "idle":
            self.state = "armed"
            self.timer = self.armed_delay

    def draw(self, surface, camera_x):
        if not self.active:
            return
        r = self.rect.move(-camera_x, 0)
        if r.right < -100 or r.left > SCREEN_W + 100:
            return
        shadow = r.move(4, 5)
        pygame.draw.rect(surface, (63, 48, 55), shadow, border_radius=3)
        pygame.draw.rect(surface, (248, 238, 206), r, border_radius=3)
        pygame.draw.rect(surface, (198, 181, 145), (r.x + 4, r.bottom - 4, r.w - 8, 3))
        pygame.draw.line(surface, (255, 252, 229), (r.x + 5, r.y + 3), (r.right - 5, r.y + 3), 2)
        pygame.draw.rect(surface, INK, r, 2, border_radius=3)

        pygame.draw.line(surface, (204, 190, 160), (r.x + 14, r.y + 5), (r.x + 25, r.bottom - 4), 1)
        pygame.draw.line(surface, (204, 190, 160), (r.right - 18, r.y + 4), (r.right - 31, r.bottom - 3), 1)

class FlyingEraser:

    def __init__(self, x, floor_y, patrol_width=150, hover_altitude=128):
        self.home_x = float(x)
        self.spawn_x = float(x)
        self.x = float(x)
        self.floor_y = floor_y
        self.patrol_width = patrol_width
        self.hover_y = float(floor_y - hover_altitude)
        self.y = self.hover_y
        self.width = 42
        self.height = 19
        self.direction = 1
        self.speed = 62.0
        self.state = "patrol"
        self.timer = 0.0
        self.vertical_speed = 0.0
        self.respawn_timer = 0.0
        self.phase = random.uniform(0.0, math.tau)

        self.knockback_vx = 0.0
        self.knockback_vy = 0.0
        self.repel_cooldown = 0.0

    @property
    def active(self):
        return self.state != "disabled"

    @property
    def rect(self):
        bob = 0
        if self.state == "patrol":
            bob = round(math.sin(self.phase) * 4)
        return pygame.Rect(round(self.x), round(self.y + bob), self.width, self.height)

    def disable(self):
        self.state = "disabled"
        self.respawn_timer = 4.5
        self.vertical_speed = 0.0
        self.knockback_vx = 0.0
        self.knockback_vy = 0.0
        self.repel_cooldown = 0.0

    def apply_knockback(self, direction):
        if not self.active or self.repel_cooldown > 0:
            return
        self.state = "knocked"
        self.knockback_vx = direction * 315.0
        self.knockback_vy = -145.0
        self.repel_cooldown = 0.16

    def update(self, dt, player, has_floor_below=None):
        if self.state == "disabled":
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.spawn_x = self.home_x
                self.x = self.home_x
                self.y = self.hover_y
                self.direction = 1
                self.state = "patrol"
            return

        self.repel_cooldown = max(0.0, self.repel_cooldown - dt)

        if self.state == "knocked":
            self.x += self.knockback_vx * dt
            self.y += self.knockback_vy * dt
            self.knockback_vy += 880 * dt
            self.knockback_vx *= 0.93 ** (dt * 60)

            supported = True if has_floor_below is None else has_floor_below(self.rect.centerx)
            if self.y > SCREEN_H + 90:
                self.disable()
            elif supported and self.y + self.height >= self.floor_y:
                self.y = self.floor_y - self.height
                self.knockback_vy = 0.0
                self.knockback_vx *= 0.70
                if abs(self.knockback_vx) < 26:
                    self.spawn_x = self.x
                    self.state = "resting"
                    self.timer = 0.24
            return

        self.phase += dt * 4.2
        if self.state == "patrol":
            self.x += self.direction * self.speed * dt
            if self.x < self.spawn_x - self.patrol_width:
                self.x = self.spawn_x - self.patrol_width
                self.direction = 1
            elif self.x > self.spawn_x + self.patrol_width:
                self.x = self.spawn_x + self.patrol_width
                self.direction = -1

            close_x = abs(player.rect.centerx - self.rect.centerx) < 145
            player_below = player.rect.centery > self.rect.centery - 10
            if close_x and player_below:
                self.state = "warning"
                self.timer = 0.32
                self.vertical_speed = 0.0

        elif self.state == "warning":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "dropping"
                self.vertical_speed = 90.0

        elif self.state == "dropping":
            self.vertical_speed += 760 * dt
            self.y += self.vertical_speed * dt
            supported = True if has_floor_below is None else has_floor_below(self.rect.centerx)
            if self.y > SCREEN_H + 90:
                self.disable()
            elif supported and self.y + self.height >= self.floor_y:
                self.y = self.floor_y - self.height
                self.state = "resting"
                self.timer = 0.34
                self.vertical_speed = 0.0

        elif self.state == "resting":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "rising"

        elif self.state == "rising":
            self.y -= 150 * dt
            if self.y <= self.hover_y:
                self.y = self.hover_y
                self.state = "patrol"

    def handle_player_contact(self, player):
        if not self.active or not self.rect.colliderect(player.rect):
            return None

        stomped_from_above = (
            player.stomp_active
            and player.vel.y >= 0
            and player.rect.bottom <= self.rect.centery + 12
        )
        if stomped_from_above:
            self.disable()
            player.stomp_active = False
            player.stomp_windup = 0.0
            player.stomp_impact_timer = 0.16
            player.vel.y = -270
            player.on_ground = False
            return None
        return "eraser"

    def draw(self, surface, camera_x):
        if not self.active:
            return
        r = self.rect.move(-camera_x, 0)
        if r.right < -100 or r.left > SCREEN_W + 100:
            return

        if self.state == "warning":
            pulse = 3 + round(abs(math.sin(pygame.time.get_ticks() * 0.025)) * 4)
            pygame.draw.line(surface, (229, 91, 91), (r.centerx, r.bottom + 4), (r.centerx, r.bottom + 12 + pulse), 2)
            pygame.draw.line(surface, (229, 91, 91), (r.centerx - 8, r.bottom + 5), (r.centerx - 12, r.bottom + 11 + pulse), 2)
            pygame.draw.line(surface, (229, 91, 91), (r.centerx + 8, r.bottom + 5), (r.centerx + 12, r.bottom + 11 + pulse), 2)

        pygame.draw.rect(surface, (63, 47, 63), r.move(3, 4), border_radius=6)
        pygame.draw.rect(surface, (239, 150, 171), r, border_radius=6)
        pygame.draw.rect(surface, (255, 208, 218), (r.x + 4, r.y + 3, r.w - 8, 6), border_radius=3)
        pygame.draw.rect(surface, (201, 112, 144), (r.x + 4, r.bottom - 6, r.w - 8, 4), border_radius=2)
        pygame.draw.rect(surface, INK, r, 2, border_radius=6)

        sleeve = pygame.Rect(r.x + 15, r.y - 1, 13, r.h + 2)
        pygame.draw.rect(surface, (236, 224, 193), sleeve)
        pygame.draw.line(surface, (188, 164, 136), (sleeve.x + 3, sleeve.y + 2), (sleeve.x + 3, sleeve.bottom - 2), 1)
        pygame.draw.rect(surface, INK, sleeve, 1)

class Bookworm:

    def __init__(self, min_x, max_x, floor_y, speed=58, style="library"):
        self.home_min_x = float(min_x)
        self.home_max_x = float(max_x)
        self.min_x = float(min_x)
        self.max_x = float(max_x)
        self.x = float(min_x)
        self.floor_y = floor_y
        self.speed = float(speed)
        self.direction = 1
        self.width = 43
        self.low_height = 17
        self.tall_height = 31
        self.alert_amount = 0.0
        self.disabled = False
        self.respawn_timer = 0.0
        self.phase = random.uniform(0.0, math.tau)

        self.y = float(self.floor_y - self.low_height)
        self.knocked = False
        self.knockback_vx = 0.0
        self.knockback_vy = 0.0
        self.repel_cooldown = 0.0
        self.style = style
        self.stun_timer = 0.0
        self.paint_color = None

    @property
    def height(self):
        return round(self.low_height + (self.tall_height - self.low_height) * self.alert_amount)

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def disable(self):
        self.disabled = True
        self.respawn_timer = 4.2
        self.knocked = False
        self.knockback_vx = 0.0
        self.knockback_vy = 0.0
        self.repel_cooldown = 0.0
        self.stun_timer = 0.0

    def stun(self, seconds=2.5):
        self.stun_timer = max(self.stun_timer, seconds)

    def apply_knockback(self, direction):
        if self.disabled or self.repel_cooldown > 0:
            return
        self.knocked = True
        self.knockback_vx = direction * 335.0
        self.knockback_vy = -115.0
        self.repel_cooldown = 0.14

    def update(self, dt, player, has_floor_below=None):
        if self.disabled:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.disabled = False
                self.min_x = self.home_min_x
                self.max_x = self.home_max_x
                self.x = self.home_min_x
                self.y = float(self.floor_y - self.low_height)
                self.direction = 1
                self.alert_amount = 0.0
                self.knocked = False
                self.knockback_vx = 0.0
                self.knockback_vy = 0.0
            return

        self.repel_cooldown = max(0.0, self.repel_cooldown - dt)
        self.stun_timer = max(0.0, self.stun_timer - dt)
        self.phase += dt * (2 if self.stun_timer > 0 else 8)

        if self.stun_timer > 0:
            return

        if self.knocked:
            self.x += self.knockback_vx * dt

            if has_floor_below is None:
                fully_supported = True
            else:
                left_supported = has_floor_below(self.rect.left + 2)
                center_supported = has_floor_below(self.rect.centerx)
                right_supported = has_floor_below(self.rect.right - 2)
                fully_supported = left_supported and center_supported and right_supported

            if fully_supported and self.y + self.height >= self.floor_y - 1:
                self.y = float(self.floor_y - self.height)
                self.knockback_vy = 0.0
                self.knockback_vx *= 0.88 ** (dt * 60)
            else:
                self.y += self.knockback_vy * dt
                self.knockback_vy += 980 * dt
                self.knockback_vx *= 0.985 ** (dt * 60)

            if self.y > SCREEN_H + 80:
                self.disable()
                return

            if fully_supported and abs(self.knockback_vx) < 14:
                patrol_width = self.max_x - self.min_x
                center_x = self.x + self.width / 2
                self.min_x = center_x - patrol_width / 2
                self.max_x = center_x + patrol_width / 2
                self.knocked = False
                self.knockback_vx = 0.0
                self.y = float(self.floor_y - self.height)
            return
        close = abs(player.rect.centerx - self.rect.centerx) < 118
        target = 1.0 if close else 0.0
        self.alert_amount = approach(self.alert_amount, target, 4.6 * dt)
        self.y = float(self.floor_y - self.height)

        move_speed = self.speed * (0.72 if self.alert_amount > 0.45 else 1.0)
        next_x = self.x + self.direction * move_speed * dt

        if has_floor_below is not None:
            next_left = next_x + 2
            next_right = next_x + self.width - 2
            if not has_floor_below(next_left) or not has_floor_below(next_right):
                self.direction *= -1
                next_x = self.x

        self.x = next_x
        if self.x <= self.min_x:
            self.x = self.min_x
            self.direction = 1
        elif self.x + self.width >= self.max_x:
            self.x = self.max_x - self.width
            self.direction = -1

    def handle_player_contact(self, player):
        if self.disabled or not self.rect.colliderect(player.rect):
            return None

        stomped_from_above = (
            player.stomp_active
            and player.vel.y >= 0
            and player.rect.bottom <= self.rect.centery + 12
        )
        if stomped_from_above:
            self.disable()
            player.stomp_active = False
            player.stomp_windup = 0.0
            player.stomp_impact_timer = 0.16
            player.vel.y = -250
            player.on_ground = False
            return None
        return "bookworm"

    def draw(self, surface, camera_x):
        if self.disabled:
            return
        r = self.rect.move(-camera_x, 0)
        if r.right < -100 or r.left > SCREEN_W + 100:
            return

        wiggle = round(math.sin(self.phase) * 2)
        if self.paint_color:
            segment_color = self.paint_color
            segment_shadow = tuple(max(0, c - 58) for c in self.paint_color)
            head_color = tuple(min(255, c + 28) for c in self.paint_color)
        elif self.style == "science":
            segment_color, segment_shadow, head_color = (151, 124, 198), (92, 73, 145), (190, 165, 225)
        elif self.style == "art":
            segment_color, segment_shadow, head_color = (238, 193, 72), (164, 117, 42), (255, 222, 104)
        elif self.style == "software":
            segment_color, segment_shadow, head_color = (8, 20, 17), (4, 10, 9), (10, 28, 22)
        elif self.style == "engineering":
            segment_color, segment_shadow, head_color = (74, 78, 82), (37, 40, 43), (104, 109, 114)
        else:
            segment_color, segment_shadow, head_color = (132, 191, 108), (76, 136, 84), (157, 213, 122)
        outline = (61, 240, 128) if self.style == "software" else INK

        body_y = r.bottom - 13
        for i, offset in enumerate((0, 11, 22)):
            sy = body_y + (wiggle if i % 2 == 0 else -wiggle)
            pygame.draw.ellipse(surface, segment_shadow, (r.x + offset + 2, sy + 3, 18, 14))
            pygame.draw.ellipse(surface, segment_color, (r.x + offset, sy, 18, 14))
            pygame.draw.ellipse(surface, outline, (r.x + offset, sy, 18, 14), 1)

        head_x = r.right - 16 if self.direction > 0 else r.x
        head_y = r.y
        pygame.draw.ellipse(surface, segment_shadow, (head_x + 2, head_y + 3, 18, 18))
        pygame.draw.ellipse(surface, head_color, (head_x, head_y, 18, 18))
        pygame.draw.ellipse(surface, outline, (head_x, head_y, 18, 18), 1)

        eye_x = head_x + (11 if self.direction > 0 else 5)
        pygame.draw.circle(surface, INK, (eye_x, head_y + 7), 2)
        pygame.draw.circle(surface, WHITE, (eye_x, head_y + 6), 1)

        antenna_h = 3 + round(7 * self.alert_amount)
        pygame.draw.line(surface, outline, (head_x + 6, head_y + 3), (head_x + 4, head_y - antenna_h), 1)
        pygame.draw.line(surface, outline, (head_x + 12, head_y + 3), (head_x + 14, head_y - antenna_h), 1)
        pygame.draw.circle(surface, (225, 139, 108), (head_x + 4, head_y - antenna_h), 2)
        pygame.draw.circle(surface, (225, 139, 108), (head_x + 14, head_y - antenna_h), 2)

        if self.stun_timer > 0:
            pygame.draw.circle(surface, (247, 222, 105), (r.centerx - 8, r.y - 10), 3)
            pygame.draw.circle(surface, (247, 222, 105), (r.centerx + 8, r.y - 14), 3)
            pygame.draw.line(surface, (247, 222, 105), (r.centerx - 1, r.y - 6), (r.centerx + 4, r.y - 18), 2)

class FloatingBookItem:
    POWER_ATTR = "has_book_power"

    def __init__(self, x, y):
        self.base_y = float(y)
        self.x = float(x)
        self.y = float(y)
        self.width = 30
        self.height = 22
        self.phase = 0.0
        self.collected = False

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt):
        if self.collected:
            return
        self.phase += dt * 4.2
        self.y = self.base_y + math.sin(self.phase) * 5

    def try_collect(self, player):

        if self.collected or player.on_ground:
            return False
        if self.rect.colliderect(player.rect):
            self.collected = True
            setattr(player, self.POWER_ATTR, True)
            return True
        return False

    def draw(self, surface, camera_x):
        if self.collected:
            return
        r = self.rect.move(-camera_x, 0)
        if r.right < -100 or r.left > SCREEN_W + 100:
            return

        glow = pygame.Surface((72, 72), pygame.SRCALPHA)
        pulse = 34 + round((math.sin(self.phase * 1.8) + 1) * 10)
        pygame.draw.circle(glow, (255, 230, 118, pulse), (36, 36), 29)
        pygame.draw.circle(glow, (255, 248, 192, 36), (36, 36), 21)
        surface.blit(glow, (r.centerx - 36, r.centery - 36))

        center_x = r.centerx
        top = r.y + 4
        bottom = r.bottom - 3
        left_page = [(center_x, top + 4), (r.x + 2, top), (r.x + 4, bottom), (center_x - 1, bottom - 3)]
        right_page = [(center_x, top + 4), (r.right - 2, top), (r.right - 4, bottom), (center_x + 1, bottom - 3)]
        pygame.draw.polygon(surface, (255, 244, 199), left_page)
        pygame.draw.polygon(surface, (255, 251, 218), right_page)
        pygame.draw.lines(surface, INK, True, left_page, 2)
        pygame.draw.lines(surface, INK, True, right_page, 2)
        pygame.draw.line(surface, (183, 143, 93), (center_x, top + 4), (center_x, bottom - 3), 2)

        for sx, sy in ((r.x - 6, r.y + 3), (r.right + 6, r.y + 7), (r.centerx, r.y - 7)):
            pygame.draw.line(surface, (255, 223, 92), (sx - 3, sy), (sx + 3, sy), 1)
            pygame.draw.line(surface, (255, 223, 92), (sx, sy - 3), (sx, sy + 3), 1)

class AcademicQuestionBlock:
    ITEM_CLASS = FloatingBookItem

    def __init__(self, x, y, size=32):
        self.rect = pygame.Rect(x, y, size, size)
        self.state = "ready"
        self.burst_timer = 0.0
        self.item = None

    def update(self, dt):
        if self.state == "burst":
            self.burst_timer -= dt
            if self.burst_timer <= 0:
                self.state = "spent"
        if self.item:
            self.item.update(dt)

    def try_hit_from_below(self, player):
        if self.state != "ready" or player.vel.y >= 0:
            return False

        underside = pygame.Rect(self.rect.x, self.rect.bottom - 7, self.rect.w, 13)
        if not underside.colliderect(player.rect):
            return False

        self.state = "burst"
        self.burst_timer = 0.30
        self.item = self.ITEM_CLASS(self.rect.centerx - 15, self.rect.y - 43)
        player.vel.y = 135
        return True

    def try_collect(self, player):
        return bool(self.item and self.item.try_collect(player))

    def draw(self, surface, camera_x):
        r = self.rect.move(-camera_x, 0)
        if r.right < -100 or r.left > SCREEN_W + 100:
            if self.item:
                self.item.draw(surface, camera_x)
            return

        if self.state == "ready":
            shadow = r.move(4, 5)
            pygame.draw.rect(surface, (78, 54, 52), shadow, border_radius=5)
            pygame.draw.rect(surface, (237, 166, 61), r, border_radius=5)
            pygame.draw.rect(surface, (255, 214, 96), (r.x + 4, r.y + 4, r.w - 8, 7), border_radius=3)
            pygame.draw.rect(surface, INK, r, 2, border_radius=5)

            q = (108, 71, 48)
            pygame.draw.rect(surface, q, (r.x + 11, r.y + 8, 11, 4))
            pygame.draw.rect(surface, q, (r.x + 19, r.y + 11, 4, 7))
            pygame.draw.rect(surface, q, (r.x + 15, r.y + 16, 7, 4))
            pygame.draw.rect(surface, q, (r.x + 14, r.y + 19, 4, 5))
            pygame.draw.rect(surface, q, (r.x + 14, r.y + 26, 4, 4))

        elif self.state == "burst":
            progress = 1.0 - self.burst_timer / 0.30
            spread = round(10 + progress * 19)
            cx, cy = r.center
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1)):
                start = (cx + dx * 8, cy + dy * 8)
                end = (cx + dx * spread, cy + dy * spread)
                pygame.draw.line(surface, (255, 221, 88), start, end, 3)
            pygame.draw.circle(surface, (255, 244, 178), (cx, cy), max(4, round(12 * (1 - progress))), 2)

        if self.item:
            self.item.draw(surface, camera_x)

class FloatingFlaskItem(FloatingBookItem):
    POWER_ATTR = "has_lab_power"

    def draw(self, surface, camera_x):
        if self.collected:
            return
        r = self.rect.move(-camera_x, 0)
        if r.right < -100 or r.left > SCREEN_W + 100:
            return

        glow = pygame.Surface((72, 72), pygame.SRCALPHA)
        pulse = 32 + round((math.sin(self.phase * 1.8) + 1) * 11)
        pygame.draw.circle(glow, (184, 128, 232, pulse), (36, 36), 29)
        pygame.draw.circle(glow, (229, 211, 248, 32), (36, 36), 20)
        surface.blit(glow, (r.centerx - 36, r.centery - 36))

        fx = r.centerx - 10
        fy = r.y
        pygame.draw.rect(surface, (91, 125, 139), (fx + 8, fy, 5, 10))
        flask = [(fx + 4, fy + 9), (fx + 17, fy + 9), (fx + 22, fy + 23), (fx, fy + 23)]
        liquid = [(fx + 2, fy + 17), (fx + 20, fy + 17), (fx + 22, fy + 23), (fx, fy + 23)]
        pygame.draw.polygon(surface, (235, 244, 244), flask)
        pygame.draw.polygon(surface, (154, 91, 199), liquid)
        pygame.draw.lines(surface, INK, True, flask, 2)

        for sx, sy in ((r.x - 5, r.y + 4), (r.right + 5, r.y + 8), (r.centerx, r.y - 7)):
            pygame.draw.line(surface, (213, 167, 245), (sx - 3, sy), (sx + 3, sy), 1)
            pygame.draw.line(surface, (213, 167, 245), (sx, sy - 3), (sx, sy + 3), 1)

class FlaskQuestionBlock(AcademicQuestionBlock):
    ITEM_CLASS = FloatingFlaskItem

class ThrownFlask:
    def __init__(self, x, y, facing):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(245 * facing, -430)
        self.width = 18
        self.height = 20
        self.active = True

    @property
    def rect(self):
        return pygame.Rect(round(self.pos.x), round(self.pos.y), self.width, self.height)

    def update(self, dt, floor_y, has_floor_below):
        if not self.active:
            return None

        self.vel.y += 980 * dt
        self.pos += self.vel * dt
        r = self.rect

        if r.top > SCREEN_H + 120:
            self.active = False
            return None

        if has_floor_below(r.centerx) and r.bottom >= floor_y:
            self.active = False
            return GasCloud(r.centerx, floor_y - 12)
        return None

    def draw(self, surface, camera_x):
        if not self.active:
            return
        r = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, (91, 125, 139), (r.x + 7, r.y, 4, 7))
        flask = [(r.x + 4, r.y + 6), (r.x + 14, r.y + 6), (r.right, r.bottom), (r.x, r.bottom)]
        liquid = [(r.x + 2, r.y + 14), (r.right - 2, r.y + 14), (r.right, r.bottom), (r.x, r.bottom)]
        pygame.draw.polygon(surface, (235, 244, 244), flask)
        pygame.draw.polygon(surface, (154, 91, 199), liquid)
        pygame.draw.lines(surface, INK, True, flask, 1)

class GasCloud:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = 76
        self.timer = 2.6
        self.phase = 0.0

    @property
    def active(self):
        return self.timer > 0

    @property
    def rect(self):
        return pygame.Rect(round(self.x - self.radius), round(self.y - self.radius),
                           self.radius * 2, self.radius * 2)

    def update(self, dt):
        self.timer -= dt
        self.phase += dt * 3.4

    def draw(self, surface, camera_x):
        if not self.active:
            return
        cx = round(self.x - camera_x)
        cy = round(self.y)
        cloud = pygame.Surface((190, 150), pygame.SRCALPHA)
        alpha = max(18, round(76 * min(1.0, self.timer)))
        for ox, oy, radius in ((58, 82, 40), (94, 58, 49), (128, 80, 42), (84, 100, 38)):
            pulse = round(math.sin(self.phase + ox * 0.03) * 5)
            pygame.draw.circle(cloud, (158, 103, 196, alpha), (ox + pulse, oy), radius)
        surface.blit(cloud, (cx - 95, cy - 112))

class GlassPlatform(PaperPlatform):
    def __init__(self, x, y, width=86, height=13):
        super().__init__(x, y, width, height)
        self.armed_delay = 0.62
        self.shake_delay = 0.20
        self.respawn_delay = 3.0

    def draw(self, surface, camera_x):
        if not self.active:
            return
        r = self.rect.move(-camera_x, 0)
        if r.right < -100 or r.left > SCREEN_W + 100:
            return

        pygame.draw.rect(surface, (70, 112, 122), r.move(4, 5), border_radius=3)
        pygame.draw.rect(surface, (198, 236, 239), r, border_radius=3)
        pygame.draw.rect(surface, (231, 251, 252), (r.x + 4, r.y + 2, r.w - 8, 4), border_radius=2)
        pygame.draw.rect(surface, (82, 145, 155), r, 2, border_radius=3)

        if self.state in ("armed", "shaking", "falling"):
            cx = r.centerx
            pygame.draw.line(surface, (103, 161, 169), (cx, r.y + 3), (cx - 11, r.bottom - 3), 1)
            pygame.draw.line(surface, (103, 161, 169), (cx, r.y + 3), (cx + 13, r.bottom - 2), 1)
            pygame.draw.line(surface, (103, 161, 169), (cx - 5, r.y + 7), (cx - 17, r.y + 3), 1)

class PurplePuddle:
    def __init__(self, x, floor_y, width=88):
        self.x = x
        self.floor_y = floor_y
        self.width = width
        self.default_timer = 0.58
        self.timer = self.default_timer
        self.explosion_timer = 0.0

    @property
    def zone(self):
        return pygame.Rect(self.x, self.floor_y - 14, self.width, 18)

    def update(self, dt, player):
        overlap = player.rect.right > self.x and player.rect.left < self.x + self.width
        on_floor = player.on_ground and abs(player.rect.bottom - self.floor_y) <= 3

        if overlap and on_floor:
            self.timer -= dt
            if self.timer <= 0:
                self.explosion_timer = 0.22
                self.timer = self.default_timer
                return True
        elif self.explosion_timer <= 0:
            self.timer = self.default_timer

        return False

    def update_visual(self, dt):
        self.explosion_timer = max(0.0, self.explosion_timer - dt)

    def draw(self, surface, camera_x):
        x = round(self.x - camera_x)
        y = self.floor_y
        if x > SCREEN_W + 120 or x + self.width < -120:
            return

        if self.explosion_timer > 0:
            cx = x + self.width // 2
            pygame.draw.circle(surface, (190, 115, 224), (cx, y - 18), 32)
            pygame.draw.circle(surface, (237, 187, 250), (cx, y - 18), 20)
            pygame.draw.circle(surface, (112, 68, 155), (cx, y - 18), 32, 3)
            return

        warning = self.timer < self.default_timer
        pulse = 2 + round(abs(math.sin(pygame.time.get_ticks() * 0.025)) * 3) if warning else 0
        puddle_rect = pygame.Rect(x, y - 9 - pulse, self.width, 13 + pulse)
        pygame.draw.ellipse(surface, (89, 54, 127), puddle_rect.move(3, 4))
        pygame.draw.ellipse(surface, (152, 91, 195), puddle_rect)
        pygame.draw.ellipse(surface, (218, 162, 238), (x + 10, y - 7 - pulse, self.width - 24, 5))
        pygame.draw.ellipse(surface, (75, 49, 105), puddle_rect, 2)

        for offset in (18, 43, 67):
            bubble_y = y - 12 - round(abs(math.sin(pygame.time.get_ticks() * 0.012 + offset)) * 7)
            pygame.draw.circle(surface, (196, 135, 224), (x + offset, bubble_y), 3, 1)

class FallingGlassShard:
    def __init__(self, x, floor_y, delay=0.0):
        self.x = float(x)
        self.floor_y = floor_y
        self.delay = delay
        self.reset()

    def reset(self):
        self.y = -42.0
        self.speed_y = 0.0
        self.state = "waiting"
        self.timer = 1.0 + self.delay
        self.delay = 0.0

    @property
    def active(self):
        return self.state != "waiting"

    @property
    def rect(self):
        return pygame.Rect(round(self.x - 11), round(self.y), 22, 38)

    def update(self, dt, player):
        self.timer -= dt

        if self.state == "waiting":
            if self.timer <= 0 and abs(player.rect.centerx - self.x) < 430:
                self.state = "warning"
                self.timer = 0.42
            return None

        if self.state == "warning":
            if self.timer <= 0:
                self.state = "falling"
                self.y = -36.0
                self.speed_y = 120.0
            return None

        if self.state == "falling":
            self.speed_y += 1080 * dt
            self.y += self.speed_y * dt

            if self.rect.colliderect(player.rect):
                self.state = "broken"
                self.timer = 0.28
                return "glass_shard"

            if self.y + 38 >= self.floor_y:
                self.y = self.floor_y - 18
                self.state = "broken"
                self.timer = 0.34
            return None

        if self.state == "broken" and self.timer <= 0:
            self.reset()
            self.timer = 0.85 + random.uniform(0.0, 0.55)

        return None

    def draw(self, surface, camera_x):
        x = round(self.x - camera_x)

        if self.state == "waiting":
            return

        if self.state == "warning":
            pygame.draw.line(surface, (208, 95, 119), (x, 42), (x, 82), 3)
            pygame.draw.polygon(surface, (244, 202, 207), [(x, 88), (x - 8, 74), (x + 8, 74)])
            return

        if self.state == "falling":
            r = self.rect.move(-camera_x, 0)
            points = [(r.centerx, r.y), (r.right, r.y + 12), (r.centerx + 4, r.bottom), (r.left, r.y + 14)]
            pygame.draw.polygon(surface, (198, 237, 241), points)
            pygame.draw.polygon(surface, (91, 151, 160), points, 2)
            pygame.draw.line(surface, (245, 255, 255), (r.centerx - 2, r.y + 5), (r.centerx + 3, r.bottom - 7), 2)
            return

        if self.state == "broken":
            y = self.floor_y - 13
            for ox, oy in ((-14, 2), (-4, -3), (8, 1), (16, -2)):
                piece = [(x + ox, y + oy), (x + ox + 7, y + oy - 5), (x + ox + 10, y + oy + 3)]
                pygame.draw.polygon(surface, (184, 227, 232), piece)
                pygame.draw.polygon(surface, (91, 151, 160), piece, 1)

class BrushProjectile(PencilProjectile):
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        r = self.rect.move(-camera_x, 0)
        if r.right < -120 or r.left > SCREEN_W + 120:
            return

        bristle = [
            (r.left, r.centery),
            (r.left + 15, r.top),
            (r.left + 20, r.bottom),
        ]
        pygame.draw.polygon(surface, (224, 64, 91), bristle)
        pygame.draw.polygon(surface, INK, bristle, 1)
        pygame.draw.line(surface, (255, 145, 158), (r.left + 4, r.centery), (r.left + 16, r.top + 2), 2)

        ferrule = pygame.Rect(r.left + 17, r.y, 13, r.h)
        pygame.draw.rect(surface, (186, 193, 202), ferrule, border_radius=2)
        pygame.draw.rect(surface, (93, 103, 116), ferrule, 1, border_radius=2)

        handle = pygame.Rect(r.left + 28, r.y + 1, r.w - 30, max(5, r.h - 2))
        pygame.draw.rect(surface, (205, 157, 96), handle, border_radius=3)
        pygame.draw.line(surface, (242, 196, 130), (handle.x + 3, handle.y + 1), (handle.right - 2, handle.y + 1), 1)
        pygame.draw.rect(surface, (118, 75, 57), handle, 1, border_radius=3)

class RedPaintTrap:
    def __init__(self, x, floor_y, width=86):
        self.x = x
        self.floor_y = floor_y
        self.width = width
        self.default_timer = 0.54
        self.timer = self.default_timer
        self.splash_timer = 0.0

    @property
    def splash_rect(self):
        return pygame.Rect(self.x - 10, self.floor_y - 82, self.width + 20, 88)

    def update(self, dt, player):
        self.splash_timer = max(0.0, self.splash_timer - dt)
        overlap = player.rect.right > self.x and player.rect.left < self.x + self.width
        on_floor = player.on_ground and abs(player.rect.bottom - self.floor_y) <= 3

        if self.splash_timer > 0 and self.splash_rect.colliderect(player.rect):
            return True

        if overlap and on_floor:
            self.timer -= dt
            if self.timer <= 0:
                self.splash_timer = 0.30
                self.timer = self.default_timer
                return self.splash_rect.colliderect(player.rect)
        elif self.splash_timer <= 0:
            self.timer = self.default_timer
        return False

    def draw(self, surface, camera_x):
        x = round(self.x - camera_x)
        y = self.floor_y
        if x > SCREEN_W + 120 or x + self.width < -120:
            return

        tube_y = y - 23
        left = x + 4
        right = x + self.width - 18
        top = tube_y
        bottom = tube_y + 18

        pressed = self.timer < self.default_timer and self.splash_timer <= 0
        press = 4 if pressed else 0
        top += press
        bottom -= press // 2

        shadow = [
            (left + 3, top + 5),
            (right + 3, top + 7),
            (right + 3, bottom + 4),
            (left + 3, bottom + 4),
        ]
        pygame.draw.polygon(surface, (113, 71, 72), shadow)

        tail = [
            (left, top + 2),
            (left + 13, top),
            (left + 15, bottom),
            (left, bottom - 2),
        ]
        pygame.draw.polygon(surface, (190, 183, 171), tail)
        pygame.draw.polygon(surface, INK, tail, 1)
        for offset in (4, 8, 12):
            pygame.draw.line(surface, (122, 116, 112), (left + offset, top + 2), (left + offset, bottom - 2), 1)

        body = [
            (left + 13, top),
            (right - 7, top + 3),
            (right, top + 7),
            (right, bottom - 5),
            (right - 7, bottom - 1),
            (left + 13, bottom),
        ]
        pygame.draw.polygon(surface, (239, 232, 216), body)
        pygame.draw.polygon(surface, INK, body, 2)

        label = [
            (left + 22, top + 4),
            (right - 13, top + 6),
            (right - 13, bottom - 6),
            (left + 22, bottom - 4),
        ]
        pygame.draw.polygon(surface, (219, 70, 88), label)
        pygame.draw.line(surface, (255, 157, 168), (left + 27, top + 6), (right - 17, top + 8), 2)

        neck = pygame.Rect(right - 1, top + 6, 9, max(6, bottom - top - 11))
        cap = pygame.Rect(right + 7, top + 4, 11, max(9, bottom - top - 7))
        pygame.draw.rect(surface, (216, 211, 201), neck, border_radius=2)
        pygame.draw.rect(surface, INK, neck, 1, border_radius=2)
        pygame.draw.rect(surface, (133, 137, 145), cap, border_radius=3)
        pygame.draw.rect(surface, INK, cap, 1, border_radius=3)
        for line_x in range(cap.x + 3, cap.right - 1, 3):
            pygame.draw.line(surface, (91, 95, 104), (line_x, cap.y + 2), (line_x, cap.bottom - 2), 1)

        if pressed:
            pygame.draw.line(surface, (255, 181, 190), (left + 24, (top + bottom) // 2), (right - 16, (top + bottom) // 2), 2)

        if self.splash_timer > 0:
            nozzle_x = right + 15
            progress = 1.0 - self.splash_timer / 0.30
            rise = round(24 + math.sin(progress * math.pi) * 55)
            pygame.draw.line(surface, (225, 67, 88), (nozzle_x, y - 13), (nozzle_x - 5, y - rise), 10)
            pygame.draw.circle(surface, (245, 99, 116), (nozzle_x - 5, y - rise), 15)
            for dx, dy, radius in ((-28, -8, 7), (24, -18, 6), (-18, -35, 5), (31, -43, 5)):
                pygame.draw.circle(surface, (232, 78, 97), (nozzle_x - 5 + dx, y - rise + dy), radius)

class FloatingPaletteItem(FloatingBookItem):
    POWER_ATTR = "has_art_power"

    def draw(self, surface, camera_x):
        if self.collected:
            return
        r = self.rect.move(-camera_x, 0)
        if r.right < -100 or r.left > SCREEN_W + 100:
            return

        glow = pygame.Surface((72, 72), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 222, 153, 45), (36, 36), 29)
        surface.blit(glow, (r.centerx - 36, r.centery - 36))

        pygame.draw.ellipse(surface, (220, 178, 119), (r.x + 2, r.y + 4, 27, 21))
        pygame.draw.ellipse(surface, INK, (r.x + 2, r.y + 4, 27, 21), 2)
        pygame.draw.circle(surface, (245, 238, 218), (r.x + 22, r.y + 10), 4)
        for color, ox, oy in (
            ((229, 78, 99), 8, 10),
            ((245, 179, 64), 14, 8),
            ((89, 151, 218), 11, 17),
            ((113, 187, 124), 18, 17),
        ):
            pygame.draw.circle(surface, color, (r.x + ox, r.y + oy), 3)

class PaletteQuestionBlock(AcademicQuestionBlock):
    ITEM_CLASS = FloatingPaletteItem

class PaintShot:
    COLORS = ((232, 84, 104), (244, 181, 69), (86, 155, 220), (116, 190, 128), (178, 108, 205))

    def __init__(self, x, y, facing):
        self.pos = pygame.Vector2(x, y)
        self.start_x = float(x)
        self.facing = facing
        self.speed = 470.0
        self.max_distance = 310
        self.radius = 8
        self.color = random.choice(self.COLORS)
        self.active = True

    @property
    def rect(self):
        return pygame.Rect(round(self.pos.x - self.radius), round(self.pos.y - self.radius), self.radius * 2, self.radius * 2)

    def update(self, dt):
        self.pos.x += self.facing * self.speed * dt
        if abs(self.pos.x - self.start_x) >= self.max_distance:
            self.active = False

    def draw(self, surface, camera_x):
        if not self.active:
            return
        x = round(self.pos.x - camera_x)
        y = round(self.pos.y)
        pygame.draw.circle(surface, self.color, (x, y), self.radius)
        pygame.draw.circle(surface, INK, (x, y), self.radius, 1)
        pygame.draw.line(surface, self.color, (x - self.facing * 18, y), (x - self.facing * 5, y), 5)

class PaintCanvas:
    def __init__(self, x, y, width=82):
        self.rect = pygame.Rect(x, y, width, 14)
        self.timer = 0.0
        self.color = (245, 242, 232)

    @property
    def active(self):
        return self.timer > 0

    def activate(self, color):
        self.color = color
        self.timer = 2.4

    def update(self, dt):
        self.timer = max(0.0, self.timer - dt)

    def draw(self, surface, camera_x):
        r = self.rect.move(-camera_x, 0)
        if self.active:
            pygame.draw.rect(surface, self.color, r, border_radius=4)
            pygame.draw.rect(surface, INK, r, 2, border_radius=4)
            pygame.draw.circle(surface, (255, 255, 245), (r.x + 15, r.centery), 4)
            pygame.draw.circle(surface, self.color, (r.right - 17, r.centery), 6)
        else:
            pygame.draw.rect(surface, (247, 244, 235), r, 2, border_radius=4)
            pygame.draw.line(surface, (184, 174, 166), (r.x + 8, r.centery), (r.right - 8, r.centery), 1)

class FlyingPalette(FlyingEraser):
    def handle_player_contact(self, player):
        death = super().handle_player_contact(player)
        return "palette" if death else None

    def draw(self, surface, camera_x):
        if not self.active:
            return
        r = self.rect.move(-camera_x, 0)
        if r.right < -100 or r.left > SCREEN_W + 100:
            return
        if self.state == "warning":
            pygame.draw.line(surface, (225, 85, 104), (r.centerx, r.bottom + 3), (r.centerx, r.bottom + 18), 3)
        pygame.draw.ellipse(surface, (214, 174, 117), r)
        pygame.draw.ellipse(surface, INK, r, 2)
        pygame.draw.circle(surface, (246, 239, 220), (r.right - 10, r.y + 7), 4)
        for color, ox, oy in (((232, 84, 104), 9, 7), ((244, 181, 69), 18, 6),
                              ((86, 155, 220), 13, 14), ((116, 190, 128), 25, 13)):
            pygame.draw.circle(surface, color, (r.x + ox, r.y + oy), 3)

class CodeProjectile(PencilProjectile):
    CODES = ("int i=0;", "for(i=0;i<n;i++)", "if(x==null)", "return 0;", "System.out.println();")
    FONT = None

    def __init__(self, x, y, speed):
        super().__init__(x, y, speed)
        self.code = random.choice(self.CODES)
        self.width, self.height = 138, 16

    def draw(self, surface, camera_x):
        r = self.rect.move(-camera_x, 0)
        if r.right < -160 or r.left > SCREEN_W + 160:
            return
        if CodeProjectile.FONT is None:
            CodeProjectile.FONT = pygame.font.SysFont("consolas", 14, bold=True)

        glow = pygame.Surface((r.w + 12, r.h + 12), pygame.SRCALPHA)
        pygame.draw.rect(glow, (52, 255, 139, 42), (0, 0, glow.get_width(), glow.get_height()), border_radius=7)
        surface.blit(glow, (r.x - 6, r.y - 6))

        pygame.draw.rect(surface, (2, 8, 10), r.move(3, 4), border_radius=4)
        pygame.draw.rect(surface, (7, 24, 24), r, border_radius=4)
        pygame.draw.rect(surface, (84, 255, 151), r, 2, border_radius=4)
        pygame.draw.polygon(surface, (255, 112, 91), [(r.x - 7, r.centery), (r.x + 3, r.y + 2), (r.x + 3, r.bottom - 2)])
        surface.blit(CodeProjectile.FONT.render(self.code, True, (144, 255, 183)), (r.x + 8, r.y - 1))

class ErrorCodePlatform(PaperPlatform):
    def draw(self, surface, camera_x):
        if not self.active:
            return
        r = self.rect.move(-camera_x, 0)
        color = (224, 67, 76) if self.state != "idle" else (48, 225, 119)
        pygame.draw.rect(surface, (4, 15, 18), r.move(3, 4), border_radius=3)
        pygame.draw.rect(surface, (9, 26, 29), r, border_radius=3)
        pygame.draw.rect(surface, color, r, 2, border_radius=3)
        pygame.draw.line(surface, color, (r.x + 7, r.centery), (r.right - 7, r.centery), 2)

class RmRfTrap:
    def __init__(self, x, floor_y, width=90):
        self.x, self.floor_y, self.width = x, floor_y, width
        self.default_timer = self.timer = 0.62

    def update(self, dt, player, debugging):
        if debugging:
            self.timer = self.default_timer
            return False
        overlap = player.rect.right > self.x and player.rect.left < self.x + self.width
        on_floor = player.on_ground and abs(player.rect.bottom - self.floor_y) <= 3
        self.timer = self.timer - dt if overlap and on_floor else self.default_timer
        return self.timer <= 0

    def draw(self, surface, camera_x):
        x, y = round(self.x - camera_x), self.floor_y - 20
        pygame.draw.rect(surface, (3, 12, 15), (x, y, self.width, 18), border_radius=3)
        color = (239, 73, 84) if self.timer < self.default_timer else (65, 231, 130)
        pygame.draw.rect(surface, color, (x, y, self.width, 18), 2, border_radius=3)
        font = pygame.font.SysFont("consolas", 14, bold=True)
        surface.blit(font.render("rm -rf /", True, color), (x + 7, y + 1))

class FloatingLaptopItem(FloatingBookItem):
    POWER_ATTR = "has_debug_power"

    def draw(self, surface, camera_x):
        if self.collected:
            return
        r = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, (18, 34, 42), (r.x + 2, r.y, 26, 17), border_radius=2)
        pygame.draw.rect(surface, (63, 239, 132), (r.x + 5, r.y + 3, 20, 10), 2)
        pygame.draw.polygon(surface, (121, 139, 145), [(r.x, r.y + 18), (r.right, r.y + 18), (r.right + 4, r.y + 22), (r.x - 4, r.y + 22)])

class LaptopQuestionBlock(AcademicQuestionBlock):
    ITEM_CLASS = FloatingLaptopItem

class PressMachine(FlyingEraser):
    def handle_player_contact(self, player):
        return "press" if super().handle_player_contact(player) else None

    def draw(self, surface, camera_x):
        if not self.active:
            return
        r = self.rect.move(-camera_x, 0)
        if self.state == "warning":
            pygame.draw.line(surface, (242, 87, 79), (r.centerx, r.bottom), (r.centerx, r.bottom + 20), 4)
        pygame.draw.rect(surface, (56, 59, 63), r.move(3, 4))
        pygame.draw.rect(surface, (132, 138, 143), r)
        pygame.draw.rect(surface, (44, 47, 50), r, 2)
        pygame.draw.rect(surface, (188, 140, 63), (r.x + 6, r.bottom - 6, r.w - 12, 5))

class BoltDrop(FallingGlassShard):
    def update(self, dt, player):
        return "bolt" if super().update(dt, player) else None

    def draw(self, surface, camera_x):
        if self.state == "waiting":
            return
        x = round(self.x - camera_x)
        if self.state == "warning":
            pygame.draw.line(surface, (231, 92, 76), (x, 42), (x, 82), 3)
            return
        r = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, (121, 126, 132), (r.centerx - 4, r.y, 8, 27))
        pygame.draw.rect(surface, (59, 63, 68), (r.centerx - 4, r.y, 8, 27), 2)
        pygame.draw.circle(surface, (156, 161, 166), (r.centerx, r.bottom - 5), 9)
        pygame.draw.circle(surface, (59, 63, 68), (r.centerx, r.bottom - 5), 9, 2)

class SpikeTrap:
    def __init__(self, x, floor_y, width=76):
        self.rect = pygame.Rect(x, floor_y - 22, width, 22)

    def draw(self, surface, camera_x):
        r = self.rect.move(-camera_x, 0)
        for x in range(r.left, r.right, 16):
            pygame.draw.polygon(surface, (164, 169, 174), [(x, r.bottom), (x + 8, r.top), (x + 16, r.bottom)])
            pygame.draw.polygon(surface, (45, 48, 51), [(x, r.bottom), (x + 8, r.top), (x + 16, r.bottom)], 1)

class FloatingRobotItem(FloatingBookItem):
    POWER_ATTR = "has_robot_power"

    def draw(self, surface, camera_x):
        if self.collected:
            return
        r = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, (83, 91, 99), (r.x + 3, r.y + 5, 24, 15), border_radius=3)
        pygame.draw.circle(surface, (44, 47, 50), (r.x + 8, r.bottom), 5)
        pygame.draw.circle(surface, (44, 47, 50), (r.right - 8, r.bottom), 5)
        pygame.draw.circle(surface, (106, 232, 151), (r.x + 10, r.y + 11), 3)

class RobotQuestionBlock(AcademicQuestionBlock):
    ITEM_CLASS = FloatingRobotItem

class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.width = 28
        self.height = 42
        self.crouch_height = 29
        self.hitbox_height = self.height
        self.facing = 1
        self.on_ground = False
        self.coyote = 0
        self.jump_buffer = 0
        self.pose = "idle"
        self.anim_t = 0
        self.costume = 0

        self.has_book_power = False
        self.has_lab_power = False
        self.has_art_power = False
        self.has_debug_power = False
        self.has_robot_power = False

        self.stomp_active = False
        self.stomp_windup = 0.0
        self.stomp_impact_timer = 0.0
        self.down_was_pressed = False

        self.crouch_amount = 0.0
        self.look_up_amount = 0.0

    @property
    def rect(self):
        return pygame.Rect(round(self.pos.x), round(self.pos.y), self.width, self.hitbox_height)

    def set_costume(self, costume):
        self.costume = costume

    def book_guard_rect(self):
        r = self.rect
        guard_h = max(34, r.h + 12)
        guard_y = r.centery - guard_h // 2
        if self.facing > 0:
            return pygame.Rect(r.right - 2, guard_y, 43, guard_h)
        return pygame.Rect(r.left - 41, guard_y, 43, guard_h)

    def _draw_academic_power(self, surface, x, body_rect):
        if not self.has_book_power:
            return

        cap_center_x = x + self.width // 2 - self.facing * 1
        cap_y = body_rect.y - 37
        cap_points = [
            (cap_center_x, cap_y - 5),
            (cap_center_x + 17, cap_y + 1),
            (cap_center_x, cap_y + 7),
            (cap_center_x - 17, cap_y + 1),
        ]
        pygame.draw.polygon(surface, (50, 62, 96), cap_points)
        pygame.draw.lines(surface, INK, True, cap_points, 2)
        pygame.draw.rect(surface, (50, 62, 96), (cap_center_x - 10, cap_y + 5, 20, 6), border_radius=2)
        pygame.draw.rect(surface, INK, (cap_center_x - 10, cap_y + 5, 20, 6), 1, border_radius=2)
        tassel_x = cap_center_x + self.facing * 15
        pygame.draw.line(surface, (245, 197, 70), (cap_center_x, cap_y + 1), (tassel_x, cap_y + 12), 2)
        pygame.draw.circle(surface, (245, 197, 70), (tassel_x, cap_y + 14), 3)

        book_w, book_h = 34, 21
        if self.facing > 0:
            bx = x + self.width + 2
        else:
            bx = x - book_w - 2
        by = body_rect.centery - 6

        glow = pygame.Surface((book_w + 22, book_h + 22), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 228, 105, 46), (0, 0, book_w + 22, book_h + 22))
        surface.blit(glow, (bx - 11, by - 11))

        center_x = bx + book_w // 2
        top = by + 2
        bottom = by + book_h - 2
        left_page = [(center_x, top + 4), (bx + 2, top), (bx + 4, bottom), (center_x - 1, bottom - 3)]
        right_page = [(center_x, top + 4), (bx + book_w - 2, top), (bx + book_w - 4, bottom), (center_x + 1, bottom - 3)]

        pygame.draw.polygon(surface, (255, 242, 194), left_page)
        pygame.draw.polygon(surface, (255, 250, 218), right_page)
        pygame.draw.lines(surface, INK, True, left_page, 2)
        pygame.draw.lines(surface, INK, True, right_page, 2)
        pygame.draw.line(surface, (181, 132, 81), (center_x, top + 4), (center_x, bottom - 3), 2)

        front_x = bx + book_w + 7 if self.facing > 0 else bx - 7
        pygame.draw.line(surface, (255, 225, 93), (front_x, by + 2), (front_x, by + book_h - 2), 2)
        pygame.draw.line(surface, (255, 238, 153), (front_x + self.facing * 7, by + 6), (front_x + self.facing * 7, by + book_h - 6), 1)

    def _draw_lab_coat(self, surface, x, body_rect):
        if not self.has_lab_power:
            return

        coat = pygame.Rect(body_rect.x - 3, body_rect.y + 6, body_rect.w + 6, max(14, body_rect.h - 2))
        pygame.draw.ellipse(surface, (242, 248, 246), coat)
        pygame.draw.ellipse(surface, (91, 125, 139), coat, 2)
        pygame.draw.line(surface, (151, 177, 181), (coat.centerx, coat.y + 3), (coat.centerx, coat.bottom - 3), 1)
        pygame.draw.circle(surface, (91, 125, 139), (coat.centerx + 4, coat.y + 9), 2)
        pygame.draw.circle(surface, (91, 125, 139), (coat.centerx + 4, coat.y + 16), 2)

        fx = x + self.width + 2 if self.facing > 0 else x - 12
        fy = coat.centery - 4
        pygame.draw.rect(surface, (91, 125, 139), (fx + 4, fy - 8, 4, 8))
        pygame.draw.polygon(surface, (231, 239, 240), [(fx + 2, fy - 1), (fx + 10, fy - 1), (fx + 12, fy + 10), (fx, fy + 10)])
        pygame.draw.polygon(surface, (157, 101, 201), [(fx + 1, fy + 5), (fx + 11, fy + 5), (fx + 12, fy + 10), (fx, fy + 10)])
        pygame.draw.polygon(surface, (91, 125, 139), [(fx + 2, fy - 1), (fx + 10, fy - 1), (fx + 12, fy + 10), (fx, fy + 10)], 1)

    def _draw_art_power(self, surface, x, body_rect):
        if not self.has_art_power:
            return

        palette_x = x - 17 if self.facing < 0 else x + self.width + 2
        palette_y = body_rect.centery - 6
        pygame.draw.ellipse(surface, (217, 177, 122), (palette_x, palette_y, 18, 15))
        pygame.draw.ellipse(surface, (102, 76, 68), (palette_x, palette_y, 18, 15), 2)
        pygame.draw.circle(surface, (245, 238, 216), (palette_x + 12, palette_y + 5), 3)
        for color, ox, oy in (
            ((226, 82, 101), 4, 4),
            ((244, 179, 62), 7, 9),
            ((89, 154, 218), 12, 10),
            ((114, 188, 125), 5, 11),
        ):
            pygame.draw.circle(surface, color, (palette_x + ox, palette_y + oy), 2)

        brush_x = x + self.width + 10 if self.facing > 0 else x - 10
        brush_y = body_rect.centery - 10
        tip_x = brush_x + self.facing * 16
        pygame.draw.line(surface, (118, 77, 55), (brush_x, brush_y), (tip_x, brush_y - 5), 4)
        pygame.draw.line(surface, (188, 135, 84), (brush_x, brush_y), (tip_x, brush_y - 5), 2)
        pygame.draw.circle(surface, (232, 87, 118), (tip_x, brush_y - 5), 4)

    def _draw_debug_power(self, surface, x, body_rect):
        if not self.has_debug_power:
            return
        lx = x + self.width + 2 if self.facing > 0 else x - 22
        ly = body_rect.centery - 8
        pygame.draw.rect(surface, (17, 34, 43), (lx, ly, 20, 14), border_radius=2)
        pygame.draw.rect(surface, (61, 235, 130), (lx + 3, ly + 3, 14, 7), 1)
        pygame.draw.line(surface, (150, 164, 168), (lx - 2, ly + 15), (lx + 22, ly + 15), 3)

    def _draw_robot_power(self, surface, x, body_rect):
        if not self.has_robot_power:
            return
        y = body_rect.bottom - 4
        pygame.draw.rect(surface, (83, 91, 99), (x - 5, y, self.width + 10, 13), border_radius=4)
        pygame.draw.circle(surface, (44, 47, 50), (x + 3, y + 13), 5)
        pygame.draw.circle(surface, (44, 47, 50), (x + self.width - 3, y + 13), 5)
        pygame.draw.circle(surface, (106, 232, 151), (x + self.width // 2, y + 6), 3)

    def set_crouch_hitbox(self, crouched, platforms):
        target_height = self.crouch_height if crouched else self.height
        if target_height == self.hitbox_height:
            return True

        old_bottom = self.rect.bottom
        candidate = pygame.Rect(
            round(self.pos.x),
            old_bottom - target_height,
            self.width,
            target_height,
        )

        if target_height > self.hitbox_height:
            for p in platforms:
                if getattr(p, "one_way", False):
                    continue
                if candidate.colliderect(p.rect):
                    return False

        self.hitbox_height = target_height
        self.pos.y = old_bottom - target_height
        return True

    def find_ground_surface(self, platforms, tolerance=3):
        rect = self.rect
        candidates = []
        for p in platforms:
            horizontal_overlap = rect.right > p.rect.left and rect.left < p.rect.right
            gap = p.rect.top - rect.bottom
            if horizontal_overlap and -1 <= gap <= tolerance:
                candidates.append(p.rect.top)
        return min(candidates) if candidates else None

    def finish_stomp(self):
        if not self.stomp_active:
            return
        self.stomp_active = False
        self.stomp_windup = 0.0
        self.stomp_impact_timer = 0.20
        self.vel.x *= 0.62

    def update(self, dt, keys, platforms):
        crouch_key = bool(keys[pygame.K_DOWN])
        look_up_key = bool(keys[pygame.K_UP])
        left = bool(keys[pygame.K_LEFT])
        right = bool(keys[pygame.K_RIGHT])
        jump = bool(keys[pygame.K_SPACE])
        down_pressed = crouch_key and not self.down_was_pressed
        self.down_was_pressed = crouch_key
        self.stomp_impact_timer = max(0.0, self.stomp_impact_timer - dt)

        support_y = self.find_ground_surface(platforms)
        if self.vel.y >= 0 and support_y is not None:
            self.pos.y = support_y - self.hitbox_height
            self.vel.y = 0
            self.on_ground = True
            self.finish_stomp()

        if crouch_key and self.on_ground:
            self.set_crouch_hitbox(True, platforms)
        elif self.hitbox_height < self.height:
            self.set_crouch_hitbox(False, platforms)

        crouching_now = self.hitbox_height < self.height

        if down_pressed and not self.on_ground and not self.stomp_active:
            self.stomp_active = True
            self.stomp_windup = 0.09
            self.vel.x *= 0.45
            self.vel.y = 0
            self.jump_buffer = 0

        accel = 1700 if crouching_now else 2500
        max_speed = (130 if crouching_now else 245) * (1.35 if self.has_robot_power else 1)
        friction = 0.78 if self.on_ground else 0.95
        gravity = 1700
        jump_speed = -610

        if jump:
            self.jump_buffer = 0.11
        else:
            self.jump_buffer = max(0, self.jump_buffer - dt)
        if self.stomp_active:

            self.jump_buffer = 0

        if self.stomp_active:

            self.vel.x *= 0.94
            self.vel.x = nspeed(self.vel.x, -82, 82)
        else:
            if left:
                self.vel.x -= accel * dt
                self.facing = -1
            if right:
                self.vel.x += accel * dt
                self.facing = 1
            if not left and not right:
                self.vel.x *= friction
                if abs(self.vel.x) < 8:
                    self.vel.x = 0
            self.vel.x = nspeed(self.vel.x, -max_speed, max_speed)

        self.coyote = 0.09 if self.on_ground else max(0, self.coyote - dt)
        if self.jump_buffer > 0 and self.coyote > 0 and not crouching_now:
            self.vel.y = jump_speed
            self.on_ground = False
            self.coyote = 0
            self.jump_buffer = 0
        if self.stomp_active:
            if self.stomp_windup > 0:

                self.stomp_windup = max(0.0, self.stomp_windup - dt)
                self.vel.y = 0
            else:
                self.vel.y = 980
        else:
            if not jump and self.vel.y < -90:
                self.vel.y += gravity * 0.85 * dt
            self.vel.y = nspeed(self.vel.y + gravity * dt, -900, 900)

        self.pos.x += self.vel.x * dt
        rect = self.rect
        for p in platforms:
            if getattr(p, "one_way", False):
                continue
            if rect.colliderect(p.rect):
                if self.vel.x > 0:
                    rect.right = p.rect.left
                elif self.vel.x < 0:
                    rect.left = p.rect.right
                self.pos.x = rect.x
                self.vel.x = 0

        if self.pos.x < 0:
            self.pos.x = 0
            if self.vel.x < 0:
                self.vel.x = 0

        previous_rect = self.rect
        self.pos.y += self.vel.y * dt
        rect = self.rect
        self.on_ground = False
        for p in platforms:
            horizontal_overlap = rect.right > p.rect.left and rect.left < p.rect.right
            if not horizontal_overlap:
                continue

            if self.vel.y >= 0 and previous_rect.bottom <= p.rect.top and rect.bottom >= p.rect.top:
                rect.bottom = p.rect.top
                self.pos.y = rect.y
                self.vel.y = 0
                self.on_ground = True
                self.finish_stomp()
                break
            if (
                self.vel.y < 0
                and not getattr(p, "one_way", False)
                and previous_rect.top >= p.rect.bottom
                and rect.top <= p.rect.bottom
            ):
                rect.top = p.rect.bottom
                self.pos.y = rect.y
                self.vel.y = 0
                break

        if self.vel.y >= 0:
            support_y = self.find_ground_surface(platforms)
            if support_y is not None:
                self.pos.y = support_y - self.hitbox_height
                self.vel.y = 0
                self.on_ground = True
                self.finish_stomp()

        held_crouch = self.hitbox_height < self.height and self.on_ground
        held_look_up = look_up_key and self.on_ground and not held_crouch

        if self.stomp_active:
            self.pose = "stomp"
        elif held_crouch:
            self.pose = "crawl" if (left or right) else "crouch"
        elif held_look_up:
            self.pose = "look_up"
        elif not self.on_ground:
            self.pose = "jump"
        elif abs(self.vel.x) > 18:
            self.pose = "run"
        else:
            self.pose = "idle"

        self.crouch_amount = approach(self.crouch_amount, 1.0 if held_crouch else 0.0, 12.0 * dt)
        self.look_up_amount = approach(self.look_up_amount, 1.0 if held_look_up else 0.0, 10.0 * dt)
        self.anim_t += dt

    def colors(self):
        palettes = [
            {
                "body": (154, 211, 239),
                "body_shadow": (112, 178, 215),
                "belly": (219, 242, 252),
                "antler": (184, 225, 245),
                "shell": (45, 151, 101),
                "shell_dark": (26, 111, 79),
                "cap": (230, 142, 99),
                "cap_dark": (154, 88, 72),
            },
            {
                "body": (242, 162, 171),
                "body_shadow": (211, 111, 129),
                "belly": (255, 225, 227),
                "antler": (255, 211, 218),
                "shell": (126, 89, 191),
                "shell_dark": (83, 59, 143),
                "cap": (247, 179, 91),
                "cap_dark": (181, 111, 61),
            },
            {
                "body": (157, 214, 165),
                "body_shadow": (104, 172, 118),
                "belly": (224, 245, 224),
                "antler": (207, 239, 208),
                "shell": (53, 133, 202),
                "shell_dark": (32, 91, 158),
                "cap": (225, 148, 103),
                "cap_dark": (151, 91, 73),
            },
        ]
        return palettes[self.costume]

    def _draw_shell(self, surface, center, facing, palette, crouch_amount=0.0):
        cx, cy = center
        shell_w = 18
        shell_h = max(17, round(24 - 5 * crouch_amount))
        shell_x = round(cx - shell_w / 2 - facing * 6)
        shell_y = round(cy - shell_h / 2)
        rect = pygame.Rect(shell_x, shell_y, shell_w, shell_h)
        pygame.draw.ellipse(surface, palette["shell_dark"], rect.inflate(4, 4))
        pygame.draw.ellipse(surface, palette["shell"], rect)

        stripe = (235, 249, 246)
        if facing > 0:
            pygame.draw.arc(surface, stripe, rect.inflate(-2, -1), -1.15, 1.15, 2)
            pygame.draw.arc(surface, stripe, rect.inflate(-7, -3), -1.15, 1.15, 2)
        else:
            pygame.draw.arc(surface, stripe, rect.inflate(-2, -1), math.pi - 1.15, math.pi + 1.15, 2)
            pygame.draw.arc(surface, stripe, rect.inflate(-7, -3), math.pi - 1.15, math.pi + 1.15, 2)
        pygame.draw.ellipse(surface, INK, rect.inflate(3, 3), 2)

    def _make_side_head(self, facing, palette):
        head = pygame.Surface((72, 68), pygame.SRCALPHA)

        face_points = [
            (16, 24), (19, 18), (25, 14), (34, 12), (43, 13),
            (51, 17), (56, 22), (59, 29), (60, 35), (60, 42),
            (58, 48), (55, 53), (50, 57), (43, 60), (34, 60),
            (26, 58), (20, 54), (16, 49), (14, 42), (14, 33),
        ]
        pygame.draw.polygon(head, palette["body"], face_points)
        pygame.draw.lines(head, INK, True, face_points, 2)

        antler = palette["antler"]
        pygame.draw.line(head, INK, (25, 21), (18, 8), 5)
        pygame.draw.line(head, antler, (25, 21), (18, 8), 3)
        pygame.draw.line(head, INK, (19, 11), (11, 7), 5)
        pygame.draw.line(head, antler, (19, 11), (11, 7), 3)
        pygame.draw.line(head, INK, (19, 12), (15, 2), 5)
        pygame.draw.line(head, antler, (19, 12), (15, 2), 3)

        pygame.draw.line(head, INK, (43, 20), (49, 8), 5)
        pygame.draw.line(head, antler, (43, 20), (49, 8), 3)
        pygame.draw.line(head, INK, (48, 11), (56, 6), 5)
        pygame.draw.line(head, antler, (48, 11), (56, 6), 3)
        pygame.draw.line(head, INK, (48, 12), (52, 2), 5)
        pygame.draw.line(head, antler, (48, 12), (52, 2), 3)

        cap_rect = pygame.Rect(26, 12, 18, 9)
        pygame.draw.ellipse(head, palette["cap_dark"], cap_rect.inflate(3, 2))
        pygame.draw.ellipse(head, palette["cap"], cap_rect)
        pygame.draw.line(head, (252, 208, 156), (28, 16), (42, 16), 2)
        pygame.draw.arc(head, INK, cap_rect.inflate(2, 1), math.pi, math.tau, 1)

        eye_rect = pygame.Rect(45, 27, 8, 12)
        pygame.draw.ellipse(head, (25, 78, 145), eye_rect)
        pygame.draw.ellipse(head, (18, 58, 116), eye_rect, 1)
        pygame.draw.ellipse(head, WHITE, (47, 28, 3, 4))
        pygame.draw.circle(head, (174, 223, 255), (51, 36), 1)

        pygame.draw.circle(head, (250, 166, 172), (42, 44), 5)
        pygame.draw.lines(
            head,
            INK,
            False,
            [(48, 43), (51, 46), (54, 43), (57, 46), (60, 43)],
            2,
        )

        if facing < 0:
            head = pygame.transform.flip(head, True, False)
        return head

    def draw(self, surface, camera_x):
        x = int(self.pos.x - camera_x)
        y = int(self.pos.y)
        palette = self.colors()

        run_cycle = math.sin(self.anim_t * 11)
        crawl_cycle = math.sin(self.anim_t * 8)
        crouch_amount = self.crouch_amount
        look_up_amount = self.look_up_amount
        stomping = self.pose == "stomp"

        feet_y = y + self.hitbox_height
        body_h = round(24 - 7 * crouch_amount - (3 if stomping else 0))
        body_w = round(19 + 8 * crouch_amount + (5 if stomping else 0))
        body_center_x = x + self.width // 2
        body_y = feet_y - body_h - 4
        body_rect = pygame.Rect(body_center_x - body_w // 2, body_y, body_w, body_h)

        tail_y = body_rect.y + body_rect.h - 8
        if self.facing > 0:
            tail = [(body_rect.x + 2, tail_y), (body_rect.x - 11, tail_y + 3), (body_rect.x + 2, tail_y + 8)]
        else:
            tail = [(body_rect.right - 2, tail_y), (body_rect.right + 11, tail_y + 3), (body_rect.right - 2, tail_y + 8)]
        pygame.draw.polygon(surface, palette["body_shadow"], tail)
        pygame.draw.lines(surface, INK, True, tail, 2)

        shell_center = (
            body_rect.centerx - self.facing * 7,
            body_rect.centery + round(1 + 2 * crouch_amount),
        )
        self._draw_shell(surface, shell_center, self.facing, palette, crouch_amount)

        pygame.draw.ellipse(surface, palette["body"], body_rect)
        pygame.draw.ellipse(surface, INK, body_rect, 2)
        belly_rect = pygame.Rect(
            body_rect.centerx - max(3, body_w // 5),
            body_rect.y + 7,
            max(6, body_w // 3),
            max(8, body_h - 10),
        )
        pygame.draw.ellipse(surface, palette["belly"], belly_rect)

        arm_swing = round(run_cycle * 2) if self.pose == "run" else 0
        arm_y = body_rect.y + 8
        rear_arm = pygame.Rect(body_rect.x - 4, arm_y - arm_swing, 7, 13)
        front_arm = pygame.Rect(body_rect.right - 3, arm_y + arm_swing, 7, 13)
        pygame.draw.ellipse(surface, palette["body"], rear_arm)
        pygame.draw.ellipse(surface, INK, rear_arm, 1)
        pygame.draw.ellipse(surface, palette["body"], front_arm)
        pygame.draw.ellipse(surface, INK, front_arm, 1)

        head_sprite = self._make_side_head(self.facing, palette)

        head_scale = 0.82
        head_sprite = pygame.transform.scale(
            head_sprite,
            (
                max(1, round(head_sprite.get_width() * head_scale)),
                max(1, round(head_sprite.get_height() * head_scale)),
            ),
        )
        head_center = pygame.Vector2(
            body_rect.centerx + self.facing * (4 + round(8 * crouch_amount)),
            body_rect.y - 7 + round(6 * crouch_amount),
        )
        head_center.x -= self.facing * round(2 * look_up_amount)
        head_center.y -= round(4 * look_up_amount)
        if stomping:
            head_center.y -= 3
            head_center.x -= self.facing * 2

        angle = self.facing * 25 * look_up_amount
        rotated_head = pygame.transform.rotate(head_sprite, angle)
        head_rect = rotated_head.get_rect(center=(round(head_center.x), round(head_center.y)))
        surface.blit(rotated_head, head_rect)

        leg_y = feet_y - 5
        if self.pose == "stomp":

            pygame.draw.ellipse(surface, palette["body_shadow"], (x + 4, leg_y - 5, 10, 6))
            pygame.draw.ellipse(surface, palette["body_shadow"], (x + 15, leg_y - 5, 10, 6))
            pygame.draw.ellipse(surface, INK, (x + 4, leg_y - 5, 10, 6), 1)
            pygame.draw.ellipse(surface, INK, (x + 15, leg_y - 5, 10, 6), 1)
        elif self.pose == "crawl":
            crawl = round(crawl_cycle * 3)
            left_leg = pygame.Rect(x + 3 + crawl, leg_y - 2, 12, 6)
            right_leg = pygame.Rect(x + 14 - crawl, leg_y - 2, 12, 6)
            pygame.draw.ellipse(surface, palette["body_shadow"], left_leg)
            pygame.draw.ellipse(surface, palette["body_shadow"], right_leg)
            pygame.draw.ellipse(surface, INK, left_leg, 1)
            pygame.draw.ellipse(surface, INK, right_leg, 1)
        elif crouch_amount > 0.05:
            pygame.draw.ellipse(surface, palette["body_shadow"], (x + 4, leg_y - 1, 10, 6))
            pygame.draw.ellipse(surface, palette["body_shadow"], (x + 15, leg_y - 1, 10, 6))
        else:
            step = round(run_cycle * 3) if self.pose == "run" else 0
            left_leg = pygame.Rect(x + 4 + step, leg_y, 9, 8)
            right_leg = pygame.Rect(x + 15 - step, leg_y, 9, 8)
            pygame.draw.ellipse(surface, palette["body_shadow"], left_leg)
            pygame.draw.ellipse(surface, palette["body_shadow"], right_leg)
            pygame.draw.ellipse(surface, INK, left_leg, 1)
            pygame.draw.ellipse(surface, INK, right_leg, 1)

        self._draw_lab_coat(surface, x, body_rect)
        self._draw_art_power(surface, x, body_rect)
        self._draw_debug_power(surface, x, body_rect)
        self._draw_robot_power(surface, x, body_rect)
        self._draw_academic_power(surface, x, body_rect)

        if self.stomp_impact_timer > 0:
            progress = 1.0 - self.stomp_impact_timer / 0.20
            spread = round(10 + 18 * progress)
            impact_y = feet_y - 1
            pygame.draw.arc(surface, WHITE, (x + 14 - spread, impact_y - 4, spread * 2, 10), math.pi, math.tau, 2)
            pygame.draw.line(surface, GOLD, (x + 5, impact_y - 2), (x - spread // 2, impact_y - 10), 2)
            pygame.draw.line(surface, GOLD, (x + 23, impact_y - 2), (x + 28 + spread // 2, impact_y - 10), 2)

    def draw_front(self, surface, x, y, t):
        palette = self.colors()
        phase = nspeed(t / 3.4, 0.0, 1.0)
        look_up_amount = math.sin(math.pi * phase) ** 2
        bob = round(math.sin(t * 2.0) * 2)
        head_lift = round(4 * look_up_amount)

        shell_rect = pygame.Rect(x + 30, y + 33 + bob, 22, 29)
        pygame.draw.ellipse(surface, palette["shell_dark"], shell_rect.inflate(3, 3))
        pygame.draw.ellipse(surface, palette["shell"], shell_rect)
        pygame.draw.arc(surface, (235, 249, 246), shell_rect.inflate(-3, -2), -1.1, 1.1, 2)
        pygame.draw.ellipse(surface, INK, shell_rect.inflate(3, 3), 2)

        body_rect = pygame.Rect(x + 10, y + 30 + bob, 30, 36)
        pygame.draw.ellipse(surface, palette["body"], body_rect)
        pygame.draw.ellipse(surface, INK, body_rect, 2)
        pygame.draw.ellipse(surface, palette["belly"], (body_rect.x + 10, body_rect.y + 10, 10, 20))

        pygame.draw.ellipse(surface, palette["body"], (x + 3, y + 39 + bob, 11, 17))
        pygame.draw.ellipse(surface, INK, (x + 3, y + 39 + bob, 11, 17), 1)
        pygame.draw.ellipse(surface, palette["body"], (x + 36, y + 39 + bob, 11, 17))
        pygame.draw.ellipse(surface, INK, (x + 36, y + 39 + bob, 11, 17), 1)
        pygame.draw.ellipse(surface, palette["body_shadow"], (x + 12, y + 61 + bob, 11, 9))
        pygame.draw.ellipse(surface, palette["body_shadow"], (x + 27, y + 61 + bob, 11, 9))

        head_rect = pygame.Rect(x + 3, y + 1 + bob - head_lift, 44, 42)
        pygame.draw.ellipse(surface, palette["body"], head_rect)
        pygame.draw.ellipse(surface, INK, head_rect, 2)

        for direction in (-1, 1):
            base_x = head_rect.centerx + direction * 11
            pygame.draw.line(surface, INK, (base_x, head_rect.y + 5), (base_x + direction * 6, head_rect.y - 9), 5)
            pygame.draw.line(surface, palette["antler"], (base_x, head_rect.y + 5), (base_x + direction * 6, head_rect.y - 9), 3)
            pygame.draw.line(surface, INK, (base_x + direction * 4, head_rect.y - 4), (base_x + direction * 12, head_rect.y - 8), 5)
            pygame.draw.line(surface, palette["antler"], (base_x + direction * 4, head_rect.y - 4), (base_x + direction * 12, head_rect.y - 8), 3)

        cap_rect = pygame.Rect(head_rect.centerx - 10, head_rect.y - 3, 20, 9)
        pygame.draw.ellipse(surface, palette["cap_dark"], cap_rect.inflate(3, 2))
        pygame.draw.ellipse(surface, palette["cap"], cap_rect)
        pygame.draw.line(surface, (252, 208, 156), (cap_rect.x + 2, cap_rect.y + 4), (cap_rect.right - 2, cap_rect.y + 4), 2)

        pygame.draw.ellipse(surface, (28, 76, 132), (head_rect.x + 11, head_rect.y + 17, 6, 9))
        pygame.draw.ellipse(surface, (28, 76, 132), (head_rect.right - 17, head_rect.y + 17, 6, 9))
        pygame.draw.rect(surface, WHITE, (head_rect.x + 13, head_rect.y + 18, 2, 3))
        pygame.draw.rect(surface, WHITE, (head_rect.right - 15, head_rect.y + 18, 2, 3))
        pygame.draw.circle(surface, (250, 166, 172), (head_rect.x + 8, head_rect.y + 29), 5)
        pygame.draw.circle(surface, (250, 166, 172), (head_rect.right - 8, head_rect.y + 29), 5)
        pygame.draw.arc(surface, INK, (head_rect.centerx - 6, head_rect.y + 26, 12, 9), 0.0, math.pi, 1)
