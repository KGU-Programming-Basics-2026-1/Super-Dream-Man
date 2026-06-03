import math
import random
import sys
from dataclasses import dataclass

import pygame


SCREEN_W = 960
SCREEN_H = 540
FPS = 60
TILE = 32

SKY_TOP = (116, 196, 255)
SKY_BOTTOM = (206, 238, 255)
WHITE = (248, 252, 255)
INK = (39, 45, 61)
GOLD = (255, 196, 75)
BLUE = (54, 112, 214)
GREEN = (80, 170, 96)
RED = (218, 83, 83)
PURPLE = (126, 94, 197)
STONE = (116, 130, 145)
DARK_STONE = (73, 82, 96)

#속도 제한, 몹들 못나가게
# 값이 최소값과 최대값 사이를 벗어나지 않도록 제한한다.
def nspeed(value, low, high):
    return max(low, min(high, value))


# 부드럽게 다가가기
def approach(current, target, amount):
    if current < target:
        return min(target, current + amount)
    return max(target, current - amount)


# 회전 
def rotate_point(point, center, angle_degrees):
    angle = math.radians(angle_degrees)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    px, py = point
    cx, cy = center
    dx = px - cx
    dy = py - cy
    return (
        round(cx + dx * cos_a - dy * sin_a),
        round(cy + dx * sin_a + dy * cos_a),
    )


# 그냥 글자 나오게 
def draw_text(surface, font, text, pos, color=INK, center=False):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(rendered, rect)
    return rect


# 그림자 글자
def draw_outlined_text(surface, font, text, pos, color=WHITE, outline=INK, center=False, thickness=2):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    shadow = font.render(text, True, (24, 31, 48))
    surface.blit(shadow, rect.move(3, 4))
    outline_rendered = font.render(text, True, outline)
    for ox, oy in ((-thickness, 0), (thickness, 0), (0, -thickness), (0, thickness),
                   (-thickness, -thickness), (-thickness, thickness),
                   (thickness, -thickness), (thickness, thickness)):
        surface.blit(outline_rendered, rect.move(ox, oy))
    surface.blit(rendered, rect)
    return rect


# 두 색 섞기
def blend_color(a, b, amount):
    amount = nspeed(amount, 0.0, 1.0)
    return tuple(round(a[i] * (1 - amount) + b[i] * amount) for i in range(3))


# 사각형에 테두리 선택
def draw_pixel_rect(surface, color, rect, scale=1, border=None):
    pygame.draw.rect(surface, color, rect)
    if border:
        pygame.draw.rect(surface, border, rect, max(1, scale))


# 글자 중앙 여러줄
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


# 클리어하면 별
def draw_star(surface, center, outer_radius=11, inner_radius=5, color=GOLD, border=INK):
    cx, cy = center
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = outer_radius if i % 2 == 0 else inner_radius
        points.append((round(cx + math.cos(angle) * radius), round(cy + math.sin(angle) * radius)))
    pygame.draw.polygon(surface, color, points)
    pygame.draw.lines(surface, border, True, points, 2)


# [기본 발판] 충돌 가능한 바닥과 발판 정보를 저장하고 그린다.
@dataclass
class Platform:
    rect: pygame.Rect
    color: tuple
    trim: tuple
    label: str = ""
    one_way: bool = False

    def draw(self, surface, camera_x, world_name=""):
        r = self.rect.move(-camera_x, 0)
        if r.right < -80 or r.left > SCREEN_W + 80:
            return

        if world_name == "인문대학":
            self.draw_library_platform(surface, r)
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


# [배경 장식] 화면을 천천히 이동하는 구름을 관리한다.
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


# [배경 장식] 화면을 날아가는 새를 관리한다.
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



# [인문대 장애물] 오른쪽에서 왼쪽으로 날아오는 연필을 관리한다.
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


# [인문대 장애물] 오래 밟으면 닫히는 책 함정을 관리한다.
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


# [인문대 장애물] 밟으면 흔들리다가 떨어지고 다시 생성되는 종이 발판이다.
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



# [인문대 몬스터] 공중을 순찰하다가 아래로 내려찍는 지우개다.
class FlyingEraser:

    def __init__(self, x, floor_y, patrol_width=150, hover_altitude=128):
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
                self.x = self.spawn_x
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


