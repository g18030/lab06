import pygame
import sys

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
DARK_BLUE = (10, 10, 40)
SHADOW_COLOR = (30, 30, 30)

# Paddle settings
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 8

# Ball settings
BALL_SIZE = 12
BALL_SPEED_X = 5
BALL_SPEED_Y = -5

# Brick settings
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
BRICK_PADDING = 5
BRICK_OFFSET_TOP = 80
BRICK_OFFSET_LEFT = (WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING))) // 2

ROW_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

class BreakoutGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Breakout - Classic Brick Breaker")
        self.clock = pygame.time.Clock()
        
        # Load fonts
        try:
            pygame.font.init()
            self.font = pygame.font.SysFont("Arial", 24, bold=True)
            self.large_font = pygame.font.SysFont("Arial", 64, bold=True)
            self.fonts_loaded = True
        except:
            self.fonts_loaded = False
            print("Warning: Fonts could not be loaded.")

        self.reset_game()

    def reset_game(self):
        """Initializes or resets the game state."""
        # Paddle
        self.paddle = pygame.Rect(
            WIDTH // 2 - PADDLE_WIDTH // 2, 
            HEIGHT - 40, 
            PADDLE_WIDTH, 
            PADDLE_HEIGHT
        )
        
        # Ball
        self.ball = pygame.Rect(
            WIDTH // 2 - BALL_SIZE // 2, 
            self.paddle.top - BALL_SIZE, 
            BALL_SIZE, 
            BALL_SIZE
        )
        self.ball_dx = BALL_SPEED_X
        self.ball_dy = BALL_SPEED_Y
        self.ball_launched = False
        
        # Bricks
        self.bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                bx = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
                by = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
                brick_rect = pygame.Rect(bx, by, BRICK_WIDTH, BRICK_HEIGHT)
                # Points: Classic Breakout scoring (varied by row)
                if row == 0: points = 7    # Red
                elif row == 1: points = 5  # Orange
                elif row == 2: points = 3  # Yellow
                elif row == 3: points = 1  # Green
                else: points = 1           # Blue

                self.bricks.append({
                    "rect": brick_rect, 
                    "color": ROW_COLORS[row], 
                    "points": points
                })
            
        self.score = 0
        self.lives = 3
        self.paused = False
        self.game_over = False
        self.win = False

    def handle_input(self):
        """Processes keyboard events and player movement."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.ball_launched and not self.game_over and not self.win:
                        self.ball_launched = True
                
                if event.key == pygame.K_p:
                    if not self.game_over and not self.win:
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

        # Keep paddle within screen bounds
        if self.paddle.left < 0:
            self.paddle.left = 0
        if self.paddle.right > WIDTH:
            self.paddle.right = WIDTH

        # Ball stays on paddle until launched
        if not self.ball_launched:
            self.ball.centerx = self.paddle.centerx
            self.ball.bottom = self.paddle.top

    def update(self):
        """Updates game logic, handles collisions and win/loss conditions."""
        if self.paused or self.game_over or self.win or not self.ball_launched:
            return

        # Move the ball
        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy

        # Wall collisions (Left/Right)
        if self.ball.left <= 0 or self.ball.right >= WIDTH:
            self.ball_dx *= -1
            # Adjust position to prevent getting stuck
            if self.ball.left <= 0: self.ball.left = 0
            if self.ball.right >= WIDTH: self.ball.right = WIDTH

        # Wall collisions (Top)
        if self.ball.top <= 0:
            self.ball_dy *= -1
            self.ball.top = 0

        # Paddle collision
        if self.ball.colliderect(self.paddle) and self.ball_dy > 0:
            self.ball_dy *= -1
            # Add some variability to bounce angle based on where it hits the paddle
            hit_pos = (self.ball.centerx - self.paddle.left) / PADDLE_WIDTH
            self.ball_dx = 12 * (hit_pos - 0.5)

        # Brick collisions
        for brick in self.bricks[:]:
            if self.ball.colliderect(brick["rect"]):
                # Determine collision side for realistic bounce
                dx_left = abs(self.ball.right - brick["rect"].left)
                dx_right = abs(self.ball.left - brick["rect"].right)
                dy_top = abs(self.ball.bottom - brick["rect"].top)
                dy_bottom = abs(self.ball.top - brick["rect"].bottom)

                if min(dx_left, dx_right) < min(dy_top, dy_bottom):
                    self.ball_dx *= -1
                else:
                    self.ball_dy *= -1
                
                self.score += brick["points"]
                self.bricks.remove(brick)
                break # Handle only one collision per frame

        # Check for Win
        if not self.bricks:
            self.win = True

        # Ball out of bounds (Loss)
        if self.ball.top > HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball_launched = False
                # Reset ball physics for next life
                self.ball_dx = BALL_SPEED_X
                self.ball_dy = BALL_SPEED_Y
                # Re-center ball on paddle
                self.ball.centerx = self.paddle.centerx
                self.ball.bottom = self.paddle.top

    def draw(self):
        """Renders the game elements to the screen."""
        self.screen.fill(DARK_BLUE)

        # Draw paddle
        pygame.draw.rect(self.screen, WHITE, self.paddle)

        # Draw ball
        pygame.draw.ellipse(self.screen, WHITE, self.ball)

        # Draw bricks with a "subtle border/shadow for depth"
        for brick in self.bricks:
            # Shadow/Highlight effect
            r = brick["rect"]
            # Main brick
            pygame.draw.rect(self.screen, brick["color"], r)
            # Subtle top-left highlight
            pygame.draw.line(self.screen, WHITE, r.topleft, r.topright, 1)
            pygame.draw.line(self.screen, WHITE, r.topleft, r.bottomleft, 1)
            # Subtle bottom-right shadow
            pygame.draw.line(self.screen, BLACK, r.bottomleft, r.bottomright, 1)
            pygame.draw.line(self.screen, BLACK, r.topright, r.bottomright, 1)

        # Draw UI
        if self.fonts_loaded:
            score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
            lives_surf = self.font.render(f"Lives: {self.lives}", True, WHITE)
            self.screen.blit(score_surf, (20, 20))
            self.screen.blit(lives_surf, (WIDTH - lives_surf.get_width() - 20, 20))

            if self.paused:
                txt = self.large_font.render("PAUSED", True, WHITE)
                self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 50))
            
            if self.game_over:
                txt = self.large_font.render("GAME OVER", True, RED)
                sub = self.font.render("Press 'R' to Restart", True, WHITE)
                self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 50))
                self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 40))
            
            if self.win:
                txt = self.large_font.render("YOU WIN!", True, GREEN)
                sub = self.font.render("Press 'R' to Restart", True, WHITE)
                self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 50))
                self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while True:
            self.clock.tick(FPS)
            self.handle_input()
            self.update()
            self.draw()

if __name__ == "__main__":
    game = BreakoutGame()
    game.run()
