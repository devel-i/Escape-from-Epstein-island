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
<<<<<<< 8fqa7b-codex/adapt-launch-for-multiple-platforms
            "Для Python 3.14 установите pygame-ce (wheel): \n"
            "  python -m pip install --only-binary=:all: pygame-ce"
        )
    else:
        hint = (
            "Установите pygame-ce (или pygame): \n"
            "  python -m pip install --only-binary=:all: pygame-ce"
        )
=======
            "Для Python 3.14 установите pygame-ce: \n"
            "  python -m pip install pygame-ce"
        )
    else:
        hint = "Установите pygame: \n  python -m pip install pygame"
>>>>>>> main
    raise SystemExit(f"Не найден модуль pygame (Python {py_ver}).\n{hint}") from exc

SCREEN_W, SCREEN_H = 1280, 720
HALF_H = SCREEN_H // 2
FOV = math.pi / 3
HALF_FOV = FOV / 2
RAYS = 360
MAX_DEPTH = 20
DELTA_ANGLE = FOV / RAYS
SCALE = SCREEN_W // RAYS

MOVE_SPEED = 0.035
ROT_SPEED = 0.03
MOUSE_SENSITIVITY = 0.0015
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
        self.message = "WASD/стрелки — идти, E — терминал, мышь — обзор"

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
                "[18+] Ночной клуб закрылся в 02:00, бармен ушёл в 02:15. "
                "Сколько минут бармен был сверхурочно?",
                "15",
            ),
            (
                "Чёрный юмор: у оптимиста стакан наполовину полон, у пессимиста — наполовину пуст. "
                "А у программиста он переполнен на сколько процентов?",
                "200",
            ),
            (
                "Сложный шифр: если А=1, Б=2, ... Я=33, то чему равна сумма букв в слове 'КОД'?",
                "27",
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
            self._handle_events()
            if not self.answer_mode and not self.win:
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
                pygame.quit()
                sys.exit()
            if self.answer_mode and ev.type == pygame.KEYDOWN:
                self._answer_input(ev)
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_e:
                self._try_interact()

        if not self.answer_mode and not self.headless:
            mx = pygame.mouse.get_rel()[0]
            self.player_a += mx * MOUSE_SENSITIVITY

    def _answer_input(self, ev: pygame.event.Event) -> None:
        if ev.key == pygame.K_RETURN and self.active_terminal:
            ans = self.answer_text.strip().lower()
            if ans == self.active_terminal.answer:
                if not self.active_terminal.solved:
                    self.active_terminal.solved = True
                    self.keys_collected += 1
                self.message = f"Доступ получен ({self.keys_collected}/3)"
            else:
                self.message = "Неверный код терминала"
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

        speed = MOVE_SPEED * dt
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
                self.message = "Победа! Ты запустил катер и сбежал с острова."
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
                    stripe = 35 * abs(math.sin(tex * math.pi * 5))
                    base = max(35, 240 - int(corrected * 24))
                    color = (int(base * 0.38 + stripe), int(base * 0.45 + stripe), int(base * 0.62 + stripe))
                    walls_to_draw.append((ray * SCALE, wall_h, int(corrected), color))
                depth += 0.02
            if not hit:
                walls_to_draw.append((ray * SCALE, 0, MAX_DEPTH, (0, 0, 0)))
        return walls_to_draw

    def _draw_background(self) -> None:
        for y in range(HALF_H):
            t = y / HALF_H
            col = (int(8 + 30 * t), int(10 + 45 * t), int(30 + 90 * t))
            pygame.draw.line(self.screen, col, (0, y), (SCREEN_W, y))

        for y in range(HALF_H, SCREEN_H):
            t = (y - HALF_H) / HALF_H
            col = (int(20 + 25 * t), int(28 + 24 * t), int(38 + 22 * t))
            pygame.draw.line(self.screen, col, (0, y), (SCREEN_W, y))

        pygame.draw.circle(self.screen, (230, 215, 150), (SCREEN_W - 170, 120), 42)

    def _draw_sprites(self) -> None:
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
                rect = pygame.Rect(sx - proj // 4, HALF_H - proj // 2, proj // 2, proj)
                color = (80, 220, 120) if t.solved else (184, 147, 255)
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
            rect = pygame.Rect(sx - proj // 3, HALF_H - proj // 2, int(proj / 1.5), proj)
            color = (100, 210, 120) if self.keys_collected >= 3 else (180, 80, 80)
            objects.append((dist, rect, color))

        for dist, rect, color in sorted(objects, key=lambda x: x[0], reverse=True):
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            glow = max(0, 120 - int(dist * 22))
            if glow > 0:
                pygame.draw.rect(self.screen, (glow, glow, glow), rect, 1, border_radius=8)

    def _draw_minimap(self) -> None:
        mm_w, mm_h = 210, 150
        mm_x, mm_y = SCREEN_W - mm_w - 16, SCREEN_H - mm_h - 16
        pygame.draw.rect(self.screen, (10, 12, 22), (mm_x, mm_y, mm_w, mm_h), border_radius=10)
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
        self._draw_background()

        for x, wall_h, distance, color in self._ray_cast():
            if wall_h <= 0:
                continue
            top = HALF_H - wall_h // 2
            fog = max(0, min(120, distance * 8))
            shaded = (
                max(0, color[0] - fog),
                max(0, color[1] - fog),
                max(0, color[2] - fog),
            )
            pygame.draw.rect(self.screen, shaded, (x, top, SCALE + 1, wall_h))
            pygame.draw.rect(self.screen, (20, 25, 35), (x, top, SCALE + 1, 1))

        self._draw_sprites()
        self._draw_ui()
        self._draw_minimap()
        pygame.display.flip()

    def _draw_ui(self) -> None:
        bar_h = 112
        pygame.draw.rect(self.screen, (8, 11, 20), (0, SCREEN_H - bar_h, SCREEN_W, bar_h))
        self.screen.blit(self.font.render(f"Ключи: {self.keys_collected}/3", True, (230, 236, 255)), (20, SCREEN_H - 98))
        self.screen.blit(self.small.render(self.message[:100], True, (184, 196, 234)), (20, SCREEN_H - 58))

        if self.answer_mode and self.active_terminal:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 165))
            self.screen.blit(overlay, (0, 0))
            box = pygame.Rect(110, 176, 1060, 290)
            pygame.draw.rect(self.screen, (18, 26, 50), box, border_radius=14)
            pygame.draw.rect(self.screen, (122, 199, 255), box, 2, border_radius=14)
            self.screen.blit(self.font.render("Терминал безопасности", True, (240, 244, 255)), (box.x + 24, box.y + 24))
            self.screen.blit(self.small.render(self.active_terminal.question[:100], True, (224, 231, 255)), (box.x + 24, box.y + 86))
            field = pygame.Rect(box.x + 24, box.y + 150, box.width - 48, 50)
            pygame.draw.rect(self.screen, (11, 17, 32), field, border_radius=8)
            pygame.draw.rect(self.screen, (122, 199, 255), field, 2, border_radius=8)
            self.screen.blit(self.small.render(self.answer_text, True, (240, 244, 255)), (field.x + 12, field.y + 14))
            self.screen.blit(self.small.render("Enter — подтвердить", True, (160, 173, 210)), (box.x + 24, box.y + 222))

        if self.win:
            text = self.font.render("ПОБЕДА! Нажмите ESC для выхода.", True, (145, 242, 167))
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