# [인문대 몬스터] 바닥을 왕복하며 가까이 가면 몸을 세우는 책벌레다.
class Bookworm:

    def __init__(self, min_x, max_x, floor_y, speed=58):
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
                self.x = self.min_x
                self.y = float(self.floor_y - self.low_height)
                self.direction = 1
                self.alert_amount = 0.0
                self.knocked = False
                self.knockback_vx = 0.0
                self.knockback_vy = 0.0
            return

        self.repel_cooldown = max(0.0, self.repel_cooldown - dt)
        self.phase += dt * 8

        if self.knocked:
            self.x += self.knockback_vx * dt
            supported = True if has_floor_below is None else has_floor_below(self.rect.centerx)

            if supported and self.y + self.height >= self.floor_y - 1:
                
                
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

            if supported and abs(self.knockback_vx) < 14:
                self.knocked = False
                self.knockback_vx = 0.0
                self.y = float(self.floor_y - self.height)
            return
        close = abs(player.rect.centerx - self.rect.centerx) < 118
        target = 1.0 if close else 0.0
        self.alert_amount = approach(self.alert_amount, target, 4.6 * dt)
        self.y = float(self.floor_y - self.height)

        
        move_speed = self.speed * (0.72 if self.alert_amount > 0.45 else 1.0)
        self.x += self.direction * move_speed * dt
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
        segment_color = (132, 191, 108)
        segment_shadow = (76, 136, 84)
        head_color = (157, 213, 122)

        
        body_y = r.bottom - 13
        for i, offset in enumerate((0, 11, 22)):
            sy = body_y + (wiggle if i % 2 == 0 else -wiggle)
            pygame.draw.ellipse(surface, segment_shadow, (r.x + offset + 2, sy + 3, 18, 14))
            pygame.draw.ellipse(surface, segment_color, (r.x + offset, sy, 18, 14))
            pygame.draw.ellipse(surface, INK, (r.x + offset, sy, 18, 14), 1)

        head_x = r.right - 16 if self.direction > 0 else r.x
        head_y = r.y
        pygame.draw.ellipse(surface, segment_shadow, (head_x + 2, head_y + 3, 18, 18))
        pygame.draw.ellipse(surface, head_color, (head_x, head_y, 18, 18))
        pygame.draw.ellipse(surface, INK, (head_x, head_y, 18, 18), 1)

        eye_x = head_x + (11 if self.direction > 0 else 5)
        pygame.draw.circle(surface, INK, (eye_x, head_y + 7), 2)
        pygame.draw.circle(surface, WHITE, (eye_x, head_y + 6), 1)

        
        antenna_h = 3 + round(7 * self.alert_amount)
        pygame.draw.line(surface, INK, (head_x + 6, head_y + 3), (head_x + 4, head_y - antenna_h), 1)
        pygame.draw.line(surface, INK, (head_x + 12, head_y + 3), (head_x + 14, head_y - antenna_h), 1)
        pygame.draw.circle(surface, (225, 139, 108), (head_x + 4, head_y - antenna_h), 2)
        pygame.draw.circle(surface, (225, 139, 108), (head_x + 14, head_y - antenna_h), 2)



# [강화 아이템] 공중에 떠 있는 빛나는 책 아이템이다.
class FloatingBookItem:

    def __init__(self, x, y):
        self.base_x = float(x)
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
            player.has_book_power = True
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


# [강화 아이템] 아래에서 점프로 치면 책 아이템을 생성하는 블록이다.
class AcademicQuestionBlock:

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
        self.item = FloatingBookItem(self.rect.centerx - 15, self.rect.y - 43)
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


