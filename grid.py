import pygame
import random
from math import sqrt

from typing import Union, List

Cell = Union[bool, List['Cell']]

pygame.init()

WIDTH, HEIGHT = 1000, 1000
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Recursive 4x4 Grid Subdivision (Full only at lowest level)")

BG_COLOR = (50, 50, 50)
GRID_COLOR = (0, 0, 0)
FULL_COLOR = (30, 144, 255)  # Dodger blue

MAX_LEVEL = 7
SUBDIVISION = 2
DIMENSION = 2

point_x = WIDTH // 2
point_y = HEIGHT // 2

POINT_SIZE = 5
MOVE_SPEED = 10

class Node:
    def __init__(self, level: int):
        self.level = level
        self.children = None  # will hold subdivisions if any
        self.generate()

    def debug(self):
        node3 = Node(2)
        node3.children = [False, False, False, False,
                          False, False, False, False,
                          False, False, False, False,
                          True, False, False, False, ]
        node2 = Node(2)
        node2.children = [True, True, False, False,
                          False, False, False, False,
                          False, False, False, False,
                          True, False, False, False, ]
        node1 = Node(1)
        node1.children = [False, False, False, False,
                         False, node3, False, False,
                         False, node3, False, False,
                         False, node2, False, False, ]
        
        node_a = Node(1)
        node_a.children = [False, False, False, False,
                          False, False, False, False,
                          node2, False, False, False,
                          False , False, False, False, ]
        
        node_b = Node(1)
        node_b.children = [node3, False, False, False,
                          False, False, False, False,
                          False, False, False, False,
                          False, False, False, False, ]
        
        self.children = [False, False, False, False,
                         False, False, False, False,
                         False, node_a, False, False,
                         False, node_b, False, False]
        
        
            

    def generate(self):
        """Generate either a full/empty cell or subdivide per child."""
        
        # Always make children array
        self.children = []
        for _ in range(SUBDIVISION ** DIMENSION):
            # Higher chance of subdividing at root level
            if self.level < MAX_LEVEL:
                if random.random() < 0.39:
                    self.children.append(Node(self.level + 1))  # Subdivide further
                else:
                    self.children.append(False)
            elif random.random() < 0.50:
                # Make an empty leaf at max depth
                
                self.children.append(True)
            else:
                self.children.append(False)


    def draw(self, surface, rect: pygame.Rect):
        """Draw this node and any children."""
        w = rect.width / SUBDIVISION
        h = rect.height / SUBDIVISION
        for x in range(SUBDIVISION):
            for y in range(SUBDIVISION):
                cell = self.children[x + y * SUBDIVISION]
                sub_rect = pygame.Rect(
                    rect.x + x * w,
                    rect.y + y * h,
                    w,
                    h
                )
                if isinstance(cell, Node):
                    cell.draw(surface, sub_rect)
                    pygame.draw.rect(surface, GRID_COLOR, sub_rect, 1)
                else:
                    color = FULL_COLOR if cell else BG_COLOR
                    pygame.draw.rect(surface, color, sub_rect)
                
                pygame.draw.rect(surface, GRID_COLOR, sub_rect, 1)

        # Draw grid outline
        pygame.draw.rect(surface, GRID_COLOR, rect, 1)
    
    def get_cell(self, x, y):
        x = int(x)
        y = int(y)
        
        node = self.children[x + y * SUBDIVISION]
        
        return node

    def has_children(self):
        return isinstance(self.children, list)


def dda_init():
            # --- Ray Setup ---
    origin_px = pygame.Vector2(point_x, point_y)
    #origin_px = pygame.Vector2(260, 680)
    mouse_px = pygame.Vector2(pygame.mouse.get_pos())
    #mouse_px = pygame.Vector2(256, 966)
    pygame.draw.circle(SCREEN, (0, 255, 0), origin_px, POINT_SIZE)
    pygame.draw.circle(SCREEN, (255, 0, 0), mouse_px, POINT_SIZE)
    pygame.draw.line(SCREEN, (100, 100, 100), origin_px, mouse_px, 1)
    
    ray_dir = mouse_px - origin_px
    if ray_dir.length() != 0:
        ray_dir = ray_dir.normalize()
        
        # Step direction
    step = pygame.Vector2(
        -1 if ray_dir.x < 0 else 1,
        -1 if ray_dir.y < 0 else 1,
    )

    # Compute ray unit step sizes
    ray_unit_step = pygame.Vector2(
        sqrt(1 + (ray_dir.y / ray_dir.x) ** 2) if ray_dir.x != 0 else float('inf'),
        sqrt(1 + (ray_dir.x / ray_dir.y) ** 2) if ray_dir.y != 0 else float('inf')
    )
    
    low = pygame.math.Vector2(0,0)
    high = pygame.math.Vector2(SUBDIVISION, SUBDIVISION)
    dda_rec(origin_px, origin_px, ray_dir, step, ray_unit_step, low, high, 1, grid)


