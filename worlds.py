import math
import random
import pygame
from game_objects import *

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

    def update_before_player(self, dt, player, camera_x, keys=None):
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

class ScienceGimmicks:
    FLOOR_Y = SCREEN_H - 72
    WIDTH = 3800
    GAPS = (
        (700, 940),
        (1390, 1680),
        (2120, 2445),
        (2880, 3230),
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.glass_platforms = [
            GlassPlatform(735, 418, 78), GlassPlatform(825, 372, 76), GlassPlatform(905, 330, 72),
            GlassPlatform(1430, 418, 78), GlassPlatform(1525, 370, 76), GlassPlatform(1615, 328, 72),
            GlassPlatform(2165, 418, 80), GlassPlatform(2265, 368, 76), GlassPlatform(2360, 326, 72),
            GlassPlatform(2925, 418, 80), GlassPlatform(3025, 368, 76), GlassPlatform(3130, 326, 72),
        ]
        self.puddles = [
            PurplePuddle(410, self.FLOOR_Y, 88),
            PurplePuddle(1040, self.FLOOR_Y, 92),
            PurplePuddle(1775, self.FLOOR_Y, 88),
            PurplePuddle(2560, self.FLOOR_Y, 94),
            PurplePuddle(3380, self.FLOOR_Y, 92),
        ]
        self.glass_shards = [
            FallingGlassShard(360, self.FLOOR_Y, 0.00),
            FallingGlassShard(520, self.FLOOR_Y, 0.18),
            FallingGlassShard(760, self.FLOOR_Y, 0.36),
            FallingGlassShard(920, self.FLOOR_Y, 0.54),
            FallingGlassShard(1240, self.FLOOR_Y, 0.24),
            FallingGlassShard(1600, self.FLOOR_Y, 0.42),
            FallingGlassShard(1810, self.FLOOR_Y, 0.10),
            FallingGlassShard(2050, self.FLOOR_Y, 0.58),
            FallingGlassShard(2480, self.FLOOR_Y, 0.30),
            FallingGlassShard(2640, self.FLOOR_Y, 0.48),
            FallingGlassShard(3040, self.FLOOR_Y, 0.16),
            FallingGlassShard(3380, self.FLOOR_Y, 0.40),
            FallingGlassShard(3620, self.FLOOR_Y, 0.62),
        ]
        self.bookworms = [
            Bookworm(170, 360, self.FLOOR_Y, speed=52, style="science"),
            Bookworm(390, 650, self.FLOOR_Y, speed=56, style="science"),
            Bookworm(960, 1230, self.FLOOR_Y, speed=58, style="science"),
            Bookworm(1260, 1360, self.FLOOR_Y, speed=61, style="science"),
            Bookworm(1710, 2030, self.FLOOR_Y, speed=64, style="science"),
            Bookworm(2480, 2820, self.FLOOR_Y, speed=68, style="science"),
            Bookworm(3260, 3640, self.FLOOR_Y, speed=72, style="science"),
        ]
        self.power_block = FlaskQuestionBlock(1110, 374)
        self.flasks = []
        self.gas_clouds = []
        self.throw_cooldown = 0.0
        self.up_was_pressed = False

    def has_floor_below(self, x):
        if x < 0 or x > self.WIDTH:
            return False
        return not any(start <= x <= end for start, end in self.GAPS)

    def support_platforms(self):
        return [
            Platform(glass.rect.copy(), (198, 236, 239), (103, 161, 169), "glass", one_way=True)
            for glass in self.glass_platforms
            if glass.active
        ]

    def try_throw(self, player, keys):
        up_pressed = bool(keys[pygame.K_UP])
        just_pressed = up_pressed and not self.up_was_pressed
        self.up_was_pressed = up_pressed

        if player.has_lab_power and just_pressed and self.throw_cooldown <= 0:
            start_x = player.rect.centerx + player.facing * 12
            start_y = player.rect.centery - 12
            self.flasks.append(ThrownFlask(start_x, start_y, player.facing))
            self.throw_cooldown = 0.65

    def update_before_player(self, dt, player, camera_x=None, keys=None):
        self.power_block.update(dt)
        self.throw_cooldown = max(0.0, self.throw_cooldown - dt)
        self.try_throw(player, keys)

        for glass in self.glass_platforms:
            glass.update(dt)

        for puddle in self.puddles:
            puddle.update_visual(dt)

        for shard in self.glass_shards:
            death = shard.update(dt, player)
            if death:
                return death

        for flask in self.flasks:
            cloud = flask.update(dt, self.FLOOR_Y, self.has_floor_below)
            if cloud:
                self.gas_clouds.append(cloud)
        self.flasks = [flask for flask in self.flasks if flask.active]

        for cloud in self.gas_clouds:
            cloud.update(dt)
            for worm in self.bookworms:
                if not worm.disabled and cloud.rect.colliderect(worm.rect):
                    worm.stun(0.18)
        self.gas_clouds = [cloud for cloud in self.gas_clouds if cloud.active]

        for worm in self.bookworms:
            worm.update(dt, player, self.has_floor_below)
            death = worm.handle_player_contact(player)
            if death:
                return death

        return None

    def update_after_player(self, dt, player, was_stomping=False):
        self.power_block.try_hit_from_below(player)
        self.power_block.try_collect(player)

        for glass in self.glass_platforms:
            glass.register_player(player)

        for puddle in self.puddles:
            if puddle.update(dt, player):
                return "puddle"

        for shard in self.glass_shards:
            if shard.state == "falling" and shard.rect.colliderect(player.rect):
                return "glass_shard"

        for worm in self.bookworms:
            death = worm.handle_player_contact(player)
            if death:
                return death

        return None

    def draw(self, surface, camera_x):
        self.power_block.draw(surface, camera_x)

        for puddle in self.puddles:
            puddle.draw(surface, camera_x)
        for glass in self.glass_platforms:
            glass.draw(surface, camera_x)
        for cloud in self.gas_clouds:
            cloud.draw(surface, camera_x)
        for worm in self.bookworms:
            worm.draw(surface, camera_x)
        for shard in self.glass_shards:
            shard.draw(surface, camera_x)
        for flask in self.flasks:
            flask.draw(surface, camera_x)

class ArtGimmicks:
    FLOOR_Y = SCREEN_H - 72
    WIDTH = 3800
    GAPS = ((560, 745), (1015, 1235), (1510, 1705), (1990, 2215), (2520, 2745), (3120, 3350))

    def __init__(self):
        self.reset()

    def reset(self):
        self.brushes = []

        self.paper_platforms = [
            PaperPlatform(590, 414, 82), PaperPlatform(674, 370, 72),
            PaperPlatform(1048, 414, 84), PaperPlatform(1140, 368, 76),
            PaperPlatform(1542, 414, 82), PaperPlatform(1628, 370, 72),
            PaperPlatform(2552, 414, 84), PaperPlatform(2650, 368, 76),
            PaperPlatform(3154, 414, 82), PaperPlatform(3242, 368, 74),
        ]

        self.paint_traps = [
            RedPaintTrap(420, self.FLOOR_Y, 86),
            RedPaintTrap(820, self.FLOOR_Y, 92),
            RedPaintTrap(1320, self.FLOOR_Y, 86),
            RedPaintTrap(2300, self.FLOOR_Y, 88),
            RedPaintTrap(3420, self.FLOOR_Y, 92),
        ]
        self.power_block = PaletteQuestionBlock(1320, 374)
        self.bookworms = [
            Bookworm(220, 500, self.FLOOR_Y, 54, "art"),
            Bookworm(760, 1000, self.FLOOR_Y, 58, "art"),
            Bookworm(1250, 1480, self.FLOOR_Y, 62, "art"),
            Bookworm(2240, 2500, self.FLOOR_Y, 66, "art"),
            Bookworm(2780, 3080, self.FLOOR_Y, 70, "art"),
            Bookworm(3380, 3670, self.FLOOR_Y, 72, "art"),
        ]
        self.palettes = [
            FlyingPalette(820, self.FLOOR_Y, 125, 132),
            FlyingPalette(1840, self.FLOOR_Y, 145, 146),
            FlyingPalette(2860, self.FLOOR_Y, 135, 138),
        ]
        self.paint_canvases = [
            PaintCanvas(2010, 422, 82),
            PaintCanvas(2110, 372, 78),
        ]
        self.paint_shots = []
        self.spawn_timer = 1.7
        self.shot_cooldown = 0.0
        self.up_was_pressed = False

    def has_floor_below(self, x):
        return 0 <= x <= self.WIDTH and not any(a <= x <= b for a, b in self.GAPS)

    def support_platforms(self):
        supports = []
        for paper in self.paper_platforms:
            if paper.active:
                supports.append(
                    Platform(
                        paper.rect.copy(),
                        (245, 232, 194),
                        (205, 185, 146),
                        "paper",
                        one_way=True,
                    )
                )

        for brush in self.brushes:
            if brush.alive:
                supports.append(Platform(brush.rect.copy(), (203, 159, 99), (232, 92, 116), "brush", one_way=True))
        for canvas in self.paint_canvases:
            if canvas.active:
                supports.append(Platform(canvas.rect.copy(), canvas.color, canvas.color, "paint_canvas", one_way=True))
        return supports

    def spawn_brush(self, camera_x, player_x):
        altitude = random.randint(26, 82)
        y = self.FLOOR_Y - altitude - 5
        x = max(camera_x + SCREEN_W + random.randint(60, 150), player_x + 610)
        self.brushes.append(BrushProjectile(x, y, random.uniform(215, 292)))

    def try_shoot(self, player, keys):
        up_pressed = bool(keys[pygame.K_UP])
        just_pressed = up_pressed and not self.up_was_pressed
        self.up_was_pressed = up_pressed

        if player.has_art_power and just_pressed and self.shot_cooldown <= 0:
            x = player.rect.centerx + player.facing * 20
            y = player.rect.centery - 6
            self.paint_shots.append(PaintShot(x, y, player.facing))
            self.shot_cooldown = 0.28

    def update_before_player(self, dt, player, camera_x, keys):
        self.power_block.update(dt)
        self.shot_cooldown = max(0.0, self.shot_cooldown - dt)
        self.try_shoot(player, keys)

        for paper in self.paper_platforms:
            paper.update(dt)
        for canvas in self.paint_canvases:
            canvas.update(dt)

        self.spawn_timer -= dt
        if player.pos.x > 260 and self.spawn_timer <= 0:
            self.spawn_brush(camera_x, player.pos.x)
            self.spawn_timer = random.uniform(1.8, 3.1)

        for brush in self.brushes:
            brush.update(dt, player)
            if brush.hits_player_from_front(player):
                return "brush"
        self.brushes = [brush for brush in self.brushes if brush.alive]

        for worm in self.bookworms:
            worm.update(dt, player, self.has_floor_below)
            if worm.handle_player_contact(player):
                return "bookworm"
        for palette in self.palettes:
            palette.update(dt, player, self.has_floor_below)
            if palette.handle_player_contact(player):
                return "palette"

        for shot in self.paint_shots:
            shot.update(dt)
            for brush in self.brushes:
                if shot.active and brush.alive and shot.rect.colliderect(brush.rect):
                    shot.active = brush.alive = False
            for worm in self.bookworms:
                if shot.active and not worm.disabled and shot.rect.colliderect(worm.rect):
                    worm.paint_color = shot.color
                    worm.stun(1.35)
                    shot.active = False
            for palette in self.palettes:
                if shot.active and palette.active and shot.rect.colliderect(palette.rect):
                    palette.disable()
                    shot.active = False
            for canvas in self.paint_canvases:
                if shot.active and shot.rect.colliderect(canvas.rect):
                    canvas.activate(shot.color)
                    shot.active = False
        self.paint_shots = [shot for shot in self.paint_shots if shot.active]
        return None

    def update_after_player(self, dt, player, was_stomping=False):
        self.power_block.try_hit_from_below(player)
        self.power_block.try_collect(player)

        for paper in self.paper_platforms:
            paper.register_player(player)

        for trap in self.paint_traps:
            if trap.update(dt, player):
                return "red_paint"

        for brush in self.brushes:
            if brush.hits_player_from_front(player):
                return "brush"
        for worm in self.bookworms:
            if worm.handle_player_contact(player):
                return "bookworm"
        for palette in self.palettes:
            if palette.handle_player_contact(player):
                return "palette"
        return None

    def draw(self, surface, camera_x):
        self.power_block.draw(surface, camera_x)

        for paper in self.paper_platforms:
            paper.draw(surface, camera_x)
        for canvas in self.paint_canvases:
            canvas.draw(surface, camera_x)
        for trap in self.paint_traps:
            trap.draw(surface, camera_x)
        for shot in self.paint_shots:
            shot.draw(surface, camera_x)
        for worm in self.bookworms:
            worm.draw(surface, camera_x)
        for palette in self.palettes:
            palette.draw(surface, camera_x)
        for brush in self.brushes:
            brush.draw(surface, camera_x)

class SoftwareGimmicks:
    FLOOR_Y, WIDTH = SCREEN_H - 72, 4100
    GAPS = ((690, 865), (1260, 1475), (1840, 2390), (2500, 2730), (3180, 3405), (3710, 3885))

    def __init__(self):
        self.reset()

    def reset(self):
        self.platforms = [ErrorCodePlatform(x, y, w) for x, y, w in (
            (725, 414, 82), (805, 370, 72), (1300, 414, 82), (1400, 370, 74),
            (2540, 414, 82), (2640, 370, 74), (3220, 414, 82), (3320, 370, 74),
            (3740, 414, 82), (3830, 370, 72))]
        self.gap_codes = []
        self.gap_spawn_timer = 0.0
        self.traps = [RmRfTrap(x, self.FLOOR_Y) for x in (430, 1010, 1580, 2860, 3490)]
        self.worms = [Bookworm(a, b, self.FLOOR_Y, s, "software") for a, b, s in (
            (170, 390, 56), (900, 1190, 60), (1500, 1830, 64), (2770, 3140, 70), (3420, 3680, 74))]
        self.codes, self.spawn_timer = [], 1.2
        self.power_block = LaptopQuestionBlock(1080, 374)

    def has_floor_below(self, x):
        return 0 <= x <= self.WIDTH and not any(a <= x <= b for a, b in self.GAPS)

    def debugging(self, player, keys):
        return player.has_debug_power and keys and keys[pygame.K_UP]

    def support_platforms(self):
        supports = [Platform(p.rect.copy(), (9, 26, 29), (48, 225, 119), "code", one_way=True) for p in self.platforms if p.active]
        supports += [Platform(c.rect.copy(), (7, 24, 24), (84, 255, 151), "code_attack", one_way=True) for c in self.codes if c.alive]
        supports += [Platform(c.rect.copy(), (7, 24, 24), (84, 255, 151), "code_gap", one_way=True) for c in self.gap_codes if c.alive]
        return supports

    def update_before_player(self, dt, player, camera_x, keys=None):
        self.power_block.update(dt)
        debug = self.debugging(player, keys)
        for p in self.platforms:
            p.update(dt)
        in_gap_zone = 1640 <= player.pos.x <= 2440
        self.gap_spawn_timer = max(0.0, self.gap_spawn_timer - dt)
        if in_gap_zone and not debug and not self.gap_codes and self.gap_spawn_timer <= 0:
            self.gap_codes = [
                CodeProjectile(2390, 420, 132),
                CodeProjectile(2240, 372, 142),
                CodeProjectile(2090, 324, 152),
            ]
            self.gap_spawn_timer = 2.8

        for code in self.gap_codes:
            if not debug:
                code.update(dt, player)
                if code.hits_player_from_front(player):
                    return "code"
        self.gap_codes = [code for code in self.gap_codes if code.alive]

        for worm in self.worms:
            if debug:
                worm.stun(0.18)
            worm.update(dt, player, self.has_floor_below)
            if not debug and worm.handle_player_contact(player):
                return "bookworm"
        self.spawn_timer -= dt
        if not debug and self.spawn_timer <= 0:
            self.codes.append(CodeProjectile(camera_x + SCREEN_W + 70, random.randint(360, 438), random.uniform(220, 285)))
            self.spawn_timer = random.uniform(1.4, 2.5)
        for code in self.codes:
            if not debug:
                code.update(dt, player)
                if code.hits_player_from_front(player):
                    return "code"
        self.codes = [c for c in self.codes if c.alive]
        return None

    def update_after_player(self, dt, player, was_stomping=False):
        keys = pygame.key.get_pressed()
        debug = self.debugging(player, keys)
        self.power_block.try_hit_from_below(player)
        self.power_block.try_collect(player)
        for p in self.platforms:
            p.register_player(player)
        for trap in self.traps:
            if trap.update(dt, player, debug):
                return "rmrf"
        if not debug:
            for code in self.codes + self.gap_codes:
                if code.hits_player_from_front(player):
                    return "code"
            for worm in self.worms:
                if worm.handle_player_contact(player):
                    return "bookworm"
        return None

    def draw(self, surface, camera_x):
        self.power_block.draw(surface, camera_x)
        for p in self.platforms:
            p.draw(surface, camera_x)
        for trap in self.traps:
            trap.draw(surface, camera_x)
        for worm in self.worms:
            worm.draw(surface, camera_x)
        for code in self.codes + self.gap_codes:
            code.draw(surface, camera_x)

class EngineeringGimmicks:
    FLOOR_Y, WIDTH = SCREEN_H - 72, 4400
    GAPS = ((610, 805), (1080, 1315), (1580, 1815), (2080, 2325), (2630, 2875), (3180, 3435), (3750, 3995))

    def __init__(self):
        self.reset()

    def reset(self):
        self.worms = [Bookworm(a, b, self.FLOOR_Y, s, "engineering") for a, b, s in (
            (150, 520, 60), (835, 1040, 64), (1345, 1550, 66), (1845, 2050, 68),
            (2355, 2600, 70), (2905, 3150, 72), (3465, 3720, 74), (4025, 4320, 76))]
        self.presses = [PressMachine(x, self.FLOOR_Y, 72, 138) for x in (915, 1925, 2465, 3570, 4160)]
        self.bolts = [BoltDrop(x, self.FLOOR_Y, d) for x, d in ((520, 0), (1180, .4), (2060, .2), (2550, .6), (3320, .3), (4020, .5))]
        self.spikes = [SpikeTrap(x, self.FLOOR_Y) for x in (390, 1450, 2360, 3660)]
        self.power_block = RobotQuestionBlock(900, 374)

    def has_floor_below(self, x):
        return 0 <= x <= self.WIDTH and not any(a <= x <= b for a, b in self.GAPS)

    def support_platforms(self):
        return []

    def hit_worms(self, player):
        for worm in self.worms:
            if worm.rect.colliderect(player.rect):
                if player.has_robot_power:
                    worm.disable()
                else:
                    return "bookworm"

    def update_before_player(self, dt, player, camera_x, keys=None):
        self.power_block.update(dt)
        for worm in self.worms:
            worm.update(dt, player, self.has_floor_below)
        for press in self.presses:
            press.update(dt, player, self.has_floor_below)
            if press.handle_player_contact(player):
                return "press"
        for bolt in self.bolts:
            if bolt.update(dt, player):
                return "bolt"
        return self.hit_worms(player)

    def update_after_player(self, dt, player, was_stomping=False):
        self.power_block.try_hit_from_below(player)
        self.power_block.try_collect(player)
        if not player.has_robot_power and any(spike.rect.colliderect(player.rect) for spike in self.spikes):
            return "spike"
        return self.hit_worms(player)

    def draw(self, surface, camera_x):
        self.power_block.draw(surface, camera_x)
        for group in (self.spikes, self.worms, self.presses, self.bolts):
            for obj in group:
                obj.draw(surface, camera_x)

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
        elif self.name == "자연과학 대학":
            self.draw_laboratory_background(surface, camera_x)
        elif self.name == "예술 대학":
            self.draw_art_studio_background(surface, camera_x)
        elif self.name == "소프트웨어경영 대학":
            self.draw_server_background(surface, camera_x)
        elif self.name == "창의공과 대학":
            self.draw_factory_background(surface, camera_x)
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

    def draw_laboratory_background(self, surface, camera_x):
        wall_top = (202, 227, 231)
        wall_bottom = (232, 244, 241)
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            color = tuple(int(wall_top[i] * (1 - t) + wall_bottom[i] * t) for i in range(3))
            pygame.draw.line(surface, color, (0, y), (SCREEN_W, y))

        for y in range(88, 360, 54):
            pygame.draw.line(surface, (188, 214, 217), (0, y), (SCREEN_W, y), 1)
        for x in range(-80, SCREEN_W + 100, 120):
            shifted = x - int(camera_x * 0.10) % 120
            pygame.draw.line(surface, (192, 217, 219), (shifted, 88), (shifted, 360), 1)

        for x in range(-120, SCREEN_W + 180, 360):
            shifted = x - int(camera_x * 0.04) % 360
            pygame.draw.rect(surface, (218, 238, 239), (shifted, 34, 166, 16), border_radius=7)
            pygame.draw.rect(surface, (246, 253, 249), (shifted + 9, 39, 148, 6), border_radius=3)

        bench_offset = int(camera_x * 0.18) % 540
        for i in range(-1, 4):
            x = i * 540 - bench_offset + 62
            pygame.draw.rect(surface, (178, 207, 207), (x, 250, 286, 18), border_radius=4)
            pygame.draw.rect(surface, (128, 169, 174), (x, 268, 286, 10))
            pygame.draw.rect(surface, (190, 218, 216), (x + 12, 278, 262, 85), border_radius=4)
            pygame.draw.rect(surface, (151, 188, 190), (x + 96, 278, 5, 85))
            pygame.draw.rect(surface, (151, 188, 190), (x + 184, 278, 5, 85))

            pygame.draw.rect(surface, (144, 177, 181), (x + 34, 218, 5, 33))
            pygame.draw.polygon(surface, (164, 193, 197), [(x + 24, 250), (x + 44, 250), (x + 40, 234), (x + 28, 234)])
            pygame.draw.rect(surface, (188, 172, 208), (x + 27, 242, 14, 7))

            pygame.draw.rect(surface, (144, 177, 181), (x + 232, 225, 34, 5))
            for j in range(4):
                pygame.draw.rect(surface, (173, 199, 201), (x + 236 + j * 8, 205, 4, 22), border_radius=2)

        floor_top = SCREEN_H - 84
        pygame.draw.rect(surface, (166, 199, 201), (0, floor_top, SCREEN_W, 84))
        pygame.draw.rect(surface, (112, 157, 163), (0, floor_top, SCREEN_W, 7))
        for x in range(-80, SCREEN_W + 120, 96):
            shifted = x - int(camera_x * 0.38) % 96
            pygame.draw.line(surface, (145, 181, 184), (shifted, floor_top), (shifted + 28, SCREEN_H), 1)

    def draw_art_studio_background(self, surface, camera_x):
        top = (244, 239, 226)
        bottom = (229, 221, 207)
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
            pygame.draw.line(surface, color, (0, y), (SCREEN_W, y))

        for y in range(72, 392, 32):
            pygame.draw.line(surface, (220, 211, 198), (0, y), (SCREEN_W, y), 1)
        for x in range(-80, SCREEN_W + 120, 52):
            shifted = x - int(camera_x * 0.08) % 52
            pygame.draw.line(surface, (226, 217, 203), (shifted, 72), (shifted, 392), 1)

        offset = int(camera_x * 0.16) % 420
        muted_paints = ((199, 132, 138), (202, 175, 116), (126, 164, 191), (139, 178, 145), (170, 139, 184))
        for i in range(-1, 4):
            x = i * 420 - offset + 78
            pygame.draw.rect(surface, (249, 246, 238), (x, 206, 76, 118), border_radius=3)
            pygame.draw.rect(surface, (165, 145, 135), (x, 206, 76, 118), 3, border_radius=3)
            for j, color in enumerate(muted_paints[:3]):
                pygame.draw.ellipse(surface, color, (x + 13 + j * 16, 242 + (j % 2) * 16, 22, 13))

        bench_offset = int(camera_x * 0.23) % 560
        for i in range(-1, 3):
            x = i * 560 - bench_offset + 185
            pygame.draw.rect(surface, (179, 156, 139), (x, 316, 228, 17), border_radius=3)
            pygame.draw.rect(surface, (145, 122, 111), (x + 14, 333, 12, 84))
            pygame.draw.rect(surface, (145, 122, 111), (x + 202, 333, 12, 84))
            for j, color in enumerate(muted_paints):
                pygame.draw.circle(surface, color, (x + 34 + j * 31, 303), 9)
            pygame.draw.rect(surface, (118, 96, 90), (x + 185, 270, 8, 44))
            pygame.draw.line(surface, (118, 96, 90), (x + 189, 270), (x + 205, 238), 5)

        floor_top = SCREEN_H - 84
        pygame.draw.rect(surface, (196, 181, 165), (0, floor_top, SCREEN_W, 84))
        pygame.draw.rect(surface, (137, 118, 112), (0, floor_top, SCREEN_W, 7))
        for x in range(-80, SCREEN_W + 120, 86):
            shifted = x - int(camera_x * 0.35) % 86
            pygame.draw.line(surface, (176, 159, 148), (shifted, floor_top), (shifted + 18, SCREEN_H), 1)

    def draw_server_background(self, surface, camera_x):
        for y in range(SCREEN_H):
            c = 10 + y * 14 // SCREEN_H
            pygame.draw.line(surface, (c, c + 5, c + 9), (0, y), (SCREEN_W, y))
        offset = int(camera_x * 0.18) % 190
        for i in range(-1, 7):
            x = i * 190 - offset + 28
            pygame.draw.rect(surface, (7, 17, 23), (x, 88, 118, 310), border_radius=4)
            pygame.draw.rect(surface, (42, 74, 81), (x, 88, 118, 310), 2, border_radius=4)
            for y in range(106, 382, 24):
                pygame.draw.rect(surface, (16, 35, 40), (x + 9, y, 100, 15))
                pygame.draw.circle(surface, (55, 227, 126), (x + 20, y + 7), 3)
                pygame.draw.circle(surface, (224, 177, 68), (x + 31, y + 7), 2)
        floor = SCREEN_H - 84
        pygame.draw.rect(surface, (8, 20, 24), (0, floor, SCREEN_W, 84))
        pygame.draw.rect(surface, (47, 116, 99), (0, floor, SCREEN_W, 5))
        for x in range(-80, SCREEN_W + 120, 72):
            pygame.draw.line(surface, (28, 59, 61), (x, floor), (x + 18, SCREEN_H), 1)

    def draw_factory_background(self, surface, camera_x):
        surface.fill((45, 48, 52))
        floor = SCREEN_H - 84
        for i in range(-1, 7):
            x = i * 190 - int(camera_x * .16) % 190 + 40
            y = 150 + (i % 3) * 72
            radius = 28 + (i % 2) * 9
            pygame.draw.circle(surface, (87, 92, 97), (x, y), radius)
            pygame.draw.circle(surface, (39, 42, 45), (x, y), radius, 4)
            angle = pygame.time.get_ticks() * .002 * (-1 if i % 2 else 1)
            for j in range(8):
                a = angle + j * math.pi / 4
                pygame.draw.line(surface, (156, 161, 166), (x, y), (x + math.cos(a) * radius, y + math.sin(a) * radius), 4)
        pygame.draw.rect(surface, (68, 72, 76), (0, floor, SCREEN_W, 84))
        pygame.draw.rect(surface, (188, 140, 63), (0, floor, SCREEN_W, 6))

    def draw_goal(self, surface, camera_x):
        x = int(self.goal_x - camera_x)
        y = SCREEN_H - 185
        pygame.draw.rect(surface, GOLD, (x, y, 12, 92))
        pygame.draw.polygon(surface, RED, [(x + 12, y + 4), (x + 76, y + 25), (x + 12, y + 46)])
        pygame.draw.rect(surface, INK, (x, y, 12, 92), 2)

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
            "subtitle": "위태위험 실험실",
            "theme": ((124, 210, 216), (221, 250, 230), (93, 156, 116)),
            "accent": GREEN,
            "width": 3800,
            "gaps": [(700, 940), (1390, 1680), (2120, 2445), (2880, 3230)],
            "platforms": [],
            "tunnels": [],
            "hurdles": [],
        },
        {
            "name": "예술 대학",
            "subtitle": "우당탕탕 예술 작업실",
            "theme": ((255, 169, 176), (251, 233, 210), (172, 102, 152)),
            "accent": PURPLE,
            "width": 3800,
            "gaps": [(560, 745), (1015, 1235), (1510, 1705), (1990, 2215), (2520, 2745), (3120, 3350)],
            "platforms": [],
            "tunnels": [],
            "hurdles": [],
        },
        {
            "name": "소프트웨어경영 대학",
            "subtitle": "오류가 가득한 어두운 서버실",
            "theme": ((8, 18, 24), (15, 30, 36), (48, 225, 119)),
            "accent": (48, 225, 119),
            "width": 4100,
            "gaps": [(690, 865), (1260, 1475), (1840, 2390), (2500, 2730), (3180, 3405), (3710, 3885)],
            "platforms": [],
            "tunnels": [],
            "hurdles": [],
        },
        {
            "name": "창의공과 대학",
            "subtitle": "뚝딱뚝딱 기계공장",
            "theme": ((45, 48, 52), (68, 72, 76), (188, 140, 63)),
            "accent": (188, 140, 63),
            "width": 4400,
            "gaps": [(610, 805), (1080, 1315), (1580, 1815), (2080, 2325), (2630, 2875), (3180, 3435), (3750, 3995)],
            "platforms": [],
            "tunnels": [],
            "hurdles": [],
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