# [인문대 관리자] 인문대학의 장애물, 몬스터, 아이템을 한꺼번에 관리한다.
class HumanitiesGimmicks:

    FLOOR_Y = SCREEN_H - 72
    WIDTH = 6000
    GAPS = (
        (900, 1210),
        (2050, 2420),
        (3330, 3730),
        (4700, 5140),
    )

    def has_floor_below(self, x):
        if x < 0 or x > self.WIDTH:
            return False
        return not any(start <= x <= end for start, end in self.GAPS)

    def __init__(self):
        self.paper_platforms = []
        self.trap_books = []
        self.pencils = []
        self.erasers = []
        self.bookworms = []
        self.power_block = None
        self.spawn_timer = 1.7
        self.reset()

    def reset(self):
        self.paper_platforms = [
            PaperPlatform(954, 414, 88), PaperPlatform(1080, 368, 82),
            PaperPlatform(2120, 414, 88), PaperPlatform(2255, 365, 84),
            PaperPlatform(3400, 418, 82), PaperPlatform(3528, 374, 78), PaperPlatform(3650, 330, 80),
            PaperPlatform(4780, 416, 86), PaperPlatform(4918, 370, 82), PaperPlatform(5050, 326, 82),
        ]
        self.trap_books = [
            TrapBook(520, self.FLOOR_Y, 86),
            TrapBook(1510, self.FLOOR_Y, 90),
            TrapBook(2730, self.FLOOR_Y, 88),
            TrapBook(4040, self.FLOOR_Y, 92),
            TrapBook(5480, self.FLOOR_Y, 88),
        ]
        self.pencils = []
        self.erasers = [
            FlyingEraser(760, self.FLOOR_Y, patrol_width=105, hover_altitude=134),
            FlyingEraser(1760, self.FLOOR_Y, patrol_width=130, hover_altitude=146),
            FlyingEraser(2890, self.FLOOR_Y, patrol_width=118, hover_altitude=130),
            FlyingEraser(4250, self.FLOOR_Y, patrol_width=145, hover_altitude=150),
            FlyingEraser(5600, self.FLOOR_Y, patrol_width=112, hover_altitude=138),
        ]
        self.bookworms = [
            Bookworm(1240, 1430, self.FLOOR_Y, speed=54),
            Bookworm(1625, 1960, self.FLOOR_Y, speed=62),
            Bookworm(2500, 3160, self.FLOOR_Y, speed=67),
            Bookworm(3840, 4560, self.FLOOR_Y, speed=72),
            Bookworm(5225, 5800, self.FLOOR_Y, speed=76),
        ]
        
        
        self.power_block = AcademicQuestionBlock(1517, 374)
        self.spawn_timer = 1.6

    def support_platforms(self):
        supports = []
        for paper in self.paper_platforms:
            if paper.active:
                supports.append(Platform(paper.rect.copy(), (245, 232, 194), (205, 185, 146), "paper", one_way=True))
        for pencil in self.pencils:
            if pencil.alive:
                supports.append(Platform(pencil.rect.copy(), (247, 196, 73), (179, 123, 50), "pencil", one_way=True))
        return supports

    def spawn_pencil(self, camera_x, player_x):
        
        
        
        altitude = random.randint(26, 82)
        y = self.FLOOR_Y - altitude - 5
        x = max(camera_x + SCREEN_W + random.randint(70, 180), player_x + 660)
        self.pencils.append(PencilProjectile(x, y, random.uniform(205, 285)))

    def spawn_pencil_staircase(self, camera_x, player_x):
        base_x = max(camera_x + SCREEN_W + random.randint(110, 180), player_x + 700)
        speed = random.uniform(220, 270)
        altitudes = (26, 40, 54, 68, 82)
        horizontal_step = 68
        for index, altitude in enumerate(altitudes):
            x = base_x + index * horizontal_step
            y = self.FLOOR_Y - altitude - 5
            self.pencils.append(PencilProjectile(x, y, speed))


    def repel_front_hazards(self, player):
        if not player.has_book_power:
            return
        guard = player.book_guard_rect()

        for pencil in self.pencils:
            if pencil.alive and guard.colliderect(pencil.rect):
                pencil.alive = False

        for eraser in self.erasers:
            if eraser.active and guard.colliderect(eraser.rect):
                eraser.direction = player.facing
                eraser.apply_knockback(player.facing)

        for worm in self.bookworms:
            if not worm.disabled and guard.colliderect(worm.rect):
                worm.direction = player.facing
                worm.alert_amount = max(0.0, worm.alert_amount - 0.55)
                worm.apply_knockback(player.facing)

        
        for book in self.trap_books:
            if not book.destroyed and guard.colliderect(book.zone):
                book.destroy()

    def update_before_player(self, dt, player, camera_x):
        self.power_block.update(dt)
        self.repel_front_hazards(player)
        for paper in self.paper_platforms:
            paper.update(dt)
        for book in self.trap_books:
            book.update_visual(dt)
        for eraser in self.erasers:
            eraser.update(dt, player, self.has_floor_below)
            death = eraser.handle_player_contact(player)
            if death:
                return death
        for worm in self.bookworms:
            worm.update(dt, player, self.has_floor_below)
            death = worm.handle_player_contact(player)
            if death:
                return death

        self.spawn_timer -= dt
        if player.pos.x > 330 and self.spawn_timer <= 0:
            
            
            
            
            if random.random() < 0.24:
                self.spawn_pencil_staircase(camera_x, player.pos.x)
                self.spawn_timer = random.uniform(4.6, 6.2)
            else:
                self.spawn_pencil(camera_x, player.pos.x)
                self.spawn_timer = random.uniform(2.7, 4.8)

        self.repel_front_hazards(player)
        for pencil in self.pencils:
            pencil.update(dt, player)
            if pencil.hits_player_from_front(player):
                return "pencil"
        self.pencils = [p for p in self.pencils if p.alive]
        return None

    def update_after_player(self, dt, player, was_stomping):
        stomp_landed = was_stomping and not player.stomp_active and player.on_ground
        self.power_block.try_hit_from_below(player)
        self.power_block.try_collect(player)
        self.repel_front_hazards(player)
        for paper in self.paper_platforms:
            paper.register_player(player)
        self.repel_front_hazards(player)
        for pencil in self.pencils:
            if pencil.hits_player_from_front(player):
                return "pencil"
        for eraser in self.erasers:
            death = eraser.handle_player_contact(player)
            if death:
                return death
        for worm in self.bookworms:
            death = worm.handle_player_contact(player)
            if death:
                return death
        for book in self.trap_books:
            if book.update_contact(dt, player, stomp_landed):
                return "book"
        return None

    def draw(self, surface, camera_x):
        self.power_block.draw(surface, camera_x)
        for paper in self.paper_platforms:
            paper.draw(surface, camera_x)
        for book in self.trap_books:
            book.draw(surface, camera_x)
        for worm in self.bookworms:
            worm.draw(surface, camera_x)
        for eraser in self.erasers:
            eraser.draw(surface, camera_x)
        for pencil in self.pencils:
            pencil.draw(surface, camera_x)

# [플레이어] 기룡이의 이동, 점프, 충돌, 자세, 강화 상태를 관리한다.
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

    def _draw_academic_power(self, surface, x, feet_y, body_rect):
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
        if self.facing > 0:
            left_page = [(center_x, top + 4), (bx + 2, top), (bx + 4, bottom), (center_x - 1, bottom - 3)]
            right_page = [(center_x, top + 4), (bx + book_w - 2, top), (bx + book_w - 4, bottom), (center_x + 1, bottom - 3)]
        else:
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
        max_speed = 130 if crouching_now else 245
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

        
        
        self._draw_academic_power(surface, x, feet_y, body_rect)

        
        
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


