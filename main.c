#include "raylib.h"
#include "raymath.h"

#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#define SCREEN_W 1600
#define SCREEN_H 900
#define MAP_W 15
#define MAP_H 11
#define TERMINAL_COUNT 3
#define WORLD_OBJECTS 18

static const char *WORLD_MAP[MAP_H] = {
    "###############",
    "#S.....#.....E#",
    "#.###..#..##..#",
    "#...T.....#...#",
    "#.###.###.#.#.#",
    "#.....#...#...#",
    "#.###.#.###.###",
    "#..T..#....T..#",
    "#.###.#######.#",
    "#.............#",
    "###############"
};

typedef struct {
    Vector3 pos;
    const char *question;
    const char *answer;
    bool solved;
    float pulse;
} Terminal;

typedef struct {
    Vector3 pos;
    float bob;
    float scale;
} Decoration;

typedef struct {
    Camera3D cam;
    Terminal terminals[TERMINAL_COUNT];
    Decoration decor[WORLD_OBJECTS];
    int solvedCount;
    bool win;
    bool showInput;
    int activeTerminal;
    char input[64];
    int inputLen;
    char message[220];
    float stamina;
    float timer;
} GameState;

static bool IsWall(float x, float z) {
    int tx = (int)floorf(x);
    int tz = (int)floorf(z);
    if (tx < 0 || tz < 0 || tx >= MAP_W || tz >= MAP_H) {
        return true;
    }
    return WORLD_MAP[tz][tx] == '#';
}

static void TryMove(Camera3D *cam, Vector3 delta) {
    Vector3 nextPos = Vector3Add(cam->position, delta);
    Vector3 nextTarget = Vector3Add(cam->target, delta);

    if (!IsWall(nextPos.x, cam->position.z)) {
        cam->position.x = nextPos.x;
        cam->target.x = nextTarget.x;
    }
    if (!IsWall(cam->position.x, nextPos.z)) {
        cam->position.z = nextPos.z;
        cam->target.z = nextTarget.z;
    }
}

static void InitGame(GameState *g) {
    memset(g, 0, sizeof(*g));

    g->cam.position = (Vector3){1.5f, 1.75f, 1.5f};
    g->cam.target = (Vector3){2.5f, 1.6f, 1.5f};
    g->cam.up = (Vector3){0.0f, 1.0f, 0.0f};
    g->cam.fovy = 80.0f;
    g->cam.projection = CAMERA_PERSPECTIVE;

    g->terminals[0] = (Terminal){(Vector3){4.5f, 1.0f, 3.5f}, "Терминал 1/3: какой язык чаще всего используют в низкоуровневых движках?", "c", false, 0.0f};
    g->terminals[1] = (Terminal){(Vector3){3.5f, 1.0f, 7.5f}, "Терминал 2/3: какой API чаще всего используют для кроссплатформенного рендера?", "vulkan", false, 1.4f};
    g->terminals[2] = (Terminal){(Vector3){11.5f, 1.0f, 7.5f}, "Терминал 3/3: как называется этап преобразования вершин в GPU-пайплайне?", "vertex shader", false, 2.2f};

    for (int i = 0; i < WORLD_OBJECTS; i++) {
        g->decor[i].pos = (Vector3){2.0f + (float)((i * 7) % 11), 0.5f, 2.0f + (float)((i * 5) % 7)};
        g->decor[i].bob = (float)i * 0.37f;
        g->decor[i].scale = 0.35f + (float)(i % 4) * 0.08f;
    }

    strcpy(g->message, "Задача: взломай 3 терминала и доберись до дока.");
    g->stamina = 100.0f;
    g->activeTerminal = -1;
}

static void HandleTerminalInput(GameState *g) {
    int key = GetCharPressed();
    while (key > 0) {
        if (key >= 32 && key <= 125 && g->inputLen < 63) {
            g->input[g->inputLen++] = (char)key;
            g->input[g->inputLen] = '\0';
        }
        key = GetCharPressed();
    }

    if (IsKeyPressed(KEY_BACKSPACE) && g->inputLen > 0) {
        g->input[--g->inputLen] = '\0';
    }

    if (IsKeyPressed(KEY_ENTER) && g->activeTerminal >= 0) {
        Terminal *t = &g->terminals[g->activeTerminal];
        char normalized[64] = {0};
        for (int i = 0; i < g->inputLen && i < 63; i++) {
            char c = g->input[i];
            if (c >= 'A' && c <= 'Z') {
                c = (char)(c + 32);
            }
            normalized[i] = c;
        }

        if (strcmp(normalized, t->answer) == 0) {
            if (!t->solved) {
                t->solved = true;
                g->solvedCount++;
            }
            snprintf(g->message, sizeof(g->message), "Терминал взломан: %d/%d", g->solvedCount, TERMINAL_COUNT);
        } else {
            strcpy(g->message, "Неверно. Попробуй другой вариант.");
        }

        g->showInput = false;
        g->activeTerminal = -1;
        g->inputLen = 0;
        g->input[0] = '\0';
    }

    if (IsKeyPressed(KEY_ESCAPE)) {
        g->showInput = false;
        g->activeTerminal = -1;
        g->inputLen = 0;
        g->input[0] = '\0';
        strcpy(g->message, "Ввод отменён.");
    }
}

