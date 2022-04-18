from asyncio import current_task
import pygame, os, json
from states.state import State
from constants import MODE
from code_modules.quad_tree.quad_point import QuadPoint
from code_modules.quad_tree.quad_rectangle import QuadRectangle
from code_modules.quad_tree.quad_circle import QuadCircle
from code_modules.quad_tree.quadtree import QuadTree
from code_modules.spline.spline import Spline
from code_modules.spline.spline_point_2D import Spline_Point2D
from code_modules.pointer_list import PointerElement
from code_modules.spline.agent import Agent
from code_modules.enemy import Enemy
from code_modules.tower import Tower
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

        self.position = pygame.Vector2(100,0)
        self.rect = pygame.Rect(
            self.position.x,
            self.position.y,
            self.background.get_width(),
            self.background.get_height()
            )


        self.SHOW_PATH = True
        self.SHOW_TOWERS = True
        self.SHOW_BALLOONS = True
        self.IS_PLACING_TOWER = False
        self.QUAD_TREE_CAPACITY = 4

        self.BOUNDARY = QuadRectangle(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
    
        self.path = self.__getPath()
        self.towerList = LinkedList()
        self.balloonList = LinkedList()
        self.enemyIdIterator = 0
    
        self.lives = 100
        self.cash = 500

        self.livesLost = 0
        self.cashLost = 0


    ## UPDATE ###
    def update(self, delta_time, actions):
        super().update(delta_time, actions)
        if self.game.mode == MODE.PLAY:
            self.SHOW_PATH = False
        
        if self.game.mode == MODE.DEBUG:
            self.SHOW_PATH = True
            self.path.update()


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

        #Reset QuadTree
        self.quad_tree = QuadTree(self.BOUNDARY, self.QUAD_TREE_CAPACITY)

        #Update ballons
        self.__update_ballons(delta_time)

        #Update towers
        self.__update_towers(delta_time)

    def __update_ballons(self, delta_time):
        current_balloon_node = self.balloonList.root
        while current_balloon_node:
            #### LOOP THROUGH ALL ITEMS ####
            next_balloon_node = current_balloon_node.get_next()
            balloon = current_balloon_node.get_data()
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
                balloon.spawn(self.addEnemy)
            # Remove balloon if any above
            if balloon.agent.REACHED_END or balloon.POPPED:
                self.balloonList.remove(balloon)
            # Advance to next balloon (node)
            current_balloon_node = next_balloon_node
        
    def __update_towers(self, delta_time):
        current_tower_node = self.towerList.root
        while current_tower_node:
            #### LOOP THROUGH ALL ITEMS ####
            next_tower_node = current_tower_node.get_next()
            tower = current_tower_node.get_data()
            tower.update(delta_time, self.quad_tree)

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
                self.towerList.remove(tower)

            # Advance to next tower (node)
            current_tower_node = next_tower_node


     ### DRAW ###
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
            self.__draw_list(self.balloonList, canvas)
    

        # DRAW TOWERS
        if self.SHOW_TOWERS:
            #self.__drawPointerList(self.towersStartPointer, canvas)
            self.__draw_list(self.towerList, canvas)

        # DRAW LEVEL BORDER
        canvas.blit(self.border, self.position)

    def __draw_list(self, list, canvas):
        current_entry = list.root
        while current_entry:
            current_entry.get_data().render(canvas)
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
        self.balloonList.add(newEnemy)
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
        new_tower = Tower(whichTower, self.game)
        # ADD THE TOWER TO LIST
        self.towerList.add(new_tower)
        # # CREATE THE TOWER
        # tower = PointerElement()
        # tower.setItem(Tower(whichTower, self.game))

        # # IF ANY OTHER TOWERS EXISTS
        # if self.towersStartPointer.hasNext:
        #     tower.setNext(self.towersStartPointer.nextItem)
        
        # # ADD THE TOWER
        # self.towersStartPointer.setNext(tower)


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


    def enter_state(self):
        super().enter_state()

    def exit_state(self):
        super().exit_state()

    def load_assets(self):
        ### LOAD ASSETS BEFORE CALLING super().load_assets() ###
        print("GAME STATE LOADING")
        super().load_assets()