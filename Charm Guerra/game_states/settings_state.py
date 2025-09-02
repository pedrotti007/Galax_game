# game_states/settings_state.py
import sys
import os

# Adiciona o diretório raiz do projeto ao path do Python para resolver o problema de importação.
# Isso garante que a pasta 'utils' seja encontrada.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pygame
from utils.game_manager import TEXTS

class SettingsState:
    def __init__(self, game_manager, screen_width, screen_height):
        self.game_manager = game_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 50)
        self.lang_font = pygame.font.Font(None, 45)
        self.credits_font = pygame.font.Font(None, 32)

        # --- Elementos da UI ---
        # As superfícies e rects serão inicializados/atualizados em _setup_ui()
        self.title_surface = None
        self.title_rect = None
        self.volume_label_surface = None
        self.language_label_surface = None
        self.credits_label_surface = None

        self.back_button_text = None
        self.back_button_rect = None
        self.lang_pt_surface = None
        self.lang_pt_rect = None
        self.lang_en_surface = None
        self.lang_en_rect = None
        self.credits_text_surfaces = []

        # Slider de Volume
        self.volume_slider_rect = pygame.Rect(self.screen_width / 2 - 150, self.screen_height / 2 - 100, 300, 20)
        self.volume_handle_rect = pygame.Rect(0, 0, 30, 40)
        self.dragging_handle = False

        # Cores
        self.text_color = (220, 220, 255)
        self.selected_lang_color = (0,0,255)  # Azul para idioma selecionado
        self.unselected_lang_color = (255, 255, 255) # Branco para não selecionado

    def enter(self):
        """Método chamado quando o estado é ativado."""
        self._setup_ui()
        # Posiciona o handle de volume com base no volume atual
        self.update_handle_position()

    def _setup_ui(self):
        """Cria ou atualiza todos os elementos de texto da UI com base no idioma atual."""
        lang = self.game_manager.language

        # Título
        title_text = TEXTS[lang]['settings']
        self.title_surface = self.font.render(title_text, True, self.text_color)
        self.title_rect = self.title_surface.get_rect(center=(self.screen_width / 2, 120))

        # Label do Volume
        volume_label_text = TEXTS[lang]['volume']
        self.volume_label_surface = self.small_font.render(volume_label_text, True, self.text_color)

        # Label do Idioma
        language_label_text = TEXTS[lang]['language']
        self.language_label_surface = self.small_font.render(language_label_text, True, self.text_color)

        # Botões de Idioma
        pt_color = self.selected_lang_color if lang == 'pt' else self.unselected_lang_color
        en_color = self.selected_lang_color if lang == 'en' else self.unselected_lang_color

        self.lang_pt_surface = self.lang_font.render("Português (Brasil)", True, pt_color)
        self.lang_pt_rect = self.lang_pt_surface.get_rect(midleft=(self.screen_width / 2 - 150, self.screen_height / 2))

        self.lang_en_surface = self.lang_font.render("English", True, en_color)
        self.lang_en_rect = self.lang_en_surface.get_rect(midleft=(self.lang_pt_rect.right + 30, self.screen_height / 2))

        # --- NOVO: CRÉDITOS ---
        # Label dos Créditos
        credits_label_text = TEXTS[lang]['credits']
        self.credits_label_surface = self.small_font.render(credits_label_text, True, self.text_color)

        # Texto dos Créditos (multi-linha)
        self.credits_text_surfaces.clear()
        credits_full_text = TEXTS[lang]['credits_text']
        for line in credits_full_text.split('\n'):
            line_surface = self.credits_font.render(line, True, self.text_color)
            self.credits_text_surfaces.append(line_surface)

        # Botão Voltar
        back_text_str = TEXTS[lang]['back']
        self.back_button_text = self.small_font.render(back_text_str, True, self.text_color)
        self.back_button_rect = self.back_button_text.get_rect(center=(self.screen_width / 2, self.screen_height - 120))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botão esquerdo do mouse
                if self.back_button_rect.collidepoint(event.pos):
                    self.game_manager.set_state('menu')
                    return

                # --- NOVO: LÓGICA DE MUDANÇA DE IDIOMA ---
                if self.lang_pt_rect.collidepoint(event.pos):
                    self.game_manager.set_language('pt')
                    self._setup_ui()  # Atualiza a UI com o novo idioma
                elif self.lang_en_rect.collidepoint(event.pos):
                    self.game_manager.set_language('en')
                    self._setup_ui()  # Atualiza a UI com o novo idioma

                if self.volume_handle_rect.collidepoint(event.pos):
                    self.dragging_handle = True
                elif self.volume_slider_rect.collidepoint(event.pos):
                    self.update_volume_from_mouse(event.pos[0])
                    self.dragging_handle = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_handle = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_handle:
                self.update_volume_from_mouse(event.pos[0])

    def update_volume_from_mouse(self, mouse_x):
        # Calcula a nova posição do handle
        new_x = max(self.volume_slider_rect.left, min(mouse_x, self.volume_slider_rect.right))
        
        # Calcula a proporção do volume (0.0 a 1.0)
        volume_ratio = (new_x - self.volume_slider_rect.left) / self.volume_slider_rect.width
        self.game_manager.set_volume(volume_ratio)
        self.update_handle_position()

    def update_handle_position(self):
        """Atualiza a posição do handle com base no volume do game_manager."""
        handle_x = self.volume_slider_rect.left + (self.game_manager.volume * self.volume_slider_rect.width)
        self.volume_handle_rect.center = (handle_x, self.volume_slider_rect.centery)

    def update(self):
        """Lógica de atualização do estado (ex: animações)."""
        pass

    def draw(self, screen):
        screen.fill((0,0,52))  # Fundo azul escuro

        # Título
        screen.blit(self.title_surface, self.title_rect)

        # Label do Volume
        volume_label_rect = self.volume_label_surface.get_rect(midright=(self.volume_slider_rect.left - 20, self.volume_slider_rect.centery))
        screen.blit(self.volume_label_surface, volume_label_rect)

        # Slider de Volume
        pygame.draw.rect(screen, (50, 50, 80), self.volume_slider_rect, border_radius=10)  # Barra
        pygame.draw.rect(screen, (180, 180, 255), self.volume_handle_rect, border_radius=8) # Handle

        # Label do Idioma
        language_label_rect = self.language_label_surface.get_rect(midright=(self.lang_pt_rect.left - 20, self.lang_pt_rect.centery))
        screen.blit(self.language_label_surface, language_label_rect)

        # Botões de Idioma
        screen.blit(self.lang_pt_surface, self.lang_pt_rect)
        screen.blit(self.lang_en_surface, self.lang_en_rect)

        # --- NOVO: DESENHAR CRÉDITOS ---
        # Posição inicial para os créditos
        credits_y_start = self.screen_height / 2 + 100

        # Label dos Créditos
        credits_label_rect = self.credits_label_surface.get_rect(center=(self.screen_width / 2, credits_y_start))
        screen.blit(self.credits_label_surface, credits_label_rect)

        # Texto dos Créditos (multi-linha)
        line_y = credits_y_start + 50
        line_height = self.credits_font.get_height() + 5
        for line_surface in self.credits_text_surfaces:
            line_rect = line_surface.get_rect(center=(self.screen_width / 2, line_y))
            screen.blit(line_surface, line_rect)
            line_y += line_height

        # Botão Voltar
        if self.back_button_text:
            screen.blit(self.back_button_text, self.back_button_rect)