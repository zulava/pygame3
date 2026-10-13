"""
"Dodge & Collect" - Week 2-3 Mini-Project (Pygame)
----------------------------------------------------------------
Uses YOUR OWN assets:
  - assets/images/guy.png   -> 4x4 walk-cycle spritesheet
                                (row 0 = down, row 1 = left,
                                 row 2 = right, row 3 = up)
  - assets/sounds/music.wav -> background music (looped)

Gameplay:
  - Move the character with arrow keys (walk animation plays
    automatically based on direction).
  - Yellow gems fall from the top -> touching one = +1 score (COLLECT).
  - Red spikes fall from the top -> touching one = game over (DODGE).

How to run:
  1. pip install pygame
  2. python main.py
  (make sure the assets/ folder sits next to this file)
"""

import pygame
import random
import os

# ---------- 1. INITIALIZATION ----------
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge & Collect")
clock = pygame.time.Clock()

# Colors (R, G, B)
WHITE = (255, 255, 255)
YELLOW = (255, 210, 0)
RED = (220, 40, 40)
BACKGROUND = (25, 130, 60)  # grassy-green background to suit the sprite

# ---------- 2. LOAD SPRITE SHEET ----------
SPRITE_PATH = "/Users/zulava/Downloads/School/Coding/Coding Week 3/guy.png"
SPRITESHEET = pygame.image.load(SPRITE_PATH).convert_alpha()

FRAME_W, FRAME_H = 16, 24          # size of a single frame in the sheet
SCALE = 3                          # scale up so it's visible on screen
DISPLAY_W, DISPLAY_H = FRAME_W * SCALE, FRAME_H * SCALE

# Row index for each facing direction in the sheet
DIRECTION_ROWS = {
    "down": 0,
    "left": 1,
    "right": 2,
    "up": 3,
}
FRAMES_PER_ROW = 4

def get_frame(direction, frame_index):
    """Cut out one frame from the spritesheet and scale it up."""
    row = DIRECTION_ROWS[direction]
    col = frame_index % FRAMES_PER_ROW
    rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
    frame = SPRITESHEET.subsurface(rect).copy()
    frame = pygame.transform.scale(frame, (DISPLAY_W, DISPLAY_H))
    return frame

# Pre-cut every frame once so we don't slice the sheet every loop
ANIMATIONS = {
    direction: [get_frame(direction, i) for i in range(FRAMES_PER_ROW)]
    for direction in DIRECTION_ROWS
}

# ---------- 3. LOAD MUSIC ----------
MUSIC_PATH = "/Users/zulava/Downloads/School/Coding/Coding Week 3/Juhani Junkala [Retro Game Music Pack] Level 2.wav"
if os.path.exists(MUSIC_PATH):
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # loop forever

# ---------- 4. PLAYER STATE ----------
player_x = WIDTH // 2 - DISPLAY_W // 2
player_y = HEIGHT // 2 - DISPLAY_H // 2
player_speed = 4

facing = "down"          # which animation row to use
anim_frame = 0            # which frame in that row (0-3)
anim_timer = 0             # counts frames to control animation speed
ANIM_SPEED = 8              # lower = faster animation

# ---------- 5. FALLING OBJECTS ----------
OBJECT_SIZE = 26
fall_speed = 4

def make_object():
    """Randomly create either a gem (collect) or a spike (dodge)."""
    kind = random.choice(["gem", "gem", "spike"])  # gems more common than spikes
    x = random.randint(0, WIDTH - OBJECT_SIZE)
    return {"kind": kind, "x": x, "y": -OBJECT_SIZE}

falling_objects = [make_object()]
spawn_timer = 0
SPAWN_INTERVAL = 45  # frames between new objects

score = 0
game_over = False


def draw_text(text, font_size, color, pos):
    f = pygame.font.SysFont(None, font_size)
    render = f.render(text, True, color)
    rect = render.get_rect(center=pos)
    screen.blit(render, rect)


def reset_game():
    global player_x, player_y, falling_objects, score, game_over, fall_speed, spawn_timer
    player_x = WIDTH // 2 - DISPLAY_W // 2
    player_y = HEIGHT // 2 - DISPLAY_H // 2
    falling_objects = [make_object()]
    score = 0
    fall_speed = 4
    spawn_timer = 0
    game_over = False


# ---------- 6. GAME LOOP ----------
running = True
while running:
    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                reset_game()

    if not game_over:
        # --- Movement & direction/animation ---
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT]:
            player_x -= player_speed
            facing = "left"
            moving = True
        elif keys[pygame.K_RIGHT]:
            player_x += player_speed
            facing = "right"
            moving = True
        elif keys[pygame.K_UP]:
            player_y -= player_speed
            facing = "up"
            moving = True
        elif keys[pygame.K_DOWN]:
            player_y += player_speed
            facing = "down"
            moving = True

        # keep player inside the screen
        player_x = max(0, min(WIDTH - DISPLAY_W, player_x))
        player_y = max(0, min(HEIGHT - DISPLAY_H, player_y))

        # advance walking animation only while moving
        if moving:
            anim_timer += 1
            if anim_timer >= ANIM_SPEED:
                anim_timer = 0
                anim_frame = (anim_frame + 1) % FRAMES_PER_ROW
        else:
            anim_frame = 0  # standing still = first frame (idle pose)

        # --- Spawn new falling objects over time ---
        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_timer = 0
            falling_objects.append(make_object())

        # --- Update falling objects ---
        player_rect = pygame.Rect(player_x, player_y, DISPLAY_W, DISPLAY_H)
        for obj in falling_objects[:]:
            obj["y"] += fall_speed
            obj_rect = pygame.Rect(obj["x"], obj["y"], OBJECT_SIZE, OBJECT_SIZE)

            if player_rect.colliderect(obj_rect):
                if obj["kind"] == "gem":
                    score += 1
                    fall_speed = min(12, 4 + score // 5)  # gets harder over time
                    falling_objects.remove(obj)
                else:  # spike
                    game_over = True
            elif obj["y"] > HEIGHT:
                falling_objects.remove(obj)

    # ---------- 7. DRAW ----------
    screen.fill(BACKGROUND)

    if not game_over:
        # Draw falling objects
        for obj in falling_objects:
            color = YELLOW if obj["kind"] == "gem" else RED
            if obj["kind"] == "gem":
                pygame.draw.circle(
                    screen, color,
                    (obj["x"] + OBJECT_SIZE // 2, obj["y"] + OBJECT_SIZE // 2),
                    OBJECT_SIZE // 2,
                )
            else:
                pygame.draw.polygon(screen, color, [
                    (obj["x"] + OBJECT_SIZE // 2, obj["y"]),
                    (obj["x"], obj["y"] + OBJECT_SIZE),
                    (obj["x"] + OBJECT_SIZE, obj["y"] + OBJECT_SIZE),
                ])

        # Draw player using the correct direction + animation frame
        current_sprite = ANIMATIONS[facing][anim_frame]
        screen.blit(current_sprite, (player_x, player_y))

        draw_text(f"Score: {score}", 36, WHITE, (90, 30))
    else:
        draw_text("GAME OVER", 64, RED, (WIDTH // 2, HEIGHT // 2 - 40))
        draw_text(f"Final score: {score}", 40, WHITE, (WIDTH // 2, HEIGHT // 2 + 20))
        draw_text("Press R to play again", 28, WHITE, (WIDTH // 2, HEIGHT // 2 + 70))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()