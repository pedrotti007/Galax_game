# game_states/menu_state.py

import pygame
import sys
import os
from utils.button import Button
from utils.game_manager import TEXTS # Importa o dicionário de textos

class MenuState:
    def __init__(self, game_manager, screen_width, screen_height):
        self.game_manager = game_manager
        self.screen_width = screen_width
        self.screen_height = screen_height

        # --- PONTO DE MODIFICAÇÃO: IMAGEM DE FUNDO ---
        # Certifique-se de que o caminho para a imagem está correto.
        # Coloque sua imagem em assets/images/background_menu.png
        self.background_image = None # Garante que o atributo sempre exista
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            image_path = os.path.join(project_root, 'assets', 'images', 'background_menu.png')
            self.background_image = pygame.image.load(image_path).convert()
            self.background_image = pygame.transform.scale(self.background_image, (screen_width, screen_height))
        except pygame.error as e:
            print(f"AVISO: Erro ao carregar imagem de fundo '{image_path}': {e}")

        # --- PONTO DE MODIFICAÇÃO: FONTE E TAMANHO ---
        # Carregue sua fonte personalizada aqui.
        # Coloque sua fonte em assets/fonts/sua_fonte.ttf
        try:
            font_path = os.path.join(project_root, 'assets', 'fonts', 'sua_fonte.ttf')
            self.title_font = pygame.font.Font(font_path, 80)
            self.button_font = pygame.font.Font(font_path, 40)
            # verifica se as fontes foram realmente criadas
            if not hasattr(self.title_font, 'render') or not hasattr(self.button_font, 'render'):
                raise Exception("Fonte inválida")
        except Exception as e:
            # Captura FileNotFoundError, pygame.error e quaisquer outros problemas
            print(f"AVISO: Fonte personalizada não encontrada ou inválida em '{font_path}'. Usando fonte padrão. Erro: {e}")
            self.title_font = pygame.font.Font(None, 80)
            self.button_font = pygame.font.Font(None, 40)

        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        # Cores dos botões
        button_base_color = (0,0,0)
        button_hover_color = (100, 149, 237) # Azul centáurea

        button_width = 300
        button_height = 70
        button_spacing = 20
        total_button_height = (button_height * 3) + (button_spacing * 2)
        start_y = (self.screen_height - total_button_height) // 2 + 50 # Ajuste para centralizar abaixo do título

        # Botão Iniciar Jogo
        start_button = Button(
            (self.screen_width - button_width) // 2,
            start_y,
            button_width,
            button_height,
            TEXTS[self.game_manager.language]['start_game'],
            self.button_font,
            button_base_color,
            button_hover_color,
            lambda: self.game_manager.set_state('cutscene')
        )
        self.buttons.append(start_button)

        # Botão Ajustes
        settings_button = Button(
            (self.screen_width - button_width) // 2,
            start_y + button_height + button_spacing,
            button_width,
            button_height,
            TEXTS[self.game_manager.language]['settings'],
            self.button_font,
            button_base_color,
            button_hover_color,
            lambda: self.game_manager.set_state('settings')
        )
        self.buttons.append(settings_button)

        # Botão Sair
        exit_button = Button(
            (self.screen_width - button_width) // 2,
            start_y + (button_height + button_spacing) * 2,
            button_width,
            button_height,
            TEXTS[self.game_manager.language]['exit_game'],
            self.button_font,
            button_base_color,
            button_hover_color,
            self._exit_game
        )
        self.buttons.append(exit_button)

    def _exit_game(self):
        pygame.quit()
        sys.exit()

    def enter(self):
        # --- PONTO DE MODIFICAÇÃO: MÚSICA DO MENU ---
        # Garante que o caminho para a música está correto.
        # Coloque sua música em assets/sounds/menu_music.mp3
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            music_path = os.path.join(project_root, 'assets', 'sounds', 'menu_music.mp3')
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.game_manager.volume)
            pygame.mixer.music.play(-1)  # Toca em loop
        except pygame.error as e:
            print(f"AVISO: Erro ao carregar ou tocar a música do menu '{music_path}': {e}")
            
        # Atualiza o texto dos botões caso o idioma tenha mudado
        # Tenta renderizar com a fonte configurada; se falhar, usa SysFont como fallback.
        for i, key in enumerate(['start_game', 'settings', 'exit_game']):
            try:
                self.buttons[i].text = TEXTS[self.game_manager.language][key]
                self.buttons[i].text_surface = self.button_font.render(self.buttons[i].text, True, (255, 255, 255))
                self.buttons[i].text_rect = self.buttons[i].text_surface.get_rect(center=self.buttons[i].rect.center)
            except Exception:
                # fallback seguro
                fallback_font = pygame.font.SysFont(None, 40)
                self.buttons[i].text = TEXTS[self.game_manager.language][key]
                self.buttons[i].text_surface = fallback_font.render(self.buttons[i].text, True, (255, 255, 255))
                self.buttons[i].text_rect = self.buttons[i].text_surface.get_rect(center=self.buttons[i].rect.center)

    def exit(self):
        # Para a música quando sai do estado do menu
        pygame.mixer.music.stop()

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def update(self):
        pass # Nenhuma lógica de atualização contínua para o menu

    def draw(self, screen):
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill((0, 0, 0)) # Fundo preto se a imagem não carregar

        # Desenha o título do jogo
        try:
            title_text_surface = self.title_font.render(TEXTS[self.game_manager.language]['game_title'], True, (255, 255, 255))
        except Exception:
            title_font_fallback = pygame.font.SysFont(None, 80)
            title_text_surface = title_font_fallback.render(TEXTS[self.game_manager.language]['game_title'], True, (255, 255, 255))
        title_text_rect = title_text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        screen.blit(title_text_surface, title_text_rect)

        for button in self.buttons:
            button.draw(screen)
