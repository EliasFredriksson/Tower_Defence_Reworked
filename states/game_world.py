import pygame, os, json
from states.state import State
from constants import MODE
from code_modules.quad_tree.quad_point import QuadPoint
from code_modules.quad_tree.quad_rectangle import QuadRectangle
from code_modules.quad_tree.quad_circle import QuadCircle
from code_modules.quad_tree.quadtree import QuadTree
from code_modules.spline.spline import Spline
from code_modules.spline.spline_point_2D import Spline_Point2D
from code_modules.tower_menu import TowerMenu
from code_modules.spline.agent import Agent
from code_modules.enemy import Enemy
from code_modules.tower import Tower
from code_modules.projectile import Projectile
from code_modules.linked_list import LinkedList
from settings import *

class Game_World(State):
    def __init__(self, game):
        ### WE SEND True TO TELL THE STATE MACHINE THAT NEW ASSETS NEEDS LOADING ###
        super().__init__(game, True)

        self.levelData = self.game.LEVEL_DATA["testLevel"]
        self.background = self.game.LEVEL_IMAGES["testLevel"]
        self.SHOWBACKGROUND = True
        self.border = self.game.LEVEL_BORDER

        self.position = pygame.Vector2(0,0)
        self.rect = pygame.Rect(
            self.position.x,
            self.position.y,
            self.background.get_width(),
            self.background.get_height()
            )


        self.SHOW_PATH = True
        self.SHOW_TOWERS = True
        self.SHOW_BALLOONS = True
        self.SHOW_PROJECTILES = True
        self.SHOW_TOWER_MENU = True
        self.IS_PLACING_TOWER = False
        self.QUAD_TREE_CAPACITY = 8

        self.BOUNDARY = QuadRectangle(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        self.quad_tree = QuadTree(self.BOUNDARY, self.QUAD_TREE_CAPACITY)

        self.path = self.__getPath()
        self.tower_list = LinkedList()
        self.balloon_list = LinkedList()
        self.projectile_list = LinkedList()
        self.enemyIdIterator = 0
    
        self.lives = 100
        self.cash = 500

        self.livesLost = 0
        self.cashLost = 0

        self.tower_menu = TowerMenu(self.game, self.add_tower)

        self.pressed = False


    ## UPDATE ###
    def update(self, delta_time, actions):
        super().update(delta_time, actions)
        if self.game.mode == MODE.PLAY:
            self.SHOW_PATH = False
        
        if self.game.mode == MODE.DEBUG:
            self.SHOW_PATH = True
            self.path.update()

        print("SIZE: ", self.tower_list.size, self.balloon_list.size, self.projectile_list.size)

        if(actions["ACTION_1"]):
            self.add_enemy("red")
        if(actions["ACTION_2"]):
            self.add_enemy("blue")
        if(actions["ACTION_3"]):
            self.add_enemy("green")
        if(actions["ACTION_4"]):
            self.add_enemy("yellow")
        if(actions["ACTION_5"]):
            self.add_enemy("pink")

        # if(actions["MOUSE_LEFT"]):
        #     if not self.pressed:
        #         self.add_tower("Cannon")
        #         self.pressed = True
        
        # if not actions["MOUSE_LEFT"]:
        #     self.pressed = False

        # Reset QuadTree
        self.quad_tree = QuadTree(self.BOUNDARY, self.QUAD_TREE_CAPACITY)

        # Update Tower Menu
        self.tower_menu.update(delta_time, actions)

        # Update ballons
        self.__update_ballons(delta_time, actions)

        # Update towers
        self.__update_towers(delta_time, actions)

        # Update projectiles
        self.__update_projectiles(delta_time, actions)

    def __update_ballons(self, delta_time, actions):
        current_balloon_node = self.balloon_list.root
        while current_balloon_node:
            #### LOOP THROUGH ALL ITEMS ####
            next_balloon_node = current_balloon_node.get_next()
            balloon = current_balloon_node.get_data()
            if balloon:
                balloon.update(delta_time)
                # Update Quad Tree
                self.quad_tree.insert(
                    QuadPoint(
                        balloon.agent.get_pos().x,
                        balloon.agent.get_pos().y,
                        balloon
                    )
                )
                # Loose life if balloon reached the end
                if balloon.agent.REACHED_END:
                    self.livesLost += balloon.health
                # Spawn new balloons if its popped
                if balloon.POPPED:
                    balloon.spawn(self.add_enemy)
                # Remove balloon if any above
                if balloon.agent.REACHED_END or balloon.POPPED:
                    self.balloon_list.remove(balloon)
            # Advance to next balloon (node)
            current_balloon_node = next_balloon_node
        
    def __update_towers(self, delta_time, actions):
        current_tower_node = self.tower_list.root
        while current_tower_node:
            #### LOOP THROUGH ALL ITEMS ####
            next_tower_node = current_tower_node.get_next()
            tower = current_tower_node.get_data()

            if tower:
                tower.update(delta_time, actions, self.quad_tree)

                # Create query range equal to the range of the tower
                query_range = QuadCircle(tower.pos.x, tower.pos.y, tower.range.radius)
                # Filter out balloons inside the range of the tower
                quad_points_in_range = self.quad_tree.query(query_range)

                # Clear all balloons from list of balloons in range
                tower.balloons_in_range.clear()
                for point in quad_points_in_range:
                    # Add balloons in range to list
                    tower.balloons_in_range.append(point.userData)

                if tower.SOLD:
                    self.tower_list.remove(tower)

            # Advance to next tower (node)
            current_tower_node = next_tower_node

    def __update_projectiles(self, delta_time, actions):
        current_projectile_node = self.projectile_list.root
        while current_projectile_node:
            next_projectile_node = current_projectile_node.get_next()
            # Get current projectile and update it
            projectile = current_projectile_node.get_data()
            if projectile:
                projectile.update(delta_time, self.quad_tree)
                if projectile.REACHED_MAX_DISTANCE or projectile.DEPLETED:
                    self.projectile_list.remove(projectile)
                
            current_projectile_node = next_projectile_node

    ### RENDER ###
    def render(self, canvas):
        # DRAW ANIMATIONS
        #self.animations.get("fire").draw(canvas)

        # DRAW BACKGROUND
        if self.SHOWBACKGROUND:
            canvas.blit(self.background, self.position)

        # DRAW PATH (IF IN DEBUG)
        if self.SHOW_PATH:
            self.path.draw(canvas)

        # DRAW BALLONS
        if self.SHOW_BALLOONS:
            #self.__drawPointerList(canvas)
            self.__draw_list(self.balloon_list, canvas)

        # DRAW TOWERS
        if self.SHOW_TOWERS:
            #self.__drawPointerList(self.towersStartPointer, canvas)
            self.__draw_list(self.tower_list, canvas)

        # DRAW PROJECTILES
        if self.SHOW_PROJECTILES:
            self.__draw_list(self.projectile_list, canvas)

        if self.SHOW_TOWER_MENU:
            self.tower_menu.render(canvas)

        # DRAW LEVEL BORDER
        canvas.blit(self.border, self.position)

    def __draw_list(self, list, canvas):
        current_entry = list.root
        #print("CURRET PROJECTILE: ", current_entry.get_data())
        while current_entry:
            data = current_entry.get_data()
            if data:
                data.render(canvas)
            current_entry = current_entry.get_next()
  
    def add_enemy(self, whichEnemy, tPrevious = 0, offset = 0):
        ### This calc is used to calculate the offset of ballons spawning from
        # other ballons popping.
        if tPrevious <= offset*10:
            tCalc = tPrevious - offset*10
        else:
            tCalc = tPrevious + offset*10

        # CREATE THE NEW BALOON
        newEnemy = Enemy(
            self.game,
            Agent(self.path, tCalc),
            whichEnemy,
            self.enemyIdIterator
            )
        self.balloon_list.add(newEnemy)
        self.enemyIdIterator += 1
        self.enemyIdIterator += 1

        # enemy = PointerElement()
        # enemy.setItem(Enemy(
        #     Agent(self.path, tCalc), 
        #     whichEnemy, 
        #     self.enemyIdIterator, 
        #     self.game
        #     ))

        # # IF ANY OTHER BALOONS EXISTS:
        # if self.enemiesStartPointer.hasNext:
        #     enemy.setNext(self.enemiesStartPointer.nextItem)

        # # ADD THE NEW BALOON
        # self.enemiesStartPointer.setNext(enemy)
        return newEnemy.id

    def add_tower(self, whichTower):
        # CREATE THE TOWER
        new_tower = Tower(whichTower, self.game, self.add_projectile)
        # ADD THE TOWER TO LIST
        self.tower_list.add(new_tower)
   
    def add_projectile(self, attack_type, target, start_pos, angle, aim_offset):
        new_projectile = Projectile(attack_type, self.game, self.quad_tree)
        new_projectile.shoot(target, start_pos, angle, aim_offset)
        self.projectile_list.add(new_projectile)


    ### PART OF CONSTRUCTION ###
    def __getPath(self):
        path = Spline()
        for entry in self.levelData["path"]:
            path.points.append(
                Spline_Point2D(
                    self.levelData["path"][entry]["x_pos"] + self.position[0],
                    self.levelData["path"][entry]["y_pos"] + self.position[1]
                    ))
        path.update()
        return path

    ### STATES ###
    def enter_state(self):
        super().enter_state()

    def exit_state(self):
        super().exit_state()

    ### EXTRA ASSETS LOADING ###
    def load_assets(self):
        ### LOAD ASSETS BEFORE CALLING super().load_assets() ###
        print("GAME STATE LOADING")
        super().load_assets()