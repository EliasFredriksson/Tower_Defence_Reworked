from typing import List, Tuple
import pygame
import math

##########################################################################################
# Author: Elias Fredriksson
# Created via watching javidx9 collision tutorials on youtube
# His youtube channel: https://www.youtube.com/c/javidx9
#
# USE:
# This is a all purpose basic rect / vector / polygon collisions library for Pygame
# that I made. So it can be reused for future pygame projects.



####################### LINE COLLISION ##################
def isCollidePointVsLine(start: pygame.Vector2, end: pygame.Vector2, point: pygame.Vector2):
    lineLength = math.dist((start.x, start.y), (end.x, end.y))

    dToStart = math.dist((point.x, point.y), (start.x, start.y))
    dToEnd = math.dist((point.x, point.y), (end.x, end.y))

    buffer = 1

    if (dToStart + dToEnd >= lineLength and dToStart+dToEnd <= lineLength+buffer):
        return True
    return False


################################### RECT COLLISSION ################################### 
def isCollidePointVsRect (
    p: pygame.Vector2,
    rect: pygame.Rect
    ):
    if (p.x >= rect.x and p.y >= rect.y and 
        p.x < rect.x + rect.width and p.y < rect.y + rect.height):
        return True

def isCollideRectVsRect (
    r1: pygame.Rect,
    r2: pygame.Rect
    ):
    if (r1.x < r2.x + r2.width and r1.x + r1.width > r2.x and
        r1.y < r2.y + r2.height and r1.y + r1.height > r2.y):
        return True
##########################################################################################



################################### RECT / VECTOR COLLISSION ################################### 
def __helper_vectorVsRect(
    pos: pygame.Vector2,
    velocity: pygame.Vector2,
    target: pygame.Rect
    ):

    contact_point = pygame.Vector2(0,0)
    contact_normal = pygame.Vector2(0,0)


    ############## LINEAR INTERPOLATION ##############
    # t is where along a line we are procent wise.
    # (a value between 0 to 1 
    # (0 = 0% (at the start))
    # (1 = 100% (at the end))

    if velocity.x == 0:
        velocity.x = 0.001
    elif velocity.y == 0:
        velocity.y = 0.001
   

    t_near = pygame.Vector2(target.topleft - pos).elementwise() / velocity
    t_far = pygame.Vector2(target.bottomright - pos).elementwise() / velocity

    if t_near.x > t_far.x:
        t_near.x, t_far.x = t_far.x, t_near.x
    if t_near.y > t_far.y:
        t_near.y, t_far.y = t_far.y, t_near.y

    t_hit_near = float(max(t_near.x, t_near.y))
    t_hit_far = float(min(t_far.x, t_far.y))


    if t_near.x > t_far.y or t_near.y > t_far.x:
        #return [False, t_hit_near, contact_normal]
        return {
            "isTowardsTarget": False,
            "timeHitNear": t_hit_near,
            "timeNear": t_near,
            "contactNormal": contact_normal,
            "contactPoint": contact_point
            }

    

    if t_hit_far < 0:
        #return [False, t_hit_near, contact_normal]
        return {
            "isTowardsTarget": False,
            "timeHitNear": t_hit_near,
            "timeNear": t_near,
            "contactNormal": contact_normal,
            "contactPoint": contact_point
            }

    contact_point = pos + t_hit_near * velocity

    if t_near.x > t_near.y:
        if velocity.x < 0:
            contact_normal = pygame.Vector2(1, 0)
        else:
            contact_normal = pygame.Vector2(-1, 0)
    elif t_near.x < t_near.y:
        if velocity.y < 0:
            contact_normal = pygame.Vector2(0, 1)
        else:
            contact_normal = pygame.Vector2(0, -1)

    #return [True, t_hit_near, contact_normal]
    return {
            "isTowardsTarget": True,
            "timeHitNear": t_hit_near,
            "timeNear": t_near,
            "contactNormal": contact_normal,
            "contactPoint": contact_point
            }

def isCollideVectorVsRect(
    self_pos: pygame.Vector2,
    self_velocity: pygame.Vector2,
    target: pygame.Rect
    ):

    global collision_data

    ### collision_data ###
    ####### KEYS #########
    # "isTowardsTarget"
    # "timeHitNear"
    # "contactNormal"
    # "contactPoint"

    collision_data = __helper_vectorVsRect(self_pos, self_velocity, target)


    if (collision_data.get("isTowardsTarget") and 
        collision_data.get("timeHitNear") < 1 and
        collision_data.get("timeHitNear") > -2):
        return [True, collision_data]
    else:
        return [False, collision_data]
    
