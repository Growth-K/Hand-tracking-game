from cv2 import add
import pygame
import time
import math

class player():
    def __init__(self, x, y, img, width, height, health, mana, top_speed, damage):
        self.x = x
        self.y = y
        self.img = img
        self.width = width
        self.height = height
        self.health = health
        self.topHealth = health
        self.topMana = mana
        self.mana = mana
        self.mana_regen = 0
        self.health_regen = 0
        self.top_speed = top_speed
        self.damage = damage
        self.has_shield = False
        self.shield_timer = 0
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        if(self.has_shield):
            pygame.draw.circle(screen, (80,240,240), (self.x + self.width/2, self.y + self.width/2), self.width, 2)
            image = pygame.Surface([self.width * 2, self.width * 2])
            image.set_colorkey((0,0,0))  # Black colors will not be blit.
            image.set_alpha(100)
            pygame.draw.circle(image, (80,240,240), (self.width, self.width), self.width)
            screen.blit(image, (self.x - self.width/2, self.y - self.height/2))

class EnemyBasic():    
        
    
    def __init__(self, x, y, img, health, scale, speed, lvl, follow = False, damage = 0, attack_frequency = 30, shoots_laser = False, is_buffing = False):
        self.x = x
        self.y = y
        self.img = img
        self.health = health
        self.width = scale[0]
        self.height = scale[1]
        self.top_health = health
        self.speed = speed
        self.lvl = lvl
        self.degree = 0
        self.original_img = img
        self.follow = follow
        self.damage = damage
        self.timer = 0
        self.attack_frequency = attack_frequency
        self.shoots_laser = shoots_laser
        self.move_oposite_direction = False
        self.confused_timer = 0
        self.already_hit_by = []
        self.is_buffing = is_buffing
        self.buff_timer = 0
        self.currently_buffing = False
        self.has_buff = False
    #draw function
    def draw(self, screen):
        screen.blit(self.img, (self.x,self.y))
        #draw health bar
        #health bar must equal the width at the start and go from there
        pygame.draw.rect(screen, (255,0,0), pygame.Rect(self.x, self.y - 3, ((self.health/self.top_health) * self.width), 3))
        self.timer += 1
        if(self.is_buffing):
            self.buff_timer += 1
        if(self.buff_timer == 60):
            self.currently_buffing = True
            self.buff_timer = 0
        if(self.currently_buffing):
            pygame.draw.circle(screen, (201,40,40), (self.x + self.width/2, self.y + self.width/2), self.width * 3, 2)
            image = pygame.Surface([self.width * 6, self.width * 6])
            image.set_colorkey((0,0,0))  # Black colors will not be blit.
            image.set_alpha(100)
            pygame.draw.circle(image, (201,40,40), (self.width * 3, self.width * 3), self.width * 3)
            screen.blit(image, (self.x - int(self.width * 2.5), self.y - int(self.height * 2.5)))
            if(self.buff_timer == 15):
                self.currently_buffing = False
        #pygame.draw.line(screen, (0,255,0), (self.x, self.y + self.height/2), (self.x - 30, self.y + self.height/2), 5)


    #make the laser
    def make_lasers(self):
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        mul_x = -1
        mul_y = 1
        angle_to_test = 0 
        if(self.degree < 90): 
            angle_to_test = self.degree
            mul_y = -1
        elif(self.degree < 180): 
            angle_to_test = 180 - self.degree
            mul_y = -1
            mul_x = 1
        elif(self.degree < 270): 
            angle_to_test = self.degree - 180
            mul_x = 1
        else: 
            angle_to_test = 360 - self.degree

        dis_x = math.cos(math.radians(angle_to_test)) * (self.height/2) * mul_x
        dis_y = math.sin(math.radians(angle_to_test)) * (self.height/2) * mul_y
        side_lenght = self.width/6 * 2
        

        add_x = math.cos(math.radians(angle_to_test)) * side_lenght * mul_x
        add_y = math.sin(math.radians(angle_to_test)) * side_lenght * mul_y
        #print(center_x, center_y, dis_x, dis_y, add_x, add_y, center_x + dis_x, center_y + dis_y)
        return laser_enemy(center_x + dis_x, center_y + dis_y, add_x, add_y, side_lenght, 2, self.damage, self.degree, 7)

    def move_to_target(self, x, y): # for follower enemy
        dif_x = x - self.x
        dif_y = y - self.y
        #update the image's rotation
        #this next really long line is used to find the angle between two vector, and in this case the vector going to the player and the vector going strait to the left
        test_angle = math.degrees(math.acos((dif_x*-1)/math.sqrt(dif_x**2 + dif_y ** 2)))


        if(dif_y > 0):
            test_angle = 360 - test_angle
        degree = test_angle - self.degree
        self.degree += degree

        if(self.degree > 360):
            self.degree -= 360
        self.img = pygame.transform.rotate(self.original_img, self.degree * -1)
        
        #update the position

        if(self.degree < 90): angle_to_test = self.degree
        elif(self.degree < 180): angle_to_test = 180 - self.degree
        elif(self.degree < 270): angle_to_test = self.degree - 180
        else: angle_to_test = 360 - self.degree

        if(self.move_oposite_direction):
            self.x -= math.cos(math.radians(self.degree)) * self.speed * -1 * 4
            self.y -= math.sin(math.radians(self.degree)) * self.speed * -1 * 4
            self.confused_timer += 1
            
        else:
            self.x += math.cos(math.radians(self.degree)) * self.speed * -1
            self.y += math.sin(math.radians(self.degree)) * self.speed * -1
        
        # dif_overall = math.sqrt(dif_x ** 2 + dif_y **2)
        # if(dif_overall != 0):
        #     dif_x /= abs(dif_overall)
        #     dif_y /= abs(dif_overall)
        #     self.x += dif_x * self.speed
        #     self.y += dif_y * self.speed
    




