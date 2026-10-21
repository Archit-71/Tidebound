import pygame, sys
from pathlib import Path
from pygame.math import Vector2 as vector

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def asset_path(*parts):
	"""Return a project asset path independent of the launch directory."""
	if parts and parts[0] == '..':
		parts = parts[1:]
	return str(PROJECT_ROOT.joinpath(*parts))

FRect = getattr(pygame, 'FRect', pygame.Rect)

def get_frect(surface, *args, **kwargs):
	"""Use floating rectangles when available, with a pygame.Rect fallback."""
	return getattr(surface, 'get_frect', surface.get_rect)(*args, **kwargs)

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
TILE_SIZE = 64
ANIMATION_SPEED = 6

# layers 
Z_LAYERS = {
	'bg': 0,
	'clouds': 1,
	'bg tiles': 2,
	'path': 3,
	'bg details': 4,
	'main': 5,
	'water': 6,
	'fg': 7
}
