# game_states/cutscene_state.py

import os
import pygame


class CutsceneState:
    """Estado de cutscene.

    Estratégia:
    - se existir 'assets/videos/cutscene.mp4' e moviepy estiver instalado, reproduz o vídeo dentro do jogo;
    - se existir o arquivo mas moviepy não estiver instalado, abre o arquivo com o player do sistema (Windows: os.startfile) e espera input para continuar;
    - se não houver vídeo, tenta carregar frames em 'assets/images/cutscene_frame_1.png'...;
    - se nada for encontrado, usa um placeholder estático.
    """

    def __init__(self, game_manager, screen_width, screen_height):
        self.game_manager = game_manager
        self.screen_width = screen_width
        self.screen_height = screen_height

        # modos: 'video', 'external', 'frames', 'placeholder'
        self.mode = 'placeholder'

        # frames (quando usar imagens estáticas)
        self.frames = []
        self.current_frame_index = 0
        self.frame_duration = 1000
        self.last_frame_time = 0

        # video reader / playback
        self.video_clip = None
        self.video_start_ticks = None
        self.video_duration = None
        self.video_reader = None
        self.video_frame_iter = None
        self.current_video_surface = None
        self.playing_video = False

        # paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        video_path = os.path.join(project_root, 'assets', 'videos', 'cutscene.mp4')

        # 1) tenta vídeo embutido com imageio (usa imageio-ffmpeg para decodificar)
        if os.path.exists(video_path):
            try:
                import imageio
                reader = imageio.get_reader(video_path, 'ffmpeg')
                meta = reader.get_meta_data()
                self.video_reader = reader
                self.video_fps = meta.get('fps', 24)
                # tenta obter nframes; se não disponível, usar duration
                try:
                    self.video_nframes = reader.count_frames()
                except Exception:
                    self.video_nframes = int(meta.get('duration', 0) * self.video_fps)
                self.video_duration = meta.get('duration', None)
                # frame duration in ms
                try:
                    self.video_frame_duration = int(1000.0 / float(self.video_fps))
                except Exception:
                    self.video_frame_duration = 33
                self.mode = 'video'
                print(f"Cutscene: usando imageio para reproduzir {video_path} (fps={self.video_fps}, nframes={self.video_nframes})")
            except Exception as e:
                print(f"Aviso: não foi possível usar imageio para reproduzir '{video_path}': {e}. Tentando frames/fallback.")

        # 2) se não for 'video' nem 'external', tenta frames em assets/images
        if self.mode not in ('video', 'external'):
            try:
                idx = 1
                loaded = False
                while True:
                    path = os.path.join(project_root, 'assets', 'images', f'cutscene_frame_{idx}.png')
                    if not os.path.exists(path):
                        break
                    frame = pygame.image.load(path).convert_alpha()
                    frame = pygame.transform.scale(frame, (self.screen_width, self.screen_height))
                    self.frames.append(frame)
                    loaded = True
                    idx += 1
                if loaded:
                    self.mode = 'frames'
                else:
                    self.mode = 'placeholder'
            except Exception as e:
                print(f"Erro ao carregar frames: {e}")
                self.mode = 'placeholder'

        # se ainda placeholder, crie um frame simples
        if self.mode == 'placeholder' and not self.frames:
            self.frames = [self._create_placeholder_frame("Cutscene vazia. Pressione qualquer tecla para continuar.", (255, 255, 255))]

    def _create_placeholder_frame(self, text, color):
        surface = pygame.Surface((self.screen_width, self.screen_height))
        surface.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 40)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        surface.blit(text_surface, text_rect)
        return surface

    def enter(self):
        # Para a música do menu ao entrar na cutscene
        pygame.mixer.music.stop()

        self.current_frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        # Se o modo for 'video' (imageio reader), inicia o temporizador
        if self.mode == 'video' and hasattr(self, 'video_reader') and self.video_reader is not None:
            self.video_start_ticks = pygame.time.get_ticks()
            # iterator over frames to avoid seeking and ffmpeg re-spawn issues
            try:
                self.video_frame_iter = self.video_reader.iter_data()
            except Exception:
                self.video_frame_iter = None
            self.current_video_surface = None
            self.playing_video = True

    def handle_event(self, event):
        # Permite pular a cutscene com qualquer tecla ou clique
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            # se um clip interno estiver rodando, libera recursos
            try:
                if self.mode == 'video' and getattr(self, 'video_reader', None):
                    try:
                        self.video_reader.close()
                    except Exception:
                        pass
                    self.video_frame_iter = None
                    self.video_reader = None
                    self.current_video_surface = None
                    self.playing_video = False
            finally:
                # evita transições duplicadas
                if self.game_manager.current_state is not None:
                    self.game_manager.set_state('gameplay')

    def update(self):
        if self.mode == 'frames':
            now = pygame.time.get_ticks()
            if now - self.last_frame_time > self.frame_duration:
                self.current_frame_index += 1
                self.last_frame_time = now
                if self.current_frame_index >= len(self.frames):
                    self.game_manager.set_state('gameplay')

        elif self.mode == 'video' and getattr(self, 'video_reader', None) is not None:
            now = pygame.time.get_ticks()
            # advance frames based on frame duration
            if hasattr(self, 'video_frame_iter') and self.video_frame_iter is not None:
                if now - self.last_frame_time >= getattr(self, 'video_frame_duration', 33):
                    try:
                        frame = next(self.video_frame_iter)
                        import numpy as np
                        arr = np.asarray(frame)
                        if arr.dtype != np.uint8:
                            arr = arr.astype(np.uint8)
                        surf = pygame.surfarray.make_surface(arr.swapaxes(0, 1))
                        if surf.get_size() != (self.screen_width, self.screen_height):
                            surf = pygame.transform.scale(surf, (self.screen_width, self.screen_height))
                        self.current_video_surface = surf
                        self.last_frame_time = now
                    except StopIteration:
                        try:
                            if getattr(self, 'video_reader', None):
                                self.video_reader.close()
                        except Exception:
                            pass
                        self.video_frame_iter = None
                        self.video_reader = None
                        self.playing_video = False
                        if self.game_manager.current_state is not None:
                            self.game_manager.set_state('gameplay')
                    except Exception as e:
                        print(f"Aviso: erro ao iterar frames do vídeo: {e}")
                        try:
                            if getattr(self, 'video_reader', None):
                                self.video_reader.close()
                        except Exception:
                            pass
                        self.video_frame_iter = None
                        self.video_reader = None
                        self.playing_video = False
                        if self.game_manager.current_state is not None:
                            self.game_manager.set_state('gameplay')

    def draw(self, screen):
        if self.mode == 'frames':
            if self.frames and self.current_frame_index < len(self.frames):
                screen.blit(self.frames[self.current_frame_index], (0, 0))
            else:
                screen.fill((0, 0, 0))

        elif self.mode == 'video' and hasattr(self, 'video_reader'):
            try:
                if getattr(self, 'current_video_surface', None) is not None:
                    screen.blit(self.current_video_surface, (0, 0))
                else:
                    screen.fill((0, 0, 0))
            except Exception as e:
                print(f"Aviso: erro ao desenhar frame de vídeo: {e}")
                screen.fill((0, 0, 0))

        elif self.mode == 'external':
            # mostra um placeholder enquanto o player externo roda; usuário deve fechar/pressionar tecla para continuar
            screen.fill((0, 0, 0))
            font = pygame.font.SysFont(None, 36)
            text = "Cutscene aberta no player externo. Pressione qualquer tecla para prosseguir."
            surf = font.render(text, True, (255, 255, 255))
            screen.blit(surf, surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2)))

        else:
            # placeholder
            screen.blit(self.frames[0], (0, 0))
