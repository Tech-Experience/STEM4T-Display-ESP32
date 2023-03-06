# micropython port based on https://github.com/VolosR/TTGOTetris/blob/main/TTgOTetris.ino
# TETRIS with M5STACK : 2018.01.20 Transplant by macsbug

import random
import utime
import micropython
import st7789
import tft_config
import tft_buttons
from machine import Pin

import gc
gc.collect()

tft = tft_config.config(1, buffer_size=64*64*2)
buttons = tft_buttons.Buttons()

Length = micropython.const(11)     # the number of pixels for a side of a block
Width  = micropython.const(10)     # the number of horizontal blocks
Height = micropython.const(20)     # the number of vertical blocks
screen = [[0 for j in range(Height)] for i in range(Width)]    # it shows color-numbers of all positions
prev_screen = [[0 for j in range(Height)] for i in range(Width)]


class Point():
  def __init__(self, X:int=0, Y:int=0):
    self.X = X
    self.Y = Y
  def __getitem__(self, i):
    return (self.X, self.Y)[i]

class Block():
  def __init__(self, points=[[Point() for i in range(4)] for j in range(4)], numRotate:int=0, color=st7789.WHITE):
    self.square = []
    for rot in range(4):
      rots = []
      for n in range(4):
        rots.append(Point(points[rot][n][0], points[rot][n][1]))
      self.square.append(rots)
    self.numRotate = numRotate
    self.color = color

pos = Point()
block = Block()

rot = 0
fall_cnt = 0
game_over = 0     # timeout before starting a new game
but_LEFT = False
but_RIGHT = False
but_A = False
but_B = False
turbo = False
game_speed_init = 100
game_speed = game_speed_init

# tetrominoes as four points, rotation, color index
blocks = (
  # I straight tetromino "Hero" cyan
  ((((-1,0),(0,0),(1,0),(2,0)),((0,-1),(0,0),(0,1),(0,2)),
  ((0,0),(0,0),(0,0),(0,0)),((0,0),(0,0),(0,0),(0,0))),2,1),
  # O square tetromino "Smashboy" yellow
  ((((0,-1),(1,-1),(0,0),(1,0)),((0,0),(0,0),(0,0),(0,0)),
  ((0,0),(0,0),(0,0),(0,0)),((0,0),(0,0),(0,0),(0,0))),1,2),
  # Z skew tetromino "Cleveland Z" red
  ((((-1,-1),(-1,0),(0,0),(1,0)),((-1,1),(0,1),(0,0),(0,-1)),
  ((-1,0),(0,0),(1,0),(1,1)),((1,-1),(0,-1),(0,0),(0,1))),4,3),
  # S skew tetromino "Rhode Island Z" green
  ((((-1,0),(0,0),(0,1),(1,1)),((0,-1),(0,0),(-1,0),(-1,1)),
  ((0,0),(0,0),(0,0),(0,0)),((0,0),(0,0),(0,0),(0,0))),2,4),
  # J L-tetromino "Blue Ricky" blue
  ((((-1,0),(0,0),(1,0),(1,-1)),((-1,-1),(0,-1),(0,0),(0,1)),
  ((-1,1),(-1,0),(0,0),(1,0)),((0,-1),(0,0),(0,1),(1,1))),4,5),
  # L-tetromino "Orange Ricky" orange
  ((((-1,1),(0,1),(0,0),(1,0)),((0,-1),(0,0),(1,0),(1,1)),
  ((0,0),(0,0),(0,0),(0,0)),((0,0),(0,0),(0,0),(0,0))),2,6),
  # T-tetromino "Teewee" purple
  ((((-1,0),(0,0),(1,0),(0,-1)),((0,-1),(0,0),(0,1),(-1,0)),
  ((-1,0),(0,0),(1,0),(0,1)),((0,-1),(0,0),(0,1),(1,0))),4,7)
)

blockColors=[
    0x18c3,  # dark grey background
    st7789.CYAN,
    st7789.YELLOW,
    st7789.RED,
    st7789.GREEN,
    st7789.BLUE,
    0xec20,  # orange
    0xa014,  # purple
    ]

