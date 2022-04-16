# import random, pygame, time
from code_modules.quad_tree.quad_point import QuadPoint 
from code_modules.quad_tree.quad_rectangle import QuadRectangle

#count = 0

class QuadTree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.divided = False

    def insert(self, p: QuadPoint):
        if not self.boundary.contains(p):
            return False

        if len(self.points) < self.capacity:
            self.points.append(p)
            return True
        else:
            if not self.divided:
                self.__subdivide()

            if self.northeast.insert(p):
                return True
            elif self.northwest.insert(p):
                return True
            elif self.southeast.insert(p):
                return True
            elif self.southwest.insert(p):
                return True

    #       |
    #  NW   |   NE
    #----------------
    #  SW   |   SE
    #       |   

    def __subdivide(self):
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.w
        h = self.boundary.h

        ne = QuadRectangle(x + w/2, y, w/2, h/2)
        self.northeast = QuadTree(ne, self.capacity)

        nw = QuadRectangle(x, y, w/2, h/2)
        self.northwest = QuadTree(nw, self.capacity)

        se = QuadRectangle(x + w/2, y + h/2, w/2, h/2)
        self.southeast = QuadTree(se, self.capacity)

        sw = QuadRectangle(x, y + h/2, w/2, h/2)
        self.southwest = QuadTree(sw, self.capacity)

        self.divided = True

    def query(self, range):
        global count
        found = []

        if not self.boundary.intersects(range):
            return found
        else:
            
            for p in self.points:
                #count += 1
                if range.contains(p):
                    found.append(p)
        
        if self.divided:
            found.extend(x for x in self.northwest.query(range) if x not in found)
            found.extend(x for x in self.northeast.query(range) if x not in found)
            found.extend(x for x in self.southwest.query(range) if x not in found)
            found.extend(x for x in self.southeast.query(range) if x not in found)

        return found

# pygame.init()
# pygame.display.set_caption("QUAD TREE VISUALISATION")
# SCREEN_WIDTH = int(820)
# SCREEN_HEIGHT = int(820)
# main_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
# main_canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))


# class Game():
#     def __init__(self):
#         boundary = Rectangle(10,10,800,800)
#         self.qTree = QuadTree(boundary, 4)
#         self.running = True
#         for i in range(1000):
#             p = Point(random.randint(0,800), random.randint(0,800))
#             self.qTree.insert(p)

#         self.targetRange = Rectangle(245,245,85,85)

#     def run(self):
#         prev_time = time.time()
#         delta_time = 0
#         clock = pygame.time.Clock()

#         while self.running:
#             ### GAME TICK ###
#             clock.tick_busy_loop(60)

#             ### DELTA TIME ###
#             now_time = time.time()
#             delta_time = now_time - prev_time
#             prev_time = now_time

#             ##### CALC UPDATES #####
#             self.update(delta_time)
          
#             ##### DRAW GRAPHICS #####
#             main_canvas.fill((0,0,0))
#             self.draw(main_canvas)

#             ##### APPLY THE CANVAS TO SCREEN #####
#             main_screen.blit(main_canvas, (0,0))
#             pygame.display.update()

#     def update(self, deltaTime):
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 self.running = False

#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_SPACE:
#                     self.randomizePoints(1)
            
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 if event.button == 1:
#                     self.createPoints(event.pos)
                   

#             if event.type == pygame.MOUSEMOTION:
#                 self.targetRange.x = event.pos[0] - self.targetRange.w/2
#                 self.targetRange.y = event.pos[1] - self.targetRange.h/2
                    
#     def randomizePoints(self, howMany):
#         for i in range(howMany):
#             p = Point(random.randint(0,800), random.randint(0,800))
#             self.qTree.insert(p)

#     def createPoints(self, mousePos):
#         p = Point(mousePos[0], mousePos[1])
#         self.qTree.insert(p)

#     def draw(self, canvas):
#         global count
#         points = self.qTree.query(self.targetRange)
#         print("COUNT: ", count)
#         count = 0

#         self.drawQTree(self.qTree, canvas)
#         pygame.draw.rect(canvas, (0,255,0), (self.targetRange.x, self.targetRange.y, self.targetRange.w, self.targetRange.h), 2)
#         for p in points:
#             #print(p.x, p.y)
#             pygame.draw.circle(main_canvas, (0,255,0), (p.x, p.y), 3)
        
#     def drawQTree(self, tree, canvas):
#         r = pygame.Rect(tree.boundary.x, tree.boundary.y, tree.boundary.w, tree.boundary.h)
#         pygame.draw.rect(canvas, (255,255,255), r, 1)
#         for p in tree.points:
#             pygame.draw.circle(canvas, (255,0,0), (p.x, p.y), 2)

#         if tree.divided:
#             self.drawQTree(tree.northeast, canvas)
#             self.drawQTree(tree.northwest, canvas)
#             self.drawQTree(tree.southeast, canvas)
#             self.drawQTree(tree.southwest, canvas)


        
        
        




# g = Game()
# g.run()
# pygame.quit()