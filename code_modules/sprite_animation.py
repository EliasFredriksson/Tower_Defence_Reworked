from typing import List, Tuple
import pygame

class Animation(pygame.sprite.Sprite):
    def __init__(self, 
                filepath: str, 
                fps: int,
                fpsFramelengths: List[int],
                spriteSize: Tuple[int,int], 
                numOfSpritesRow: int,
                numOfSpritesColumn: int,
                flip_hor: bool,
                flip_ver: bool,
                repeat_animation: bool,
                frame_repeat = 1):
        super(Animation, self).__init__()
        self.sheet = pygame.image.load(filepath).convert_alpha()
        self.original_images = self.__load_strip(
            pygame.Rect(0,0,spriteSize[0],spriteSize[1]),
            numOfSpritesRow, numOfSpritesColumn
        )

        self.index = 0
        self.image = self.original_images[self.index]

        ### POSITION INCLUDED IN RECT ###
        self.rect = self.image.get_rect()
        
        self.sprite_group = pygame.sprite.Group(self)

        self.repeat_animation = repeat_animation
        self.frame_repeat = frame_repeat
        self.animation_speed = 1000 / fps
        self.frame_length_list = fpsFramelengths
        self.last_update_frame_length = 0
        self.last_update = 0

        self.angle = 0
        self.scale = 1
        self.flip_hor = flip_hor
        self.flip_ver = flip_ver

    #Rotates / flips each surface in self.images to given angle
    def __rotate_scale_flip_to(self, angle, scale, flipHor, flipVer):
        self.sprite_group.empty()
        self.processed_imgs = []
        for img in self.original_images:
            rot_sprite = pygame.transform.flip(img, flipHor, flipVer)
            rot_flipped_sprite = pygame.transform.rotozoom(rot_sprite, angle, scale)
            self.processed_imgs.append(rot_flipped_sprite)

        self.rect = self.processed_imgs[0].get_rect(topleft = self.rect.topleft)
        self.sprite_group.add(self)
        #center = self.rect.center
           
    # Load a whole strip of images
    def __load_strip(self, rect, image_count_row, image_count_column):
        "Loads a spritesheet of images and returns them as a list"
        tups = [(rect.x + rect.width*x, rect.y + rect.height*y, rect.width, rect.height) 
            for y in range(image_count_row)
            for x in range(image_count_column)]
        return [self.sheet.subsurface(rect) for rect in tups]
    
    # Updates each frame, animates based on animationspeed
    def __update(self):
        if pygame.time.get_ticks() - self.last_update > self.animation_speed:
            self.last_update = pygame.time.get_ticks()
            self.last_update_frame_length += 1
            if len(self.frame_length_list) == 0 or self.last_update_frame_length >= self.frame_length_list[self.index]:
                self.last_update_frame_length = 0
                self.index += 1
                if self.index >= len(self.processed_imgs):
                    if self.repeat_animation:
                        self.index = 0
                    else:
                        self.index -= self.frame_repeat
                self.image = self.processed_imgs[self.index]
        
    # !!!!! IMPORTANT !!!!!
    # ONLY call the draw function. NOT update.
    def draw(self, canvas):
        self.__rotate_scale_flip_to(self.angle, 
                                    self.scale,
                                    self.flip_hor,
                                    self.flip_ver)
        self.__update()
        self.sprite_group.draw(canvas)

    def flip(self, 
            flipHorizontal: bool, 
            flipVertical: bool):
        self.flip_hor = flipHorizontal
        self.flip_ver = flipVertical

    def rotate_to(self, angel: int):
        self.angle = angel

    def get_image(self):
        return self.image

    def set_position(self, position):
        self.rect.center = position
   



