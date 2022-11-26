# import the opencv library
import cv2
import mediapipe as mp
import time

from pygame.draw import rect
import HandTrackingModule as htm
import pygame 
import ClassEntities as ce 
import random
import math
import numpy as np
import ClassAttackPlayer as attack

def check_colision(x1, y1, x2, y2, width1, height1, width2, height2):
    if(x1 + width1 > x2 and x1 < x2 + width2 and y1 + height1 > y2 and y1 < y2 + height2):
        return True
    return False

def check_colision_rect_circle(x1, y1, x2, y2, width, height, raduis):
    
    x2 = x2 + width/2
    y2 = y2 + height/2
    circleDistanceX = abs(x1 - x2)
    circleDistanceY = abs(y1 - y2)

    #if they are too far apart and cant possibly intersect
    if(circleDistanceX > (width/2 + raduis)): return False
    if(circleDistanceY > (height/2 + raduis)): return False

    #if the center of the circle lies in the rectangle, return true
    if(circleDistanceX <= (width/2)): return True
    if(circleDistanceY <= (height/2)): return True

    cornerDistance_sq = (circleDistanceX - width/2)**2 + (circleDistanceY - height/2)**2
    return (cornerDistance_sq <= (raduis**2))


def main():
    #start camera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    #innitiate pygame
    pygame.init()
    X = 1800
    Y = 900
    black = (0,0,0)
    white = (255,255,255)
    green = (0,255,0)
    red = (255,0,0)
    dead = False
    is_hurt = False
    to_pass_to_next_level = 20
    enemy_weight_to_test = 0
    invulnerable_time = time.time() + 1000
    

    screen = pygame.display.set_mode([X, Y])
    pygame.display.set_caption('Hand Tracking Game')
    running = True
    screen.fill(black)
    

    #make the list of star for background
    list_star = make_star_list(X,Y)
    #powerUp variable
    possible_powerUp = ["Speed", "Speed", "Mana", "Health", "Health_boost", "Health_boost", "Mana_boost", "Mana_boost", "Mana_boost", "Damage", "Shield", "Shield", "Shield"]
    #add more of certain powerUp to increase the likelyhood of falling on those
    list_powerup = []

    player = ce.player(X/4, Y/2, pygame.transform.scale(pygame.transform.rotate(pygame.image.load("image\SpaceShip.png"), 270), (40,40)), 40, 40, 100, 100, 15, 10)

    enemy_defeated = 0
    
    

    #creates the basic enemy
    scale_enemy_lv1 = [20,25]
    image_enemy_lv1 = pygame.transform.flip(pygame.image.load("image\enemy_robot.png"), True, False)
    image_enemy_lv1 = pygame.transform.scale(image_enemy_lv1, (scale_enemy_lv1[0],scale_enemy_lv1[1]))


    #prepare the more advance enemy
    scale_enemy_lv2 = [40,41]
    image_enemy_lv2 = pygame.transform.scale(pygame.image.load("image\EnemyBasic.png"), (scale_enemy_lv2[0], scale_enemy_lv2[1]))

    #prepare lvl 3 enemy
    scale_enemy_lv3 = [41,40]
    image_enemy_lv3 = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("image\enemy_ship_lv3.png"), (scale_enemy_lv3[0], scale_enemy_lv3[1])), 90)
    
    #prepare lvl 4 enemy
    scale_enemy_lv4 = [41,40]
    image_enemy_lv4 = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("image\Enemy_lv4.png"), (scale_enemy_lv4[0], scale_enemy_lv4[1])), 90)

    #prepare lvl 5 enemy
    scale_enemy_lv5 = [24,40]
    image_enemy_lv5 = pygame.transform.scale(pygame.image.load("image\Fast_boi.png"), (scale_enemy_lv5[0], scale_enemy_lv5[1]))

    #prepare lvl 6 enemy
    scale_enemy_lv6 = [62,60]
    image_enemy_lv6 = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("image\Buffing_ship.png"), (scale_enemy_lv6[0], scale_enemy_lv6[1])), 90)



    #array for the lasers
    laser_array = []
    enemy_laser_array = []

    life_color = (0,255,0)

    test_mode = False

    #make the enemy
    
    
    
    enemy_array = []
    if(test_mode):
        enemy_number = 25
        max_enemy_weight = 40
        current_enemy_weight = 40
        weighted_level_list = [1,2,2,3,3,3,4,4,4,4,5,5,5,5,5,6,6,6,6,6,6]
        level = 5
        for enemies in range(enemy_number):
            enemy_array.append(ce.EnemyBasic(X - random.randrange(200), random.randrange(Y - scale_enemy_lv1[1]), image_enemy_lv1, 10, scale_enemy_lv1, 1, 1))
        enemy_array.append(ce.EnemyBasic(X - random.randrange(200), random.randrange(Y - scale_enemy_lv2[1]), image_enemy_lv2, 20, scale_enemy_lv2, 1, 2))
        enemy_array.append(ce.EnemyBasic(X - random.randrange(200), random.randrange(Y - scale_enemy_lv3[1]), image_enemy_lv3, 15, scale_enemy_lv3, 4, 3, True, 10))
        enemy_array.append(ce.EnemyBasic(X - random.randrange(200), random.randrange(Y - scale_enemy_lv4[1]), image_enemy_lv4, 30, scale_enemy_lv4, 5, 4, True, 10, 80, True))
        enemy_array.append(ce.EnemyBasic(X - random.randrange(200), random.randrange(Y - scale_enemy_lv5[1]), image_enemy_lv5, 15, scale_enemy_lv5, 4, 5))
        enemy_array.append(ce.EnemyBasic(X - random.randrange(200), random.randrange(Y - scale_enemy_lv6[1]), image_enemy_lv6, 40, scale_enemy_lv6, 1, 6, is_buffing = True))

    else:
        enemy_number = 10
        max_enemy_weight = 10
        current_enemy_weight = 10
        weighted_level_list = [1]
        level = 1
        for enemies in range(enemy_number):
            enemy_array.append(ce.EnemyBasic(X + random.randrange(200), random.randrange(Y - scale_enemy_lv1[1]), image_enemy_lv1, 10, scale_enemy_lv1, 1, 0.75))
    font = pygame.font.Font("font\Cyberbit.ttf", 35)
    font_gameover = pygame.font.Font("font\Cyberbit.ttf", 70)


    c_time = 0
    p_time = 0
    detector = htm.handDetector()
    frames = 0
    cooldown = 0
    current_handsign = "None"
    add_enemy_weight = True

    while running:
        frames += 1
        cooldown += 1
        successs, img = cap.read()
        img = cv2.flip(img,1)
        #get the hands in the image
        img, numHands = detector.findHands(img)
        #get the list of all the point in the right hand
        if(numHands <= 1):
            rightlmList = detector.findPosition(img, 0, draw = False)
            leftlmList = []
        else:
            temp_lm_list = detector.findPosition(img, 1, draw = False)
            temp_lm_list_1 = detector.findPosition(img, 0, draw = False)
            if(temp_lm_list[9][1] <= temp_lm_list_1[9][1]):
                rightlmList = temp_lm_list_1
                leftlmList = temp_lm_list
            else:
                rightlmList = temp_lm_list
                leftlmList = temp_lm_list_1
        h, w, c = img.shape
        if(len(rightlmList) != 0):
            speed_x = 0
            speed_y = 0
            if(rightlmList[9][1] > int(w/2)):
                if rightlmList[9][1] > int(((w/4) * 3)):
                    speed_x = int((rightlmList[9][1] - (w/4 * 3))/(w/4) * player.top_speed)
                    player.x += speed_x
                elif rightlmList:
                    speed_x = int((((rightlmList[9][1] - (w/2))/(w/4)) * -1 + 1) * player.top_speed)
                    player.x -= speed_x
                
                if rightlmList[9][2] > int(h/2):
                    speed_y = int((rightlmList[9][2] - h/2)/(h/2) * player.top_speed)
                    player.y += speed_y
                else:
                    speed_y = int((rightlmList[9][2]/(h/2) * -1 + 1) * player.top_speed)
                    player.y -= speed_y
            if(player.x + player.width > X): player.x = X - player.width
            if(player.x < 0): player.x = 0
            if(player.y + player.height > Y): player.y = Y - player.height
            if(player.y < 0): player.y = 0

        if(len(leftlmList) != 0):
            if(cooldown > 10):
                #check if fingers are under the upper palm to check different hand signs, and start attacking in function to those hand signs
                has_hand_sign = False
                index_finger_closed = False
                middle_finger_closed = False
                ring_finger_closed = False
                pinky_finger_closed = False
                thumb_over_hand = False
                crossed_middle_and_index = False


                if(leftlmList[8][2] > leftlmList[9][2]):
                    index_finger_closed = True
                if(leftlmList[11][2] > leftlmList[9][2]):
                    middle_finger_closed = True
                if(leftlmList[16][2] > leftlmList[9][2]):
                    ring_finger_closed = True
                if(leftlmList[20][2] > leftlmList[9][2]):
                    pinky_finger_closed = True
                if(leftlmList[4][1] < leftlmList[9][1]):
                    thumb_over_hand = True
                if(leftlmList[8][1] < leftlmList[12][1]):
                    crossed_middle_and_index = True
                
                if(middle_finger_closed and ring_finger_closed and not has_hand_sign):
                    if(current_handsign != "Ring_and_middle_closed"):
                        if(player.mana - 3 >= 0):
                            laser_array.append(attack.laser(player.x + player.width, int(player.y + player.height/2), player.damage, 15, red, player.width/2 + 2, 0, 3))
                            player.mana -= 3
                            cooldown = 0
                    has_hand_sign = True
                    current_handsign = "Ring_and_middle_closed"
                if(index_finger_closed and middle_finger_closed and not has_hand_sign):
                    if(not has_hand_sign):
                        if(player.mana - 12 >= 0 and current_handsign != "Index_and_middle_closed"):
                            laser_array.append(attack.arc(player.x + player.width, player.y, player.damage, 10, (100,100,255), player.width/2 + 2, player.height, 5*math.pi/3, math.pi/3, 3, False)) #creates an arc from 300 degree to 60 degree in countreclowise direction
                            player.mana -= 12
                            cooldown = 0
                        has_hand_sign = True
                        current_handsign = "Index_and_middle_closed"

                if(thumb_over_hand and not has_hand_sign):
                    if(player.mana - 6 >= 0 and current_handsign != "Thumb_Over_Hand"):
                            laser_array.append(attack.laser(player.x + player.width, int(player.y + player.height/2), player.damage, 15, (200,100,100), player.width/2 + 2, 0, 3, True))
                            player.mana -= 6
                            cooldown = 0
                    current_handsign = "Thumb_Over_Hand"
                    has_hand_sign = True

                elif(pinky_finger_closed and ring_finger_closed and not has_hand_sign):
                    if(player.mana - 20 >= 0 and current_handsign != "Pinky_and_ring_closed"):
                            laser_array.append(attack.lightning_attack(player.x + player.width, int(player.y + player.height/2), player.damage, (147,185,223), 4, 0, 10, 200, nearest_enemy_to_player))
                            player.mana -= 20
                            cooldown = 0
                    current_handsign = "Pinky_and_ring_closed"
                    has_hand_sign = True
                
                elif(pinky_finger_closed and index_finger_closed and not has_hand_sign):
                    if(player.mana - 15 >= 0 and current_handsign != "index_and_pinky_closed"):
                            laser_array.append(attack.earthquake(int(player.x + player.width/2), int(player.y + player.height/2), int(player.damage/2), (112,72,60), 75))
                            player.mana -= 15
                            cooldown = 0
                    current_handsign = "index_and_pinky_closed"
                    has_hand_sign = True

                if(not has_hand_sign):
                    current_handsign = "open_Hand"
                    player.color = white
    
                
            #print(leftlmList[9])
        player.health_regen = int((player.topHealth - 100)/10)
        player.mana_regen = int((player.topMana - 100)/10 + 1)

        #gets fps on top left
        c_time = time.time()
        fps = 1/(c_time - p_time)
        _, intergerOfSeconds = math.modf(c_time)
        _, intergerOfSecondsPrev = math.modf(p_time)
        #for the regenerations of health and mana, check if the second is the same of not
        if(intergerOfSeconds != intergerOfSecondsPrev):
            if(player.mana + player.mana_regen >= player.topMana):
                player.mana = player.topMana
            else:
                player.mana += player.mana_regen
            
            if(player.health + player.health_regen >= player.topHealth):
                player.health = player.topHealth
            else:
                player.health += player.health_regen
        
        if(c_time - invulnerable_time >= 0.5):
            is_hurt = False
        p_time = c_time



        #display fps
        cv2.putText(img, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
        #draw grid for clearer view
        img = cv2.rectangle(img, (int(w/4 * 3), 0), (int(w/4 * 3), h), green, 5)
        img = cv2.rectangle(img, (int(w/2), 0), (int(w/2), h), green, 5)
        img = cv2.rectangle(img, (0, int(h/2)), (w, int(h/2)), green, 5)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

        image_display = pygame.surfarray.make_surface(imgRGB)
        image_display = pygame.transform.rotate(image_display, 270)
        image_display = pygame.transform.flip(image_display, True, False)
        image_display = pygame.transform.scale(image_display, (w/2,h/2))
        
        screen.fill(black)
        
        
        #start drawing ---------------------------------------------------------------------------------------------------

        draw_background(screen, list_star)
        #draw the player
        screen.blit(image_display, (0, Y - h/2))
        #draw health bar in the bottom of the screen
        #player.health = 50
        if player.health <= 0:
            death_message = "died because of low health"
            running = False
            dead = True
            player.health = 0
        life_color = ((player.health/player.topHealth * -1 + 1) * 255, player.health/player.topHealth * 255, 0)
        pygame.draw.rect(screen, life_color, pygame.Rect(int(X/7 * 2), Y - 80, int(X/7 * 3), 30), 3, 15)
        pygame.draw.rect(screen, life_color, pygame.Rect(int(X/7 * 2), Y - 80, int(player.health/player.topHealth * X/7 * 3), 30), border_radius = 15)
        health_text = font.render("{}/{}".format(player.health, player.topHealth), True, white)
        textRecthealth = health_text.get_rect()
        textRecthealth.center = (X // 2, Y - 67)
        screen.blit(health_text ,textRecthealth)
        
        #draw mana bar bottom right of the screen
        mana_color = (0,0, 200)
        pygame.draw.rect(screen, mana_color, pygame.Rect(int(X/7 * 2), Y - 120, int(X/7 * 3), 30), 3, 15)
        pygame.draw.rect(screen, mana_color, pygame.Rect(int(X/7 * 2), Y - 120, int(player.mana/player.topMana * X/7 * 3), 30), border_radius = 15)
        Mana_text = font.render("{}/{}".format(player.mana, player.topMana), True, white)
        textRectMana = Mana_text.get_rect()
        textRectMana.center = (X // 2, Y - 107)
        screen.blit(Mana_text, textRectMana)

        

        #have the level number top right
        level_text = font.render("Level: {}".format(level), True, white)
        textLevelRect = level_text.get_rect()
        textLevelRect.center = (X - level_text.get_width(), level_text.get_height())
        screen.blit(level_text, textLevelRect)

        #display and animate powerup
        for powerUp in list_powerup:
            powerUp.draw(screen)
            if(c_time - powerUp.last_check > 0.25):
                powerUp.last_check = c_time
                if(not powerUp.toShrink):
                    powerUp.radius += 1
                    if(powerUp.radius >= 10):
                        powerUp.toShrink = True
                else:
                    powerUp.radius -= 1
                    if(powerUp.radius <= 3):
                        powerUp.toShrink = False
            #adds the powerUp to the player
            if(check_colision_rect_circle(powerUp.x, powerUp.y, player.x, player.y, player.width, player.height, powerUp.radius)):
                if(powerUp.nature == "Health"):
                    progression_to_full_health = player.health/player.topHealth
                    player.topHealth += 10
                    player.health = int(player.topHealth * progression_to_full_health)
                elif(powerUp.nature == "Speed"):
                    player.top_speed += 1
                elif(powerUp.nature == "Mana"):
                    progression_to_full_mana = player.mana/player.topMana
                    player.topMana += 10
                    player.mana = int(player.topMana * progression_to_full_mana)
                elif(powerUp.nature == "Health_boost"):
                    player.health += 10 + level
                    if(player.health > player.topHealth):
                        player.health = player.topHealth
                elif(powerUp.nature == "Mana_boost"):
                    player.mana += 20 + level * 2
                    if(player.mana > player.topMana):
                        player.mana = player.topMana
                elif(powerUp.nature == "Damage"):
                    player.damage += 1
                elif(powerUp.nature == "Shield"):
                    player.has_shield = True
                    player.shield_timer = 0
                list_powerup.pop(list_powerup.index(powerUp))
        if(player.has_shield):
            player.shield_timer += 1
            if(player.shield_timer == 110):
                player.has_shield = False
                #move the lasers thrown by the player
        for lz in laser_array:
            if(isinstance(lz, attack.arc)):
                lz.x += lz.speed
            # For the laser attack
            elif(isinstance(lz, attack.lightning_attack)):
                try:
                    index_of_enemy = enemy_array.index(lz.nearest_enemy)
                    lz.attack_enemy(screen, int(enemy_array[index_of_enemy].x + enemy_array[index_of_enemy].width/2), int(enemy_array[index_of_enemy].y + enemy_array[index_of_enemy].height/2))
                    if(lz.current_enemy != None):
                        try:
                            index_of_enemy = enemy_array.index(lz.current_enemy)
                            lz.x = int(enemy_array[index_of_enemy].x + enemy_array[index_of_enemy].width/2)
                            lz.y = int(enemy_array[index_of_enemy].y + enemy_array[index_of_enemy].height/2)
                        except ValueError as e:
                            pass
                    else:
                        lz.x = int(player.x + player.width)
                        lz.y = int(player.y + player.height/2)
                    lz.timer += 1
                    if(lz.timer % 5 == 0):
                        if(lz.num_enemy + 2 > lz.max_num_enemy):
                            index_of_enemy = enemy_array.index(lz.nearest_enemy)
                            enemy_array[index_of_enemy].health -= lz.damage
                            laser_array.pop(laser_array.index(lz))
                        else:
                            #change its x y coordinate to the new "current" enemy
                            index_of_enemy = enemy_array.index(lz.nearest_enemy)
                            lz.x = int(enemy_array[index_of_enemy].x + enemy_array[index_of_enemy].width/2)
                            lz.y = int(enemy_array[index_of_enemy].y + enemy_array[index_of_enemy].height/2)
                            lz.current_enemy = lz.nearest_enemy
                            lz.enemies_already_visited.append(lz.current_enemy)
                            index_of_enemy = enemy_array.index(lz.current_enemy)
                            enemy_array[index_of_enemy].health -= lz.damage
                            #find nearest enemy
                            shortest_distance_to_enemy = 99999999
                            has_enemy_in_range = False
                            list_enemy_in_range = []
                            for enemies in enemy_array:
                                distance_to_laser = math.sqrt((enemies.x - lz.x) ** 2 + (enemies.y - lz.y) ** 2)
                                if(distance_to_laser <= lz.range and enemies.x + enemies.width/2 < X):
                                    is_already_visited = False
                                    for already_visited in lz.enemies_already_visited:
                                        if(already_visited == enemies):
                                            is_already_visited = True
                                    if(not is_already_visited):
                                        if(distance_to_laser < shortest_distance_to_enemy):
                                            shortest_distance_to_enemy = distance_to_laser
                                            lz.nearest_enemy = enemies
                                        list_enemy_in_range.append(enemies)
                                        has_enemy_in_range = True
                            #change its coordinate to match the new enemy
                            if(not has_enemy_in_range):
                                laser_array.pop(laser_array.index(lz))
                            else:
                                lz.num_enemy += 1
                                
                                
                    
                except ValueError as e:
                    laser_array.pop(laser_array.index(lz))
            elif isinstance(lz, attack.earthquake):
                lz.timer += 1
                if(lz.timer % 5 == 0):
                    if(lz.cycle >= 3):
                        laser_array.pop(laser_array.index(lz))
                    else:
                        lz.add_point_to_next_cyle()

            else:
                if(lz.is_tracker):
                    try:
                        #keep tracking the same enemy
                        enemy_to_track = enemy_array.index(lz.is_tracking)
                        enemy_x = enemy_array[enemy_to_track].x + enemy_array[enemy_to_track].width/2
                        enemy_y = enemy_array[enemy_to_track].y + enemy_array[enemy_to_track].height/2
                    except ValueError as e:
                        #if it does not find the enemy, find the next nearest enemy
                        min_test_dis = 1000000
                        index = 0
                        index_of_min = 0
                        for enemies_test in enemy_array:
                            test_dis = math.sqrt((enemies_test.x - lz.x) ** 2 + (enemies_test.y - lz.y) ** 2)
                            if(test_dis < min_test_dis):
                                min_test_dis = test_dis
                                index_of_min = index
                            index += 1

                        enemy_x = enemy_array[index_of_min].x + enemy_array[index_of_min].width/2
                        enemy_y = enemy_array[index_of_min].y + enemy_array[index_of_min].height/2
                        lz.is_tracking = enemy_array[index_of_min]
                    lz.move_to_target(enemy_x, enemy_y)
                else:
                    lz.x += lz.speed
            lz.draw(screen)
            if(lz.x > X):
                laser_array.pop(laser_array.index(lz))
            
        #all the enemy action here ------------------------------------------------------------------------------
        shortest_distance = 200000
        for enemies in enemy_array:
            enemy_dead = False

            #move enemy
            for lasers in laser_array:
                #check whick type of attack
                if(isinstance(lasers, attack.arc)):
                    #show_hitbox(screen, lasers.x, lasers.y, lasers.width, lasers.height)
                    if(check_colision(lasers.x, lasers.y, enemies.x, enemies.y, lasers.width, lasers.height, enemies.width, enemies.height)):
                        try:
                            enemies.already_hit_by.index(lasers)
                        except ValueError as e:
                            enemies.health -= lasers.damage
                            enemies.move_oposite_direction = True
                            enemies.already_hit_by.append(lasers)
                elif(isinstance(lasers, attack.lightning_attack)):pass
                elif isinstance(lasers, attack.earthquake):
                    if(check_colision_rect_circle(lasers.x, lasers.y, enemies.x, enemies.y, enemies.width, enemies.height, lasers.radius)):
                        if(lasers.timer % 5 == 0):
                            enemies.health -= lasers.damage
                else:
                    if(check_collision_line_rectangle(lasers.x, lasers.y, enemies.x, enemies.y, enemies.width, enemies.height, lasers.add_x, lasers.add_y)):
                        enemies.health -= lasers.damage
                        laser_array.pop(laser_array.index(lasers))

            if(enemies.health <= 0):
                enemy_dead = True
                enemy_defeated += 1
                current_enemy_weight -= enemies.lvl
                if(add_enemy_weight):
                    max_enemy_weight += 1
                add_enemy_weight = not add_enemy_weight
                enemy_weight_to_test += 1
                
                #adds an enemy if one is dead
                #adds the new enemy to keep the difficulty rising
                level_to_add = random.choice(weighted_level_list) #gives the level to add
                #print(weighted_level_list)
                if(level_to_add + current_enemy_weight <= max_enemy_weight):
                    #adds the enemy based on the level
                    for _ in range(int((max_enemy_weight - current_enemy_weight)/level_to_add)):
                        if(level_to_add == 1): enemy_array.append(ce.EnemyBasic(X + random.randrange(100) + scale_enemy_lv1[0], random.randrange(Y - scale_enemy_lv1[1]), image_enemy_lv1, 10, scale_enemy_lv1, 1, 1))
                        if(level_to_add == 2): enemy_array.append(ce.EnemyBasic(X + random.randrange(100) + scale_enemy_lv2[0], random.randrange(Y - scale_enemy_lv2[1]), image_enemy_lv2, 20, scale_enemy_lv2, 1, 2))
                        if(level_to_add == 3): enemy_array.append(ce.EnemyBasic(X + random.randrange(100) + scale_enemy_lv3[0], random.randrange(Y - scale_enemy_lv3[1]), image_enemy_lv3, 15, scale_enemy_lv3, 4, 3, True, 10))
                        if(level_to_add == 4): enemy_array.append(ce.EnemyBasic(X + random.randrange(100) + scale_enemy_lv4[0], random.randrange(Y - scale_enemy_lv4[1]), image_enemy_lv4, 20, scale_enemy_lv4, 5, 4, True, 10, 80, True))
                        if(level_to_add == 5): enemy_array.append(ce.EnemyBasic(X + random.randrange(100) + scale_enemy_lv5[0], random.randrange(Y - scale_enemy_lv5[1]), image_enemy_lv5, 15, scale_enemy_lv5, 4, 5))
                        if(level_to_add == 6): enemy_array.append(ce.EnemyBasic(X + random.randrange(100) + scale_enemy_lv6[0], random.randrange(Y - scale_enemy_lv6[1]), image_enemy_lv6, 40, scale_enemy_lv6, 1, 6, is_buffing = True))
                        current_enemy_weight += level_to_add
                #every time a certain amount of enemy are defeated, it increase the level of the game so that more, harder enemy can spawn

                if(enemy_weight_to_test % to_pass_to_next_level == 0 and not test_mode):
                    to_pass_to_next_level += 10
                    level += 1
                    enemy_weight_to_test = 0
                    for _ in range(level):
                        weighted_level_list.append(level)

                #drops powerup
                if(test_mode):
                    if(random.randrange(10) != 1):
                        random_index = random.randrange(len(possible_powerUp))
                        list_powerup.append(ce.powerUp(int(enemies.x + enemies.width/2), int(enemies.y + enemies.height/2), 7, possible_powerUp[random_index]))
                else:
                    if(random.randrange(5 - math.floor((enemies.lvl - 1)/2)) == 0):
                        random_index = random.randrange(len(possible_powerUp))
                        list_powerup.append(ce.powerUp(int(enemies.x + enemies.width/2), int(enemies.y + enemies.height/2), 7, possible_powerUp[random_index]))

                enemy_array.pop(enemy_array.index(enemies))

                        #lasers
                        #once every thirty frames
            if(enemies.timer % enemies.attack_frequency == 0 and enemies.shoots_laser and enemies.timer != 0):
                enemy_laser_array.append(enemies.make_lasers())
                #print(enemy_laser_array)
            if(not enemy_dead):
                if(random.randrange(15) != 5):
                    if(not enemies.follow):
                        if(enemies.move_oposite_direction):
                            enemies.x += enemies.speed
                        else:
                            enemies.x -= enemies.speed
                    else:
                        enemies.move_to_target(player.x, player.y)
                enemies.draw(screen)
                distance_to_player = math.sqrt((enemies.x - player.x) ** 2 + (enemies.y - player.y) ** 2)
                if(distance_to_player < shortest_distance):
                    shortest_distance = distance_to_player
                    nearest_enemy_to_player = enemies

            #End game if enemy go all the way to the left
            if enemies.x + enemies.width < 0:
                death_message = "died because enemy of level {} went over the border".format(enemies.lvl)
                running = False
                dead = True
            
            #incase the enemie follow, if it hits the player, deals damage
            if(enemies.follow):
                #kind of rustic but works efficiently considering the situation
                if(check_colision(enemies.x, enemies.y, player.x, player.y, enemies.width, enemies.height, player.width, player.height)):
                    if(not is_hurt and not player.has_shield):
                        player.health -= enemies.damage
                        is_hurt = True
                        invulnerable_time = time.time()
                    enemies.move_oposite_direction = True
                    
                if(enemies.confused_timer > 5):
                    enemies.move_oposite_direction = False
                    enemies.confused_timer = 0
            else:
                if(enemies.confused_timer > 15):
                    enemies.move_oposite_direction = False
                    enemies.confused_timer = 0
                elif(enemies.move_oposite_direction):
                    enemies.confused_timer += 1
            
            if(enemies.is_buffing):
                if(enemies.currently_buffing and enemies.buff_timer == 0):
                    for enemies_check in enemy_array:
                        if(check_colision_rect_circle(enemies.x, enemies.y, enemies_check.x, enemies_check.y, enemies_check.width, enemies_check.height, enemies.width * 3)):
                            if(not enemies_check.has_buff and enemies_check != enemies):
                                enemies_check.width *= 1.4
                                enemies_check.height *= 1.4
                                enemies_check.has_buff = True
                                enemies_check.speed *= 2
                                enemies_check.damage *= 1.5
                                enemies_check.img = pygame.transform.scale(enemies_check.img, (enemies_check.width, enemies_check.height))
                                enemies_check.original_img = enemies_check.img



        for laser_enemy in enemy_laser_array:
            laser_enemy.move()
            laser_enemy.draw(screen)
            #check collision player and laser
            if(check_collision_line_rectangle(laser_enemy.x, laser_enemy.y, player.x, player.y, player.width, player.height, laser_enemy.add_x, laser_enemy.add_y)):
                enemy_laser_array.pop(enemy_laser_array.index(laser_enemy))
                if(not is_hurt and not player.has_shield):
                    player.health -= laser_enemy.damage
                    is_hurt = True
                    invulnerable_time = time.time()
                
                
            #makes the laser dispear if going offscreen
            if(laser_enemy.x > X or laser_enemy.x < 0):
                try:
                    enemy_laser_array.pop(enemy_laser_array.index(laser_enemy))
                except ValueError as e:
                    pass
            if(laser_enemy.y > Y or laser_enemy.y < 0):
                try:
                    enemy_laser_array.pop(enemy_laser_array.index(laser_enemy))
                except ValueError as e:
                    pass
        
        player.draw(screen)

        #draw red rectangle over the player is hurt
        #dont know if I like it, might remove
        if(is_hurt):
            tintDamage(screen, 0.25)

        pygame.display.flip()


       

        #get event to close out
        for event in pygame.event.get():
                #close when x is pressed
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    #if q is hit
                    if event.key == pygame.K_q:
                        running = False
    
    if(dead):
        death_screen_running = True
        c_time = time.time()
        while death_screen_running:
            Game_over_text = font_gameover.render("GAME OVER", True, white)
            death_message_text = font.render(death_message, True, white)
            Game_over_text_rect = Game_over_text.get_rect()
            death_message_text_rect = death_message_text.get_rect()
            Game_over_text_rect.center = (X // 2, (Y // 2))
            death_message_text_rect.center = (X // 2, Y // 2 + (Y // 12))
            font_credit = pygame.font.Font("font\Cyberbit.ttf", 20)
            credits_text = font_credit.render("Made by:\nKilian Taillandier\nSierraFox\nBarbara", True, white)
            credits_text_rect = credits_text.get_rect()
            credits_text_rect.center = (X // 2, (Y // 2) + (Y // 18 * 3))
            #screen.blit(credits_text, credits_text_rect)
            screen.blit(Game_over_text, Game_over_text_rect)
            screen.blit(death_message_text, death_message_text_rect)
            if(time.time() - c_time >= 30):
                death_screen_running = False

            for event in pygame.event.get():
                #close when x is pressed
                if event.type == pygame.QUIT:
                    death_screen_running = False
                if event.type == pygame.KEYDOWN:
                    #if q is hit
                    if event.key == pygame.K_q:
                        death_screen_running = False
            pygame.display.flip()


def make_star_list(X,Y):
    list_star = []
    for num_stars in range(random.randrange(40) + 40):
        temp_list = []
        center_x = random.randrange(X)
        center_y = random.randrange(Y)
        side_lenght = random.randrange(8) + 3
        num_point = random.randrange(5) + 3
        angle = math.radians(360/num_point)
        
        start_angle = random.randrange(int(360/num_point))
        x = math.sin(math.radians(start_angle)) * side_lenght
        y = math.sqrt(side_lenght ** 2 - x ** 2)
        temp_list.append((center_x + int(x), center_y + int(y)))
        prev_x = x
        for points in range(num_point - 1):
            x = x*math.cos(angle) - y * math.sin(angle)
            y = y*math.cos(angle) + prev_x * math.sin(angle)
            prev_x = x
            temp_list.append((center_x + int(x), center_y + int(y)))
        list_star.append(temp_list)
    return list_star


def draw_background(screen, arr):
    for stars in arr:
        pygame.draw.polygon(screen, (255,255,255), stars)

def check_collision_line_rectangle(x1, y1, x2, y2, width, height, add_x, add_y):
    #check if the line intersect with any of the edges of the rectangle, if yes, return True.
    if(check_intersect_line([x1, y1], [x1 + add_x, y1 + add_y], [x2, y2], [x2 + width, y2])): return True
    if(check_intersect_line([x1, y1], [x1 + add_x, y1 + add_y], [x2, y2], [x2, y2 + height])): return True
    if(check_intersect_line([x1, y1], [x1 + add_x, y1 + add_y], [x2, y2 + height], [x2 + width, y2 + height])): return True
    if(check_intersect_line([x1, y1], [x1 + add_x, y1 + add_y], [x2 + width, y2], [x2 + width, y2 + height])): return True
    return False

#basicly stole the code from "Introduction to algorithm, third Edition" p 1039 chapter 33 so go there for extra info
def check_intersect_line(p1, p2, p3, p4):
    d1 = direction(p3,p4,p1)
    d2 = direction(p3,p4,p2)
    d3 = direction(p1,p2,p3)
    d4 = direction(p1,p2,p4)
    if((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    elif d1 == 0 and on_segment(p3,p4,p1): return True
    elif d2 == 0 and on_segment(p3,p4,p2): return True
    elif d3 == 0 and on_segment(p1,p2,p3): return True
    elif d4 == 0 and on_segment(p1,p2,p4): return True
    else: return False


def direction(p0,p1,p2):
    return (p1[0] - p0[0])*(p2[1] - p0[1]) - (p2[0] - p0[0]) * (p1[1] - p0[1])

def on_segment(p0,p1,p2):
    if min(p0[0], p1[0]) <= p2[0] and p2[0] <= max(p0[0], p1[0]) and min(p0[1], p1[1]) <= p2[1] and p2[1] <= max(p0[1], p1[1]):
        return True
    return False

def tintDamage(surface, scale):
    GB = min(255, max(0, round(255 * (1-scale))))
    surface.fill((255, GB, GB), special_flags = pygame.BLEND_MULT)

def show_hitbox(screen, x, y, width, height):
    pygame.draw.circle(screen, (0,255,0), (x, y), 3)
    pygame.draw.circle(screen, (0,255,0), (x + width, y), 3)
    pygame.draw.circle(screen, (0,255,0), (x, y + height), 3)
    pygame.draw.circle(screen, (0,255,0), (x + width, y + height), 3)

#stole this code from hackmd.io, uses the separating axis theorem
#input an array of point verticies for both shape in form: [[x1,y1],[x2,y2]] in the counter clockwise direction
def polygon_collide(p1, p2):
    '''
    Return True and the MPV if the shapes collide. Otherwise, return False and
    None.

    p1 and p2 are lists of ordered pairs, the vertices of the polygons in the
    counterclockwise direction.
    '''

    p1 = [np.array(v, 'float64') for v in p1]
    p2 = [np.array(v, 'float64') for v in p2]

    edges = edges_of(p1)
    edges += edges_of(p2)
    orthogonals = [orthogonal(e) for e in edges]

    push_vectors = []
    for o in orthogonals:
        separates, pv = is_separating_axis(o, p1, p2)

        if separates:
            # they do not collide and there is no push vector
            return False, None
        else:
            push_vectors.append(pv)

    # they do collide and the push_vector with the smallest length is the MPV
    mpv =  min(push_vectors, key=(lambda v: np.dot(v, v)))

    # assert mpv pushes p1 away from p2
    d = centers_displacement(p1, p2) # direction from p1 to p2
    if np.dot(d, mpv) > 0: # if it's the same direction, then invert
        mpv = -mpv

    return True, mpv


def centers_displacement(p1, p2):
    """
    Return the displacement between the geometric center of p1 and p2.
    """
    # geometric center
    c1 = np.mean(np.array(p1), axis=0)
    c2 = np.mean(np.array(p2), axis=0)
    return c2 - c1

def edges_of(vertices):
    """
    Return the vectors for the edges of the polygon p.

    p is a polygon.
    """
    edges = []
    N = len(vertices)

    for i in range(N):
        edge = vertices[(i + 1)%N] - vertices[i]
        edges.append(edge)

    return edges

def orthogonal(v):
    """
    Return a 90 degree clockwise rotation of the vector v.
    """
    return np.array([-v[1], v[0]])

def is_separating_axis(o, p1, p2):
    """
    Return True and the push vector if o is a separating axis of p1 and p2.
    Otherwise, return False and None.
    """
    min1, max1 = float('+inf'), float('-inf')
    min2, max2 = float('+inf'), float('-inf')

    for v in p1:
        projection = np.dot(v, o)

        min1 = min(min1, projection)
        max1 = max(max1, projection)

    for v in p2:
        projection = np.dot(v, o)

        min2 = min(min2, projection)
        max2 = max(max2, projection)

    if max1 >= min2 and max2 >= min1:
        d = min(max2 - min1, max1 - min2)
        # push a bit more than needed so the shapes do not overlap in future
        # tests due to float precision
        d_over_o_squared = d/np.dot(o, o) + 1e-10
        pv = d_over_o_squared*o
        return False, pv
    else:
        return True, None



#Game credit: mettre Tom aka Barbara
if __name__ == "__main__": main()