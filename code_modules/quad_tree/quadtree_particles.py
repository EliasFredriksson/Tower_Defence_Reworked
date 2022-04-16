import random, pygame, time, math

######## QUADTREE ########
count = 0

class Point:
    def __init__(self, x ,y, userData):
        self.x = x
        self.y = y
        self.userData = userData

class Circle:
    def __init__(self, x, y, radius) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.rSquared = self.radius * self.radius

        self.type = "Circle"

    def contains(self, p):
        return getDistanceSquaredPointVsPoint((self.x, self.y), (p.x, p.y)) < self.radius**2    

    def intersects(self, range):
        return getDistanceSquaredPointVsPoint((self.x, self.y), (range.x, range.y)) < (self.radius + range.radius)**2

class Rectangle:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.type = "Rect"

    def contains(self, p):
        return (
            p.x >= self.x and
            p.x <= self.x + self.w and
            p.y >= self.y and
            p.y <= self.y + self.h
            )

    def intersects(self, range):
        if range.type == "Circle":
            Xn = max(self.x, min(range.x, (self.x + self.w)))
            Yn = max(self.y, min(range.y, (self.y + self.h)))

            Dx = Xn - range.x
            Dy = Yn - range.y
            return (Dx**2 + Dy**2) <= range.radius**2
        else:
            return not (
                range.x > self.x + self.w or
                range.x + range.w < self.x or
                range.y > self.y + self.h or
                range.y + range.h < self.y )

class QuadTree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.divided = False

    def insert(self, p: Point):
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

        ne = Rectangle(x + w/2, y, w/2, h/2)
        self.northeast = QuadTree(ne, self.capacity)

        nw = Rectangle(x, y, w/2, h/2)
        self.northwest = QuadTree(nw, self.capacity)

        se = Rectangle(x + w/2, y + h/2, w/2, h/2)
        self.southeast = QuadTree(se, self.capacity)

        sw = Rectangle(x, y + h/2, w/2, h/2)
        self.southwest = QuadTree(sw, self.capacity)

        self.divided = True

    def query(self, range):
        global count
        found = []

        if not self.boundary.intersects(range):
            return found
        else:
            
            for p in self.points:
                count += 1
                if range.contains(p):
                    found.append(p)
        
        if self.divided:
            found.extend(x for x in self.northwest.query(range) if x not in found)
            found.extend(x for x in self.northeast.query(range) if x not in found)
            found.extend(x for x in self.southwest.query(range) if x not in found)
            found.extend(x for x in self.southeast.query(range) if x not in found)

        return found
###########################


######## PARTICLES ########
class Particle:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.radius = random.randint(6,12)
        self.highlight = False

    def move(self):
        self.x += random.randint(-1, 1)
        self.y += random.randint(-1, 1)

    def render(self, canvas):
        if self.highlight:
            color = (0,255,255)
        else:
            color = (255,255,255)

        pygame.draw.circle(canvas, color, (self.x, self.y), self.radius)

    def intersects(self, other):
        distanceSquared = getDistanceSquaredPointVsPoint((self.x, self.y), (other.x, other.y))
        return (distanceSquared < (self.radius + other.radius)**2)

    def setHighlight(self, value):
        self.highlight = value


def getDistanceSquaredPointVsPoint(p1, p2):
    distanceSquared = (
        (p1[0] - p2[0]) * (p1[0] - p2[0]) + 
        (p1[1] - p2[1]) * (p1[1] - p2[1])
    )
    return distanceSquared
###########################