def isCollideDynamicRectVsRect(
    self_position: pygame.Vector2,
    self_velocity: pygame.Vector2,
    self_hitbox: pygame.Rect,
    target_hitbox: pygame.Rect,
    delta_time: float
    ):

    if self_velocity.x == 0 and self_velocity.y == 0:
        return [False, None]

    expanded_target_hitbox = pygame.Rect(
        (target_hitbox.x - (self_hitbox.width/2), target_hitbox.y - (self_hitbox.height/2)),
        (target_hitbox.width + self_hitbox.width, target_hitbox.height + self_hitbox.height)
    )

    answer = isCollideVectorVsRect(self_position + (self_hitbox.width / 2, self_hitbox.height / 2), 
                                    self_velocity.elementwise() * delta_time,
                                    expanded_target_hitbox)
    return answer
##########################################################################################




################################### CIRCLE COLLISION ################################### 
class Circle():
    def __init__(self, pos: pygame.Vector2, radius):
        self.pos = pos
        self.radius = radius

def isCollidePointVsCircle(p: pygame.Vector2, c: Circle):
    distance = math.sqrt(
        (p.x - c.pos.x) * (p.x - c.pos.x) + 
        (p.y - c.pos.y) * (p.y - c.pos.y)
    )
    if distance < c.radius:
        return True
    return False

def isCollideCircleVsCircle(c1: Circle, c2: Circle):
    distanceSquared = (
        (c2.pos.x - c1.pos.x) * (c2.pos.x - c1.pos.x) + 
        (c2.pos.y - c1.pos.y) * (c2.pos.y - c1.pos.y)
    )
    if distanceSquared < ((c1.radius + c2.radius)*(c1.radius + c2.radius)):
        return True
    return False
##########################################################################################



################################### POLYGON COLLISSION ################################### 
class Polygon():
    def __init__(self):
        self.points = []                    # Transformed Points
        self.pos = pygame.Vector2           # Position of shape
        self.angle = float                  # Direction of shape
        self.model = []                     # "Model" of shape
        self.overlap = False                # Flag to indicate if overlap has occured

class PolygonHandler():
    def __init__(self, shapes: List[Polygon]):
        self.shapes = shapes
        self.activeShape = 0

        self.LEFT = False
        self.RIGHT = False
        self.UP = False
        self.DOWN = False

        self.ROTATERIGHT = False
        self.ROTATELEFT = False

    def update(self):
        if self.LEFT:
            self.shapes[self.activeShape].pos.x -= 2
        if self.RIGHT:
            self.shapes[self.activeShape].pos.x += 2
        if self.UP:
            self.shapes[self.activeShape].pos.y -= 2
        if self.DOWN:
            self.shapes[self.activeShape].pos.y += 2

        if self.ROTATERIGHT:
            self.shapes[self.activeShape].angle += 0.01
        if self.ROTATELEFT:
            self.shapes[self.activeShape].angle -= 0.01

        for poly in self.shapes:
            for i in range(len(poly.model)):
                poly.points[i] = pygame.Vector2(
                    (poly.model[i].x * math.cos(poly.angle)) - (poly.model[i].y * math.sin(poly.angle)) + poly.pos.x,  #Update xpos
                    (poly.model[i].x * math.sin(poly.angle)) + (poly.model[i].y * math.cos(poly.angle)) + poly.pos.y   #Update ypos
                )
            poly.overlap = False
        
        for poly1 in range(len(self.shapes)):
            #for poly2 in range(poly1 + 1 ,len(self.shapes)) :
            for poly2 in range(len(self.shapes)) :
                #self.shapes[poly1].overlap = self.shapes[poly1].overlap or shapeOverlap_SAT(self.shapes[poly1], self.shapes[poly2])
                if poly1 != poly2:
                    #self.shapes[poly1].overlap = self.shapes[poly1].overlap or shapeOverlap_SAT_STATIC(self.shapes[poly1], self.shapes[poly2])
                    self.shapes[poly1].overlap = shapeOverlap_SAT(self.shapes[poly1], self.shapes[poly2])

    def draw(self, canvas):
        
        for i in range(len(self.shapes)):
            if self.shapes[i].overlap:
                color = (255,0,0)
            else:
                color = (0,0,255)
            
            #Draw the Polygon
            pygame.draw.polygon(canvas, color, self.shapes[i].points, 1)

            #Draw direction
            pygame.draw.line(canvas, color,
                self.shapes[i].points[0],
                self.shapes[i].pos,
            )

            if i == self.activeShape:
                color = (255,255,0)
            else:
                color = (255,0,0)

            #Draw position
            pygame.draw.circle(canvas, color,
                self.shapes[i].pos,
                4
            )