static void UpdateGame(GameState *g, float dt) {
    g->timer += dt;

    if (g->showInput) {
        HandleTerminalInput(g);
        return;
    }

    UpdateCamera(&g->cam, CAMERA_FIRST_PERSON);

    Vector3 dir = Vector3Normalize(Vector3Subtract(g->cam.target, g->cam.position));
    Vector3 strafe = Vector3Normalize(Vector3CrossProduct(dir, (Vector3){0, 1, 0}));

    float baseSpeed = 2.6f;
    bool sprint = IsKeyDown(KEY_LEFT_SHIFT) && g->stamina > 0.0f;
    float speed = sprint ? baseSpeed * 1.8f : baseSpeed;
    if (sprint && (IsKeyDown(KEY_W) || IsKeyDown(KEY_A) || IsKeyDown(KEY_S) || IsKeyDown(KEY_D))) {
        g->stamina -= 25.0f * dt;
        if (g->stamina < 0.0f) g->stamina = 0.0f;
    } else {
        g->stamina += 18.0f * dt;
        if (g->stamina > 100.0f) g->stamina = 100.0f;
    }

    Vector3 delta = {0};
    if (IsKeyDown(KEY_W)) delta = Vector3Add(delta, Vector3Scale((Vector3){dir.x, 0, dir.z}, speed * dt));
    if (IsKeyDown(KEY_S)) delta = Vector3Add(delta, Vector3Scale((Vector3){dir.x, 0, dir.z}, -speed * dt));
    if (IsKeyDown(KEY_A)) delta = Vector3Add(delta, Vector3Scale((Vector3){strafe.x, 0, strafe.z}, -speed * dt));
    if (IsKeyDown(KEY_D)) delta = Vector3Add(delta, Vector3Scale((Vector3){strafe.x, 0, strafe.z}, speed * dt));

    TryMove(&g->cam, delta);

    if (IsKeyPressed(KEY_E)) {
        for (int i = 0; i < TERMINAL_COUNT; i++) {
            float dist = Vector3Distance(g->cam.position, g->terminals[i].pos);
            if (dist < 1.9f) {
                if (g->terminals[i].solved) {
                    strcpy(g->message, "Этот терминал уже активирован.");
                } else {
                    g->showInput = true;
                    g->activeTerminal = i;
                    g->inputLen = 0;
                    g->input[0] = '\0';
                    strncpy(g->message, g->terminals[i].question, sizeof(g->message) - 1);
                }
                return;
            }
        }
        strcpy(g->message, "Рядом нет интерактивного терминала.");
    }

    Vector3 exitPos = {13.5f, 1.0f, 1.5f};
    if (Vector3Distance(g->cam.position, exitPos) < 1.1f) {
        if (g->solvedCount >= TERMINAL_COUNT) {
            g->win = true;
            strcpy(g->message, "Победа! Доступ к доку получен, катер готов.");
        } else {
            snprintf(g->message, sizeof(g->message), "Доступ к доку заблокирован: %d/%d", g->solvedCount, TERMINAL_COUNT);
        }
    }
}

static void DrawWorld(const GameState *g) {
    DrawPlane((Vector3){7.5f, 0.0f, 5.5f}, (Vector2){26.0f, 22.0f}, (Color){24, 30, 42, 255});

    for (int z = 0; z < MAP_H; z++) {
        for (int x = 0; x < MAP_W; x++) {
            char c = WORLD_MAP[z][x];
            if (c == '#') {
                Color wall = (Color){55 + (unsigned char)((x * 11 + z * 19) % 70), 78, 120, 255};
                DrawCube((Vector3){x + 0.5f, 1.0f, z + 0.5f}, 1.0f, 2.0f, 1.0f, wall);
                DrawCubeWires((Vector3){x + 0.5f, 1.0f, z + 0.5f}, 1.0f, 2.0f, 1.0f, (Color){25, 30, 55, 255});
            }
        }
    }

    for (int i = 0; i < WORLD_OBJECTS; i++) {
        float bob = sinf(g->timer * 2.0f + g->decor[i].bob) * 0.15f;
        Vector3 p = g->decor[i].pos;
        p.y += bob;
        DrawSphere(p, g->decor[i].scale, (Color){40, 190, 255, 90});
    }

    for (int i = 0; i < TERMINAL_COUNT; i++) {
        const Terminal *t = &g->terminals[i];
        float pulse = (sinf(g->timer * 4.0f + t->pulse) + 1.0f) * 0.5f;
        Color core = t->solved ? (Color){80, 250, 145, 255} : (Color){195, 120, 255, 255};
        DrawCube((Vector3){t->pos.x, 0.9f, t->pos.z}, 0.7f, 1.4f, 0.7f, core);
        DrawCubeWires((Vector3){t->pos.x, 0.9f, t->pos.z}, 0.74f, 1.44f, 0.74f, (Color){220, 230, 255, 255});
        DrawSphere((Vector3){t->pos.x, 1.9f + pulse * 0.35f, t->pos.z}, 0.15f + pulse * 0.08f, (Color){120, 220, 255, 180});
    }

    Color exitColor = g->solvedCount >= TERMINAL_COUNT ? (Color){70, 255, 120, 255} : (Color){255, 130, 90, 255};
    DrawCylinder((Vector3){13.5f, 0.2f, 1.5f}, 0.35f, 0.35f, 0.4f, 24, exitColor);
    DrawCylinderWires((Vector3){13.5f, 0.2f, 1.5f}, 0.35f, 0.35f, 0.4f, 24, RAYWHITE);
}