pom=0
pom2=0
pom3=0
pom4=0

score=0
lvl=1


def DrawFrame():
  global score, lvl
  TD.clear()
  TD.tft.line(11,19,122,19,TMOMAGENTA)
  TD.tft.line(11,19,11,240,TMOMAGENTA)
  TD.tft.line(122,19,122,240,TMOMAGENTA)
  
  TD.typeset("Score: {}".format(score), 0, 0, font=tft_typeset.font1)
  TD.typeset("LVL:{}".format(lvl), 10, 0, font=tft_typeset.font1)


def Draw(refresh=False):
  global screen, prev_screen, blackColors, Height, Width, Length
  for i in range(Width):
    for j in range(Height):
      if screen[i][j] != prev_screen[i][j] or refresh:  
        TD.tft.fill_rect(i * Length + 12, j * Length + 20, Length-1, Length-1, blockColors[screen[i][j]])
        prev_screen[i][j] = screen[i][j]
        ## Draw a little specular highlight
        # if screen[i][j] != 0:
        #   TD.tft.fill_rect(i * Length + Length + 7, j * Length + Length + 5, 2, 2, st7789.WHITE)


def ClearKeys():
  global but_A, but_B, but_LEFT, but_RIGHT
  but_A = False
  but_B = False
  but_LEFT = False
  but_RIGHT = False


def KeyPadLoop() -> bool:
  global pom, pom2, pom3, pom4, but_A, but_B, but_LEFT, but_RIGHT
  # Move left
  if (buttons.left.value() == Pin.DRIVE_0 and buttons.right.value() == Pin.DRIVE_1):
    if (pom == 0):
      pom = 1
      ClearKeys()
      but_LEFT = True
      return True
    else:
      pom = 0
  # Move right
  if(buttons.left.value() == Pin.DRIVE_1 and buttons.right.value() == Pin.DRIVE_0):
    if (pom2 == 0):
      pom2 = 1
      ClearKeys()
      but_RIGHT = True
      return True
    else:
      pom2 = 0
  # Drop faster
  if(buttons.b.value() == Pin.DRIVE_0):
    if (pom3 == 0):
      pom3 = 1
      ClearKeys()
      but_B = True
      return True
    else:
      pom3 = 0
  # Both buttons to rotate
  if (buttons.left.value() == Pin.DRIVE_0 and buttons.right.value() == Pin.DRIVE_0):
    if (pom4==0):
      pom4 = 1
      ClearKeys()
      but_A = True
      return True
    else:
      pom4 = 0
  return False


def PutStartPos():
  global pos, block, blocks, rot, turbo
  pos.X = random.randint(1,7)
  pos.Y = 1
  turbo = False
  randblock = random.randint(0,len(blocks)-1)
  block = Block(blocks[randblock][0],blocks[randblock][1],blocks[randblock][2])
  rot = random.randint(0, block.numRotate-1)


def GameOver():
  global Width, Height, screen
  utime.sleep(1)
  # Cycle colors to blank
  for i in range(Width):
    for j in range(Height):
      if (screen[i][j] != 0):
        screen[i][j] = (screen[i][j] + 1) % 8
  Draw()
  TD.typeset("GAME".format(score), 2, 3, font=tft_typeset.font2, fg=st7789.RED)
  TD.typeset("OVER".format(score), 2, 4, font=tft_typeset.font2, fg=st7789.RED)


def GetNextPosRot(rot):
  global but_LEFT, but_RIGHT, but_A, but_B, turbo, block, pos, fall_cnt, screen
  pnext_pos = Point(pos.X, pos.Y)
  pnext_rot = rot
  fall_cnt = (fall_cnt + 1) % 10
  if (fall_cnt == 0 or turbo):
    pnext_pos.Y += 1
  else:
    if but_LEFT == True:
      but_LEFT = False
      pnext_pos.X -= 1
    elif but_RIGHT == True:
      but_RIGHT = False
      pnext_pos.X += 1
    elif but_A == True:
      but_A = False
      pnext_rot = (rot + block.numRotate - 1) % block.numRotate

  turbo = buttons.b.value() == Pin.DRIVE_0

  return (pnext_pos, pnext_rot)  


