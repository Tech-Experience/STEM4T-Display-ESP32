# pongs.py
#
# Use common game module "gameESP.py" for ESP8266  or ESP32
# by Billy Cheung  2019 10 26
#
import gc
import sys
gc.collect()
print ("heap: %dkB" % gc.mem_free())
import utime
from utime import sleep_ms
from math import sqrt
# all dislplay, buttons, paddle, sound logics are in gameESP.mpy module
from gameESP import *
g=gameESP()

scores = [0,0]

maxScore = 15
gameOver = False
exitGame = False


class bat(Rect):
  def __init__(self, velocity, up_key, down_key, *args, **kwargs):
    self.velocity = velocity
    self.up_key = up_key
    self.down_key = down_key
    super().__init__(*args, **kwargs)

  def move_bat(self, board_height, bat_HEIGHT, balls):
    g.getBtn()

    if self.up_key == 0  : # use AI
      ballXdiff = 40
      ballY = -1
      for ball in balls :
          if abs(ball.x - self.x) < ballXdiff :
              ballXdiff = abs(ball.x - self.x)
              ballY = ball.y
      if ballY >= 0 :
          # self.y = max(min(ballY - pong.bat_HEIGHT//2 +  g.random(0,pong.bat_HEIGHT//2+1), board_height-pong.bat_HEIGHT),0)
          diffY = ballY - self.y
          if diffY < 0:
              self.y = self.y - 1
          elif diffY > 0:
              self.y = self.y + 1

    elif self.up_key == -1 : # use Paddle
      self.y = int (g.getPaddle() / (1024 / (board_height-pong.bat_HEIGHT)))
      self.y = int (g.getPaddle() / (1024 / (board_height-pong.bat_HEIGHT)))

    elif self.up_key == -2 : # use Paddle 2
      self.y = int (g.getPaddle2() / (1024 / (board_height-pong.bat_HEIGHT)))
    else :
      if g.pressed(self.up_key):
          self.y = max(self.y - self.velocity,0)
      if g.pressed(self.down_key):
          self.y = min(self.y + self.velocity, board_height-pong.bat_HEIGHT)

class Ball(Rect):
    def __init__(self, velocity, *args, **kwargs):
        self.velocity = velocity
        self.angle = 0
        super().__init__(*args, **kwargs)

    def move_ball(self):
        self.x += self.velocity
        self.y += self.angle


class Pong:
    HEIGHT = 135
    WIDTH = 240

    bat_WIDTH = 2
    bat_HEIGHT = 20
    bat_VELOCITY = 3
    bat_COLOR = st7789.WHITE

    BALL_WIDTH = 4
    BALL_VELOCITY = 2
    BALL_ANGLE = 0

    BALL_COLOR = st7789.MAGENTA
    scores = [0,0]
    maxScore = 15
    maxballs = 3
    ballschance = 10

    def init (self, onePlayer, demo, usePaddle):
        # Setup the screen
        global scores
        scores = [0,0]
        # Create the player objects.
        self.bats = []
        self.balls = []

        if demo or onePlayer:
          self.bats.append(bat(  # The left bat, AI
              self.bat_VELOCITY,
              0,
              0,
              0,
              int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
              self.bat_WIDTH,
              self.bat_HEIGHT))
#         elif usePaddle :
#           self.bats.append(bat(  # The left bat, use Paddle
#               self.bat_VELOCITY,
#               -1,
#               -1,
#               0,
#               int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
#               self.bat_WIDTH,
#               self.bat_HEIGHT))

        else:
          self.bats.append(bat(  # The left bat, button controlled
              self.bat_VELOCITY,
              g.btnB,
              g.btnA,
              0,
              int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
              self.bat_WIDTH,
              self.bat_HEIGHT))

        # set up control method for right Bat
        if demo:
          self.bats.append(bat(  # The right bat, AI
              self.bat_VELOCITY,
              0,
              0,
              self.WIDTH - self.bat_WIDTH-1,
              int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
              self.bat_WIDTH,
              self.bat_HEIGHT
              ))
#         elif usePaddle and g.paddle2 :  # only use paddle2 if its present on the boards
#           self.bats.append(bat(      # The right bat, use Paddle
#               self.bat_VELOCITY,
#               -2,
#               -2,
#               self.WIDTH - self.bat_WIDTH-1,
#               int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
#               self.bat_WIDTH,
#               self.bat_HEIGHT))
        else :  # use buttons for the right bat
          self.bats.append(bat(  # The right bat, button controlled
              self.bat_VELOCITY,
              g.btnB,
              g.btnA,
              self.WIDTH - self.bat_WIDTH-1,
              int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
              self.bat_WIDTH,
              self.bat_HEIGHT
              ))

        self.balls.append(Ball(
            self.BALL_VELOCITY,
            int(self.WIDTH / 2 - self.BALL_WIDTH / 2),
            int(self.HEIGHT / 2 - self.BALL_WIDTH / 2),
            self.BALL_WIDTH,
            self.BALL_WIDTH))


    def score(self, player, ball):
      global gameOver
      global scores
      scores[player] += 1
      g.playTone ('g4', 100)

      if len (self.balls) > 1 :
          self.balls.remove(ball)
      else :
          ball.velocity = - ball.velocity
          ball.angle = g.random(0,3) - 2
          ball.x = int(self.WIDTH / 2 - self.BALL_WIDTH / 2)
          ball.y = int(self.HEIGHT / 2 - self.BALL_WIDTH / 2)


      if scores[player] >= maxScore :
        gameOver = True

    def check_ball_hits_wall(self):
      for ball in self.balls:

        if ball.x < 0:
          self.score(1, ball)


        if ball.x > self.WIDTH :
          self.score(0, ball)

        if ball.y > self.HEIGHT - self.BALL_WIDTH or ball.y < 0:
          ball.angle = -ball.angle
          g.display.fill(0)


    def check_ball_hits_bat(self):
      for ball in self.balls:
          for bat in self.bats:
            if ball.colliderect(bat):
                  ball.velocity = -ball.velocity
                  ball.angle = g.random (0,3) - 2
                  g.playTone ('c6', 10)
                  break

    def game_loop(self):
      global gameOver, exitGame, scores
      demoOn = False
      exitGame = False
      while not exitGame:
        if demoOn :
            players = 0
            demo = True
        else :
            players = 1
            demo = False

        onePlayer = True
        usePaddle = False
        gameOver = False

        #menu screen
        while True:
            # g.display.fill(0)
            g.display.text(font, 'Pong', 10, 0, st7789.WHITE)
            g.display.text(font, 'A Start', 10, 16,  st7789.WHITE)
