from settings import * 
from level import Level
from pytmx.util_pygame import load_pygame
from support import * 
from data import Data
from debug import debug
from ui import UI
from overworld import Overworld

class Game:
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption('Tidebound')
		
		self.clock = pygame.time.Clock()
		self.import_assets()

		self.ui = UI(self.font, self.ui_frames)
		self.data = Data(self.ui)
		self.game_over = False
		self.menu_title_font = pygame.font.Font(None, 68)
		self.menu_font = pygame.font.Font(None, 34)
		self.tmx_maps = {
			level: load_pygame(asset_path('data', 'levels', f'{level}.tmx'))
			for level in range(6)
		}
		self.tmx_overworld = load_pygame(asset_path('data', 'overworld', 'overworld.tmx'))
		self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.audio_files, self.data, self.switch_stage)
		self.bg_music.play(-1)

	def switch_stage(self, target, unlock = 0):
		if target == 'level':
			self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.audio_files, self.data, self.switch_stage)
		elif target == 'respawn':
			self.data.health -= 1
			self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.audio_files, self.data, self.switch_stage)
			
		else: # overworld 
			if unlock > 0:
				self.data.unlocked_level = max(self.data.unlocked_level, unlock)
			else:
				self.data.health -= 1
			self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage)

	def import_assets(self):
		self.level_frames = {
			'flag': import_folder('..', 'graphics', 'level', 'flag'),
			'saw': import_folder('..', 'graphics', 'enemies', 'saw', 'animation'),
			'floor_spike': import_folder('..', 'graphics','enemies', 'floor_spikes'),
			'palms': import_sub_folders('..', 'graphics', 'level', 'palms'),
			'candle': import_folder('..', 'graphics','level', 'candle'),
			'window': import_folder('..', 'graphics','level', 'window'),
			'big_chain': import_folder('..', 'graphics','level', 'big_chains'),
			'small_chain': import_folder('..', 'graphics','level', 'small_chains'),
			'candle_light': import_folder('..', 'graphics','level', 'candle light'),
			'player': import_sub_folders('..', 'graphics','player'),
			'saw': import_folder('..', 'graphics', 'enemies', 'saw', 'animation'),
			'saw_chain': import_image('..',  'graphics', 'enemies', 'saw', 'saw_chain'),
			'helicopter': import_folder('..', 'graphics', 'level', 'helicopter'),
			'boat': import_folder('..',  'graphics', 'objects', 'boat'),
			'spike': import_image('..',  'graphics', 'enemies', 'spike_ball', 'Spiked Ball'),
			'spike_chain': import_image('..',  'graphics', 'enemies', 'spike_ball', 'spiked_chain'),
			'tooth': import_folder('..', 'graphics','enemies', 'tooth', 'run'),
			'shell': import_sub_folders('..', 'graphics','enemies', 'shell'),
			'pearl': import_image('..',  'graphics', 'enemies', 'bullets', 'pearl'),
			'items': import_sub_folders('..', 'graphics', 'items'),
			'particle': import_folder('..', 'graphics', 'effects', 'particle'),
			'water_top': import_folder('..', 'graphics', 'level', 'water', 'top'),
			'water_body': import_image('..', 'graphics', 'level', 'water', 'body'),
			'bg_tiles': import_folder_dict('..', 'graphics', 'level', 'bg', 'tiles'),
			'cloud_small': import_folder('..', 'graphics','level', 'clouds', 'small'),
			'cloud_large': import_image('..', 'graphics','level', 'clouds', 'large_cloud'),
		}
		self.font = pygame.font.Font(asset_path('graphics', 'ui', 'runescape_uf.ttf'), 40)
		self.ui_frames = {
			'heart': import_folder('..', 'graphics', 'ui', 'heart'), 
			'coin':import_image('..', 'graphics', 'ui', 'coin')
		}
		self.overworld_frames = {
			'palms': import_folder('..', 'graphics', 'overworld', 'palm'),
			'water': import_folder('..', 'graphics', 'overworld', 'water'),
			'path': import_folder_dict('..', 'graphics', 'overworld', 'path'),
			'icon': import_sub_folders('..', 'graphics', 'overworld', 'icon'),
		}

		self.audio_files = {
			'coin': pygame.mixer.Sound(asset_path('audio', 'coin.wav')),
			'attack': pygame.mixer.Sound(asset_path('audio', 'attack.wav')),
			'jump': pygame.mixer.Sound(asset_path('audio', 'jump.wav')),
			'damage': pygame.mixer.Sound(asset_path('audio', 'damage.wav')),
			'pearl': pygame.mixer.Sound(asset_path('audio', 'pearl.wav')),
		}
		self.bg_music = pygame.mixer.Sound(asset_path('audio', 'starlight_city.mp3'))
		self.bg_music.set_volume(0.5)

	def check_game_over(self):
		self.game_over = self.data.health <= 0

	def restart(self):
		level_to_retry = self.data.current_level
		unlocked_level = self.data.unlocked_level
		self.ui = UI(self.font, self.ui_frames)
		self.data = Data(self.ui)
		self.data.current_level = level_to_retry
		self.data.unlocked_level = unlocked_level
		self.current_stage = Level(
			self.tmx_maps[self.data.current_level],
			self.level_frames,
			self.audio_files,
			self.data,
			self.switch_stage)
		self.game_over = False

	def draw_game_over(self):
		overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
		overlay.fill((12, 16, 30, 205))
		self.display_surface.blit(overlay, (0, 0))

		panel = pygame.Rect(0, 0, 640, 300)
		panel.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
		pygame.draw.rect(self.display_surface, '#252b3d', panel, border_radius=16)
		pygame.draw.rect(self.display_surface, '#e8bd63', panel, width=3, border_radius=16)

		lines = (
			('GAME OVER', self.menu_title_font, '#f5d38b', panel.centery - 72),
			('Press ENTER or R to retry this level', self.menu_font, 'white', panel.centery + 4),
			('Press ESC to quit', self.menu_font, '#c8ccda', panel.centery + 52),
		)
		for text, font, color, y in lines:
			text_surface = font.render(text, True, color)
			text_rect = text_surface.get_rect(center=(panel.centerx, y))
			self.display_surface.blit(text_surface, text_rect)

	def run(self):
		while True:
			dt = self.clock.tick(60) / 1000
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if self.game_over and event.type == pygame.KEYDOWN:
					if event.key in (pygame.K_RETURN, pygame.K_r):
						self.restart()
					elif event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit()

			if self.game_over:
				self.draw_game_over()
			else:
				self.current_stage.run(dt)
				self.ui.update(dt)
				self.check_game_over()
				if self.game_over:
					self.draw_game_over()

			pygame.display.flip()

if __name__ == '__main__':
	game = Game()
	game.run()
