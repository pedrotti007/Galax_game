# main.py

import pygame
import sys
import os
from utils.game_manager import GameManager
from game_states.menu_state import MenuState
from game_states.cutscene_state import CutsceneState
from game_states.gameplay_state import GameplayState
from game_states.settings_state import SettingsState

# --- CONFIGURAÇÕES DA TELA ---
# Resolução final da janela
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
# Resolução lógica da gameplay para o efeito "pixel art" escalado
GAMEPLAY_LOGICAL_WIDTH = 480
GAMEPLAY_LOGICAL_HEIGHT = 270
FPS = 60 # Frames por segundo

def main():
    pygame.init()
    pygame.mixer.init() # Inicializa o mixer para áudio

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Guerra Intergalatica") # Título da janela do jogo

    game_manager = GameManager()

    # Adiciona os estados ao gerenciador
    game_manager.add_state('menu', MenuState(game_manager, SCREEN_WIDTH, SCREEN_HEIGHT))
    game_manager.add_state('cutscene', CutsceneState(game_manager, SCREEN_WIDTH, SCREEN_HEIGHT))
    game_manager.add_state('gameplay', GameplayState(game_manager, GAMEPLAY_LOGICAL_WIDTH, GAMEPLAY_LOGICAL_HEIGHT))
    game_manager.add_state('settings', SettingsState(game_manager, SCREEN_WIDTH, SCREEN_HEIGHT))

    # Define o estado inicial do jogo
    game_manager.set_state('menu')

    clock = pygame.time.Clock()
    running = True

    # --- PONTO DE MODIFICAÇÃO: MÚSICA DE FUNDO DO MENU ---
    # Carregue e toque a música do menu aqui
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        music_file = os.path.join(script_dir, 'assets', 'audio', 'sounds', 'background_music.mp3')
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(game_manager.volume) # Define o volume inicial
        pygame.mixer.music.play(-1) # -1 para tocar em loop infinito
    except pygame.error as e:
        print(f"Erro ao carregar música de fundo: {e}")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game_manager.handle_event(event) # Passa o evento para o estado atual

        game_manager.update() # Atualiza a lógica do estado atual

        game_manager.draw(screen) # Desenha o estado atual na tela

        pygame.display.flip() # Atualiza a tela inteira
        clock.tick(FPS) # Controla o FPS

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
