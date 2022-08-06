import pygame
from pygame.constants import K_SPACE, KEYDOWN, KEYUP, NOEVENT 
from support import import_csv_layout, import_cut_graphics
from settings import tile_size, screen_height, screen_width, check_kick_an
from tiles import Tile, StaticTile, Crate, Coin, Palm
from enemy import Enemy
from decoration import Sky, Water, Clouds
from player import Player
from particles import ParticleEffect
from game_data import levels

class Level:
	def __init__(self,current_level,surface,create_overworld,change_coins,change_health):
		# general setup
		self.display_surface = surface
		self.world_shift = 0
		self.current_x = None

		# audio 
		self.coin_sound = pygame.mixer.Sound('../audio/effects/coin.wav')
		self.stomp_sound = pygame.mixer.Sound('../audio/effects/stomp.wav')

		# overworld connection 
		self.create_overworld = create_overworld
		self.current_level = current_level
		level_data = levels[self.current_level]
		self.new_max_level = level_data['unlock']

		# goal
		self.goal_sprite = pygame.sprite.Group()

		# player 
		player_layout = import_csv_layout(level_data['player'])
		self.player = pygame.sprite.GroupSingle()
		self.player_setup(player_layout,change_health)
		self.player_origin_x = self.player.sprite.rect.x  #########################
		self.player_origin_y = self.player.sprite.rect.y  #########################


		# user interface 
		self.change_coins = change_coins

		# dust 
		self.dust_sprite = pygame.sprite.GroupSingle()
		self.player_on_ground = False

		# explosion particles 
		self.explosion_sprites = pygame.sprite.Group()

		# terrain setup
		terrain_layout = import_csv_layout(level_data['terrain'])
		self.terrain_sprites = self.create_tile_group(terrain_layout,'terrain')
		self.terrain_origin = self.terrain_sprites.sprites()[0].rect.x   #############################
		# troll        ########################
		terrain_troll_sprites = import_csv_layout(level_data['terrain_troll'])
		self.terrain_troll_sprites = self.create_tile_group(terrain_troll_sprites,'terrain_troll')
		self.terrain_hien_sprites = pygame.sprite.Group()
		#an            ########################
		self.an = True
		an_layout = import_csv_layout(level_data['an'])
		self.an_sprites = self.create_tile_group(an_layout,'an')

		# grass setup 
		grass_layout = import_csv_layout(level_data['grass'])
		self.grass_sprites = self.create_tile_group(grass_layout,'grass')

		# crates 
		crate_layout = import_csv_layout(level_data['crates'])
		self.crate_sprites = self.create_tile_group(crate_layout,'crates')

		# coins 
		coin_layout = import_csv_layout(level_data['coins'])
		self.coin_sprites = self.create_tile_group(coin_layout,'coins')

		# foreground palms 
		fg_palm_layout = import_csv_layout(level_data['fg palms'])
		self.fg_palm_sprites = self.create_tile_group(fg_palm_layout,'fg palms')

		# background palms 
		bg_palm_layout = import_csv_layout(level_data['bg palms'])
		self.bg_palm_sprites = self.create_tile_group(bg_palm_layout,'bg palms')

		# enemy 
		enemy_layout = import_csv_layout(level_data['enemies'])
		self.enemy_sprites = self.create_tile_group(enemy_layout,'enemies')
		self.length_enemy = len(self.enemy_sprites.sprites())    #$$$$$$$$$$

		# constraint 
		constraint_layout = import_csv_layout(level_data['constraints'])
		self.constraint_sprites = self.create_tile_group(constraint_layout,'constraint')

		# decoration 
		self.sky = Sky(8)
		level_width = len(terrain_layout[0]) * tile_size
		self.water = Water(screen_height - 20,level_width)
		self.clouds = Clouds(400,level_width,30)

		###############################
		self.collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palm_sprites.sprites() + self.terrain_troll_sprites.sprites()
		#$$$$$$$$$$
		self.time = False
		self.frame_time = 0

		self.wait_sprites = pygame.sprite.Group()

	def create_tile_group(self,layout,type):
		sprite_group = pygame.sprite.Group()

		for row_index, row in enumerate(layout):
			for col_index,val in enumerate(row):
				if val != '-1':
					x = col_index * tile_size
					y = row_index * tile_size

					if type == 'terrain':
						terrain_tile_list = import_cut_graphics('../graphics/terrain/terrain_tiles.png')
						tile_surface = terrain_tile_list[int(val)]
						sprite = StaticTile(tile_size,x,y,tile_surface)

					if type == 'terrain_troll':  #############################
						terrain_tile_list = import_cut_graphics('../graphics/terrain/terrain_tiles.png')
						tile_surface = terrain_tile_list[int(val)]
						sprite = StaticTile(tile_size,x,y,tile_surface)

					if type == 'an': ############################
						terrain_tile_list = import_cut_graphics('../graphics/terrain/terrain_tiles.png')
						tile_surface = terrain_tile_list[int(val)]
						sprite = StaticTile(tile_size,x,y,tile_surface)
						
					if type == 'grass':
						grass_tile_list = import_cut_graphics('../graphics/decoration/grass/grass.png')
						tile_surface = grass_tile_list[int(val)]
						sprite = StaticTile(tile_size,x,y,tile_surface)
					
					if type == 'crates':
						sprite = Crate(tile_size,x,y)

					if type == 'coins':
						if val == '0': sprite = Coin(tile_size,x,y,'../graphics/coins/gold',5)
						if val == '1': sprite = Coin(tile_size,x,y,'../graphics/coins/silver',1)

					if type == 'fg palms':
						if val == '0': sprite = Palm(tile_size,x,y,'../graphics/terrain/palm_small',38)
						if val == '1': sprite = Palm(tile_size,x,y,'../graphics/terrain/palm_large',64)

					if type == 'bg palms':
						sprite = Palm(tile_size,x,y,'../graphics/terrain/palm_bg',64)

					if type == 'enemies':         ######### truyền tham số
						sprite = Enemy(tile_size,x,y, self.current_level)

					if type == 'constraint':
						sprite = Tile(tile_size,x,y)

					sprite_group.add(sprite)
		
		return sprite_group

	def player_setup(self,layout,change_health):
		for row_index, row in enumerate(layout):
			for col_index,val in enumerate(row):
				x = col_index * tile_size
				y = row_index * tile_size
				if val == '0':
					sprite = Player((x,y),self.display_surface,self.create_jump_particles,change_health)
					self.player.add(sprite)
				if val == '1':
					hat_surface = pygame.image.load('../graphics/character/hat.png').convert_alpha()
					sprite = StaticTile(tile_size,x,y,hat_surface)
					self.goal_sprite.add(sprite)

	def enemy_collision_reverse(self):
		for enemy in self.enemy_sprites.sprites():
			if pygame.sprite.spritecollide(enemy,self.constraint_sprites,False):
				enemy.reverse()

	def create_jump_particles(self,pos):
		if self.player.sprite.facing_right:
			pos -= pygame.math.Vector2(10,5)
		else:
			pos += pygame.math.Vector2(10,-5)
		jump_particle_sprite = ParticleEffect(pos,'jump')
		self.dust_sprite.add(jump_particle_sprite)

	def horizontal_movement_collision(self, collidable_sprites): ############### thêm tham số
		player = self.player.sprite
		player.collision_rect.x += player.direction.x * player.speed
		for sprite in collidable_sprites:
			if sprite.rect.colliderect(player.collision_rect):
				if (sprite in self.terrain_troll_sprites) and (sprite not in self.terrain_hien_sprites): ######## chạm vào cạnh terrain_troll
					self.terrain_hien_sprites.add(sprite)
				if player.direction.x < 0:
					player.collision_rect.left = sprite.rect.right
					player.on_left = True
					self.current_x = player.rect.left
				elif player.direction.x > 0:
					player.collision_rect.right = sprite.rect.left
					player.on_right = True
					self.current_x = player.rect.right

		if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):      # phần này là code của phần 1 trên youtobe họ chưa thêm vào, không thêm cũng k sao
			player.on_left = False
		if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
			player.on_right = False

	def vertical_movement_collision(self, collidable_sprites):   #################### thêm tham số
		player = self.player.sprite
		player.apply_gravity()
		for sprite in collidable_sprites:
			if sprite.rect.colliderect(player.collision_rect):
				if (sprite in self.terrain_troll_sprites) and (sprite not in self.terrain_hien_sprites): ######## nhảy lên terrain_troll
					self.terrain_hien_sprites.add(sprite)
				if player.direction.y > 0:
					player.direction.y = 0
					player.collision_rect.bottom = sprite.rect.top
					player.on_ground = True

				elif player.direction.y < 0:
					player.direction.y = 0
					player.collision_rect.top = sprite.rect.bottom
					player.on_ceiling = True
		if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
			player.on_ground = False

	def scroll_x(self):
		player = self.player.sprite
		player_x = player.rect.centerx
		direction_x = player.direction.x

		if player_x < screen_width / 3 and direction_x < 0:  ########## sửa thành 3 cho dễ chơi
			self.world_shift = 8
			player.speed = 0
		elif player_x > screen_width - (screen_width / 3) and direction_x > 0:  ##########
			self.world_shift = -8
			player.speed = 0
		else:
			self.world_shift = 0
			player.speed = 8

	def get_player_on_ground(self):
		if self.player.sprite.on_ground:
			self.player_on_ground = True
		else:
			self.player_on_ground = False

	def create_landing_dust(self):
		if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
			if self.player.sprite.facing_right:
				offset = pygame.math.Vector2(10,15)
			else:
				offset = pygame.math.Vector2(-10,15)
			fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset,'land')
			self.dust_sprite.add(fall_dust_particle)

	def check_death(self):      ############ check rơi xuống nước
		if self.player.sprite.rect.y > screen_height:
			self.terrain_hien_sprites.empty()
			if self.terrain_sprites.sprites()[0].rect.x < self.terrain_origin:
				self.world_shift = self.terrain_origin - self.terrain_sprites.sprites()[0].rect.x
			elif self.terrain_sprites.sprites()[0].rect.x > self.terrain_origin:
				self.world_shift = self.terrain_origin - self.terrain_sprites.sprites()[0].rect.x
			else:
				self.world_shift = 0
				self.player.sprite.collision_rect.x = self.player_origin_x
				self.player.sprite.collision_rect.y = self.player_origin_y
				self.player.sprite.drowning()
			
	def check_win(self):
		if len(self.goal_sprite.sprites()) == 0:
			self.create_overworld(self.current_level,self.new_max_level)

	def mini_map(self):               #$$$$$$$$$$
		if self.player.sprite.facing_right:
			pos = self.player.sprite.rect.topright + pygame.math.Vector2(0, 0)
		else:
			pos = self.player.sprite.rect.topleft + pygame.math.Vector2(20, 0)
		explosion_sprite = ParticleEffect(pos,'mini_map')
		self.explosion_sprites.add(explosion_sprite)
	
	def wait(self):  #$$$$$$$$$$
		if self.player.sprite.facing_right:
			pos = self.player.sprite.rect.topleft + pygame.math.Vector2(5, 0)
		else:
			pos = self.player.sprite.rect.topright + pygame.math.Vector2(10, 0)
		wait = ParticleEffect(pos,'wait')
		self.wait_sprites.add(wait)

	def check_an(self): #$$$$$$$$$$
		if self.length_enemy - len(self.enemy_sprites.sprites()) == check_kick_an[self.current_level] and self.an: #$$$$$$$$$$
			self.collidable_sprites += self.an_sprites.sprites()
			self.an = False
			self.mini_map()       #$$$$$$$$$$
			
	def check_troll(self):    #####################
		trolls = pygame.sprite.spritecollide(self.player.sprite,self.terrain_troll_sprites,False)
		if trolls:
			for sprite in trolls:
				if sprite not in self.terrain_hien_sprites:
					self.terrain_hien_sprites.add(sprite)
			
	def check_goal_collisions(self):
			collided_goal = pygame.sprite.spritecollide(self.player.sprite,self.goal_sprite,True)
			if collided_goal:
				self.coin_sound.play()

	def check_coin_collisions(self):  #################
		collided_coins = pygame.sprite.spritecollide(self.player.sprite,self.coin_sprites,True)
		if collided_coins:
			self.coin_sound.play()
			for coin in collided_coins:
				self.change_coins(coin.value)
				explosion_sprite = ParticleEffect(coin.rect.center,'coin_disappear')
				self.explosion_sprites.add(explosion_sprite)

	def check_enemy_collisions(self):
		enemy_collisions = pygame.sprite.spritecollide(self.player.sprite,self.enemy_sprites,False)

		if enemy_collisions:
			for enemy in enemy_collisions:
				enemy_center = enemy.rect.centery
				enemy_top = enemy.rect.top
				player_bottom = self.player.sprite.rect.bottom
				if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
					self.stomp_sound.play()
					self.player.sprite.direction.y = -15
					explosion_sprite = ParticleEffect(enemy.rect.center,'explosion')
					self.explosion_sprites.add(explosion_sprite)
					enemy.kill()
				else:
					self.player.sprite.get_damage()

	#$$$$$$$$$$
	def check_time(self, time):
		self.frame_time +=1
		if self.frame_time == time * 60:
			self.frame_time = 0
			return True
		else:
			return False

	def check_key(self):  #$$$$$$$$$$$
		keys = pygame.key.get_pressed()
		if keys[pygame.K_f] and len(self.wait_sprites.sprites()) == 0:
			self.wait()
		
		if keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_LEFT] or keys[pygame.K_SPACE] :
			self.frame_time = 0
			self.wait_sprites.empty()
		elif self.check_time(4):
			self.wait()

	def run(self):
		# sky 
		self.sky.draw(self.display_surface)
		self.clouds.draw(self.display_surface,self.world_shift)
		
		# background palms
		self.bg_palm_sprites.update(self.world_shift)
		self.bg_palm_sprites.draw(self.display_surface) 

		# dust particles 
		self.dust_sprite.update(self.world_shift)
		self.dust_sprite.draw(self.display_surface)
		
		# map an         #################
		self.an_sprites.update(self.world_shift)  
		if self.an == False:
			self.an_sprites.draw(self.display_surface)

		# terrain 
		self.terrain_sprites.update(self.world_shift)
		self.terrain_sprites.draw(self.display_surface)

		# troll và hiện   ###############
		self.terrain_troll_sprites.update(self.world_shift)
		self.terrain_hien_sprites.draw(self.display_surface)
		# enemy 
		self.enemy_sprites.update(self.world_shift)
		self.constraint_sprites.update(self.world_shift)
		self.enemy_collision_reverse()
		self.enemy_sprites.draw(self.display_surface)
		# self.explosion_sprites.update(self.world_shift)
		# self.explosion_sprites.draw(self.display_surface)

		# crate 
		self.crate_sprites.update(self.world_shift)
		self.crate_sprites.draw(self.display_surface)

		# grass
		self.grass_sprites.update(self.world_shift)
		self.grass_sprites.draw(self.display_surface)

		# coins 
		self.coin_sprites.update(self.world_shift)
		self.coin_sprites.draw(self.display_surface)

		# foreground palms
		self.fg_palm_sprites.update(self.world_shift)
		self.fg_palm_sprites.draw(self.display_surface)

		# player sprites    
		self.player.update()
		self.horizontal_movement_collision(self.collidable_sprites) ####
		
		self.get_player_on_ground()
		self.vertical_movement_collision(self.collidable_sprites)  ####
		self.create_landing_dust()

		self.scroll_x()
		self.check_death()     ###########
		self.check_win()
		self.check_an()       #########
		self.player.draw(self.display_surface)
		self.goal_sprite.update(self.world_shift)
		self.goal_sprite.draw(self.display_surface)

		
		self.check_goal_collisions()
		self.check_coin_collisions()         #############
		self.check_enemy_collisions()

		# hiện 1 lần  #$$$$$$$$$$
		self.explosion_sprites.update(self.world_shift)
		self.explosion_sprites.draw(self.display_surface)
		self.wait_sprites.update(self.world_shift)
		self.wait_sprites.draw(self.display_surface)
		self.check_key()
		# water
		
		self.water.draw(self.display_surface,self.world_shift)