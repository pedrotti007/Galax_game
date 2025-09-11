# main.pyc
# pyright: ignore[reportMissingImports]
import pygame
import sys
from utils.game_manager import GameManager
from game_states.menu_state import MenuState
from game_states.cutscene_state import CutsceneState
from game_states.gameplay_state import GameplayState
from game_states.settings_state import SettingsState

# --- CONFIGURAÇÕES DA TELA ---
FPS = 90 # Frames por segundo

def main():
    pygame.init()
    pygame.mixer.init() # Inicializa o mixer para áudio

    # Obtém a resolução do monitor
    info = pygame.display.Info()
    SCREEN_WIDTH = info.current_w
    SCREEN_HEIGHT = info.current_h

    # Configura tela cheia
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Guerra Intergalatica") # Título da janela do jogo

    game_manager = GameManager()

    # Adiciona os estados ao gerenciador
    game_manager.add_state('menu', MenuState(game_manager, SCREEN_WIDTH, SCREEN_HEIGHT))
    game_manager.add_state('cutscene', CutsceneState(game_manager, SCREEN_WIDTH, SCREEN_HEIGHT))
    game_manager.add_state('gameplay', GameplayState(game_manager, SCREEN_WIDTH, SCREEN_HEIGHT))
    game_manager.add_state('settings', SettingsState(game_manager, SCREEN_WIDTH, SCREEN_HEIGHT))
    game_manager.add_state('boss_fight', GameplayState(game_manager, SCREEN_WIDTH, SCREEN_HEIGHT, is_boss_fight=True)) # Estado para a luta contra o chefe
    # Define o estado inicial do jogo
    game_manager.set_state('menu')

    clock = pygame.time.Clock()
    running = True

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
