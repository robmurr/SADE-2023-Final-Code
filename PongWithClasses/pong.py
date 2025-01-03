import pygame
import numpy as np
import math

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 60
BALL_RADIUS = 5
PADDLE_SPEED = 3
BALL_SPEED = 5
BALL_SPEED_MAX = 5
WALL_PADDING = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Player class
class Player:
    def __init__(self, x):
        self.x = x
        self.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.score = 0

    def move_up(self):
        if self.y > 0:
            self.y -= PADDLE_SPEED

    def move_down(self):
        if self.y < SCREEN_HEIGHT - PADDLE_HEIGHT:
            self.y += PADDLE_SPEED

    def update(self, ball):
        # Track the height of the ball
        if self.y + PADDLE_HEIGHT // 2 < ball.y:
            self.move_down()
        elif self.y + PADDLE_HEIGHT // 2 > ball.y:
            self.move_up()

    def score_point(self):
        self.score += 1


# Ball class
class Ball:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed = BALL_SPEED
        self.velocity_x = 0  # Ball's velocity in the x-axis
        self.velocity_y = 0  # Ball's velocity in the y-axis
        self.set_random_angle()

    def set_random_angle(self):
        angle = np.random.uniform(-math.pi / 4, math.pi / 4)
        self.velocity_x = self.speed * math.cos(angle) * np.random.choice([-1, 1])
        self.velocity_y = self.speed * math.sin(angle) * np.random.choice([-0.5, 0.5])

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), BALL_RADIUS)

    def update(self, player1, player2):
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Collision with paddles
        if (
                player1.x <= self.x + WALL_PADDING + BALL_RADIUS <= player1.x + PADDLE_WIDTH and
                player1.y <= self.y <= player1.y + PADDLE_HEIGHT
        ):
            self.velocity_x *= -1

            middle_y = player1.y + PADDLE_HEIGHT / 2
            difference_in_y = middle_y - self.y
            reduction_factor = (PADDLE_HEIGHT / 2) / BALL_SPEED_MAX
            velocity_y = difference_in_y / reduction_factor
            self.velocity_y = -1 * velocity_y

        elif (
                player2.x <= self.x - WALL_PADDING - BALL_RADIUS <= player2.x + PADDLE_WIDTH and
                player2.y <= self.y <= player2.y + PADDLE_HEIGHT
        ):
            self.velocity_x *= -1

            middle_y = player2.y + PADDLE_HEIGHT / 2
            difference_in_y = middle_y - self.y
            reduction_factor = (PADDLE_HEIGHT / 2) / BALL_SPEED_MAX
            velocity_y = difference_in_y / reduction_factor
            self.velocity_y = -1 * velocity_y

        # Collision with walls
        if self.y <= 0 or self.y >= SCREEN_HEIGHT:
            self.velocity_y = -self.velocity_y

        # Scoring
        if self.x < 0:
            player1.score_point()
            self.__init__()  # Reset ball position
            self.speed = BALL_SPEED  # Reset ball speed
            player1.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
            player2.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        elif self.x > SCREEN_WIDTH:
            player2.score_point()
            self.__init__()  # Reset ball position
            self.speed = BALL_SPEED  # Reset ball speed
            player1.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
            player2.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2


class GameInformation:
    def __init__(self, player2_hits, player1_hits, player2_score, player1_score):
        self.player2_hits = player2_hits
        self.player1_hits = player1_hits
        self.player2_score = player2_score
        self.player1_score = player1_score


# Game class
class Game:
    def __init__(self):
        self.running = False
        self.screen = None
        self.clock = None
        self.player1 = None
        self.player2 = None
        self.ball = None

        self.player2_hits = 0
        self.player1_hits = 0
        self.player2_score = 0
        self.player1_score = 0

    def initialize(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.player1 = Player(SCREEN_WIDTH - PADDLE_WIDTH)
        self.player2 = Player(0)
        self.ball = Ball()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.player1.move_up()
        elif keys[pygame.K_DOWN]:
            self.player1.move_down()

        if keys[pygame.K_w]:
            self.player2.move_up()
        elif keys[pygame.K_s]:
            self.player2.move_down()

    def update(self):
        self.player2.update(self.ball)  # player2 automatically tracks ball's position and moves accordingly
        self.ball.update(self.player1, self.player2)

    def draw(self):
        self.screen.fill(BLACK)
        dash_length = 10  # Length of each dash segment
        gap_length = 10  # Length of each gap segment

        # Draw the dashed line
        y = 0
        while y < SCREEN_HEIGHT:
            pygame.draw.line(
                self.screen, WHITE, (SCREEN_WIDTH // 2, y), (SCREEN_WIDTH // 2, y + dash_length), 1
            )
            y += dash_length + gap_length

        # Draw the paddles with separation from the edges
        pygame.draw.rect(self.screen, WHITE,
                         (self.player1.x - WALL_PADDING, self.player1.y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(self.screen, WHITE,
                         (self.player2.x + WALL_PADDING, self.player2.y, PADDLE_WIDTH, PADDLE_HEIGHT))

        self.ball.draw(self.screen)

        font = pygame.font.Font(None, 36)
        score1_text = font.render(str(self.player1.score), True, WHITE)
        score2_text = font.render(str(self.player2.score), True, WHITE)
        score1_rect = score1_text.get_rect(center=(SCREEN_WIDTH // 2 + 50, 30))
        score2_rect = score2_text.get_rect(center=(SCREEN_WIDTH // 2 - 50, 30))
        self.screen.blit(score1_text, score1_rect)
        self.screen.blit(score2_text, score2_rect)

        pygame.display.flip()

    def run(self):
        self.initialize()

        while self.running:
            ball_x_velocity = self.ball.velocity_x
            player1_points = self.player1.score
            player2_points = self.player2.score

            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

            if ball_x_velocity > 0 > self.ball.velocity_x:
                self.player1_hits += 1
            elif self.ball.velocity_x > 0 > ball_x_velocity:
                self.player2_hits += 1

            if player1_points < self.player1.score:
                self.player1_score += 1
            elif player2_points < self.player2.score:
                self.player2_score += 1

            game_info = GameInformation(
                self.player2_hits, self.player1_hits, self.player2_score, self.player1_score)

            if self.player1.score >= 10 or self.player2.score >= 10:
                self.running = False

        pygame.quit()

    def loop(self):
        ball_x_velocity = self.ball.velocity_x
        player1_points = self.player1.score
        player2_points = self.player2.score

        self.handle_events()
        self.update()
        self.draw()

        if ball_x_velocity > 0 > self.ball.velocity_x:
            self.player1_hits += 1
        elif self.ball.velocity_x > 0 > ball_x_velocity:
            self.player2_hits += 1

        if player1_points < self.player1.score:
            self.player1_score += 1
        elif player2_points < self.player2.score:
            self.player2_score += 1

        game_info = GameInformation(
            self.player2_hits, self.player1_hits, self.player2_score, self.player1_score)
        return game_info
