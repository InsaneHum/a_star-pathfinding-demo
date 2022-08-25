import pygame
from queue import PriorityQueue

WIDTH = 900
WIN = pygame.display.set_mode((WIDTH, WIDTH))  # set up display size
pygame.display.set_caption("A* Path Finding Algorithm")  # set window name

# set up colour value tuples:
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:  # or the nodes that make up the grid
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE  # set the default color of the node to white
        self.neighbours = []  # a list to store the neighbours of the node
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    # check for node state functions
    def is_closed(self):  # check if the node is closed or not
        return self.color == RED

    def is_open(self):  # check if the node is in the open set
        return self.color == GREEN

    def is_barrier(self):  # check if the node is a barrier
        return self.color == BLACK

    def is_start(self):  # check if the node is the start node
        return self.color == ORANGE

    def is_end(self):  # check if the node is the end node
        return self.color == TURQUOISE

    # set node state functions
    def reset(self):  # reset the node to its default state
        self.color = WHITE

    def make_closed(self):  # set the node state to closed
        self.color = RED

    def make_open(self):  # set the node state to open
        self.color = GREEN

    def make_barrier(self):  # set the node as a barrier
        self.color = BLACK

    def make_start(self):  # set the node as the start node
        self.color = ORANGE

    def make_end(self):  # set the node as the end node
        self.color = TURQUOISE

    def make_path(self):  # set the node as a path node
        self.color = PURPLE

    # define draw function that draws the node on the window
    def draw(self, win):  # win = where to draw
        # in pygame (0,0) is the top left corner
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))  # draw rectangle

    def update_neighbours(self, grid):  # check for nodes starting from the start node that are not barriers
        self.neighbours = []

        # check if there is a valid neighbour under the current node and is the neighbour a barrier
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbours.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbours.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbours.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbours.append(grid[self.row][self.col - 1])

    def __lt__(self, other):  # the "less than(<)" dunder method that is called when comparing two nodes
        return False


# define the heuristic(h) function that calculates the distance of the current node and the end node
def h(p1, p2):
    # calculate manhattan distance(find the quickest 'L') between two nodes
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


# define the algorithm function
def algorithm(draw, grid, start, end):
    count = 0  # node count
    open_set = PriorityQueue()  # priority queue will return the minimum element in queue
    open_set.put((0, count, start))  # put the f score, node count and start node in the open set
    came_from = {}  # keep track of previous node
    g_score = {spot: float("inf") for row in grid for spot in row}  # define g score with a value of infinity
    g_score[start] = 0  # g = shortest distance of start node and current node
    f_score = {spot: float("inf") for row in grid for spot in row}  # define f score with a value of infinity
    f_score[start] = h(start.get_pos(), end.get_pos())  # h = predicted distance of current node and end node

    open_set_hash = {start}  # keep track of the items in or not in of the priority queue

    while not open_set.empty():  # the algorithm will run until the open set is empty
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]  # get current node
        open_set_hash.remove(current)  # remove the current node from the hash

        if current == end:  # check if reached end, if so, draw path
            reconstruct_path(came_from, end, draw)  # draw the path
            end.make_end()  # re-write the end node that is written over by path
            start.make_start()
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbour]:  # if neighbour has better g score, update best path
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())

                if neighbour not in open_set_hash:
                    count += 1  # increase node count
                    open_set.put((f_score[neighbour], count, neighbour))  # put the neighbour in the open set
                    open_set_hash.add(neighbour)  # record the node in the hash
                    neighbour.make_open()  # mark the node as open

        draw()

        if current != start:  # if the current node is not the start node, make it close
            current.make_closed()

    return False


# the grid will be a square, so rows = cols
def make_grid(rows, width):  # create the grid (how many rows/width, width of grid)
    grid = []
    gap = width // rows  # calculate width of each node

    for i in range(rows):  # row of the node
        grid.append([])
        for j in range(rows):  # col of the node
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width):  # function that draws the grid lines
    gap = width // rows

    # draw a horizontal line for each row
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))  # window. colour, start point, end point

        # draw a vertical line that separates every grid in that row
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


# define main draw function that draw everything on the window
def draw(win, grid, rows, width):  # window, grid, rows/width, width
    win.fill(WHITE)  # fills the entire screen with one colour

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()  # update the display


# define function that gets the position of the mouse on the grid
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


# define main loop
def main(win, width):
    ROWS = 50  # how many rows/cols you want the grid to be
    grid = make_grid(ROWS, width)  # create the grid

    start = None  # start position
    end = None  # end position

    run = True  # is the main loop running
    started = False  # has the algorithm started yet

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():  # check for every event that has happened(mouse press etc)
            if event.type == pygame.QUIT:  # if the quit(X) button is pressed, terminate the loop
                run = False

            # check if the left mouse button is pressed
            if pygame.mouse.get_pressed()[0]: # the index of the left mouse button is 0
                pos = pygame.mouse.get_pos()  # find where the mouse is on the pygame window
                row, col = get_clicked_pos(pos, ROWS, width)  # translate the position of the mouse into grid position
                spot = grid[row][col]

                if not start and spot != end:  # check if the start node has been assigned yet
                    start = spot
                    start.make_start()  # set the node as the start node

                elif not end and spot != start:  # check if the end node has been assigned yet
                    end = spot
                    end.make_end()  # set the node as the end node

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # the index of the right mouse button is 2
                pos = pygame.mouse.get_pos()  # find where the mouse is on the pygame window
                row, col = get_clicked_pos(pos, ROWS, width)  # translate the position of the mouse into grid position
                spot = grid[row][col]

                spot.reset()  # reset the node to default

                # reset the start and end node
                if spot == start:
                    start = None

                if spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:  # check for pressed key
                if event.key == pygame.K_SPACE and start and end:  # check if the start and end node is registered
                    for row in grid:
                        for spot in row:
                            spot.update_neighbours(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:  # clear the screen if c is pressed
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()  # if the loop is terminated, close the program


main(WIN, WIDTH)
