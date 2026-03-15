import pygame
import sys

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 50)

# Paddle settings
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 8

# Ball settings
BALL_SIZE = 10
BALL_SPEED_X = 5
BALL_SPEED_Y = -5

# Brick settings
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
BRICK_PADDING = 5
BRICK_OFFSET_TOP = 60
BRICK_OFFSET_LEFT = (WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING))) // 2

ROW_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

class BreakoutGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Breakout")
        self.clock = pygame.time.Clock()
        
        # Safely load fonts to prevent crashes on unsupported Python versions
        self.fonts_loaded = True
        try:
            pygame.font.init()
            self.font = pygame.font.SysFont("Arial", 24, bold=True)
            self.large_font = pygame.font.SysFont("Arial", 48, bold=True)
        except Exception as e:
            print(f"Warning: Pygame font module failed to load. Running without text. Error: {e}")
            self.fonts_loaded = False
        
        self.reset_game()

    def reset_game(self):
        # Paddle
        self.paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)
        
        # Ball
        self.ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, self.paddle.top - BALL_SIZE, BALL_SIZE, BALL_SIZE)
        self.ball_dx = BALL_SPEED_X
        self.ball_dy = BALL_SPEED_Y
        self.ball_launched = False
        
        # Bricks
        self.bricks = []
        for row in range(BRICK_ROWS):
            row_bricks = []
            for col in range(BRICK_COLS):
                brick_x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
                brick_y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
                brick_rect = pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT)
                row_bricks.append({"rect": brick_rect, "color": ROW_COLORS[row], "row": row})
            self.bricks.append(row_bricks)
            
        self.score = 0
        self.lives = 3
        self.paused = False
        self.game_over = False
        self.win = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.ball_launched and not self.game_over and not self.paused:
                    self.ball_launched = True
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if event.key == pygame.K_r:
                    self.reset_game()

        if self.paused or self.game_over or self.win:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.x += PADDLE_SPEED

        # Keep paddle on screen
        if self.paddle.left < 0:
            self.paddle.left = 0
        if self.paddle.right > WIDTH:
            self.paddle.right = WIDTH

        # Ball follows paddle if not launched
        if not self.ball_launched:
            self.ball.centerx = self.paddle.centerx
            self.ball.bottom = self.paddle.top

    def update(self):
        if self.paused or self.game_over or self.win:
            return

        if not self.ball_launched:
            return

        # Move ball
        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy

        # Wall collisions
        if self.ball.left <= 0 or self.ball.right >= WIDTH:
            self.ball_dx *= -1
        if self.ball.top <= 0:
            self.ball_dy *= -1

        # Paddle collision
        if self.ball.colliderect(self.paddle) and self.ball_dy > 0:
            self.ball_dy *= -1
            # Adjust angle based on where it hits the paddle
            hit_pos = (self.ball.centerx - self.paddle.left) / PADDLE_WIDTH
            self.ball_dx = 10 * (hit_pos - 0.5)

        # Brick collisions
        for row_bricks in self.bricks:
            for brick in row_bricks[:]:
                if self.ball.colliderect(brick["rect"]):
                    # Determine which side was hit
                    overlap_left = abs(self.ball.right - brick["rect"].left)
                    overlap_right = abs(self.ball.left - brick["rect"].right)
                    overlap_top = abs(self.ball.bottom - brick["rect"].top)
                    overlap_bottom = abs(self.ball.top - brick["rect"].bottom)

                    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                    if min_overlap == overlap_top or min_overlap == overlap_bottom:
                        self.ball_dy *= -1
                    else:
                        self.ball_dx *= -1
                    
                    row_bricks.remove(brick)
                    # Points: Top row (row 0) is +20, others +10
                    if brick["row"] == 0:
                        self.score += 20
                    else:
                        self.score += 10
                    break # Only hit one brick per update
            else:
                continue
            break

        # Check for Win
        if not any(self.bricks):
            self.win = True

        # Ball out of bounds
        if self.ball.top > HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball_launched = False
                self.ball.centerx = self.paddle.centerx
                self.ball.bottom = self.paddle.top

    def draw(self):
        self.screen.fill(DARK_BLUE)

        # Draw paddle
        pygame.draw.rect(self.screen, WHITE, self.paddle)

        # Draw ball
        pygame.draw.ellipse(self.screen, WHITE, self.ball)

        # Draw bricks
        for row_bricks in self.bricks:
            for brick in row_bricks:
                pygame.draw.rect(self.screen, brick["color"], brick["rect"])
                pygame.draw.rect(self.screen, BLACK, brick["rect"], 1) # Border

        # Draw UI
        if self.fonts_loaded:
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
            self.screen.blit(score_text, (20, 20))
            self.screen.blit(lives_text, (WIDTH - 120, 20))

        if self.paused:
            if self.fonts_loaded:
                pause_text = self.large_font.render("PAUSED", True, WHITE)
                self.screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))

        if self.game_over:
            if self.fonts_loaded:
                over_text = self.large_font.render("GAME OVER", True, RED)
                restart_text = self.font.render("Press 'R' to Restart", True, WHITE)
                self.screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 50))
                self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))

        if self.win:
            if self.fonts_loaded:
                win_text = self.large_font.render("YOU WIN!", True, GREEN)
                restart_text = self.font.render("Press 'R' to Restart", True, WHITE)
                self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
                self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_input()
            self.update()
            self.draw()

if __name__ == "__main__":
    game = BreakoutGame()
    game.run()
