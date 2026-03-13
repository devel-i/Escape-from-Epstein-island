"""Escape from Epstein Island - 3D desktop puzzle game (raycasting + pygame)."""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass

try:
    import pygame
except ModuleNotFoundError as exc:
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info >= (3, 14):
        hint = (
            "Для Python 3.14 установите pygame-ce (wheel): \n"
            "  python -m pip install --only-binary=:all: pygame-ce"
        )
    else:
        hint = (
            "Установите pygame-ce (или pygame): \n"
            "  python -m pip install --only-binary=:all: pygame-ce"
        )
    raise SystemExit(f"Не найден модуль pygame (Python {py_ver}).\n{hint}") from exc

SCREEN_W, SCREEN_H = 1280, 720
HALF_H = SCREEN_H // 2
FOV = math.pi / 3
HALF_FOV = FOV / 2
RAYS = 360
MAX_DEPTH = 20
DELTA_ANGLE = FOV / RAYS
SCALE = SCREEN_W // RAYS

MOVE_SPEED = 0.012
SPRINT_MULT = 1.65
STAMINA_MAX = 100.0
STAMINA_DRAIN = 0.10
STAMINA_RECOVERY = 0.06
ROT_SPEED = 0.03
MOUSE_SENSITIVITY_X = 0.0015
MOUSE_SENSITIVITY_Y = 0.20
MAX_PITCH = 120
PLAYER_RADIUS = 0.2

WORLD_MAP = [
    "############",
    "#S...#....E#",
    "#.##.#.##..#",
    "#....#..T..#",
    "#.##.##.##.#",
    "#..T....#..#",
    "#.####..#T.#",
    "#......##..#",
    "############",
]


@dataclass
class Terminal:
    x: float
    y: float
    question: str
    answer: str
    solved: bool = False


