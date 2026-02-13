"""Escape from Epstein Island - desktop 2D game (Python + Pygame)."""

from __future__ import annotations

import sys
from dataclasses import dataclass

import pygame

WIDTH, HEIGHT = 960, 640
TILE = 48
FPS = 60

BG = (15, 21, 38)
WALL = (33, 47, 83)
FLOOR = (22, 32, 56)
PLAYER_COLOR = (122, 199, 255)
EXIT_LOCKED = (130, 80, 80)
EXIT_OPEN = (90, 180, 100)
TERMINAL_COLOR = (184, 147, 255)
TEXT = (240, 244, 255)

LEVEL = [
    "####################",
    "#S....#...........E#",
    "#.##.#.#.######.##.#",
    "#....#.#......#....#",
    "#.####.######.#.##.#",
    "#......T..#...#..T.#",
    "#.#######.#.#####..#",
    "#....T....#........#",
    "####################",
]


@dataclass
class Terminal:
    x: int
    y: int
    prompt: str
    answer: str
    solved: bool = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x * TILE + 8, self.y * TILE + 8, TILE - 16, TILE - 16)


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Побег с острова Эпштейна — 2D Desktop")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)
        self.small_font = pygame.font.SysFont("arial", 18)

        self.walls: set[tuple[int, int]] = set()
        self.exit_pos = (0, 0)
        self.player = pygame.Rect(0, 0, TILE - 14, TILE - 14)
        self.terminals: list[Terminal] = []
        self.keys = 0
        self.message = "WASD/стрелки — движение, E — взаимодействие, Enter — ответ"
        self.answer_mode = False
        self.answer_text = ""
        self.active_terminal: Terminal | None = None
        self.win = False

        self._parse_level()

    def _parse_level(self) -> None:
        prompts = [
            ("Я нечётное число. Убери одну букву — стану even. Ответ?", "семь"),
            ("2+2*2 = ?", "6"),
            ("Столица Франции?", "париж"),
        ]
        i = 0
        for y, row in enumerate(LEVEL):
            for x, cell in enumerate(row):
                if cell == "#":
                    self.walls.add((x, y))
                elif cell == "S":
                    self.player.x = x * TILE + 7
                    self.player.y = y * TILE + 7
                elif cell == "E":
                    self.exit_pos = (x, y)
                elif cell == "T":
                    prompt, answer = prompts[i]
                    i += 1
                    self.terminals.append(Terminal(x, y, prompt, answer))

    def run(self) -> None:
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            if not self.answer_mode and not self.win:
                self.update_player()
                self.check_exit()
            self.draw()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.answer_mode:
                    self._handle_answer_input(event)
                elif event.key == pygame.K_e:
                    self.try_interact()

    def _handle_answer_input(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_RETURN and self.active_terminal:
            normalized = self.answer_text.strip().lower()
            if normalized == self.active_terminal.answer:
                if not self.active_terminal.solved:
                    self.active_terminal.solved = True
                    self.keys += 1
                self.message = f"Верно! Ключ-карта получена ({self.keys}/3)."
            else:
                self.message = "Неверный ответ. Попробуй ещё раз позже."
            self.answer_mode = False
            self.answer_text = ""
            self.active_terminal = None
            return
        if event.key == pygame.K_BACKSPACE:
            self.answer_text = self.answer_text[:-1]
            return
        if event.unicode and event.unicode.isprintable():
            self.answer_text += event.unicode

    def update_player(self) -> None:
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        speed = 4

        if dx:
            self.player.x += dx * speed
            if self.collides_wall():
                self.player.x -= dx * speed
        if dy:
            self.player.y += dy * speed
            if self.collides_wall():
                self.player.y -= dy * speed

    def collides_wall(self) -> bool:
        points = [
            (self.player.left // TILE, self.player.top // TILE),
            ((self.player.right - 1) // TILE, self.player.top // TILE),
            (self.player.left // TILE, (self.player.bottom - 1) // TILE),
            ((self.player.right - 1) // TILE, (self.player.bottom - 1) // TILE),
        ]
        return any(p in self.walls for p in points)

    def try_interact(self) -> None:
        player_tile = (self.player.centerx // TILE, self.player.centery // TILE)
        for terminal in self.terminals:
            if abs(terminal.x - player_tile[0]) + abs(terminal.y - player_tile[1]) <= 1:
                if terminal.solved:
                    self.message = "Этот терминал уже взломан."
                else:
                    self.answer_mode = True
                    self.active_terminal = terminal
                    self.message = terminal.prompt
                return
        self.message = "Рядом нет терминала."

    def check_exit(self) -> None:
        tile = (self.player.centerx // TILE, self.player.centery // TILE)
        if tile == self.exit_pos:
            if self.keys >= 3:
                self.win = True
                self.message = "Победа! Ты собрал ключ-карты и покинул остров."
            else:
                self.message = f"Дверь закрыта. Нужно 3 ключ-карты, сейчас: {self.keys}."

    def draw(self) -> None:
        self.screen.fill(BG)
        for y, row in enumerate(LEVEL):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                if cell == "#":
                    pygame.draw.rect(self.screen, WALL, rect)
                else:
                    pygame.draw.rect(self.screen, FLOOR, rect)

        for terminal in self.terminals:
            color = (90, 180, 100) if terminal.solved else TERMINAL_COLOR
            pygame.draw.rect(self.screen, color, terminal.rect, border_radius=8)

        ex, ey = self.exit_pos
        exit_rect = pygame.Rect(ex * TILE + 8, ey * TILE + 8, TILE - 16, TILE - 16)
        pygame.draw.rect(self.screen, EXIT_OPEN if self.keys >= 3 else EXIT_LOCKED, exit_rect, border_radius=6)

        pygame.draw.rect(self.screen, PLAYER_COLOR, self.player, border_radius=8)

        ui_y = len(LEVEL) * TILE + 8
        pygame.draw.rect(self.screen, (10, 14, 26), (0, ui_y - 6, WIDTH, HEIGHT - ui_y + 6))
        self.screen.blit(self.font.render(f"Ключ-карты: {self.keys}/3", True, TEXT), (16, ui_y))
        self.screen.blit(self.small_font.render(self.message[:92], True, TEXT), (16, ui_y + 34))

        if self.answer_mode and self.active_terminal:
            self._draw_answer_modal()
        if self.win:
            self._draw_win_overlay()

        pygame.display.flip()

    def _draw_answer_modal(self) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        box = pygame.Rect(130, 170, 700, 250)
        pygame.draw.rect(self.screen, (22, 32, 56), box, border_radius=12)
        pygame.draw.rect(self.screen, (122, 199, 255), box, 2, border_radius=12)

        prompt = self.active_terminal.prompt if self.active_terminal else ""
        self.screen.blit(self.font.render("Терминал безопасности", True, TEXT), (box.x + 20, box.y + 18))
        self.screen.blit(self.small_font.render(prompt[:80], True, TEXT), (box.x + 20, box.y + 64))

        input_rect = pygame.Rect(box.x + 20, box.y + 112, box.width - 40, 44)
        pygame.draw.rect(self.screen, (9, 15, 30), input_rect, border_radius=8)
        pygame.draw.rect(self.screen, (122, 199, 255), input_rect, 2, border_radius=8)
        self.screen.blit(self.font.render(self.answer_text, True, TEXT), (input_rect.x + 10, input_rect.y + 10))

        hint = "Введите ответ и нажмите Enter"
        self.screen.blit(self.small_font.render(hint, True, (176, 184, 216)), (box.x + 20, box.y + 170))

    def _draw_win_overlay(self) -> None:
        text = self.font.render("Побег выполнен! Нажми Esc для выхода.", True, (145, 242, 167))
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 18))


if __name__ == "__main__":
    Game().run()