def dda_rec(old_origin: 'pygame.Vector2',
            origin: 'pygame.Vector2',
            ray_dir: 'pygame.Vector2',
            step: 'pygame.Vector2',
            ray_unit_step: 'pygame.Vector2',
            low: 'pygame.Vector2',
            high: 'pygame.Vector2',
            depth: int,
            node: Node):

    cell_jump = SUBDIVISION ** (depth)
    cell_size = WIDTH / cell_jump
    
            # grid lines check
    origin_grid = origin / cell_size
    map_check = pygame.Vector2(int(origin_grid.x), int(origin_grid.y))
    
    
            # ray init length
    delta = origin_grid - map_check
    ray_length = pygame.Vector2(0, 0)

    if ray_dir.x < 0:
        ray_length.x = delta.x * ray_unit_step.x
    else:
        ray_length.x = (1 - delta.x) * ray_unit_step.x

    if ray_dir.y < 0:
        ray_length.y = delta.y * ray_unit_step.y
    else:
        ray_length.y = (1 - delta.y) * ray_unit_step.y
    
    size_xy = pygame.math.Vector2(SUBDIVISION, SUBDIVISION)
    
    dist = 0
    cell = node.get_cell(map_check.x % SUBDIVISION, map_check.y % SUBDIVISION)
    
    # if no subdivision at map_check then jump to nearest boundary
    if (not isinstance(cell, Node)) or (depth != 1 and old_origin != origin):
        if ray_length.x < ray_length.y:
            map_check.x += step.x
            dist = ray_length.x
            ray_length.x += ray_unit_step.x
        else:
            map_check.y += step.y
            dist = ray_length.y
            ray_length.y += ray_unit_step.y
        epsilon = 0
        if map_check.x < low.x - epsilon or map_check.y < low.y - epsilon or \
           map_check.x >= high.x + epsilon or map_check.y >= high.y:
            return False
    
    max_step_count = SUBDIVISION * 2 - 1
    for _ in range(max_step_count):
        color = (255, 255, 255)
        size = 1
        
        cell = node.get_cell(map_check.x % SUBDIVISION, map_check.y % SUBDIVISION)
        
        if isinstance(cell, Node):
            next_low = map_check * SUBDIVISION
            next_high = next_low + size_xy
            hit = dda_rec(origin, origin + ray_dir * dist * cell_size * 0.999999, ray_dir, step, ray_unit_step, next_low, next_high, depth + 1, cell)
            if hit:
                return True
        elif cell:
            color = (252, 63, 239)
            size = 3
        else:
            pass
        
        pygame.draw.circle(SCREEN, color,
            origin + ray_dir * dist * cell_size,
            size)
        if size == 3:
            return True

        if ray_length.x < ray_length.y:
            map_check.x += step.x
            dist = ray_length.x
            ray_length.x += ray_unit_step.x
        else:
            map_check.y += step.y
            dist = ray_length.y
            ray_length.y += ray_unit_step.y

        epsilon = 0
        if map_check.x < low.x - epsilon or map_check.y < low.y - epsilon or \
           map_check.x >= high.x + epsilon or map_check.y >= high.y:
            return False
    return False


clock = pygame.time.Clock()
running = True

top_grid_size = 4
top_cell_w = WIDTH / top_grid_size
top_cell_h = HEIGHT / top_grid_size

grid = Node(1)
#grid.debug()
b = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


        # --- Movement ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        point_y -= MOVE_SPEED
    if keys[pygame.K_s]:
        point_y += MOVE_SPEED
    if keys[pygame.K_a]:
        point_x -= MOVE_SPEED
    if keys[pygame.K_d]:
        point_x += MOVE_SPEED
    if keys[pygame.K_t]:
        print((point_x, point_y))
        print(pygame.mouse.get_pos())

    # Keep point in bounds
    point_x = max(0, min(WIDTH, point_x))
    point_y = max(0, min(HEIGHT, point_y))

    SCREEN.fill(BG_COLOR)
    
        # Movable point

    rect = pygame.Rect(0,  0, WIDTH, HEIGHT)
    grid.draw(SCREEN, rect)

    depth = 0
    dda_init()
    

    pygame.display.flip()
    clock.tick(30)

pygame.quit()