def DeleteLine():
  ## Check for completed rows
  global Height, Width, screen, score, lvl, game_speed
  points = 1
  for j in range(Height):
    Delete = True
    for i in range(Width):
      if (screen[i][j] == 0):
        Delete = False
    if (Delete):
      for k in range(j, 0, -1): 
        for i in range(Width):
          screen[i][k] = screen[i][k - 1]  
      score += points
      points *= 2
      lvl = min(int(score / 10.0),10)
      game_speed = game_speed_init - (10 * lvl)
      DrawFrame()
      Draw(refresh=True)
      utime.sleep(0.2)
      
      
def GetSquares(block, pos, rot):
  ## Collision check with boundaries and dropped blocks in screen
  global Height, Width, screen
  squares = [Point() for i in range(4)]
  overlap = False
  for i in range(4):
    p = Point()
    p.X = pos.X + block.square[rot][i].X
    p.Y = pos.Y + block.square[rot][i].Y
    overlap |= p.X < 0 or p.X >= Width or p.Y < 0 or p.Y >= Height or screen[p.X][p.Y] != 0
    squares[i] = p
  return (not bool(overlap), squares)


def ReviseScreen(next_pos, next_rot):
  global pos, rot, block, screen, game_over, score
  for i in range(4):
    screen[pos.X + block.square[rot][i].X][pos.Y + block.square[rot][i].Y] = 0
  (movable, next_squares) = GetSquares(block, next_pos, next_rot)
  if movable:
    for i in range(4):
      screen[next_squares[i].X][next_squares[i].Y] = block.color
    pos = next_pos
    rot = next_rot
  
  else:
    for i in range(4):
      screen[pos.X + block.square[rot][i].X][pos.Y + block.square[rot][i].Y] = block.color
    if (next_pos.Y == pos.Y + 1):
      DeleteLine()
      PutStartPos()
      (movable, next_squares) = GetSquares(block, pos, rot)
      if not movable:
        for i in range(4):
          screen[pos.X + block.square[rot][i].X][pos.Y + block.square[rot][i].Y] = block.color
        game_over = 10
        print(f"Final score: %d" % score)
  if game_over <= 0:
    Draw()

def ResetGame():
  global game_over, game_speed, buttons, Height, Width, score, lvl
  global turbo, screen, pos, block, rot
  ## Reset for new game
  for j in range(Height):
    for i in range(Width):
      screen[i][j] = 0
      prev_screen[i][j] = 0
  game_over = 0
  score = 0
  game_speed = game_speed_init
  lvl = 1
  PutStartPos()
  for i in range(4):
    screen[pos.X + block.square[rot][i].X][pos.Y + block.square[rot][i].Y] = block.color
  DrawFrame()
  Draw(refresh=True)


def setup():
    TD.clear()
    TD.tft.rotation(0)
    TD.tft.fill(TMOMAGENTA)
    
    DrawFrame()
    PutStartPos()
    for i in range(block.numRotate):
      screen[pos.X + block.square[rot][i].X][pos.Y + block.square[rot][i].Y] = block.color
    Draw(refresh=True)


def loop():
  global game_over, buttons, game_speed, turbo, pos, rot
  if game_over > 0:
    GameOver() 
    if (buttons.left.value() == Pin.DRIVE_0) or game_over == 1:
      ResetGame()  # start a new game
    if (buttons.right.value() == Pin.DRIVE_0):
      game_over += 1000  # let user revel in their score a bit longer
    game_over -= 1
    return

  KeyPadLoop()

  if game_over <= 0:
    (next_pos, next_rot) = GetNextPosRot(rot)
    ReviseScreen(next_pos, next_rot)
    gc.collect()
    if not turbo:
      utime.sleep(game_speed / 1000.0)

#========================================================================
# main
#========================================================================
setup()
while True:
  loop()
