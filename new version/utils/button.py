import pygame
import os


class Button:
    """Uma classe de botão simples e reutilizável para Pygame.

    Suporta duas formas de chamada para compatiblidade com código existente:
    - Button(x, y, w, h, text, on_click, font_size=36, font_name=None)
      (assinatura antiga)
    - Button(x, y, w, h, text, font_obj, base_color, hover_color, on_click)
      (usada em `game_states/menu_state.py` neste projeto)
    """

    def __init__(self, x, y, width, height, text, *args, font_size=36, font_name=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False

        # valores default
        self.color = (100, 100, 100)  # Cinza escuro
        self.hover_color = (150, 150, 150)  # Cinza claro
        self.on_click = None
        self.font = None

        # Interpreta os args para suportar ambas assinaturas
        # Possibilidades esperadas:
        # 1) (on_click[, font_size, font_name])
        # 2) (font_obj, base_color, hover_color, on_click)

        try:
            if len(args) >= 1 and isinstance(args[0], pygame.font.Font):
                # Assinatura nova: (font_obj, base_color, hover_color, on_click)
                self.font = args[0]
                if len(args) >= 2:
                    self.color = args[1]
                if len(args) >= 3:
                    self.hover_color = args[2]
                if len(args) >= 4:
                    self.on_click = args[3]
            else:
                # Assinatura antiga: (on_click[, font_size, font_name])
                if len(args) >= 1 and callable(args[0]):
                    self.on_click = args[0]
                # Sobrescreve font se font_name fornecido via kwargs
                if font_name:
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(script_dir)
                    font_path = os.path.join(project_root, 'assets', 'fonts', font_name)
                    try:
                        self.font = pygame.font.Font(font_path, font_size)
                    except pygame.error:
                        print(f"AVISO: Falha ao carregar a fonte '{font_path}'. Usando fonte padrão.")
                        self.font = pygame.font.Font(None, font_size)
                else:
                    # Usa font_size para criar uma fonte padrão se nenhuma fonte foi atribuída
                    self.font = pygame.font.Font(None, font_size)
        except Exception as e:
            print(f"AVISO: Erro ao inicializar Button: {e}")
            # fallback explícito
            if not self.font:
                self.font = pygame.font.Font(None, font_size)

        # Garante que on_click seja uma função (fallback noop)
        if not callable(self.on_click):
            self.on_click = lambda: None

        # Renderiza o texto e centraliza, com fallback caso a fonte seja inválida
        try:
            if not self.font:
                raise ValueError("Fonte inválida")
            self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        except Exception:
            # Cria uma fonte padrão como fallback e tenta renderizar novamente
            try:
                self.font = pygame.font.Font(None, font_size)
                self.text_surface = self.font.render(self.text, True, (255, 255, 255))
            except Exception as e:
                # Como último recurso, cria uma superfície simples contendo o texto via SysFont
                try:
                    sysfont = pygame.font.SysFont(None, font_size)
                    self.text_surface = sysfont.render(self.text, True, (255, 255, 255))
                except Exception as e2:
                    # Cria uma superfície vazia para evitar exceções posteriores
                    print(f"AVISO: Não foi possível renderizar texto do botão: {e2}")
                    self.text_surface = pygame.Surface((1, 1))

        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1:  # Botão esquerdo do mouse
                try:
                    self.on_click()
                except Exception as e:
                    print(f"Erro ao executar callback do botão: {e}")

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        screen.blit(self.text_surface, self.text_rect)

