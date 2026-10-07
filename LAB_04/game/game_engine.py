import pygame
import array
from .bird import Bird
from .pipe import Pipe

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
RED = (230, 50, 50)
YELLOW = (255, 215, 0)

def generate_beep(frequency, duration, volume=0.3, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    amplitude = int(32767 * volume)
    period = sample_rate / frequency
    for i in range(n_samples):
        val = amplitude if (i % period) < (period / 2) else -amplitude
        buf.append(val)
    return pygame.mixer.Sound(buf)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.snd_flap = generate_beep(600, 0.08)
            self.snd_score = generate_beep(880, 0.12)
            self.snd_die = generate_beep(180, 0.35)
        except Exception:
            self.snd_flap = None
            self.snd_score = None
            self.snd_die = None
        self.font = pygame.font.SysFont('Arial', 26)
        self.large_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.difficulties = {'Easy': {'speed': 3, 'gap': 180, 'interval': 110}, 'Medium': {'speed': 4, 'gap': 150, 'interval': 90}, 'Hard': {'speed': 6, 'gap': 125, 'interval': 65}}
        self.difficulty = 'Medium'
        self.reset(self.difficulty)

    def reset(self, difficulty=None):
        if difficulty:
            self.difficulty = difficulty
        cfg = self.difficulties[self.difficulty]
        self.pipe_speed = cfg['speed']
        self.pipe_gap = cfg['gap']
        self.pipe_interval = cfg['interval']
        self.bird = Bird(self.width // 4, self.height // 2)
        self._spawn_timer = 0
        self.pipes = [Pipe(self.width + 100, self.height, gap=self.pipe_gap, speed=self.pipe_speed)]
        self.score = 0
        self.game_over = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.game_over and event.key == pygame.K_SPACE:
                self.bird.flap()
                if self.snd_flap: self.snd_flap.play()
            elif self.game_over:
                if event.key == pygame.K_1:
                    self.reset('Easy')
                elif event.key == pygame.K_2:
                    self.reset('Medium')
                elif event.key == pygame.K_3:
                    self.reset('Hard')
                elif event.key == pygame.K_r:
                    self.reset(self.difficulty)
        elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
            self.bird.flap()
            if self.snd_flap: self.snd_flap.play()

    def handle_input(self):
        pass

    def trigger_game_over(self):
        if not self.game_over:
            self.game_over = True
            if self.snd_die: self.snd_die.play()

    def update(self):
        if self.game_over:
            return
        self.bird.update()
        if self.bird.y - self.bird.radius <= 0 or self.bird.y + self.bird.radius >= self.height:
            self.trigger_game_over()
            return
        self._spawn_timer += 1
        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0
            self.pipes.append(Pipe(self.width, self.height, gap=self.pipe_gap, speed=self.pipe_speed))
        for pipe in self.pipes:
            pipe.move()
            if pipe.top_rect().colliderect(self.bird.rect()) or pipe.bottom_rect().colliderect(self.bird.rect()):
                self.trigger_game_over()
                return
            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1
                if self.snd_score: self.snd_score.play()
        self.pipes = [p for p in self.pipes if not p.off_screen()]

    def render(self, screen):
        for pipe in self.pipes:
            pygame.draw.rect(screen, GREEN, pipe.top_rect())
            pygame.draw.rect(screen, GREEN, pipe.bottom_rect())
        pygame.draw.circle(screen, WHITE, (int(self.bird.x), int(self.bird.y)), self.bird.radius)
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        diff_text = self.font.render(f'Mode: {self.difficulty}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(diff_text, (self.width - diff_text.get_width() - 10, 10))
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            go_lbl = self.large_font.render('GAME OVER', True, RED)
            sc_lbl = self.font.render(f'Final Score: {self.score}', True, WHITE)
            r_lbl = self.font.render('Press R to Restart', True, YELLOW)
            opt_lbl = self.font.render('Select Difficulty:', True, WHITE)
            e_lbl = self.font.render('[1] Easy   [2] Medium   [3] Hard', True, WHITE)
            screen.blit(go_lbl, (self.width // 2 - go_lbl.get_width() // 2, 180))
            screen.blit(sc_lbl, (self.width // 2 - sc_lbl.get_width() // 2, 250))
            screen.blit(r_lbl, (self.width // 2 - r_lbl.get_width() // 2, 320))
            screen.blit(opt_lbl, (self.width // 2 - opt_lbl.get_width() // 2, 390))
            screen.blit(e_lbl, (self.width // 2 - e_lbl.get_width() // 2, 430))
