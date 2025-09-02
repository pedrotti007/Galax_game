# utils/game_manager.py
import pygame

class GameManager:
    def __init__(self):
        self.current_state = None
        self.states = {}
        self.volume = 0.5 # Volume inicial (0.0 a 1.0)
        self.language = 'pt' # Idioma inicial

    def add_state(self, name, state):
        self.states[name] = state

    def set_state(self, name):
        if name in self.states:
            self.current_state = self.states[name]
            self.current_state.enter() # Método para inicializar o estado
        else:
            print(f"Erro: Estado '{name}' não encontrado.")

    def handle_event(self, event):
        if self.current_state:
            self.current_state.handle_event(event)

    def update(self):
        if self.current_state:
            self.current_state.update()

    def draw(self, screen):
        if self.current_state:
            self.current_state.draw(screen)

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol)) # Garante que o volume esteja entre 0 e 1
        pygame.mixer.music.set_volume(self.volume)
        print(f"Volume ajustado para: {self.volume}")

    def set_language(self, lang):
        self.language = lang
        print(f"Idioma ajustado para: {self.language}")

# Dicionário de textos para localização
TEXTS = {
    'pt': {
        'game_title': 'GUERRA INTERGALAXIA',
        'start_game': 'Iniciar Jogo',
        'settings': 'Ajustes',
        'exit_game': 'Sair',
        'volume': 'Volume:',
        'language': 'Idioma:',
        'credits': 'Créditos:',
        'credits_text': 'Desenvolvido por:Pedro Jorge, Rafael Veloso, Alef Pires e Victor Solano\nArt: Yasmin França\nMusic: Dimitri Araujo',
        'back': 'Voltar'
    },
    'en': {
        'game_title': 'INTERGALAXY WAR',
        'start_game': 'Start Game',
        'settings': 'Settings',
        'exit_game': 'Exit',
        'volume': 'Volume:',
        'language': 'Language:',
        'credits': 'Credits:',
        'credits_text': 'Developed by: Pedro Jorge, Rafael Veloso, Alef Pires and Victor Solano\nArt: Yasmin França\nMusic: Dimitri Araujo',
        'back': 'Back'
    }
}
