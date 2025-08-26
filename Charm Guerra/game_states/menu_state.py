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
        except pygame.error as e:
            print(f"AVISO: Fonte personalizada não encontrada em '{font_path}'. Usando fonte padrão. Erro: {e}")
            self.title_font = pygame.font.Font(None, 80)
            self.button_font = pygame.font.Font(None, 40)

        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        # Cores dos botões
        button_base_color = (70, 130, 180) # Azul aço
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
        # Atualiza o texto dos botões caso o idioma tenha mudado
        self.buttons[0].text = TEXTS[self.game_manager.language]['start_game']
        self.buttons[0].text_surface = self.button_font.render(self.buttons[0].text, True, (255, 255, 255))
        self.buttons[0].text_rect = self.buttons[0].text_surface.get_rect(center=self.buttons[0].rect.center)

        self.buttons[1].text = TEXTS[self.game_manager.language]['settings']
        self.buttons[1].text_surface = self.button_font.render(self.buttons[1].text, True, (255, 255, 255))
        self.buttons[1].text_rect = self.buttons[1].text_surface.get_rect(center=self.buttons[1].rect.center)

        self.buttons[2].text = TEXTS[self.game_manager.language]['exit_game']
        self.buttons[2].text_surface = self.button_font.render(self.buttons[2].text, True, (255, 255, 255))
        self.buttons[2].text_rect = self.buttons[2].text_surface.get_rect(center=self.buttons[2].rect.center)


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
        title_text_surface = self.title_font.render(TEXTS[self.game_manager.language]['game_title'], True, (255, 255, 255)) # Cor do texto branca
        title_text_rect = title_text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        screen.blit(title_text_surface, title_text_rect)

        for button in self.buttons:
            button.draw(screen)
