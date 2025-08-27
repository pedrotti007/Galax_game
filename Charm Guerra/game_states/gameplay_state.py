# game_states/gameplay_state.py

import pygame

class GameplayState:
    def __init__(self, game_manager, screen_width, screen_height):
        self.game_manager = game_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_pos = [screen_width // 2, screen_height // 2]
        self.player_speed = 5
        # --- PONTO DE MODIFICAÇÃO: INICIALIZAÇÃO DO GAMEPLAY ---
        # Carregue assets específicos do gameplay, inicialize personagens, etc.
        self.player_image = None
        try:
            self.player_image = pygame.image.load('assets/images/player.png').convert_alpha()
            self.player_image = pygame.transform.scale(self.player_image, (50, 50))
        except Exception:
            # Se não houver imagem, manter None e desenhar um retângulo como fallback
            print("Aviso: 'assets/images/player.png' não encontrado. Usando fallback de retângulo para o jogador.")
        
    def enter(self):
        print("Entrando no estado de Gameplay!")
        # Inicie a música do jogo aqui, se houver
        # pygame.mixer.music.load('assets/audio/game_music.mp3')
        # pygame.mixer.music.play(-1) # -1 para loop infinito

    def handle_event(self, event):
        # --- PONTO DE MODIFICAÇÃO: EVENTOS DO GAMEPLAY ---
        # Lógica de input do jogador, colisões, etc.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # Exemplo: Voltar para o menu com ESC
                self.game_manager.set_state('menu')

    def update(self):
        # --- PONTO DE MODIFICAÇÃO: LÓGICA DE ATUALIZAÇÃO DO GAMEPLAY ---
        # Mova personagens, atualize estados de jogo, verifique colisões, etc.
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: 
            self.player_pos[0] -= self.player_speed
        if keys[pygame.K_RIGHT]:
            self.player_pos[0] += self.player_speed
        if keys[pygame.K_UP]:
            self.player_pos[1] -= self.player_speed
        if keys[pygame.K_DOWN]:
            self.player_pos[1] += self.player_speed

        # Limita o jogador à tela
        self.player_pos[0] = max(0, min(self.screen_width - 50, self.player_pos[0]))
        self.player_pos[1] = max(0, min(self.screen_height - 50, self.player_pos[1]))


    def draw(self, screen):
        # --- PONTO DE MODIFICAÇÃO: DESENHO DO GAMEPLAY ---
        # Desenhe o cenário, personagens, UI do jogo, etc.
        screen.fill((50, 50, 150)) # Fundo azul escuro para o gameplay

        # Exemplo: Desenhar um quadrado representando o jogador
        if self.player_image:
            screen.blit(self.player_image, (self.player_pos[0], self.player_pos[1]))
        else:
            pygame.draw.rect(screen, (255, 0, 0), (self.player_pos[0], self.player_pos[1], 50, 50))

        # Texto de exemplo
        font = pygame.font.SysFont(None, 30)
        text_surface = font.render("Gameplay! Pressione ESC para voltar ao menu.", True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
