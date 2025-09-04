import os
import pygame
import numpy as np
import random
import sys
import colorsys


class Ball:
    def __init__(self, position, velocity):
        self.pos = np.array(position, dtype=np.float64)
        self.v = np.array(velocity, dtype=np.float64)
        self.hue = 0
        self.hue_speed = 0.002


pygame.init()
WIDTH = 450
HEIGHT = 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (0, 150, 255)
font = pygame.font.Font('freesansbold.ttf', 30)

CIRCLE_CENTER = np.array([WIDTH / 2, HEIGHT / 2], dtype=np.float64)
CIRCLE_RADIUS = 150

BALL_RADIUS = 5
ball_pos = np.array([WIDTH / 2, HEIGHT / 2 - 120], dtype=np.float64)

GRAVITY = 0.1
ball_vel = np.array([2, 3], dtype=np.float64)
balls = [Ball(ball_pos, ball_vel)]
counter = 0

bounce_sfx = pygame.mixer.Sound('bounce.mp3')
snippet_dir = "snippets"
snippets = [pygame.mixer.Sound(os.path.join(snippet_dir, f))
            for f in sorted(os.listdir(snippet_dir)) if f.endswith('.wav')]
current_snippet = 0
last_bounce_time = 0

running = True


def play_next_snippet(cooldown=165):
    global current_snippet
    global last_bounce_time
    now = pygame.time.get_ticks()
    if now - last_bounce_time >= cooldown:
        snippets[current_snippet].play()
        current_snippet = (current_snippet + 1) % len(snippets)
        last_bounce_time = now

def hsv_to_rgb(h, s ,v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r*255), int(g*255), int(b*255)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for ball in balls:
        ball.v[1] += GRAVITY
        ball.pos += ball.v
        ball.hue += ball.hue_speed
        if ball.hue > 1:
            ball.hue-=1
        dist = np.linalg.norm(ball.pos - CIRCLE_CENTER)
        if dist + BALL_RADIUS > CIRCLE_RADIUS:
                d = ball.pos - CIRCLE_CENTER
                d_unit = d / np.linalg.norm(d)
                ball.pos = CIRCLE_CENTER + (CIRCLE_RADIUS - BALL_RADIUS) * d_unit
                t = np.array([-d[1], d[0]], dtype=np.float64)
                proj_v_t = (np.dot(ball.v, t) / np.dot(t, t)) * t
                ball.v = 2 * proj_v_t - ball.v
                play_next_snippet()
                BALL_RADIUS+=1
                counter+=1

    window.fill(BLACK)
    pygame.draw.circle(window, WHITE, CIRCLE_CENTER, CIRCLE_RADIUS, 4)
    for ball in balls:
        ball_color = hsv_to_rgb(ball.hue, 1, 1)
        pygame.draw.circle(window, ball_color, ball.pos, BALL_RADIUS)
    ball_counter = font.render(f"Balls: {counter}", True, WHITE)
    if BALL_RADIUS <= 10:
        diff_text = font.render(f"IMPOSSIBLE", True, RED)
    elif BALL_RADIUS < 20:
        diff_text = font.render(f"EXTRA HARD", True, ORANGE)
    elif BALL_RADIUS < 35:
        diff_text = font.render(f"HARD", True, YELLOW)
    elif BALL_RADIUS < 50:
        diff_text = font.render(f"MEDIUM", True, GREEN)
    elif BALL_RADIUS < 70:
        diff_text = font.render(f"EASY", True, DARK_GREEN)
    elif BALL_RADIUS < 100:
        diff_text = font.render(f"SUPER EASY", True, BLUE)
    elif BALL_RADIUS < 150:
        diff_text = font.render(f"NOOB", True, LIGHTBLUE)
    else:
        diff_text = font.render(f"BABY", True, WHITE)
    diff_text_rect = diff_text.get_rect(center = (WIDTH / 2, HEIGHT / 2-200))
    counter_text = font.render(f"BOUNCES: {counter}", True, WHITE)
    counter_text_rect = counter_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 200))
    window.blit(diff_text, diff_text_rect)
    window.blit(counter_text, counter_text_rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