class Game3D:
    def __init__(self, headless: bool = False, smoke_frames: int = 0) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Побег с острова Эпштейна — 3D")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 28)
        self.small = pygame.font.SysFont("arial", 22)

        self.map_w = len(WORLD_MAP[0])
        self.map_h = len(WORLD_MAP)
        self.walls: set[tuple[int, int]] = set()
        self.exit_pos = (1.5, 1.5)
        self.terminals: list[Terminal] = []
        self.player_x, self.player_y, self.player_a = 1.5, 1.5, 0.0

        self.keys_collected = 0
        self.win = False
        self.paused = False
        self.stamina = STAMINA_MAX
        self.camera_pitch = 0.0
        self.scene_time = 0.0

        self.story_intro = (
            "Сюжет: ты проник на остров, чтобы угнать катер. Чтобы снять блокировку, "
            "взломай 3 терминала с шуточными квестами."
        )
        self.message = self.story_intro

        self.answer_mode = False
        self.answer_text = ""
        self.active_terminal: Terminal | None = None

        self.headless = headless
        self.smoke_frames = smoke_frames
        if not headless:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)

        self._parse_level()

    def _parse_level(self) -> None:
        qa = [
            (
                "Квест 1/3: Охранник просит пароль от Wi-Fi. Подсказка: "
                "на табличке написано 'чай без сахара'. Введи: chai.",
                "chai",
            ),
            (
                "Квест 2/3: Бармен откажется мешать коктейль, если не назовёшь мем. "
                "Введи классический ответ: eto baza.",
                "eto baza",
            ),
            (
                "Квест 3/3: Диджей отдаст ключ от катера только тому, кто знает язык шейдеров. "
                "Введи один вариант: glsl, hlsl или c++.",
                "glsl",
            ),
        ]
        idx = 0
        for y, row in enumerate(WORLD_MAP):
            for x, cell in enumerate(row):
                if cell == "#":
                    self.walls.add((x, y))
                elif cell == "S":
                    self.player_x, self.player_y = x + 0.5, y + 0.5
                elif cell == "E":
                    self.exit_pos = (x + 0.5, y + 0.5)
                elif cell == "T":
                    q, a = qa[idx]
                    idx += 1
                    self.terminals.append(Terminal(x + 0.5, y + 0.5, q, a))

    def run(self) -> None:
        frame = 0
        while True:
            dt = min(self.clock.tick(60), 33)
            self.scene_time += dt * 0.001
            self._handle_events()
            if not self.answer_mode and not self.win and not self.paused:
                self._update_player(dt)
                self._check_exit()
            self._draw_scene()
            frame += 1
            if self.headless and frame >= self.smoke_frames:
                break

    def _handle_events(self) -> None:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                if self.answer_mode:
                    self.answer_mode = False
                    self.answer_text = ""
                    self.active_terminal = None
                    self.message = "Ввод отменён"
                else:
                    self.paused = not self.paused
            if self.answer_mode and ev.type == pygame.KEYDOWN:
                self._answer_input(ev)
            elif self.paused and ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_p):
                    self.paused = False
                elif ev.key in (pygame.K_q, pygame.K_F10):
                    pygame.quit()
                    sys.exit()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_e:
                self._try_interact()

        if not self.answer_mode and not self.paused and not self.headless:
            mx, my = pygame.mouse.get_rel()
            self.player_a += mx * MOUSE_SENSITIVITY_X
            self.camera_pitch = max(-MAX_PITCH, min(MAX_PITCH, self.camera_pitch - my * MOUSE_SENSITIVITY_Y))

    def _answer_input(self, ev: pygame.event.Event) -> None:
        if ev.key == pygame.K_RETURN and self.active_terminal:
            ans = self.answer_text.strip().lower()
            valid_answers = {self.active_terminal.answer}
            if self.active_terminal.answer == "glsl":
                valid_answers = {"glsl", "hlsl", "c++"}
            if ans in valid_answers:
                if not self.active_terminal.solved:
                    self.active_terminal.solved = True
                    self.keys_collected += 1
                self.message = f"Квест выполнен ({self.keys_collected}/3). Следуй к следующему терминалу."
            else:
                self.message = "Шутка не засчитана. Попробуй ещё раз"
            self.answer_mode = False
            self.answer_text = ""
            self.active_terminal = None
            return
        if ev.key == pygame.K_BACKSPACE:
            self.answer_text = self.answer_text[:-1]
        elif ev.unicode and ev.unicode.isprintable():
            self.answer_text += ev.unicode

    def _update_player(self, dt: int) -> None:
        keys = pygame.key.get_pressed()
        sin_a = math.sin(self.player_a)
        cos_a = math.cos(self.player_a)

        moving = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_s] or keys[pygame.K_DOWN] or keys[pygame.K_a] or keys[pygame.K_d]
        sprinting = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.stamina > 0 and moving
        if sprinting:
            speed = MOVE_SPEED * SPRINT_MULT * dt
            self.stamina = max(0.0, self.stamina - dt * STAMINA_DRAIN)
        else:
            speed = MOVE_SPEED * dt
            self.stamina = min(STAMINA_MAX, self.stamina + dt * STAMINA_RECOVERY)
        dx = dy = 0.0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dx += cos_a * speed
            dy += sin_a * speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dx -= cos_a * speed
            dy -= sin_a * speed
        if keys[pygame.K_a]:
            dx += sin_a * speed
            dy -= cos_a * speed
        if keys[pygame.K_d]:
            dx -= sin_a * speed
            dy += cos_a * speed
        if keys[pygame.K_LEFT]:
            self.player_a -= ROT_SPEED * dt
        if keys[pygame.K_RIGHT]:
            self.player_a += ROT_SPEED * dt

        self._move_with_collision(dx, dy)

    def _move_with_collision(self, dx: float, dy: float) -> None:
        nx = self.player_x + dx
        ny = self.player_y + dy

        if not self._is_wall(nx, self.player_y):
            self.player_x = nx
        if not self._is_wall(self.player_x, ny):
            self.player_y = ny

    def _is_wall(self, x: float, y: float) -> bool:
        tx, ty = int(x), int(y)
        return (tx, ty) in self.walls

    def _try_interact(self) -> None:
        for t in self.terminals:
            if math.dist((self.player_x, self.player_y), (t.x, t.y)) < 1.2:
                if t.solved:
                    self.message = "Терминал уже взломан"
                else:
                    self.answer_mode = True
                    self.active_terminal = t
                    self.message = t.question
                return
        self.message = "Рядом нет терминала"

    def _check_exit(self) -> None:
        if math.dist((self.player_x, self.player_y), self.exit_pos) < 0.6:
            if self.keys_collected >= 3:
                self.win = True
                self.message = "Победа! Все квесты закрыты, катер заведён, остров позади."
            else:
                self.message = f"Выход заблокирован: {self.keys_collected}/3 ключей"

    def _ray_cast(self) -> list[tuple[int, int, int, tuple[int, int, int]]]:
        walls_to_draw = []
        start_angle = self.player_a - HALF_FOV
        for ray in range(RAYS):
            ray_angle = start_angle + ray * DELTA_ANGLE
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)
            depth = 0.02
            hit = False
            hit_x = hit_y = 0.0
            while depth < MAX_DEPTH and not hit:
                x = self.player_x + cos_a * depth
                y = self.player_y + sin_a * depth
                if self._is_wall(x, y):
                    hit = True
                    hit_x, hit_y = x, y
                    corrected = depth * math.cos(self.player_a - ray_angle)
                    wall_h = min(int(900 / max(corrected, 0.0001)), SCREEN_H)

                    tex = (hit_x - int(hit_x)) if abs(cos_a) > abs(sin_a) else (hit_y - int(hit_y))
                    stripe = 35 * abs(math.sin(tex * math.pi * 5 + self.scene_time * 3.0))
                    base = max(35, 240 - int(corrected * 24))
                    color = (int(base * 0.40 + stripe), int(base * 0.48 + stripe), int(base * 0.70 + stripe))
                    walls_to_draw.append((ray * SCALE, wall_h, int(corrected), color))
                depth += 0.02
            if not hit:
                walls_to_draw.append((ray * SCALE, 0, MAX_DEPTH, (0, 0, 0)))
        return walls_to_draw

    def _draw_background(self) -> int:
        horizon = HALF_H + int(self.camera_pitch)
        horizon = max(120, min(SCREEN_H - 120, horizon))

        for y in range(0, horizon):
            t = y / max(horizon, 1)
            col = (int(6 + 24 * t), int(12 + 48 * t), int(34 + 110 * t))
            pygame.draw.line(self.screen, col, (0, y), (SCREEN_W, y))

        for i in range(40):
            drift = int((self.scene_time * 12 + i * 31) % SCREEN_W)
            sx = (i * 193 + drift) % SCREEN_W
            sy = (i * 107) % max(40, horizon - 12)
            star = 140 + (i * 17) % 110
            pygame.draw.circle(self.screen, (star, star, star), (sx, sy), 1)

        moon_x = SCREEN_W - 170 + int(math.sin(self.scene_time * 0.5) * 35)
        moon_y = 120 + int(math.cos(self.scene_time * 0.35) * 9)
        pygame.draw.circle(self.screen, (230, 215, 150), (moon_x, moon_y), 42)

        cloud_wobble = int(math.sin(self.scene_time) * 8)
        for i in range(4):
            cx = int((self.scene_time * (30 + i * 8) + i * 290) % (SCREEN_W + 300) - 220)
            cy = 84 + i * 30 + cloud_wobble
            pygame.draw.ellipse(self.screen, (70, 84, 120), (cx, cy, 180, 38))

        for y in range(horizon, SCREEN_H):
            t = (y - horizon) / max(SCREEN_H - horizon, 1)
            shimmer = int(10 * math.sin(self.scene_time * 2.0 + y * 0.03))
            col = (int(18 + 30 * t), int(24 + 28 * t + shimmer), int(36 + 26 * t + shimmer))
            pygame.draw.line(self.screen, col, (0, y), (SCREEN_W, y))

        for i in range(1, 12):
            yy = horizon + int(i * i * 1.6)
            if yy < SCREEN_H:
                pulse = int(10 * math.sin(self.scene_time * 2.2 + i))
                pygame.draw.line(self.screen, (38 + pulse, 46 + pulse, 62 + pulse), (0, yy), (SCREEN_W, yy), 1)

        return horizon

    def _draw_sprites(self, center_y: int) -> None:
        objects: list[tuple[float, pygame.Rect, tuple[int, int, int]]] = []

        for t in self.terminals:
            dx = t.x - self.player_x
            dy = t.y - self.player_y
            dist = math.hypot(dx, dy)
            angle = math.atan2(dy, dx) - self.player_a
            while angle > math.pi:
                angle -= 2 * math.pi
            while angle < -math.pi:
                angle += 2 * math.pi
            if abs(angle) < HALF_FOV + 0.25 and dist > 0.2:
                proj = int(520 / dist)
                sx = int((angle + HALF_FOV) / FOV * SCREEN_W)
                rect = pygame.Rect(sx - proj // 4, center_y - proj // 2, proj // 2, proj)
                pulse = int(30 * (1 + math.sin(self.scene_time * 4 + dist)))
                color = (80, min(255, 190 + pulse), 120) if t.solved else (184, 120 + pulse // 2, 255)
                objects.append((dist, rect, color))

        dx = self.exit_pos[0] - self.player_x
        dy = self.exit_pos[1] - self.player_y
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx) - self.player_a
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        if abs(angle) < HALF_FOV + 0.25 and dist > 0.2:
            proj = int(580 / dist)
            sx = int((angle + HALF_FOV) / FOV * SCREEN_W)
            rect = pygame.Rect(sx - proj // 3, center_y - proj // 2, int(proj / 1.5), proj)
            pulse = int(25 * (1 + math.sin(self.scene_time * 3.0)))
            color = (100, min(255, 180 + pulse), 120) if self.keys_collected >= 3 else (180 + pulse // 2, 80, 80)
            objects.append((dist, rect, color))

        for dist, rect, color in sorted(objects, key=lambda x: x[0], reverse=True):
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            glow = max(0, 120 - int(dist * 22))
            if glow > 0:
                pygame.draw.rect(self.screen, (glow, glow, glow), rect, 1, border_radius=8)

    def _draw_minimap(self) -> None:
        mm_w, mm_h = 240, 162
        mm_x, mm_y = SCREEN_W - mm_w - 16, SCREEN_H - mm_h - 16
        panel_col = (10, 12, 22 + int(8 * math.sin(self.scene_time * 3)))
        pygame.draw.rect(self.screen, panel_col, (mm_x, mm_y, mm_w, mm_h), border_radius=10)
        pygame.draw.rect(self.screen, (90, 120, 170), (mm_x, mm_y, mm_w, mm_h), 1, border_radius=10)

        sx = (mm_w - 20) / self.map_w
        sy = (mm_h - 20) / self.map_h
        ox, oy = mm_x + 10, mm_y + 10

        for wx, wy in self.walls:
            pygame.draw.rect(self.screen, (64, 77, 105), (ox + wx * sx, oy + wy * sy, sx, sy))

        for t in self.terminals:
            col = (70, 200, 115) if t.solved else (185, 120, 240)
            pygame.draw.circle(self.screen, col, (int(ox + t.x * sx), int(oy + t.y * sy)), 4)

        pygame.draw.circle(
            self.screen,
            (245, 235, 95),
            (int(ox + self.exit_pos[0] * sx), int(oy + self.exit_pos[1] * sy)),
            4,
        )

        px, py = ox + self.player_x * sx, oy + self.player_y * sy
        pygame.draw.circle(self.screen, (240, 110, 100), (int(px), int(py)), 4)
        pygame.draw.line(
            self.screen,
            (240, 110, 100),
            (px, py),
            (px + math.cos(self.player_a) * 13, py + math.sin(self.player_a) * 13),
            2,
        )

    def _draw_scene(self) -> None:
        center_y = self._draw_background()

        for x, wall_h, distance, color in self._ray_cast():
            if wall_h <= 0:
                continue
            top = center_y - wall_h // 2
            fog = max(0, min(120, distance * 8))
            shaded = (
                max(0, color[0] - fog),
                max(0, color[1] - fog),
                max(0, color[2] - fog),
            )
            pygame.draw.rect(self.screen, shaded, (x, top, SCALE + 1, wall_h))
            pygame.draw.rect(self.screen, (20, 25, 35), (x, top, SCALE + 1, 1))

        self._draw_sprites(center_y)
        self._draw_ui()
        self._draw_minimap()

        vignette = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (0, 0, 0, 0), (0, 0, SCREEN_W, SCREEN_H), border_radius=0)
        pygame.draw.rect(vignette, (0, 0, 0, 58), (0, 0, SCREEN_W, SCREEN_H), 24)
        self.screen.blit(vignette, (0, 0))

        pygame.display.flip()

    def _draw_wrapped_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        x: int,
        y: int,
        max_w: int,
        max_lines: int,
    ) -> int:
        words = text.split()
        lines: list[str] = []
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if font.size(test)[0] <= max_w:
                line = test
            else:
                lines.append(line)
                line = word
            if len(lines) >= max_lines:
                break
        if line and len(lines) < max_lines:
            lines.append(line)

        used_h = 0
        for chunk in lines:
            surf = font.render(chunk, True, color)
            self.screen.blit(surf, (x, y + used_h))
            used_h += surf.get_height() + 4
        return used_h

    def _draw_ui(self) -> None:
        bar_h = 116
        pygame.draw.rect(self.screen, (8, 11, 20), (0, SCREEN_H - bar_h, SCREEN_W, bar_h))
        self.screen.blit(self.font.render(f"Ключи: {self.keys_collected}/3", True, (230, 236, 255)), (20, SCREEN_H - 102))
        self._draw_wrapped_text(self.message, self.small, (184, 196, 234), 20, SCREEN_H - 66, 740, 2)

        objective = "Цель: найти 3 терминала и открыть катер" if not self.win else "Цель выполнена: остров покинут"
        self.screen.blit(self.small.render(objective, True, (164, 200, 255)), (20, SCREEN_H - 32))

        stamina_col = (110, 220, 255) if self.stamina > 25 else (255, 170, 90)
        pygame.draw.rect(self.screen, (20, 30, 44), (700, SCREEN_H - 26, 220, 10), border_radius=5)
        pygame.draw.rect(
            self.screen,
            stamina_col,
            (700, SCREEN_H - 26, int(220 * (self.stamina / STAMINA_MAX)), 10),
            border_radius=5,
        )
        self.screen.blit(self.small.render("Выносливость (Shift)", True, (160, 173, 210)), (928, SCREEN_H - 37))

        if self.answer_mode and self.active_terminal:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 165))
            self.screen.blit(overlay, (0, 0))
            box = pygame.Rect(96, 164, 1088, 316)
            pygame.draw.rect(self.screen, (18, 26, 50), box, border_radius=14)
            pygame.draw.rect(self.screen, (122, 199, 255), box, 2, border_radius=14)
            self.screen.blit(self.font.render("Терминал квестов", True, (240, 244, 255)), (box.x + 24, box.y + 22))
            self._draw_wrapped_text(
                self.active_terminal.question,
                self.small,
                (224, 231, 255),
                box.x + 24,
                box.y + 78,
                box.width - 48,
                5,
            )
            field = pygame.Rect(box.x + 24, box.y + 204, box.width - 48, 52)
            pygame.draw.rect(self.screen, (11, 17, 32), field, border_radius=8)
            pygame.draw.rect(self.screen, (122, 199, 255), field, 2, border_radius=8)
            self.screen.blit(self.small.render(self.answer_text, True, (240, 244, 255)), (field.x + 12, field.y + 14))
            self.screen.blit(
                self.small.render("Enter — подтвердить, Esc — отменить", True, (160, 173, 210)),
                (box.x + 24, box.y + 270),
            )

        if self.paused and not self.answer_mode:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 175))
            self.screen.blit(overlay, (0, 0))
            panel = pygame.Rect(SCREEN_W // 2 - 230, SCREEN_H // 2 - 130, 460, 260)
            pygame.draw.rect(self.screen, (12, 18, 32), panel, border_radius=14)
            pygame.draw.rect(self.screen, (122, 199, 255), panel, 2, border_radius=14)
            self.screen.blit(self.font.render("ПАУЗА", True, (240, 245, 255)), (panel.x + 165, panel.y + 26))
            self.screen.blit(self.small.render("Enter / P — продолжить", True, (200, 220, 255)), (panel.x + 92, panel.y + 104))
            self.screen.blit(self.small.render("Q / F10 — выход", True, (200, 220, 255)), (panel.x + 128, panel.y + 144))
            self.screen.blit(self.small.render("Мышь X/Y — обзор", True, (200, 220, 255)), (panel.x + 132, panel.y + 184))

        if self.win:
            text = self.font.render("ПОБЕДА! Нажмите ESC для паузы/выхода", True, (145, 242, 167))
            self.screen.blit(text, (SCREEN_W // 2 - text.get_width() // 2, 24))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless-smoke", type=int, default=0, help="run N frames and exit")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    headless = args.headless_smoke > 0
    if headless:
        import os

        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    Game3D(headless=headless, smoke_frames=args.headless_smoke).run()