class QuadTreeVisualisation():
    def __init__(self):
        self.CAPTION = "QUAD TREE VISUALISATION"
        self.SCREEN_WIDTH = int(820)
        self.SCREEN_HEIGHT = int(820)
                         
        boundary = Rectangle(10,10,800,800)
        self.qTree = QuadTree(boundary, 4)
        self.running = True
        for i in range(1000):
            p = Point(random.randint(0,800), random.randint(0,800))
            self.qTree.insert(p)

        self.targetRange = Rectangle(245,245,85,85)

    def run(self):
        pygame.init()
        pygame.display.set_caption(self.CAPTION)
        self.main_screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.DOUBLEBUF)
        self.main_canvas = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        prev_time = time.time()
        delta_time = 0
        clock = pygame.time.Clock()

        while self.running:
            ### GAME TICK ###
            clock.tick_busy_loop(60)

            ### DELTA TIME ###
            now_time = time.time()
            delta_time = now_time - prev_time
            prev_time = now_time

            ##### CALC UPDATES #####
            self.update(delta_time)
          
            ##### DRAW GRAPHICS #####
            self.main_canvas.fill((0,0,0))
            self.draw(self.main_canvas)

            ##### APPLY THE CANVAS TO SCREEN #####
            self.main_screen.blit(self.main_canvas, (0,0))
            pygame.display.update()

    def update(self, deltaTime):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.randomizePoints(1)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.createPoints(event.pos)
                   

            if event.type == pygame.MOUSEMOTION:
                self.targetRange.x = event.pos[0] - self.targetRange.w/2
                self.targetRange.y = event.pos[1] - self.targetRange.h/2
                    
    def randomizePoints(self, howMany):
        for i in range(howMany):
            p = Point(random.randint(0,800), random.randint(0,800))
            self.qTree.insert(p)

    def createPoints(self, mousePos):
        p = Point(mousePos[0], mousePos[1])
        self.qTree.insert(p)

    def draw(self, canvas):
        global count
        points = self.qTree.query(self.targetRange,self)
        print("COUNT: ", count)
        count = 0

        self.drawQTree(self.qTree, canvas)
        pygame.draw.rect(canvas, (0,255,0), (self.targetRange.x, self.targetRange.y, self.targetRange.w, self.targetRange.h), 2)
        for p in points:
            #print(p.x, p.y)
            pygame.draw.circle(self.main_canvas, (0,255,0), (p.x, p.y), 3)
        
    def drawQTree(self, tree, canvas):
        r = pygame.Rect(tree.boundary.x, tree.boundary.y, tree.boundary.w, tree.boundary.h)
        pygame.draw.rect(canvas, (255,255,255), r, 1)
        for p in tree.points:
            pygame.draw.circle(canvas, (255,0,0), (p.x, p.y), 2)

        if tree.divided:
            self.drawQTree(tree.northeast, canvas)
            self.drawQTree(tree.northwest, canvas)
            self.drawQTree(tree.southeast, canvas)
            self.drawQTree(tree.southwest, canvas)


class ParticleSimulation():
    def __init__(self) -> None:
        self.CAPTION = "QUAD TREE VISUALISATION"
        self.SCREEN_WIDTH = int(820)
        self.SCREEN_HEIGHT = int(820)

        self.running = True
        self.FPS = 30
        self.particles = []

        for i in range(500):
            self.particles.append(Particle(random.randint(0, self.SCREEN_WIDTH), random.randint(0, self.SCREEN_HEIGHT)))
            
    def run(self):
        ##### INIT #####
        pygame.init()
        pygame.display.set_caption(self.CAPTION)
        self.main_screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.DOUBLEBUF)
        self.main_canvas = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        ##### FONT #####
        font = pygame.font.SysFont("arial", 20)

        ##### FPS COUNTER #####
        counter = 0
        startTime = time.time()

        ##### DELTATIME #####
        prev_time = time.time()
        delta_time = 0
        clock = pygame.time.Clock()

        ##### GAMELOOP #####
        while self.running:
            ### GAME TICK ###
            clock.tick_busy_loop(self.FPS)

            ### DELTA TIME ###
            now_time = time.time()
            delta_time = now_time - prev_time
            prev_time = now_time

            ##### CALC UPDATES #####
            self.update(delta_time)
          
            ##### DRAW GRAPHICS #####
            self.main_canvas.fill((0,0,0))
            self.draw(self.main_canvas)

            ##### FPS PRINT #####
            counter += 1
            FPS = counter / (time.time() - startTime)
            fpsText = font.render("FPS: " + str(round(FPS, 5)), True, (255,0,0))
            self.main_canvas.blit(fpsText, (10,10))
            counter = 0
            startTime = time.time()

            ##### APPLY THE CANVAS TO SCREEN #####
            self.main_screen.blit(self.main_canvas, (0,0))
            pygame.display.update()

    def update(self, deltaTime):
        ##### INPUT #####
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pass
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pass

            if event.type == pygame.MOUSEMOTION:
                pass

        ##### PARTICLES #####
        # Remake the quadtree each frame to account for movement
        boundary = Rectangle(0,0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.qTree = QuadTree(boundary, 6)

        for p in self.particles:
            point = Point(p.x, p.y, p)
            self.qTree.insert(point)

        ##### QUAD TREE #####
        for p in self.particles:        
            p.move()
            p.setHighlight(False)

            circleRange = Circle(p.x, p.y, 12*2)
            others = self.qTree.query(circleRange)

            for point in others:
                other = point.userData
                if p != other and p.intersects(other):
                    p.setHighlight(True) 
                    #PROJECTILE p COLLIDED WITH THE BALLOON other INSIDE others.

    def draw(self, canvas):
        for p in self.particles:
            p.render(canvas)
        
        




g = ParticleSimulation()
g.run()
pygame.quit()