# [월드 데이터] 대학별 이름, 배경, 발판, 시작점, 골인지점을 관리한다.
class World:
    def __init__(self, name, subtitle, theme, platforms, start, goal_x):
        self.name = name
        self.subtitle = subtitle
        self.theme = theme
        self.platforms = platforms
        self.start = start
        self.goal_x = goal_x

    def draw_background(self, surface, camera_x, font):
        if self.name == "인문대학":
            self.draw_library_background(surface, camera_x)
        else:
            top, bottom, accent = self.theme
            for y in range(SCREEN_H):
                t = y / SCREEN_H
                color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
                pygame.draw.line(surface, color, (0, y), (SCREEN_W, y))
            base = SCREEN_H - 84
            for i in range(12):
                bx = i * 180 - (camera_x * 0.22 % 180)
                h = 44 + (i % 4) * 14
                pygame.draw.rect(surface, (*accent,), (bx, base - h, 82, h))
                pygame.draw.rect(surface, (255, 255, 255), (bx + 10, base - h + 12, 12, 8))
                pygame.draw.rect(surface, (255, 255, 255), (bx + 36, base - h + 12, 12, 8))
        draw_text(surface, font, self.name, (24, 20), WHITE)

    def draw_library_background(self, surface, camera_x):
        wall_top = (104, 73, 67)
        wall_bottom = (184, 145, 108)
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            color = tuple(int(wall_top[i] * (1 - t) + wall_bottom[i] * t) for i in range(3))
            pygame.draw.line(surface, color, (0, y), (SCREEN_W, y))

        
        pygame.draw.rect(surface, (84, 57, 55), (0, 0, SCREEN_W, 94))
        pygame.draw.rect(surface, (210, 174, 132), (0, 176, SCREEN_W, 5))
        pygame.draw.rect(surface, (92, 62, 55), (0, 181, SCREEN_W, 11))

        shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        pygame.draw.rect(shade, (33, 22, 25, 38), (0, 0, SCREEN_W, 112))
        pygame.draw.rect(shade, (34, 22, 25, 46), (0, 414, SCREEN_W, 126))
        pygame.draw.rect(shade, (28, 18, 22, 38), (0, 0, 58, SCREEN_H))
        pygame.draw.rect(shade, (28, 18, 22, 32), (SCREEN_W - 58, 0, 58, SCREEN_H))
        surface.blit(shade, (0, 0))

        
        window_spacing = 360
        window_offset = int(camera_x * 0.08) % window_spacing
        for i in range(-1, 4):
            x = i * window_spacing - window_offset + 54
            pygame.draw.rect(surface, (61, 53, 60), (x, 54, 118, 108), border_radius=7)
            pygame.draw.rect(surface, (168, 198, 210), (x + 8, 62, 102, 92), border_radius=5)
            pygame.draw.rect(surface, (194, 218, 223), (x + 14, 68, 42, 80), border_radius=3)
            pygame.draw.line(surface, (61, 53, 60), (x + 59, 62), (x + 59, 154), 4)
            pygame.draw.line(surface, (61, 53, 60), (x + 8, 108), (x + 110, 108), 4)
            pygame.draw.rect(surface, (48, 41, 47), (x - 5, 162, 128, 8))

        
        lamp_spacing = 560
        lamp_offset = int(camera_x * 0.04) % lamp_spacing
        glow = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for i in range(-1, 3):
            x = i * lamp_spacing - lamp_offset + 190
            pygame.draw.line(surface, (58, 43, 40), (x, 0), (x, 39), 3)
            pygame.draw.circle(glow, (255, 218, 148, 24), (x, 55), 54)
            pygame.draw.circle(surface, (222, 177, 96), (x, 53), 15)
            pygame.draw.circle(surface, (255, 232, 166), (x, 53), 7)
        surface.blit(glow, (0, 0))

        
        shelf_spacing = 520
        shelf_offset = int(camera_x * 0.18) % shelf_spacing
        for i in range(-1, 4):
            world_index = i + int(camera_x * 0.18) // shelf_spacing
            if world_index % 3 == 1:
                continue
            x = i * shelf_spacing - shelf_offset + 74
            y = 256 + (world_index % 2) * 18
            w = 184 + (world_index % 2) * 26
            h = 150 - (world_index % 2) * 12
            pygame.draw.rect(surface, (52, 37, 36), (x + 7, y + 8, w, h), border_radius=3)
            pygame.draw.rect(surface, (83, 54, 45), (x, y, w, h), border_radius=3)
            pygame.draw.rect(surface, (111, 73, 52), (x + 9, y + 9, w - 18, h - 18))
            for row_y in (y + 48, y + 92):
                pygame.draw.rect(surface, (58, 40, 37), (x + 7, row_y, w - 14, 8))
            
            muted_books = ((118, 72, 64), (73, 92, 101), (93, 105, 76), (130, 101, 65))
            for j in range(7):
                bx = x + 16 + j * 21
                bh = 18 + (j * 7 + world_index * 3) % 14
                pygame.draw.rect(surface, muted_books[(j + world_index) % len(muted_books)], (bx, y + 47 - bh, 12, bh))

        
        desk_spacing = 900
        desk_offset = int(camera_x * 0.30) % desk_spacing
        for i in range(-1, 3):
            x = i * desk_spacing - desk_offset + 270
            pygame.draw.rect(surface, (58, 41, 38), (x + 6, 402, 170, 15))
            pygame.draw.rect(surface, (101, 67, 49), (x, 394, 170, 15))
            pygame.draw.rect(surface, (67, 45, 40), (x + 18, 409, 13, 55))
            pygame.draw.rect(surface, (67, 45, 40), (x + 138, 409, 13, 55))

        
        pygame.draw.rect(surface, (93, 66, 56), (0, SCREEN_H - 84, SCREEN_W, 84))
        pygame.draw.rect(surface, (67, 45, 42), (0, SCREEN_H - 84, SCREEN_W, 6))
        for x in range(-40, SCREEN_W + 90, 112):
            shifted = x - int(camera_x * 0.42) % 112
            pygame.draw.line(surface, (79, 56, 49), (shifted, SCREEN_H - 84), (shifted + 34, SCREEN_H), 1)

    def draw_goal(self, surface, camera_x):
        x = int(self.goal_x - camera_x)
        y = SCREEN_H - 185
        pygame.draw.rect(surface, GOLD, (x, y, 12, 92))
        pygame.draw.polygon(surface, RED, [(x + 12, y + 4), (x + 76, y + 25), (x + 12, y + 46)])
        pygame.draw.rect(surface, INK, (x, y, 12, 92), 2)


