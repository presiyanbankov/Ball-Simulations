import os
import pygame
import numpy as np
import math
import random


class Ball:
    def __init__(self, position, velocity):
        self.pos = np.array(position, dtype=np.float64)
        self.v = np.array(velocity, dtype=np.float64)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.is_in = True
        self.whoosh = True


def draw_arc(window, center, radius, start_angle, end_angle):
    p1 = center + (radius + 1000) * np.array([math.cos(start_angle), math.sin(start_angle)])
    p2 = center + (radius + 1000) * np.array([math.cos(end_angle), math.sin(end_angle)])
    pygame.draw.polygon(window, BLACK, [center, p1, p2], 0)


def is_ball_in_arc(ball_pos, CIRCLE_CENTER, start_angle, end_angle):
    dx = ball_pos[0] - CIRCLE_CENTER[0]
    dy = ball_pos[1] - CIRCLE_CENTER[1]
    ball_angle = math.atan2(dy, dx)
    start_angle = start_angle % (2 * math.pi)
    end_angle = end_angle % (2 * math.pi)
    if start_angle > end_angle:
        end_angle += 2 * math.pi
    if start_angle <= ball_angle <= end_angle or (start_angle <= ball_angle + 2 * math.pi <= end_angle):
        return True


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

BALL_RADIUS = 8
ball_pos = np.array([WIDTH / 2, HEIGHT / 2 - 120], dtype=np.float64)

GRAVITY = 0.1
spinning_speed = 0.02
arc_degree = 30
start_angle = math.radians(-arc_degree / 2)
end_angle = math.radians(arc_degree / 2)
ball_vel = np.array([0.2, 0.2], dtype=np.float64)
balls = [Ball(ball_pos, ball_vel)]
counter = 1

bounce_sfx = pygame.mixer.Sound('bounce.mp3')
whoosh_sfx = pygame.mixer.Sound('whoosh.mp3')
snippet_dir = "snippets"
snippets = [pygame.mixer.Sound(os.path.join(snippet_dir, f))
            for f in sorted(os.listdir(snippet_dir)) if f.endswith('.wav')]
current_snippet = 0
last_bounce_time = 0

running = True


def play_next_snippet(cooldown=100):
    global current_snippet
    global last_bounce_time
    now = pygame.time.get_ticks()
    if now - last_bounce_time >= cooldown:
        snippets[current_snippet].play()
        current_snippet = (current_snippet + 1) % len(snippets)
        last_bounce_time = now


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    start_angle += spinning_speed
    end_angle += spinning_speed
    for ball in balls:
        if ball.pos[1] > HEIGHT or ball.pos[0] < 0 or ball.pos[0] > WIDTH or ball.pos[1] < 0:
            balls.remove(ball)
            counter-=1

        ball.v[1] += GRAVITY
        ball.pos += ball.v
        dist = np.linalg.norm(ball.pos - CIRCLE_CENTER)
        if dist + BALL_RADIUS > CIRCLE_RADIUS:
            if is_ball_in_arc(ball.pos, CIRCLE_CENTER, start_angle, end_angle):

                if ball.whoosh:
                    # whoosh_sfx.play()
                    ball.whoosh = False
                    balls.append(
                        Ball(position=[WIDTH // 2, HEIGHT // 2 - 120],
                             velocity=[random.uniform(-1, 1), random.uniform(-0.2, 0.2)]))
                    balls.append(
                        Ball(position=[WIDTH // 2, HEIGHT // 2 - 120],
                             velocity=[random.uniform(-1, 1), random.uniform(-0.2, 0.2)]))
                    counter+=2
                ball.is_in = False

            if ball.is_in == True:
                d = ball.pos - CIRCLE_CENTER
                d_unit = d / np.linalg.norm(d)
                ball.pos = CIRCLE_CENTER + (CIRCLE_RADIUS - BALL_RADIUS) * d_unit
                t = np.array([-d[1], d[0]], dtype=np.float64)
                proj_v_t = (np.dot(ball.v, t) / np.dot(t, t)) * t
                ball.v = 2 * proj_v_t - ball.v
                # ball.v += t * spinning_speed / 5
                play_next_snippet()
    window.fill(BLACK)
    pygame.draw.circle(window, WHITE, CIRCLE_CENTER, CIRCLE_RADIUS, 4)
    draw_arc(window, CIRCLE_CENTER, CIRCLE_RADIUS, start_angle, end_angle)
    for ball in balls:
        pygame.draw.circle(window, ball.color, ball.pos, BALL_RADIUS)
    ball_counter = font.render(f"Balls: {counter}", True, WHITE)
    if counter <= 2:
        diff_text = font.render(f"IMPOSSIBLE", True, RED)
    elif counter < 6:
        diff_text = font.render(f"EXTRA HARD", True, ORANGE)
    elif counter < 10:
        diff_text = font.render(f"HARD", True, YELLOW)
    elif counter < 20:
        diff_text = font.render(f"MEDIUM", True, GREEN)
    elif counter < 50:
        diff_text = font.render(f"EASY", True, DARK_GREEN)
    elif counter < 100:
        diff_text = font.render(f"SUPER EASY", True, BLUE)
    elif counter < 1000:
        diff_text = font.render(f"NOOB", True, LIGHTBLUE)
    else:
        diff_text = font.render(f"BABY", True, WHITE)
    diff_text_rect = diff_text.get_rect(center = (340,216))
    window.blit(diff_text, diff_text_rect)
    window.blit(ball_counter, (20, 200))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