#SAT = Seperated Axis Thereom
def shapeOverlap_SAT(p1: Polygon, p2: Polygon):
    for i in range(2):
        if i == 1:
            p1, p2 = p2, p1
        
        for currentPointIndex in range(len(p1.points)):
            nextPointIndex = (currentPointIndex + 1) % len(p1.points)
            axisProjected = pygame.Vector2(
                -(p1.points[nextPointIndex].y - p1.points[currentPointIndex].y),  #Y axis (They are inverted to give the Normal to the edge)
                p1.points[nextPointIndex].x - p1.points[currentPointIndex].x      #X axis
            )

            # Work out min and max for point 1 (p1)
            min_p1 = math.inf
            max_p1 = -math.inf
            for point in p1.points:
                scalarValue = point.dot(axisProjected)
                min_p1 = min(min_p1, scalarValue)
                max_p1 = max(max_p1, scalarValue)
            
            # Work out min and max for point 2 (p2)
            min_p2 = math.inf
            max_p2 = -math.inf
            for point in p2.points:
                scalarValue = point.dot(axisProjected)
                min_p2 = min(min_p2, scalarValue)
                max_p2 = max(max_p2, scalarValue)

            if not (max_p2 >= min_p1 and max_p1 >= min_p2):
                return False

    return True
##########################################################################################



#################################### THESE ARE FOR POLYGON TESTING ###################################
def addPentagonStatic():
    shape = Polygon()
    shape.pos = pygame.Vector2(400,400)
    shape.angle = 0
    shape.static = True
    shape.rotate = False

    fTheta = math.pi * 2 / 5 #divided by 5 sence a Polygon has 5 sides.
    for i in range(5):
        temp_v = pygame.Vector2(
            30 * math.cos(fTheta * i),
            30 * math.sin(fTheta * i)
        )
        shape.model.append(temp_v)
        shape.points.append(temp_v)
    return shape

def addPentagonMovable():
    shape = Polygon()
    shape.pos = pygame.Vector2(200,450)
    shape.angle = 0
    shape.static = False
    shape.rotate = False

    fTheta = math.pi * 2 / 5 #divided by 5 sence a Polygon has 5 sides.
    for i in range(5):
        temp_v = pygame.Vector2(
            30 * math.cos(fTheta * i),
            30 * math.sin(fTheta * i)
        )
        shape.model.append(temp_v)
        shape.points.append(temp_v)
    return shape

def addTriangle():
    shape = Polygon()
    shape.pos = pygame.Vector2(200,200)
    shape.angle = 0

    shape.static = False
    shape.rotate = False

    fTheta = math.pi * 2 / 3 #divided by 3 sense its a triangle  (2pi / 3)
    for i in range(3):
        temp_v = pygame.Vector2(
            20 * math.cos(fTheta * i),
            20 * math.sin(fTheta * i)
        )
        shape.model.append(temp_v)
        shape.points.append(temp_v)
    
    return shape

def addQuadStatic():
    shape = Polygon()
    shape.pos = pygame.Vector2(300,300)
    shape.angle = 0
    shape.static = True
    shape.rotate = False

    #MODEL
    shape.model.append(pygame.Vector2(-30, -30))
    shape.model.append(pygame.Vector2(-30, 30))
    shape.model.append(pygame.Vector2(30, 30))
    shape.model.append(pygame.Vector2(30, -30))

    #POINTS
    shape.points.append(pygame.Vector2(-30, -30))
    shape.points.append(pygame.Vector2(-30, 30))
    shape.points.append(pygame.Vector2(30, 30))
    shape.points.append(pygame.Vector2(30, -30))

    return shape

def addQuadMovable():
    shape = Polygon()
    shape.pos = pygame.Vector2(400,300)
    shape.angle = 0
    shape.static = False
    shape.rotate = True

    #MODEL
    shape.model.append(pygame.Vector2(-30, -30))
    shape.model.append(pygame.Vector2(-30, 30))
    shape.model.append(pygame.Vector2(30, 30))
    shape.model.append(pygame.Vector2(30, -30))

    #POINTS
    shape.points.append(pygame.Vector2(-30, -30))
    shape.points.append(pygame.Vector2(-30, 30))
    shape.points.append(pygame.Vector2(30, 30))
    shape.points.append(pygame.Vector2(30, -30))

    return shape
##########################################################################################




################################ EXTRA FUNCTIONS ################################
def getDistancePointVsPoint(p1: pygame.Vector2, p2: pygame.Vector2):
    distance = math.sqrt(
        (p1.x - p2.x) * (p1.x - p2.x) + 
        (p1.y - p2.y) * (p1.y - p2.y)
    )
    return distance

def getDistanceSquaredPointVsPoint(p1: pygame.Vector2, p2: pygame.Vector2):
    distanceSquared = (
        (p1.x - p2.x) * (p1.x - p2.x) + 
        (p1.y - p2.y) * (p1.y - p2.y)
    )
    return distanceSquared