from cv2 import add
import pygame
import time
import math
import random


class laser():
    def __init__(self, x, y, damage, speed, color, add_x, add_y, thickness, is_tracker = False):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.color = color
        self.add_x = add_x
        self.side_lenght = add_x
        self.add_y = add_y
        self.thickness = thickness
        self.degree = 180
        self.is_tracker = is_tracker
        self.is_tracking = None
    
    def draw(self, screen):
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.x + self.add_x, self.y + self.add_y), self.thickness)
    
    def move_to_target(self, x, y):
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
        #change add_x and add_y to get the direction right
        self.add_x = math.cos(math.radians(angle_to_test)) * mul_x * self.side_lenght
        self.add_y = math.sin(math.radians(angle_to_test)) * mul_y * self.side_lenght


        #update the position
        self.x += math.cos(math.radians(self.degree)) * self.speed * -1
        self.y += math.sin(math.radians(self.degree)) * self.speed * -1

class arc:
    def __init__(self, x, y, damage, speed, color, width, height, start_angle, end_angle, thickness, is_tracker = False):
        """
        if start_angle < end_angle, the arc is drawn in a counterclockwise direction from the start_angle to the stop_angle
        """
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.color = color
        self.width = width
        self.height = height
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.thickness = thickness
        self.degree = 180
        self.is_tracker = is_tracker
        self.is_tracking = None


    def draw(self, screen):
        pygame.draw.arc(screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height), self.start_angle, self.end_angle, self.thickness)


class lightning_attack:
    def __init__(self, x, y, damage, color, thickness, num_enemy, max_num_enemy, range, nearest_ememies):
        """
        the num_enemy takes in how many enemy before the lightning stops, and the range how far apart the enemy can be before it hits them
        """
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.thickness = thickness
        self.max_num_enemy = max_num_enemy
        self.num_enemy = num_enemy
        self.range = range
        self.nearest_enemy = nearest_ememies
        self.timer = 0
        self.enemies_already_visited = [nearest_ememies]
        self.current_enemy = None

    def draw(self, screen):
        pass

    def attack_enemy(self, screen, x, y):
        """
        pass the enemy coordinate to attack 
        """
        dis_x = self.x - x
        dis_y = self.y - y
        if(self.x > x):
            list_points = [[x, y]]
        else:
            list_points = [[self.x, self.y]]
        #b = (dis_y/dis_x * self.x - self.y) * -1
        if(dis_x != 0):
            slope = dis_y/dis_x
        else:
            slope = 9999999999999
        for times in range(random.randrange(5) + 2):
            x_to_test = random.randrange(0, abs(dis_x)) #get a random x
            if(dis_x > 0):
                x_to_test *= -1
            y_to_test = slope * x_to_test
            y_to_test += random.randrange(31) - 15
            x_to_test += random.randrange(31) - 15
            #orders it to make it easier later on
            index = 0
            placed_in_array = False
            for points in list_points:
                if(points[0] > self.x + x_to_test and not placed_in_array):
                    list_points.insert(index, [self.x + x_to_test, self.y + y_to_test])
                    placed_in_array = True
                index += 1
            if(not placed_in_array):
                list_points.append([self.x + x_to_test, self.y + y_to_test])

        if(self.x > x):
            list_points.append([self.x, self.y])
        else:
            list_points.append([x, y])
        #drawing it
        index = 0
        for point in list_points:
            if(index <= len(list_points) - 2):
                pygame.draw.line(screen, self.color, (point[0], point[1]), (list_points[index + 1][0], list_points[index + 1][1]), self.thickness)
            index += 1

class earthquake:
    def __init__(self, x, y, damage, color, radius):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.radius = radius
        self.timer = 0
        
        self.cycle = 0
        num_add = 40
        random_addition = random.randrange(120)
        random_num_of_list = random.randrange(3) + 3
        self.list_of_points = []
        for num_of_points in range(random_num_of_list):
            self.list_of_points.append([[0,0]])
        for index in range(random_num_of_list):
            for num in range(9):
                r = self.radius/(9 - num)
                theta = num_add + random.randrange(40) + random_addition
                x = r * math.cos(math.radians(theta))
                y = r * math.sin(math.radians(theta))
                self.list_of_points[index].append([x,y])
            num_add += 360/random_num_of_list
        


    def draw(self, screen):
        image = pygame.Surface([self.radius * 2, self.radius * 2])
        image.set_colorkey((0,0,0))  # Black colors will not be blit.
        image.set_alpha(100)
        pygame.draw.circle(image, self.color, (self.radius, self.radius), self.radius)
        for list_of_points in self.list_of_points:
            for points in range((self.cycle * 3)):
                pygame.draw.line(image, (0, 0, 0), (list_of_points[points][0] + self.radius, list_of_points[points][1] + self.radius), (list_of_points[points + 1][0] + self.radius, list_of_points[points + 1][1] + self.radius), self.cycle)
                

        screen.blit(image, (self.x - self.radius, self.y - self.radius))
        pygame.draw.circle(screen, (142, 102, 90), (self.x, self.y), self.radius, 4)
    #stole this code from stack overflow
    def add_point_to_next_cyle(self):
        
        

        #wrong thing, does not do what I thought it would, very ugly
        

        self.cycle += 1