class powerUp():
    def __init__(self, x, y, radius, nature):
        self.x = x
        self.y = y
        self.nature = nature
        self.radius = radius
        self.toShrink = False
        self.last_check = 0

    def draw(self, screen):
        if(self.nature == "Health"):
            pygame.draw.circle(screen, (0,255,0), (self.x, self.y), self.radius)
            pygame.draw.rect(screen, (255,255,255), pygame.Rect(self.x - self.radius + 1, self.y - 1, self.radius * 2 - 2, 2))
            pygame.draw.rect(screen, (255,255,255), pygame.Rect(self.x - 1, self.y - self.radius + 1, 2, self.radius * 2 - 2))
        elif(self.nature == "Speed"):
            image = pygame.transform.scale(pygame.image.load("image\speed_up.png"), (self.radius * 2, self.radius * 2))
            screen.blit(image, (self.x - self.radius, self.y - self.radius))
        elif(self.nature == "Mana"):
            image = pygame.transform.scale(pygame.image.load("image\mana.png"), (self.radius * 2, self.radius * 2))
            screen.blit(image, (self.x - self.radius, self.y - self.radius))
        elif(self.nature == "Health_boost"):
            image = pygame.transform.scale(pygame.image.load("image\Life_regen.png"), (self.radius * 2, self.radius * 2))
            screen.blit(image, (self.x - self.radius, self.y - self.radius))
        elif(self.nature == "Mana_boost"):
            image = pygame.transform.scale(pygame.image.load("image\crystal_mana_regen.png"), (self.radius * 2, self.radius * 2))
            screen.blit(image, (self.x - self.radius, self.y - self.radius))
        elif(self.nature == "Damage"):
            image = pygame.transform.scale(pygame.image.load("image\Damage_powerUp.png"), (self.radius * 2, self.radius * 2))
            screen.blit(image, (self.x - self.radius, self.y - self.radius))
        elif(self.nature == "Shield"):
            image = pygame.transform.scale(pygame.image.load("image\Shield.png"), (self.radius * 2, self.radius * 2))
            screen.blit(image, (self.x - self.radius, self.y - self.radius))
        

        #screen.blit(self.img, (self.x, self.y))


class laser_enemy():
    def __init__(self, x, y, add_x, add_y, lenght, width, damage, degree, speed):
        self.x = x
        self.y = y
        self.damage = damage
        self.lenght = lenght
        self.width = width
        self.degree = degree
        self.add_x = add_x
        self.add_y = add_y
        self.speed = speed

    def draw(self, screen):
        #pygame.draw.line(screen, (0,255,0), (100,100), (200,200))
        #print(self.x, self.y, self.add_x, self.add_y, self.width)
        pygame.draw.line(screen, (0,255,0), (self.x, self.y), (self.x + self.add_x, self.y + self.add_y), self.width)
    
    def move(self):
        self.x += math.cos(math.radians(self.degree)) * self.speed * -1
        self.y += math.sin(math.radians(self.degree)) * self.speed * -1

