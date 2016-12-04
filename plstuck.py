from pymouse import PyMouse
from pykeyboard import PyKeyboard
from pykeyboard import PyKeyboardEvent
import time
import itertools
from operator import itemgetter

import gtk.gdk
"""
w = gtk.gdk.get_default_root_window()
sz = w.get_size()
print "The size of the window is %d x %d" % sz
pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
if (pb != None):
    pb.save("screenshot.png","png")
    print "Screenshot saved to screenshot.png."
else:
    print "Unable to get the screenshot."
"""

mouse = PyMouse()
key = PyKeyboard()

def move((x,y)):
    mouse.move(x,y)

def down((x,y)):
    mouse.press(x,y)

def up((x,y)):
    mouse.release(x,y)

locs = itertools.product(range(5), range(6))
corner=(1029,301)
scale=64
colors =    [ (123, 108, 97) #skull
            , (128,60,53) #red
            , (81, 113, 69)  #green
            , (85,129,152) #blue
            , (140, 108, 62) #yellow
            , (99, 60, 136)  #purple
            ]

colormap = ['s', 'r', 'g', 'b', 'y', 'p']

moves = 0

def getBoardImg():
    global corner
    width = 5*scale
    height = 6*scale
    w = gtk.gdk.get_default_root_window()
    sz = w.get_size()
    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,width, height)
    pb = pb.get_from_drawable(w,w.get_colormap(),corner[0],corner[1],0,0,width, height)
    return pb.get_pixels_array()    

def compareColor(c1, c2):
    error = 0
    for l, r in zip(c1, c2):
        error += (l-r)**2
    return error

def matchColor(color):
    errs = [compareColor(color, x) for x in colors]
    return errs.index(min(errs))

def getOrb(img, pos):
    r = 0
    g = 0
    b = 0
    for x in range(pos[0]*scale,(pos[0]+1)*scale):
        for y in range(pos[1]*scale,(pos[1]+1)*scale):
            p = img[y][x]
            r += p[0]
            g += p[1]
            b += p[2]
    r /= scale*scale
    b /= scale*scale
    g /= scale*scale
    return matchColor((r,g,b))

def getBoard():
    img = getBoardImg()
    result = []

    for y in range(0,6):
        row = [getOrb(img, (x,y)) for x in range(0,5)]
        result.append(row)
    return result

def boardToString(board):
    nboard = []
    for line in board:
        row = [colormap[x] for x in line]
        nboard.append(row)
    return nboard

def printBoard(board, weights = []):
    for i, row in enumerate(boardToString(board)):
        if 5-i >= len(weights):
            print(("{} "*5).format(*row))
        else:
            print(("{} "*5+"  {w}").format(*row, w=colormap[weights[5-i][0]]))
    

def swapBoard(board, start, stop):
    board[start[1]][start[0]] ^= board[stop[1]][stop[0]]
    board[stop[1]][stop[0]] ^= board[start[1]][start[0]]
    board[start[1]][start[0]] ^= board[stop[1]][stop[0]]
    return board

def compareBoard(b1, b2):
    errs = 0
    for x in range(5):
        for y in range(6):
            if b1[y][x] != b2[y][x]:
                errs+=1
    return errs

def coords((x,y)):
    return int(corner[0] + scale*(x+.5)), int(corner[1] + scale*(y+.5))

def swap(board, start, stop, fake=False):
    global moves
    swapBoard(board, start, stop)
    moves += 1
    start = coords(start)
    stop = coords(stop)
    if not fake:
        t = [.08, 0, .05]
        move(start)
        time.sleep(t[0])
        down(start)
        time.sleep(t[1])
        move(stop)
        time.sleep(t[2])
        up(stop)


def moveorb(board, start, stop, fake = False):
    script = []
    x = start[0]
    y = start[1]
    while (x,y) != stop:
        if x < stop[0]:
            script.append(((x, y),(x+1,y)))
            x+=1
        elif x > stop[0]:
            script.append(((x, y),(x-1,y)))
            x-=1
        elif y < stop[1]:
            script.append(((x, y),(x,y+1)))
            y+=1
        elif y > stop[1]:
            script.append(((x, y),(x,y-1)))
            y-=1
        else:
            break
    for a, b in script:
        swap(board, a,b, fake)

def dist(a,b):
    return abs(a[0] - b[0])+abs(a[1]-b[1])

def findColors(board, color, exclude = []):
    clist = []
    for x in range(5):
        for y in range(6):
            if board[y][x] == color and (x,y) not in exclude:
                clist.append((x,y))
    return clist

def colorCenter(board):
    result = []
    for color in range(len(colors)):
        clist = findColors(board, color)
        if len(clist) > 2:
            x = float(sum([a[0] for a in clist]))/len(clist)
            y = float(sum([a[1] for a in clist]))/len(clist)
#            result.append((color, x,y, len(clist) if len(clist) < 5 else 5))
            result.append((color, x,y, len(clist)))
    result = sorted(result, key= lambda x: x[2], reverse=True)
    result = sorted(result, key= itemgetter(3,2), reverse=True)
    return result

def printColors(centers):
    for color, x, y, num in centers:
        print("{} {}".format(colormap[color], num))


def colorToPoint(board, color, pos, exclude):
    clist = []
    if board[pos[1]][pos[0]] == color:
        return 0,0
    for x in range(5):
        for y in range(6):
            if board[y][x] == color and (x,y) not in exclude and y != pos[1]:
                clist.append((x,y))
    if len(clist) == 0:
        return 0,0
    errs = [dist(pos, x) for x in clist]
    best = clist[errs.index(min(errs))]
    return best, pos


def fillRow(board, row, color, lock, fake = False):
    y = row
    for x in range(5)[::-1]:
        start, stop = colorToPoint(board, color, (x, y), lock)
        lock.append((x,y))
#        print(start, stop)
        if start != 0:
            moveorb(board, start, stop, fake)
    return lock

#s, r, g, b, y, p
#0, 1, 2, 3, 4, 5

def doRows(fake = False):
    global moves
    moves = 0
    times = []

    lock = []

    board = getBoard()
    weights = colorCenter(board)
    printColors(weights)
    printBoard(board)

    times.append(time.time())

    for i in range(len(weights)):
        lock = fillRow(board, 5-i, weights[i][0], lock, fake)

    times.append(time.time() - times[-1])

    print("moves: {}".format(moves))
    if not fake:
        print("times: {}".format(times[1:]))
    else:
        print("times: {}".format(moves*.13))
    printBoard(board, weights)
    print("")

    if not fake:
        move(coords((6,0)))
        board2 = getBoard()
        printBoard(board2)
        print("errors: {}\n".format(compareBoard(board, board2)))

class Keyboard(PyKeyboardEvent):

    def __init__(self):
        PyKeyboardEvent.__init__(self)

    def tap(self, keycode, character, press):
        global corner
        if press:
            if keycode == key.function_keys[1]:
                doRows(True)
            if keycode == key.function_keys[2]:
                doRows(False)
            if keycode == key.function_keys[3]:
                corner = mouse.position()
                print("Corner = {}".format(corner))

keyrec = Keyboard()
keyrec.run()

while 1:
    time.sleep(.1)

