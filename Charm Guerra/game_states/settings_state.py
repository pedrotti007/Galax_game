# game_states/settings_state.py

import pygame
from utils.button import Button
from utils.game_manager import TEXTS


class SettingsState:
    def __init__(self, game_manager, screen_width, screen_height):
        self.game_manager = game_manager
        self.screen_width = screen_width
        self.screen_height = screen_height

        # --- PONTO DE MODIFICAÇÃO: FONTE PARA AJUSTES ---
        try:
            self.font_path = 'assets/fonts/game_font.ttf'  # Caminho para sua fonte
            self.settings_font = pygame.font.Font(self.font_path, 30)
            self.credits_font = pygame.font.Font(self.font_path, 20)
        except FileNotFoundError:
            print("Fonte personalizada não encontrada. Usando fonte padrão do Pygame para ajustes.")
            self.settings_font = pygame.font.SysFont('Arial', 30)
            self.credits_font = pygame.font.SysFont('Arial', 20)

        self.buttons = []
        self._create_buttons()

        self.slider_rect = pygame.Rect(self.screen_width // 2 - 100, 200, 200, 20)
        self.slider_handle_rect = pygame.Rect(
            self.slider_rect.x + self.game_manager.volume * (self.slider_rect.width - 20), self.slider_rect.y - 5, 20,
            30)
        self.dragging_slider = False

    def _create_buttons(self):
        button_base_color = (70, 130, 180)
        button_hover_color = (100, 149, 237)
        button_width = 150
        button_height = 50
        spacing = 10

        # Botões de idioma
        lang_x = self.screen_width // 2 - (button_width * 2 + spacing) // 2
        pt_button = Button(lang_x, 300, button_width, button_height, "Português", self.settings_font, button_base_color,
                           button_hover_color, lambda: self.game_manager.set_language('pt'))
        en_button = Button(lang_x + button_width + spacing, 300, button_width, button_height, "English",
                           self.settings_font, button_base_color, button_hover_color,
                           lambda: self.game_manager.set_language('en'))
        self.buttons.extend([pt_button, en_button])

        # Botão Voltar
        back_button = Button(
            (self.screen_width - button_width) // 2,
            self.screen_height - 100,
            button_width,
            button_height,
            TEXTS[self.game_manager.language]['back'],
            self.settings_font,
            button_base_color,
            button_hover_color,
            lambda: self.game_manager.set_state('menu')
        )
        self.buttons.append(back_button)

    def enter(self):
        # Atualiza o texto do botão "Voltar" caso o idioma tenha mudado
        self.buttons[-1].text = TEXTS[self.game_manager.language]['back']
        self.buttons[-1].text_surface = self.settings_font.render(self.buttons[-1].text, True, (255, 255, 255))
        self.buttons[-1].text_rect = self.buttons[-1].text_surface.get_rect(center=self.buttons[-1].rect.center)

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

        # Lógica do slider de volume
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.slider_handle_rect.collidepoint(event.pos):
                self.dragging_slider = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_slider = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_slider:
                new_x = event.pos[0] - self.slider_handle_rect.width // 2
                new_x = max(self.slider_rect.x,
                            min(new_x, self.slider_rect.x + self.slider_rect.width - self.slider_handle_rect.width))
                self.slider_handle_rect.x = new_x

                # Calcula o volume baseado na posição do handle
                volume_ratio = (self.slider_handle_rect.x - self.slider_rect.x) / (
                            self.slider_rect.width - self.slider_handle_rect.width)
                self.game_manager.set_volume(volume_ratio)

    def update(self):
        # Atualiza a posição do handle do slider se o volume for alterado por outro meio
        self.slider_handle_rect.x = self.slider_rect.x + self.game_manager.volume * (
                    self.slider_rect.width - self.slider_handle_rect.width)

    def draw(self, screen):
        screen.fill((50, 50, 50))  # Fundo cinza escuro

        # Título da tela de ajustes
        title_text_surface = self.settings_font.render(TEXTS[self.game_manager.language]['settings'], True,
                                                       (255, 255, 255))
        title_text_rect = title_text_surface.get_rect(center=(self.screen_width // 2, 50))
        screen.blit(title_text_surface, title_text_rect)

        # Texto Volume
        volume_text_surface = self.settings_font.render(TEXTS[self.game_manager.language]['volume'], True,
                                                        (255, 255, 255))
        screen.blit(volume_text_surface, (self.screen_width // 2 - 100, 150))

        # Desenha o slider de volume
        pygame.draw.rect(screen, (100, 100, 100), self.slider_rect, border_radius=5)  # Barra do slider
        pygame.draw.rect(screen, (200, 200, 200), self.slider_handle_rect, border_radius=5)  # Handle do slider

        # Texto Idioma
        lang_text_surface = self.settings_font.render(TEXTS[self.game_manager.language]['language'], True,
                                                      (255, 255, 255))
        screen.blit(lang_text_surface, (self.screen_width // 2 - 100, 250))

        # Texto Créditos
        credits_title_surface = self.settings_font.render(TEXTS[self.game_manager.language]['credits'], True,
                                                          (255, 255, 255))
        credits_title_rect = credits_title_surface.get_rect(center=(self.screen_width // 2, 400))
        screen.blit(credits_title_surface, credits_title_rect)

        # Conteúdo dos créditos
        credits_content = TEXTS[self.game_manager.language]['credits_text'].split('\n')
        y_offset = 450
        for line in credits_content:
            line_surface = self.credits_font.render(line, True, (255, 255, 255))
            line_rect = line_surface.get_rect(center=(self.screen_width // 2, y_offset))
            screen.blit(line_surface, line_rect)
            y_offset += self.credits_font.get_height() + 5

        for button in self.buttons:
            button.draw(screen)
