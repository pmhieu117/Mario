import pygame
from support import import_folder

class ParticleEffect(pygame.sprite.Sprite):
	def __init__(self,pos,type):
		super().__init__()
		self.frame_index = 0
		self.animation_speed = 0.5
		
		if type == 'jump':
			self.frames = import_folder('../graphics/character/dust_particles/jump')
		if type == 'land':
			self.frames = import_folder('../graphics/character/dust_particles/land')
		if type == 'explosion':
			self.frames = import_folder('../graphics/enemy/explosion')
		if type == 'coin_disappear':              ####################### coin biến mất
			self.frames = import_folder('../graphics/coins/disappear')
		if type == 'mini_map':          #$$$$$$$$$$
			self.animation_speed = 0.1
			self.frames = import_folder('../graphics/unfolding')
		if type == 'wait':          #$$$$$$$$$$
			self.animation_speed = 0.09
			self.frames = import_folder('../graphics/exclamation')
		self.image = self.frames[self.frame_index]
		if type == 'wait' or type == 'mini_map': #$$$$$$$$$$
			self.image = pygame.transform.scale2x(self.image)
		self.rect = self.image.get_rect(center = pos)

	def animate(self):
		self.frame_index += self.animation_speed
		if self.frame_index >= len(self.frames):
			self.kill()
		else:
			self.image = self.frames[int(self.frame_index)]

	def update(self,x_shift):
		self.animate()
		self.rect.x += x_shift