#             if usePaddle :
#                 g.display.text(font, 'U Paddle', 10,32,  st7789.WHITE)
#             else :
#                 g.display.text(font, 'U Button', 10,32,  st7789.WHITE)
            if players == 0 :
                g.display.text(font, 'B AI-Player', 10,48, st7789.WHITE)
            elif players == 1 :
                g.display.text(font, 'B 1-Player', 10,48, st7789.WHITE)
            else :
                g.display.text(font, 'B 2-Player', 10,48, st7789.WHITE)
            g.display.text(font, '  Frame/s {}'.format(g.frameRate), 10,64, st7789.WHITE)
            g.display.text(font, '  Sound FX', 10, 80, st7789.WHITE)
            g.display.rect(100,80, g.max_vol*4+2,6,st7789.WHITE)
            g.display.fill_rect(101,81, g.vol * 4,4,st7789.CYAN)
            # g.display.show()
            sleep_ms(10)
            g.getBtn()
#             if g.setVol() :
#                 pass
#             elif g.pressed (g.btnB) and g.justPressed(g.btnL) :
#                 exitGame = True
#                 gameOver= True
#                 break
            if g.justPressed(g.btnA) or demoOn :
                if players == 0 : # demo
                    onePlayer = False
                    demo = True
                    demoOn = True
                    g.display.fill(0)
                    g.display.text(font, 'DEMO', 5, 0, st7789.WHITE)
                    g.display.text(font, 'B to Stop', 5, 30, st7789.WHITE)
                    # g.display.show()
                    sleep_ms(1000)

                elif players == 1 :
                    onePlayer = True
                    demo = False
                else :
                    onePlayer = False
                    demo = False
                break
#             elif g.justPressed(g.btnU) :
#                 usePaddle =  not usePaddle
            elif g.justPressed(g.btnB) :
                players = (players + 1) % 3
                print("players: %d" % players)
                if not players:
                    demoOn = True

#             elif g.justPressed(g.btnR) :
#                 if g.pressed(g.btnB) :
#                     g.frameRate = g.frameRate - 5 if g.frameRate > 5 else 100
#                 else :
#                     g.frameRate = g.frameRate + 5 if g.frameRate < 100 else 5

        self.init(onePlayer, demo, usePaddle)
        g.display.fill(0)
        
        # Game loop
        while not gameOver:
          g.getBtn()
#           if g.pressed (g.btnB) and g.justReleased(g.btnL) :
#               gameOver = True
#               demoOn = False

          self.check_ball_hits_bat()
          self.check_ball_hits_wall()

          # Redraw the screen.
          # g.display.fill(0)

          for bat in self.bats:
            g.display.fill_rect(bat.x, bat.y, self.bat_WIDTH, self.bat_HEIGHT, st7789.BLACK)
            bat.move_bat(self.HEIGHT, self.bat_HEIGHT,self.balls)
            g.display.fill_rect(bat.x, bat.y, self.bat_WIDTH, self.bat_HEIGHT, self.bat_COLOR)

          for ball in self.balls:
            g.display.fill_rect(ball.x, ball.y, self.BALL_WIDTH, self.BALL_WIDTH, st7789.BLACK)
            ball.move_ball()
            g.display.fill_rect(ball.x, ball.y, self.BALL_WIDTH, self.BALL_WIDTH, self.BALL_COLOR)


          g.display.text (font, '{} : {}'.format (scores[0], scores[1]), 112, 0, st7789.YELLOW)

          if gameOver :
            g.display.fill_rect(125, 25, 80, 30, st7789.RED)
            g.display.text (font, "Game Over", 130, 34, st7789.BLUE, st7789.RED)
            # g.display.show()
            g.playTone ('c5', 200)
            g.playTone ('g4', 200)
            g.playTone ('g4', 200)
            g.playTone ('a4', 200)
            g.playTone ('g4', 400)
            g.playTone ('b4', 200)
            g.playTone ('c5', 400)
          elif len(self.balls) < self.maxballs and g.random(0,10000) < self.ballschance :
                  self.balls.append(Ball(
                      self.BALL_VELOCITY,
                      int(self.WIDTH / 2 - self.BALL_WIDTH / 2),
                      int(self.HEIGHT / 2 - self.BALL_WIDTH / 2),
                      self.BALL_WIDTH,
                      self.BALL_WIDTH))

          g.display_and_wait()


#if __name__ == '__main__':
pong = Pong()
print ("We got a Pong")
pong.game_loop()

if g.ESP32 :
    g.deinit()
    del sys.modules["gameESP"]
gc.collect()

print ("game exit")