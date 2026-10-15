import pygame
import random
from .fruit import Fruit

# Game Engine

WHITE = (255, 255, 255)
BOMB_BLACK = (30, 30, 30)
FRUIT_COLORS = [(220, 60, 60), (230, 140, 40), (230, 200, 40), (90, 180, 90)]

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.fruits = []
        self.trail = []  # recent mouse positions, drawn as the "blade"

        self.spawn_interval = 55  # frames between spawns
        self._spawn_timer = 0
        self.bomb_chance = 0.15
        self.speed_scale = 1.0

        self.lives = 3
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.game_over = False

        self.difficulty = "Medium"

        self.difficulty_settings = {
            "Easy": {
                "spawn_interval": 75,
                "bomb_chance": 0.05,
            },
            "Medium": {
                "spawn_interval": 55,
                "bomb_chance": 0.12,
            },
            "Hard": {
                "spawn_interval": 35,
                "bomb_chance": 0.22,
            },
        }

        self.should_exit = False

    def start_new_game(self, difficulty):
            self.difficulty = difficulty

            settings = self.difficulty_settings[difficulty]
            self.spawn_interval = settings["spawn_interval"]
            self.bomb_chance = settings["bomb_chance"]

            self.fruits.clear()
            self.trail.clear()

            self.score = 0
            self.lives = 3
            self._spawn_timer = 0
            self.game_over = False

    def get_menu_buttons(self):
            labels = ["Easy", "Medium", "Hard", "Exit"]

            button_width = 120
            button_height = 48
            gap = 12

            total_width = len(labels) * button_width + (
                len(labels) - 1
            ) * gap

            start_x = (self.width - total_width) // 2
            y = self.height // 2 + 65

            return {
                label: pygame.Rect(
                    start_x + i * (button_width + gap),
                    y,
                    button_width,
                    button_height,
                )
                for i, label in enumerate(labels)
            }
    def spawn_fruit(self):
        x = random.randint(60, self.width - 60)
        vy = -random.uniform(13, 16) * self.speed_scale
        vx = random.uniform(-2, 2)
        gravity = 0.35
        kind = "bomb" if random.random() < self.bomb_chance else "fruit"

        fruit = Fruit(x, self.height + 30, vx, vy, gravity, kind=kind)
        fruit.color = BOMB_BLACK if kind == "bomb" else random.choice(FRUIT_COLORS)
        self.fruits.append(fruit)

    def handle_event(self, event):
            if self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for label, rect in self.get_menu_buttons().items():
                        if rect.collidepoint(event.pos):
                            if label == "Exit":
                                self.should_exit = True
                            else:
                                self.start_new_game(label)
                            return
                return

            if event.type == pygame.MOUSEMOTION:
                self._handle_motion(event.pos)

    def _handle_motion(self, pos):
        x, y = pos
        for fruit in self.fruits:
            if not fruit.sliced and fruit.contains_point(x, y):
                self._slice(fruit)

        self.trail.append(pos)
        if len(self.trail) > 15:
            self.trail.pop(0)

    def _slice(self, fruit):
        fruit.sliced = True
        if fruit.kind == "bomb":
            self.game_over = True
        else:
            self.score += 1

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.spawn_fruit()

        still_alive = []
        for fruit in self.fruits:
            fruit.update()
            if fruit.sliced:
                continue
            if fruit.off_screen(self.height):
                if fruit.kind == "fruit":
                    self.lives -= 1
                continue
            still_alive.append(fruit)
        self.fruits = still_alive

        if self.lives <= 0:
            self.game_over = True

    def render(self, screen):
        for fruit in self.fruits:
            color = getattr(fruit, "color", WHITE)
            pygame.draw.circle(screen, color, (int(fruit.x), int(fruit.y)), fruit.radius)

        if len(self.trail) >= 2:
            pygame.draw.lines(screen, WHITE, False, self.trail, 3)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(lives_text, (self.width - 130, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            title_font = pygame.font.SysFont("Arial", 56, bold=True)
            title = title_font.render(
                "GAME OVER", True, (255, 80, 80)
            )
            screen.blit(
                title,
                title.get_rect(
                    center=(self.width // 2, self.height // 2 - 100)
                ),
            )

            score_text = self.font.render(
                f"Final Score: {self.score}", True, WHITE
            )
            screen.blit(
                score_text,
                score_text.get_rect(
                    center=(self.width // 2, self.height // 2 - 40)
                ),
            )

            prompt = self.font.render(
                "Choose a difficulty or exit", True, WHITE
            )
            screen.blit(
                prompt,
                prompt.get_rect(
                    center=(self.width // 2, self.height // 2 + 15)
                ),
            )

            for label, rect in self.get_menu_buttons().items():
                pygame.draw.rect(
                    screen, (65, 85, 125), rect, border_radius=8
                )
                pygame.draw.rect(
                    screen, WHITE, rect, width=2, border_radius=8
                )

                text = self.font.render(label, True, WHITE)
                screen.blit(text, text.get_rect(center=rect.center))