# 대학별 월드와 발판 배치
def make_worlds():
    floor_y = SCREEN_H - 72

    def add_platform(plats, x, y, w, h, color, trim):
        plats.append(Platform(pygame.Rect(x, y, w, h), color, trim))

    def add_floor_segments(plats, width, gaps, color, trim):
        cursor = 0
        for gap_start, gap_end in sorted(gaps):
            if gap_start > cursor:
                add_platform(plats, cursor, floor_y, gap_start - cursor, 96, color, trim)
            cursor = max(cursor, gap_end)
        if cursor < width:
            add_platform(plats, cursor, floor_y, width - cursor, 96, color, trim)

    def add_crouch_tunnel(plats, x, width, color, trim):
        
        
        add_platform(plats, x, floor_y - 54, width, 20, color, trim)

    def add_hurdle(plats, x, height, width, color, trim):
        add_platform(plats, x, floor_y - height, width, height, color, trim)

    specs = [
        {
            "name": "인문대학",
            "subtitle": "인문대생들의 시끌벅적 도서관",
            "theme": ((115, 186, 255), (218, 240, 252), (132, 146, 160)),
            "accent": BLUE,
            "width": 6000,
            "gaps": [(900, 1210), (2050, 2420), (3330, 3730), (4700, 5140)],
            
            
            "platforms": [],
            "tunnels": [],
            "hurdles": [],
        },
        {
            "name": "자연과학 대학",
            "subtitle": "짧은 착지 지점과 연속 점프를 통과하는 관찰 코스",
            "theme": ((124, 210, 216), (221, 250, 230), (93, 156, 116)),
            "accent": GREEN,
            "width": 3800,
            "gaps": [(610, 765), (1155, 1340), (1770, 1960), (2460, 2650), (3160, 3350)],
            "platforms": [
                (650, 414, 72, 18),
                (935, 386, 92, 18),
                (1207, 420, 76, 18),
                (1510, 392, 88, 18), (1645, 356, 76, 18),
                (1827, 408, 76, 18),
                (2185, 374, 104, 18),
                (2517, 404, 76, 18),
                (2850, 382, 86, 18), (2975, 346, 78, 18),
                (3217, 410, 76, 18),
                (3500, 365, 112, 18),
            ],
            "tunnels": [(800, 185), (2025, 205), (2735, 185)],
            "hurdles": [(1030, 50, 42), (1420, 58, 46), (2320, 42, 44), (3030, 60, 48)],
        },
        {
            "name": "예술 대학",
            "subtitle": "좁은 발판을 리듬감 있게 밟는 정밀 점프 코스",
            "theme": ((255, 169, 176), (251, 233, 210), (172, 102, 152)),
            "accent": PURPLE,
            "width": 3800,
            "gaps": [(560, 745), (1015, 1235), (1510, 1705), (1990, 2215), (2520, 2745), (3120, 3350)],
            "platforms": [
                (615, 417, 68, 18),
                (1060, 421, 60, 18), (1145, 382, 52, 18),
                (1550, 405, 58, 18), (1633, 367, 54, 18),
                (2040, 418, 58, 18), (2128, 378, 52, 18),
                (2570, 412, 58, 18), (2660, 368, 54, 18),
                (2885, 346, 72, 18),
                (3170, 416, 58, 18), (3262, 373, 54, 18),
                (3480, 336, 92, 18),
            ],
            "tunnels": [(790, 175), (2260, 185), (2800, 165)],
            "hurdles": [(1335, 54, 42), (1810, 64, 44), (2960, 52, 42), (3590, 66, 48)],
        },
        {
            "name": "소프트웨어경영 대학",
            "subtitle": "낮은 통로 직후 점프가 이어지는 입력 전환 코스",
            "theme": ((116, 173, 235), (231, 243, 255), (82, 112, 145)),
            "accent": (65, 135, 195),
            "width": 4100,
            "gaps": [(690, 865), (1260, 1475), (1880, 2090), (2500, 2730), (3180, 3405), (3710, 3885)],
            "platforms": [
                (740, 413, 72, 18),
                (1312, 418, 66, 18), (1402, 377, 58, 18),
                (1935, 410, 66, 18), (2023, 369, 54, 18),
                (2555, 414, 64, 18), (2646, 371, 56, 18),
                (3234, 408, 66, 18), (3322, 365, 56, 18),
                (3756, 413, 72, 18),
            ],
            "tunnels": [(425, 190), (930, 205), (1540, 210), (2160, 210), (2810, 205), (3460, 190)],
            "hurdles": [(1160, 58, 44), (1770, 66, 46), (2390, 62, 46), (3060, 70, 46), (3610, 58, 44)],
        },
        {
            "name": "창의공과 대학",
            "subtitle": "긴 연속 점프와 좁은 통로를 결합한 최종 코스",
            "theme": ((255, 186, 111), (237, 245, 230), (142, 128, 99)),
            "accent": RED,
            "width": 4400,
            "gaps": [(610, 805), (1080, 1315), (1580, 1815), (2080, 2325), (2630, 2875), (3180, 3435), (3750, 3995)],
            "platforms": [
                (660, 416, 68, 18), (748, 375, 48, 18),
                (1132, 414, 62, 18), (1218, 370, 54, 18),
                (1632, 410, 62, 18), (1718, 365, 54, 18),
                (2132, 414, 62, 18), (2218, 368, 54, 18),
                (2682, 407, 62, 18), (2768, 362, 54, 18),
                (3232, 410, 62, 18), (3318, 365, 54, 18),
                (3802, 414, 62, 18), (3888, 369, 54, 18),
                (4105, 335, 92, 18),
            ],
            "tunnels": [(860, 170), (1360, 170), (1870, 165), (2380, 175), (2930, 170), (3490, 175)],
            "hurdles": [(1015, 62, 42), (1510, 72, 44), (2010, 68, 44), (2550, 76, 46), (3080, 72, 44), (3650, 78, 46), (4200, 68, 46)],
        },
    ]

    worlds = []
    for spec in specs:
        accent = spec["accent"]
        trim = tuple(max(0, c - 38) for c in accent)
        plats = []
        add_floor_segments(plats, spec["width"], spec["gaps"], accent, trim)
        for x, y, w, h in spec["platforms"]:
            add_platform(plats, x, y, w, h, accent, trim)
        for x, tunnel_width in spec["tunnels"]:
            add_crouch_tunnel(plats, x, tunnel_width, accent, trim)
        for x, height, hurdle_width in spec["hurdles"]:
            add_hurdle(plats, x, height, hurdle_width, accent, trim)

        worlds.append(
            World(
                spec["name"],
                spec["subtitle"],
                spec["theme"],
                plats,
                (96, SCREEN_H - 160),
                spec["width"] - 180,
            )
        )
    return worlds

