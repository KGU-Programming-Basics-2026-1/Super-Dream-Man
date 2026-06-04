import random
import sys
from pathlib import Path
import pygame
from game_objects import *
from worlds import *

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Kiryong Campus Platformer")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock() #게임 프레임 속도 관리용 시간
        self.font = pygame.font.SysFont("malgungothic", 24)
        self.big_font = pygame.font.SysFont("malgungothic", 44, bold=True)
        self.small_font = pygame.font.SysFont("malgungothic", 18) 
        self.worlds = make_worlds()
        self.map_images = self.load_map_images()
        self.state = "main"
        self.menu_index = 0 # 0은 코, 1은 월
        self.world_index = 0
        self.costume = 0
        self.player = Player(*self.worlds[0].start)
        self.camera_x = 0 #카메라 이동 x
        self.clouds = [Cloud(random.randint(-100, SCREEN_W), random.randint(38, 175), random.uniform(10, 26), random.randint(20, 36)) for _ in range(6)]
        self.birds = [Bird() for _ in range(4)]
        self.completed_worlds = set()
        self.gimmicks = {
            "인문대학": HumanitiesGimmicks(),
            "자연과학 대학": ScienceGimmicks(),
            "예술 대학": ArtGimmicks(),
            "소프트웨어경영 대학": SoftwareGimmicks(),
            "창의공과 대학": EngineeringGimmicks(),
        }
        self.death_timer = 0.0
        self.death_reason = "" 

    def load_map_images(self):
        images_dir = Path(__file__).resolve().parent / "images"
        loaded = []

        for number in range(1, 6):
            image_path = images_dir / f"map{number}.png"
            image = None

            if image_path.exists():
                try:
                    image = pygame.image.load(str(image_path)).convert()
                except pygame.error:
                    pass

            loaded.append(image)

        return loaded

    def draw_map_image(self, image, rect):
        if image is None:
            return False

        source_w, source_h = image.get_size()
        if source_w <= 0 or source_h <= 0:
            return False

        scale = max(rect.w / source_w, rect.h / source_h)
        scaled_w = max(1, round(source_w * scale))
        scaled_h = max(1, round(source_h * scale))
        scaled = pygame.transform.smoothscale(image, (scaled_w, scaled_h))

        crop_x = max(0, (scaled_w - rect.w) // 2)
        crop_y = max(0, (scaled_h - rect.h) // 2)
        crop_rect = pygame.Rect(crop_x, crop_y, rect.w, rect.h)
        self.screen.blit(scaled, rect, crop_rect)
        return True

    def reset_player(self):
        world = self.worlds[self.world_index]
        self.player = Player(*world.start)
        self.player.set_costume(self.costume)
        self.camera_x = 0
        self.death_timer = 0.0
        self.death_reason = ""
        gimmick = self.gimmicks.get(world.name)
        if gimmick:
            gimmick.reset()
    ##게임 상태는 main, costume, world, play, dead, clear
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
            "슈퍼 기룡맨 어드벤처",
            (SCREEN_W // 2, title_y),
            color=title_color,
            outline=(54, 72, 125),
            center=True,
            thickness=2,
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
            top, bottom, accent = world.theme

            image_loaded = self.draw_map_image(self.map_images[i], rect)

            if image_loaded:
                title_panel = pygame.Surface((rect.w, 52), pygame.SRCALPHA)
                pygame.draw.rect(title_panel, (18, 28, 44, 150), (0, 0, rect.w, 52))
                self.screen.blit(title_panel, (rect.x, rect.y))

                if i in self.completed_worlds:
                    clear_panel = pygame.Surface((rect.w, 34), pygame.SRCALPHA)
                    pygame.draw.rect(clear_panel, (18, 28, 44, 118), (0, 0, rect.w, 34))
                    self.screen.blit(clear_panel, (rect.x, rect.bottom - 34))
            else:
                pygame.draw.rect(self.screen, GOLD if selected else WHITE, rect)

            pygame.draw.rect(self.screen, GOLD if selected else INK, rect, 4 if selected else 2)

            if world.name == "소프트웨어경영 대학":
                title_lines = ["소프트웨어경영", "대학"]
            else:
                title_lines = [world.name]

            if image_loaded:
                label_color = WHITE
                title_outline = (24, 33, 50)
            else:
                label_color = (30, 41, 68) if selected else INK
                title_outline = (255, 250, 224) if selected else None

            draw_centered_lines(
                self.screen,
                self.small_font,
                title_lines,
                rect.centerx,
                y + 10,
                label_color,
                gap=0,
                outline=title_outline,
            )

            if not image_loaded:
                building_y = y + (61 if len(title_lines) == 2 else 48)
                building_h = 45 if len(title_lines) == 2 else 54
                pygame.draw.rect(self.screen, accent, (x + 18, building_y, 92, building_h))
                pygame.draw.rect(self.screen, DARK_STONE, (x + 18, building_y, 92, building_h), 2)

            if i in self.completed_worlds:
                draw_outlined_text(
                    self.screen,
                    self.small_font,
                    "CLEAR!!",
                    (rect.centerx, rect.bottom - 18),
                    color=(255, 220, 70),
                    outline=(112, 78, 32),
                    center=True,
                    thickness=1,
                    shadow=False,
                )
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
            "게임 조작: ← → 이동 / Space 점프 / 지상 ↓  기어가기",
            (SCREEN_W // 2, 478),
            color=(255, 236, 173),
            outline=(45, 60, 99),
            center=True,
            thickness=1,
        )
        draw_outlined_text(
            self.screen,
            self.small_font,
            "공중 ↓ 엉덩이 찍기 / ↑ 고개 들기, 아이템 능력 사용 / R 재시작",
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
        gimmick = self.gimmicks.get(world.name)
        if not gimmick:
            self.draw_ambient()
        world.draw_goal(self.screen, self.camera_x)
        for p in world.platforms:
            p.draw(self.screen, self.camera_x, world.name)
        if gimmick:
            gimmick.draw(self.screen, self.camera_x)
        if draw_player:
            self.player.draw(self.screen, self.camera_x)

    def play_update_draw(self, dt):
        world = self.worlds[self.world_index]
        keys = pygame.key.get_pressed()
        support_platforms = list(world.platforms)

        gimmick = self.gimmicks.get(world.name)
        if gimmick:
            death = gimmick.update_before_player(dt, self.player, self.camera_x, keys)
            if death:
                self.kill_player(death)
                self.draw_play_scene(world)
                return
            support_platforms.extend(gimmick.support_platforms())

        was_stomping = self.player.stomp_active
        self.player.update(dt, keys, support_platforms)

        if gimmick:
            death = gimmick.update_after_player(dt, self.player, was_stomping)
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
            "puddle": "보라색 웅덩이가 폭발했다!",
            "glass_shard": "떨어지는 유리 조각에 맞았다!",
            "brush": "날아오는 붓에 맞았다!",
            "red_paint": "튀어 오른 빨간 물감에 맞았다!",
            "palette": "하늘에서 내려찍는 팔레트에 맞았다!",
            "code": "날아오는 코드에 맞았다!",
            "rmrf": "rm -rf 명령으로 존재가 사라졌다!",
            "press": "압축 기계에 눌렸다!",
            "bolt": "떨어지는 볼트와 너트에 맞았다!",
            "spike": "가시에 찔렸다!",
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
        gimmick = self.gimmicks.get(world.name)
        if gimmick:
            gimmick.draw(self.screen, self.camera_x)
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
