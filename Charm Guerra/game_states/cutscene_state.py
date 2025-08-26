# game_states/cutscene_state.py

import pygame

class CutsceneState:
    def __init__(self, game_manager, screen_width, screen_height):
        self.game_manager = game_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_frame_index = 0
        self.frames = []
        self.frame_duration = 1000 # Duração de cada frame em milissegundos (1 segundo)
        self.last_frame_time = 0

        # --- PONTO DE MODIFICAÇÃO: FRAMES DA CUTSCENE ---
        # Carregue suas imagens da cutscene aqui.
        # Coloque-as em assets/images/cutscene_frame_X.png
        # Exemplo:
        # self.frames.append(pygame.image.load('assets/images/cutscene_frame_1.png').convert_alpha())
        # self.frames.append(pygame.image.load('assets/images/cutscene_frame_2.png').convert_alpha())
        # ... adicione mais frames conforme necessário
        # Certifique-se de que as imagens são do tamanho da tela ou escale-as.

        # Placeholder para frames:
        # Se você não tiver imagens, pode usar uma tela preta com texto
        self.frames.append(pygame.image.load('assets/videos/cutscene.mp4').convert_alpha())
        # Fim do placeholder

        if not self.frames:
            print("Aviso: Nenhuma imagem de cutscene carregada. A cutscene será pulada.")
            self.frames.append(self._create_placeholder_frame("Cutscene vazia. Pressione qualquer tecla para continuar.", (255,255,255)))


    def _create_placeholder_frame(self, text, color):
        """Cria uma superfície com texto para usar como frame placeholder."""
        surface = pygame.Surface((self.screen_width, self.screen_height))
        surface.fill((0, 0, 0)) # Fundo preto
        font = pygame.font.SysFont('Arial', 40)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        surface.blit(text_surface, text_rect)
        return surface

    def enter(self):
        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()

    def handle_event(self, event):
        # Permite pular a cutscene com qualquer tecla ou clique
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.game_manager.set_state('gameplay')

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_time > self.frame_duration:
            self.current_frame_index += 1
            self.last_frame_time = current_time
            if self.current_frame_index >= len(self.frames):
                self.game_manager.set_state('gameplay') # Terminou a cutscene, vai para o gameplay

    def draw(self, screen):
        if self.frames and self.current_frame_index < len(self.frames):
            screen.blit(self.frames[self.current_frame_index], (0, 0))
        else:
            screen.fill((0, 0, 0)) # Tela preta se não houver frames ou se já terminou
