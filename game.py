import pygame
import sys

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
YELLOW = (255, 255, 50)
DARK_BLUE = (10, 10, 40)
GRAY = (150, 150, 150)

# Paddle settings
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 8

# Ball settings
BALL_SIZE = 12
BALL_SPEED_X = 5
BALL_SPEED_Y = -5

# Brick settings
BRICK_ROWS = 4
BRICK_COLS = 10
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
BRICK_PADDING = 5
BRICK_OFFSET_TOP = 80
BRICK_OFFSET_LEFT = (WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING))) // 2

# Only Red and Yellow
ROW_COLORS = [RED, RED, YELLOW, YELLOW]

class BreakoutGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Breakout - Red & Yellow Edition")
        self.clock = pygame.time.Clock()
        
        # Load fonts
        try:
            pygame.font.init()
            # Try to find a bold, game-like font
            font_name = pygame.font.match_font('impact', 'arial', 'verdana')
            self.font = pygame.font.Font(font_name, 28)
            self.large_font = pygame.font.Font(font_name, 72)
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
                
                # Points: Red rows (0, 1) = 10 points, Yellow rows (2, 3) = 5 points
                color = ROW_COLORS[row]
                points = 10 if color == RED else 5

                self.bricks.append({
                    "rect": brick_rect, 
                    "color": color, 
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
            if self.ball.left <= 0: self.ball.left = 0
            if self.ball.right >= WIDTH: self.ball.right = WIDTH

        # Wall collisions (Top)
        if self.ball.top <= 0:
            self.ball_dy *= -1
            self.ball.top = 0

        # Paddle collision
        if self.ball.colliderect(self.paddle) and self.ball_dy > 0:
            self.ball_dy *= -1
            hit_pos = (self.ball.centerx - self.paddle.left) / PADDLE_WIDTH
            self.ball_dx = 12 * (hit_pos - 0.5)

        # Brick collisions
        for brick in self.bricks[:]:
            if self.ball.colliderect(brick["rect"]):
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
                break 

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
                self.ball_dx = BALL_SPEED_X
                self.ball_dy = BALL_SPEED_Y
                self.ball.centerx = self.paddle.centerx
                self.ball.bottom = self.paddle.top

    def draw_text_with_shadow(self, text, x, y, color=WHITE, shadow_color=BLACK, large=False):
        """Helper to draw text with a subtle shadow."""
        font = self.large_font if large else self.font
        # Draw shadow
        shadow_surf = font.render(text, True, shadow_color)
        self.screen.blit(shadow_surf, (x + 2, y + 2))
        # Draw main text
        text_surf = font.render(text, True, color)
        self.screen.blit(text_surf, (x, y))
        return text_surf.get_width()

    def draw(self):
        """Renders the game elements to the screen."""
        self.screen.fill(DARK_BLUE)

        # Draw paddle
        pygame.draw.rect(self.screen, WHITE, self.paddle)

        # Draw ball
        pygame.draw.ellipse(self.screen, WHITE, self.ball)

        # Draw bricks
        for brick in self.bricks:
            r = brick["rect"]
            pygame.draw.rect(self.screen, brick["color"], r)
            pygame.draw.line(self.screen, WHITE, r.topleft, r.topright, 1)
            pygame.draw.line(self.screen, WHITE, r.topleft, r.bottomleft, 1)
            pygame.draw.line(self.screen, BLACK, r.bottomleft, r.bottomright, 1)
            pygame.draw.line(self.screen, BLACK, r.topright, r.bottomright, 1)

        # Draw UI
        if self.fonts_loaded:
            # Score (Top-Left)
            self.draw_text_with_shadow(f"SCORE: {self.score}", 20, 20, YELLOW)
            
            # Lives (Top-Right)
            lives_text = f"LIVES: {self.lives}"
            # Calculate width to align right
            lives_width = self.font.size(lives_text)[0]
            self.draw_text_with_shadow(lives_text, WIDTH - lives_width - 20, 20, RED)

            if self.paused:
                txt = "PAUSED"
                w = self.large_font.size(txt)[0]
                self.draw_text_with_shadow(txt, WIDTH // 2 - w // 2, HEIGHT // 2 - 50, WHITE, large=True)
            
            if self.game_over:
                txt = "GAME OVER"
                sub = "Press 'R' to Restart"
                w1 = self.large_font.size(txt)[0]
                w2 = self.font.size(sub)[0]
                self.draw_text_with_shadow(txt, WIDTH // 2 - w1 // 2, HEIGHT // 2 - 50, RED, large=True)
                self.draw_text_with_shadow(sub, WIDTH // 2 - w2 // 2, HEIGHT // 2 + 40, WHITE)
            
            if self.win:
                txt = "YOU WIN!"
                sub = "Press 'R' to Restart"
                w1 = self.large_font.size(txt)[0]
                w2 = self.font.size(sub)[0]
                self.draw_text_with_shadow(txt, WIDTH // 2 - w1 // 2, HEIGHT // 2 - 50, YELLOW, large=True)
                self.draw_text_with_shadow(sub, WIDTH // 2 - w2 // 2, HEIGHT // 2 + 40, WHITE)

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