static void DrawHUD(const GameState *g) {
    DrawRectangleGradientV(0, 0, SCREEN_W, 180, (Color){6, 10, 22, 190}, (Color){6, 10, 22, 20});
    DrawRectangle(20, SCREEN_H - 170, SCREEN_W - 40, 150, (Color){8, 14, 26, 210});
    DrawRectangleLinesEx((Rectangle){20, SCREEN_H - 170, SCREEN_W - 40, 150}, 2.0f, (Color){110, 185, 255, 210});

    DrawText("Escape from Epstein Island // C Edition", 30, 20, 28, RAYWHITE);
    DrawText(TextFormat("Терминалы: %d/%d", g->solvedCount, TERMINAL_COUNT), 30, SCREEN_H - 150, 30, (Color){185, 240, 255, 255});
    DrawText(g->message, 30, SCREEN_H - 105, 24, (Color){205, 220, 255, 255});
    DrawText("WASD + мышь | Shift: спринт | E: взаимодействие", 30, SCREEN_H - 64, 20, (Color){150, 180, 230, 255});

    DrawRectangle(SCREEN_W - 340, SCREEN_H - 88, 300, 24, (Color){20, 35, 55, 255});
    DrawRectangle(SCREEN_W - 340, SCREEN_H - 88, (int)(300.0f * (g->stamina / 100.0f)), 24,
                  g->stamina > 20.0f ? (Color){80, 200, 255, 255} : (Color){255, 130, 100, 255});
    DrawRectangleLines(SCREEN_W - 340, SCREEN_H - 88, 300, 24, (Color){140, 200, 255, 255});

    if (g->showInput && g->activeTerminal >= 0) {
        DrawRectangle(180, 170, SCREEN_W - 360, 300, (Color){5, 10, 20, 235});
        DrawRectangleLines(180, 170, SCREEN_W - 360, 300, (Color){125, 200, 255, 255});
        DrawText("ТЕРМИНАЛ", 220, 205, 34, RAYWHITE);
        DrawText(g->terminals[g->activeTerminal].question, 220, 255, 24, (Color){220, 230, 255, 255});
        DrawRectangle(220, 330, SCREEN_W - 440, 60, (Color){12, 22, 40, 255});
        DrawRectangleLines(220, 330, SCREEN_W - 440, 60, (Color){110, 185, 255, 255});
        DrawText(g->input, 235, 347, 28, (Color){240, 245, 255, 255});
        DrawText("Ответ не показан в вопросе. Enter — проверить, Esc — выйти", 220, 410, 20, (Color){150, 180, 230, 255});
    }

    if (g->win) {
        DrawRectangle(0, 0, SCREEN_W, SCREEN_H, (Color){6, 22, 10, 80});
        DrawText("ПОБЕДА", SCREEN_W / 2 - 120, 110, 64, (Color){125, 255, 180, 255});
    }
}

int main(void) {
    SetConfigFlags(FLAG_MSAA_4X_HINT | FLAG_WINDOW_RESIZABLE);
    InitWindow(SCREEN_W, SCREEN_H, "Escape from Epstein Island - Modern C 3D");
    InitAudioDevice();
    DisableCursor();
    SetTargetFPS(120);

    GameState game;
    InitGame(&game);

    while (!WindowShouldClose()) {
        float dt = GetFrameTime();
        if (!game.win) {
            UpdateGame(&game, dt);
        }

        BeginDrawing();
        ClearBackground((Color){5, 8, 16, 255});

        BeginMode3D(game.cam);
        DrawWorld(&game);
        EndMode3D();

        DrawHUD(&game);
        EndDrawing();
    }

    CloseAudioDevice();
    CloseWindow();
    return 0;
}
