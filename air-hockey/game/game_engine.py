
import random
import time

from game.puck import Puck
from game.paddle import Paddle
from game.ai import ComputerAI
from game.collisions import handle_paddle_collision
from game.renderer import (
    WIDTH,
    HEIGHT,
    MARGIN,
    GOAL_TOP,
    GOAL_BOTTOM,
)

PLAYER_SPEED = 6
PUCK_RADIUS = 12
PADDLE_RADIUS = 28
INITIAL_PUCK_SPEED = 4.5
MATCH_DURATION = 30


class GameEngine:
    def __init__(self):
        self.puck = Puck(WIDTH / 2, HEIGHT / 2, PUCK_RADIUS)

        self.player = Paddle(
            x=WIDTH * 0.15,
            y=HEIGHT / 2,
            radius=PADDLE_RADIUS,
            min_x=MARGIN + PADDLE_RADIUS,
            max_x=WIDTH / 2 - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS,
            max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )

        self.computer = Paddle(
            x=WIDTH * 0.85,
            y=HEIGHT / 2,
            radius=PADDLE_RADIUS,
            min_x=WIDTH / 2 + PADDLE_RADIUS,
            max_x=WIDTH - MARGIN - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS,
            max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )

        self.ai = ComputerAI()

        # Task 2: Scoring
        self.player_score = 0
        self.computer_score = 0

        # Task 3: Timer
        self.match_duration = MATCH_DURATION
        self.start_time = time.monotonic()
        self.time_left = MATCH_DURATION
        self.match_over = False

        self._launch_puck()

    def _launch_puck(self):
        angle_choices = [0.3, 0.6, -0.3, -0.6]
        direction = random.choice([-1, 1])
        vy_factor = random.choice(angle_choices)

        self.puck.vx = INITIAL_PUCK_SPEED * direction
        self.puck.vy = INITIAL_PUCK_SPEED * vy_factor

    def handle_input(self, keys_pressed):
        import pygame

        if self.match_over:
            return

        dx = 0
        dy = 0

        # WASD controls
        if keys_pressed[pygame.K_w]:
            dy -= PLAYER_SPEED
        if keys_pressed[pygame.K_s]:
            dy += PLAYER_SPEED
        if keys_pressed[pygame.K_a]:
            dx -= PLAYER_SPEED
        if keys_pressed[pygame.K_d]:
            dx += PLAYER_SPEED

        self.player.move_by(dx, dy)

    def update_timer(self):
        elapsed = time.monotonic() - self.start_time
        self.time_left = max(
            0,
            self.match_duration - int(elapsed),
        )

        if self.time_left == 0:
            self.match_over = True
            self.puck.vx = 0
            self.puck.vy = 0

    def update(self):
        if self.match_over:
            return

        self.update_timer()

        if self.match_over:
            return

        self.ai.update(self.computer, self.puck)

        # Task 1: Track the puck's previous position.
        previous_x = self.puck.x
        previous_y = self.puck.y

        self.puck.move()
        self.puck.bounce_off_walls(HEIGHT, MARGIN)

        handle_paddle_collision(
            self.puck,
            self.player,
            previous_x,
            previous_y,
        )

        handle_paddle_collision(
            self.puck,
            self.computer,
            previous_x,
            previous_y,
        )

        self._handle_goals()

    def _handle_goals(self):
        # Left goal: computer scores.
        if self.puck.x - self.puck.radius < MARGIN:
            if GOAL_TOP < self.puck.y < GOAL_BOTTOM:
                self.computer_score += 1
                self._reset_puck()
            else:
                self.puck.x = MARGIN + self.puck.radius
                self.puck.vx = abs(self.puck.vx)

        # Right goal: player scores.
        elif self.puck.x + self.puck.radius > WIDTH - MARGIN:
            if GOAL_TOP < self.puck.y < GOAL_BOTTOM:
                self.player_score += 1
                self._reset_puck()
            else:
                self.puck.x = WIDTH - MARGIN - self.puck.radius
                self.puck.vx = -abs(self.puck.vx)

    def _reset_puck(self):
        self.puck.x = WIDTH / 2
        self.puck.y = HEIGHT / 2
        self._launch_puck()

    def get_winner(self):
        if self.player_score > self.computer_score:
            return "Player wins!"
        elif self.computer_score > self.player_score:
            return "Computer wins!"
        return "Draw!"

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_table(surface)

        renderer.draw_paddle(
            surface, self.player, renderer.COLOR_PLAYER
        )
        renderer.draw_paddle(
            surface, self.computer, renderer.COLOR_COMPUTER
        )
        renderer.draw_puck(surface, self.puck)

        renderer.draw_text(
            surface,
            font,
            f"Player: {self.player_score}",
            (MARGIN + 15, MARGIN + 10),
            renderer.COLOR_PLAYER,
        )

        renderer.draw_text(
            surface,
            font,
            f"Computer: {self.computer_score}",
            (WIDTH - 180, MARGIN + 10),
            renderer.COLOR_COMPUTER,
        )

        renderer.draw_text(
            surface,
            font,
            f"Time: {self.time_left}",
            (WIDTH // 2 - 40, MARGIN + 10),
            renderer.COLOR_TEXT,
        )

        if self.match_over:
            renderer.draw_banner(
                surface,
                font,
                self.get_winner(),
            )