# [게임 전체 관리] 메뉴, 월드 선택, 플레이, 사망, 클리어 흐름을 관리한다.
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Kiryong Campus Platformer Prototype")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("malgungothic", 24)
        self.big_font = pygame.font.SysFont("malgungothic", 44, bold=True)
        self.small_font = pygame.font.SysFont("malgungothic", 18)
        self.worlds = make_worlds()
        self.state = "main"
        self.menu_index = 0
        self.world_index = 0
        self.costume = 0
        self.player = Player(*self.worlds[0].start)
        self.camera_x = 0
        self.clouds = [Cloud(random.randint(-100, SCREEN_W), random.randint(38, 175), random.uniform(10, 26), random.randint(20, 36)) for _ in range(6)]
        self.birds = [Bird() for _ in range(4)]
        self.finish_timer = 0
        self.completed_worlds = set()
        self.humanities_gimmicks = HumanitiesGimmicks()
        self.death_timer = 0.0
        self.death_reason = ""

    def reset_player(self):
        world = self.worlds[self.world_index]
        self.player = Player(*world.start)
        self.player.set_costume(self.costume)
        self.camera_x = 0
        self.finish_timer = 0
        self.death_timer = 0.0
        self.death_reason = ""
        if world.name == "인문대학":
            self.humanities_gimmicks.reset()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type != pygame.KEYDOWN:
            return
        if self.state == "main":
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                self.menu_index = 1 - self.menu_index
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.state = "costume" if self.menu_index == 0 else "world"
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif self.state == "costume":
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.costume = (self.costume + (1 if event.key == pygame.K_RIGHT else -1)) % 3
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.player.set_costume(self.costume)
                self.state = "main"
            elif event.key == pygame.K_ESCAPE:
                self.state = "main"
        elif self.state == "world":
            if event.key in (pygame.K_LEFT, pygame.K_UP):
                self.world_index = (self.world_index - 1) % len(self.worlds)
            elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                self.world_index = (self.world_index + 1) % len(self.worlds)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset_player()
                self.state = "play"
            elif event.key == pygame.K_ESCAPE:
                self.state = "main"
        elif self.state == "play":
            if event.key == pygame.K_ESCAPE:
                self.state = "world"
            elif event.key == pygame.K_r:
                self.reset_player()
        elif self.state == "dead":
            if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                self.reset_player()
                self.state = "play"
            elif event.key == pygame.K_ESCAPE:
                self.state = "world"
        elif self.state == "clear":
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self.state = "world"

    def update_ambient(self, dt):
        for cloud in self.clouds:
            cloud.update(dt)
        for bird in self.birds:
            bird.update(dt)

    def draw_ambient(self):
        for cloud in self.clouds:
            cloud.draw(self.screen)
        for bird in self.birds:
            bird.draw(self.screen)

    def draw_main_kiryong(self):
        t = pygame.time.get_ticks() / 1000
        cycle = t % 7.0
        ground_y = SCREEN_H - 126
        old_pos = self.player.pos.copy()
        old_pose = self.player.pose
        old_facing = self.player.facing
        old_anim_t = self.player.anim_t

        walk_seconds = 5.2
        wobble_seconds = 3.4
        full_cycle = (walk_seconds + wobble_seconds) * 2
        cycle = t % full_cycle
        segment = int(cycle // (walk_seconds + wobble_seconds))
        local = cycle % (walk_seconds + wobble_seconds)
        moving_right = segment == 0
        left_x = 180
        right_x = SCREEN_W - 222

        if local < walk_seconds:
            walk_t = local / walk_seconds
            eased = 0.5 - math.cos(walk_t * math.pi) * 0.5
            if moving_right:
                x = int(left_x + eased * (right_x - left_x))
                self.player.facing = 1
            else:
                x = int(right_x - eased * (right_x - left_x))
                self.player.facing = -1
            self.player.pos = pygame.Vector2(x, ground_y)
            self.player.pose = "run"
            self.player.anim_t = t * 0.72
            self.player.draw(self.screen, 0)
        else:
            x = right_x - 21 if moving_right else left_x - 21
            wobble_t = local - walk_seconds
            self.player.draw_front(self.screen, x, SCREEN_H - 148, wobble_t)

        self.player.pos = old_pos
        self.player.pose = old_pose
        self.player.facing = old_facing
        self.player.anim_t = old_anim_t

    def draw_main(self, dt):
        self.update_ambient(dt)
        self.draw_sky()
        self.draw_ambient()

        
        
        title_t = pygame.time.get_ticks() / 1000
        title_y = 108 + round(math.sin(title_t * 2.0) * 4)
        color_phase = (math.sin(title_t * 1.35) + 1) * 0.5
        title_color = blend_color((255, 214, 82), (255, 132, 166), color_phase)
        draw_outlined_text(
            self.screen,
            self.big_font,
            "기룡이 캠퍼스 어드벤처",
            (SCREEN_W // 2, title_y),
            color=title_color,
            outline=(54, 72, 125),
            center=True,
            thickness=2,
        )
        draw_outlined_text(
            self.screen,
            self.font,
            "도트 플랫폼 게임 프로토타입",
            (SCREEN_W // 2, 157),
            color=WHITE,
            outline=(54, 72, 125),
            center=True,
            thickness=1,
        )
        options = ["코스튬 선택", "월드 선택"]
        for i, label in enumerate(options):
            rect = pygame.Rect(SCREEN_W // 2 - 150, 220 + i * 64, 300, 48)
            color = GOLD if i == self.menu_index else WHITE
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, INK, rect, 3)
            draw_text(self.screen, self.font, label, rect.center, INK, center=True)
        self.draw_main_kiryong()
        draw_text(self.screen, self.small_font, "방향키 선택 / Enter 또는 Space 확인", (SCREEN_W // 2, 485), WHITE, center=True)

    def draw_sky(self):
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            color = tuple(int(SKY_TOP[i] * (1 - t) + SKY_BOTTOM[i] * t) for i in range(3))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_W, y))
        pygame.draw.rect(self.screen, (98, 184, 104), (0, SCREEN_H - 84, SCREEN_W, 84))
        pygame.draw.rect(self.screen, (60, 142, 78), (0, SCREEN_H - 70, SCREEN_W, 70))

    def draw_kiryong_preview(self, x, y):
        old_pos = self.player.pos.copy()
        old_pose = self.player.pose
        old_anim_t = self.player.anim_t
        self.player.pos = pygame.Vector2(x, y)
        self.player.pose = "idle"
        self.player.anim_t = 0
        self.player.draw(self.screen, 0)
        self.player.pos = old_pos
        self.player.pose = old_pose
        self.player.anim_t = old_anim_t

    def draw_costume(self):
        self.draw_sky()
        self.draw_ambient()
        draw_text(self.screen, self.big_font, "코스튬 선택", (SCREEN_W // 2, 92), WHITE, center=True)
        names = ["경기 블루", "축제 레드", "캠퍼스 그린"]
        self.player.set_costume(self.costume)
        self.draw_kiryong_preview(SCREEN_W // 2 - 16, 235)
        draw_text(self.screen, self.font, names[self.costume], (SCREEN_W // 2, 330), WHITE, center=True)
        draw_text(self.screen, self.small_font, "← → 변경 / Space 확정 / Esc 뒤로", (SCREEN_W // 2, 480), WHITE, center=True)

    def draw_world_select(self):
        self.draw_sky()
        self.draw_ambient()

        
        
        heading_panel = pygame.Surface((330, 74), pygame.SRCALPHA)
        pygame.draw.rect(heading_panel, (37, 62, 105, 155), (0, 0, 330, 74), border_radius=18)
        pygame.draw.rect(heading_panel, (245, 251, 255, 105), (0, 0, 330, 74), 2, border_radius=18)
        self.screen.blit(heading_panel, (SCREEN_W // 2 - 165, 34))
        draw_outlined_text(
            self.screen,
            self.big_font,
            "월드 선택",
            (SCREEN_W // 2, 70),
            color=(255, 221, 103),
            outline=(45, 60, 99),
            center=True,
            thickness=2,
        )
        for i, world in enumerate(self.worlds):
            x = 120 + i * 168
            y = 185
            rect = pygame.Rect(x, y, 128, 146)
            selected = i == self.world_index
            pygame.draw.rect(self.screen, GOLD if selected else WHITE, rect)
            pygame.draw.rect(self.screen, INK, rect, 3 if selected else 2)
            top, bottom, accent = world.theme

            
            if world.name == "소프트웨어경영 대학":
                title_lines = ["소프트웨어경영", "대학"]
            else:
                title_lines = [world.name]
            label_color = (30, 41, 68) if selected else INK
            draw_centered_lines(
                self.screen,
                self.small_font,
                title_lines,
                rect.centerx,
                y + 10,
                label_color,
                gap=0,
                outline=(255, 250, 224) if selected else None,
            )

            building_y = y + (61 if len(title_lines) == 2 else 48)
            building_h = 45 if len(title_lines) == 2 else 54
            pygame.draw.rect(self.screen, accent, (x + 18, building_y, 92, building_h))
            pygame.draw.rect(self.screen, DARK_STONE, (x + 18, building_y, 92, building_h), 2)

            
            if i in self.completed_worlds:
                draw_star(self.screen, (rect.right - 14, rect.bottom - 15), outer_radius=10, inner_radius=5)
        world = self.worlds[self.world_index]
        subtitle_panel = pygame.Surface((760, 56), pygame.SRCALPHA)
        pygame.draw.rect(subtitle_panel, (35, 54, 88, 145), (0, 0, 760, 56), border_radius=14)
        self.screen.blit(subtitle_panel, (SCREEN_W // 2 - 380, 365))
        draw_outlined_text(
            self.screen,
            self.font,
            world.subtitle,
            (SCREEN_W // 2, 393),
            color=WHITE,
            outline=(36, 48, 76),
            center=True,
            thickness=1,
        )
        controls_panel = pygame.Surface((900, 86), pygame.SRCALPHA)
        pygame.draw.rect(controls_panel, (35, 54, 88, 150), (0, 0, 900, 86), border_radius=14)
        self.screen.blit(controls_panel, (SCREEN_W // 2 - 450, 438))
        draw_outlined_text(
            self.screen,
            self.small_font,
            "월드 선택: 방향키 변경 / Space 시작 / Esc 뒤로",
            (SCREEN_W // 2, 454),
            color=WHITE,
            outline=(45, 60, 99),
            center=True,
            thickness=1,
        )
        draw_outlined_text(
            self.screen,
            self.small_font,
            "게임 조작: ← → 이동 / Space 점프 / 지상 ↓ 엎드리기·기어가기",
            (SCREEN_W // 2, 478),
            color=(255, 236, 173),
            outline=(45, 60, 99),
            center=True,
            thickness=1,
        )
        draw_outlined_text(
            self.screen,
            self.small_font,
            "공중 ↓ 엉덩이 찍기 / ↑ 고개 들기 / R 재시작",
            (SCREEN_W // 2, 502),
            color=(255, 236, 173),
            outline=(45, 60, 99),
            center=True,
            thickness=1,
        )

    def kill_player(self, reason):
        if self.state != "play":
            return
        self.state = "dead"
        self.death_timer = 0.0
        self.death_reason = reason
        self.player.pose = "jump"
        self.player.vel.y = -315 if reason == "pencil" else -245
        self.player.vel.x = -205 if reason == "pencil" else 0

    def draw_play_scene(self, world, draw_player=True):
        world.draw_background(self.screen, self.camera_x, self.font)
        if world.name != "인문대학":
            self.draw_ambient()
        world.draw_goal(self.screen, self.camera_x)
        for p in world.platforms:
            p.draw(self.screen, self.camera_x, world.name)
        if world.name == "인문대학":
            self.humanities_gimmicks.draw(self.screen, self.camera_x)
        if draw_player:
            self.player.draw(self.screen, self.camera_x)

    def play_update_draw(self, dt):
        world = self.worlds[self.world_index]
        keys = pygame.key.get_pressed()
        support_platforms = list(world.platforms)

        if world.name == "인문대학":
            death = self.humanities_gimmicks.update_before_player(dt, self.player, self.camera_x)
            if death:
                self.kill_player(death)
                self.draw_play_scene(world)
                return
            support_platforms.extend(self.humanities_gimmicks.support_platforms())

        was_stomping = self.player.stomp_active
        self.player.update(dt, keys, support_platforms)

        if world.name == "인문대학":
            death = self.humanities_gimmicks.update_after_player(dt, self.player, was_stomping)
            if death:
                self.kill_player(death)

        if self.player.pos.y > SCREEN_H + 160:
            self.kill_player("fall")

        self.camera_x = nspeed(self.player.pos.x - SCREEN_W * 0.42, 0, max(0, world.goal_x - SCREEN_W + 260))
        self.draw_play_scene(world)
        if self.state == "dead":
            return
        if self.player.pos.x > world.goal_x:
            self.completed_worlds.add(self.world_index)
            self.state = "clear"

    def dead_update_draw(self, dt):
        world = self.worlds[self.world_index]
        self.death_timer += dt
        self.player.vel.y += 940 * dt
        self.player.pos += self.player.vel * dt
        self.camera_x = nspeed(self.player.pos.x - SCREEN_W * 0.42, 0, max(0, world.goal_x - SCREEN_W + 260))
        self.draw_play_scene(world)

        px = round(self.player.pos.x - self.camera_x + self.player.width // 2)
        py = round(self.player.pos.y - 15)
        for i in range(4):
            angle = self.death_timer * 5.5 + i * math.pi / 2
            sx = px + round(math.cos(angle) * 26)
            sy = py + round(math.sin(angle) * 14)
            draw_star(self.screen, (sx, sy), outer_radius=6, inner_radius=3, color=(255, 223, 103))

        death_labels = {
            "pencil": "연필에 맞았다!",
            "book": "책이 닫혔다!",
            "eraser": "지우개에 부딪혔다!",
            "bookworm": "책벌레에게 잡혔다!",
            "fall": "낙하했다!",
        }
        label = death_labels.get(self.death_reason, "기룡이가 쓰러졌다!")
        draw_outlined_text(self.screen, self.font, label, (SCREEN_W // 2, 138), color=WHITE, outline=(60, 45, 61), center=True, thickness=1)
        draw_outlined_text(self.screen, self.small_font, "잠시 후 다시 시작 / Space 즉시 재시작", (SCREEN_W // 2, 173), color=(255, 236, 173), outline=(60, 45, 61), center=True, thickness=1)

        if self.death_timer >= 1.18:
            self.reset_player()
            self.state = "play"

    def draw_clear(self):
        world = self.worlds[self.world_index]
        world.draw_background(self.screen, self.camera_x, self.font)
        for p in world.platforms:
            p.draw(self.screen, self.camera_x, world.name)
        if world.name == "인문대학":
            self.humanities_gimmicks.draw(self.screen, self.camera_x)
        self.player.draw(self.screen, self.camera_x)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((20, 30, 45, 145))
        self.screen.blit(overlay, (0, 0))
        draw_text(self.screen, self.big_font, "클리어!", (SCREEN_W // 2, 210), WHITE, center=True)
        draw_text(self.screen, self.font, f"{world.name} 코스 완료", (SCREEN_W // 2, 270), WHITE, center=True)
        draw_text(self.screen, self.small_font, "Space 또는 Enter로 월드 선택으로 돌아가기", (SCREEN_W // 2, 335), WHITE, center=True)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                self.handle_event(event)

            if self.state == "main":
                self.draw_main(dt)
            elif self.state == "costume":
                self.update_ambient(dt)
                self.draw_costume()
            elif self.state == "world":
                self.update_ambient(dt)
                self.draw_world_select()
            elif self.state == "play":
                self.update_ambient(dt)
                self.play_update_draw(dt)
            elif self.state == "dead":
                self.dead_update_draw(dt)
            elif self.state == "clear":
                self.draw_clear()

            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
