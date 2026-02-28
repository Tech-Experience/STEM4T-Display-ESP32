"""
arkanoid.py - Arkanoid game with colorful blocks and powerups.
Left button moves paddle left, right button moves right.
Press both buttons to launch the ball.
"""

import gc
gc.collect()

import random
import utime
import st7789
import tft_config
import vga1_8x16 as font
from machine import Pin

tft = tft_config.config(0, buffer_size=64*64*2)

btn1 = Pin(0, mode=Pin.IN, pull=Pin.PULL_UP)    # left
btn2 = Pin(35, mode=Pin.IN, pull=Pin.PULL_UP)   # right


def main():
    tft.init()
    tft.fill(st7789.BLACK)
    W = tft.width()     # 135
    H = tft.height()    # 240

    # Custom RGB565 colors
    ORANGE = 0xFC00
    PURPLE = 0xA014
    DKGRAY = 0x4208

    # Block row colors (rainbow cycle)
    ROW_COLORS = [
        st7789.RED, ORANGE, st7789.YELLOW, st7789.GREEN,
        st7789.CYAN, st7789.BLUE, PURPLE, st7789.MAGENTA
    ]

    # Powerup types
    PW_WIDE  = 0    # wider paddle
    PW_MULTI = 1    # extra ball
    PW_SLOW  = 2    # slow ball
    PW_LIFE  = 3    # extra life
    PW_COLOR = [st7789.GREEN, st7789.CYAN, st7789.YELLOW, st7789.RED]
    PW_DROP  = 22   # % chance per block destroyed

    # Block grid constants
    BW    = 15      # block width in pixels
    BH    = 7       # block height
    BCOLS = 9       # blocks per row (9 * 15 = 135 = screen width)
    BSTEP = 8       # vertical step between rows (BH + 1px gap)
    BTOP  = 20      # y of first block row

    # Paddle constants
    PAD_H = 3
    PAD_Y = H - 16

    # Ball constant
    BSZ = 3

    # Game state dict (mutable from nested functions)
    g = {
        'score': 0,
        'lives': 3,
        'level': 1,
        'padw': 26,
        'padx': 0,
        'frozen': True,
    }
    g['padx'] = (W - g['padw']) // 2

    balls = []       # list of [x, y, vx, vy] (floats)
    blocks = []      # list of [x, y, color, alive]
    powerups = []    # list of [x, y, type]

    # ---- Drawing helpers ----

    def draw_block(b):
        if b[3]:
            tft.fill_rect(b[0] + 1, b[1], BW - 2, BH, b[2])

    def erase_block(b):
        tft.fill_rect(b[0], b[1], BW, BH + 1, st7789.BLACK)

    def draw_all_blocks():
        for b in blocks:
            draw_block(b)

    def draw_hud():
        tft.fill_rect(0, 0, W, 18, st7789.BLACK)
        tft.text(font, str(g['score']), 2, 1, st7789.WHITE)
        tft.text(font, 'L{}'.format(g['level']), 56, 1, st7789.CYAN)
        for i in range(g['lives']):
            tft.fill_rect(W - 8 - i * 10, 5, 6, 8, st7789.YELLOW)

    def draw_paddle():
        tft.fill_rect(g['padx'], PAD_Y, g['padw'], PAD_H, st7789.WHITE)

    def erase_paddle():
        tft.fill_rect(0, PAD_Y, W, PAD_H, st7789.BLACK)

    def draw_ball(b, color=st7789.WHITE):
        tft.fill_rect(int(b[0]), int(b[1]), BSZ, BSZ, color)

    def draw_powerup(pw, color=None):
        c = color if color is not None else PW_COLOR[pw[2]]
        tft.fill_rect(int(pw[0]), int(pw[1]), 7, 7, c)

    # ---- Level management ----

    def make_blocks():
        blocks.clear()
        rows = min(5 + g['level'] - 1, 10)
        for r in range(rows):
            color = ROW_COLORS[r % len(ROW_COLORS)]
            for c in range(BCOLS):
                blocks.append([c * BW, BTOP + r * BSTEP, color, True])

    def new_ball():
        bx = g['padx'] + g['padw'] // 2 - BSZ // 2
        by = PAD_Y - BSZ - 1
        vx = random.choice([-1.5, -1.0, 1.0, 1.5])
        vy = -(1.5 + g['level'] * 0.15)
        return [float(bx), float(by), vx, vy]

    def start_level():
        tft.fill(st7789.BLACK)
        g['padx'] = (W - g['padw']) // 2
        g['frozen'] = True
        balls.clear()
        powerups.clear()
        make_blocks()
        draw_all_blocks()
        draw_hud()
        balls.append(new_ball())
        draw_paddle()
        draw_ball(balls[0])
        gc.collect()

    def blocks_alive():
        for b in blocks:
            if b[3]:
                return True
        return False

    # ---- Title screen ----

    tft.text(font, 'ARKANOID', 36, 30, st7789.CYAN)
    tft.fill_rect(10, 56, 115, 2, PURPLE)

    tft.text(font, 'L=Left R=Right', 4, 70, st7789.WHITE)
    tft.text(font, 'Both = Launch', 8, 90, st7789.WHITE)

    tft.text(font, 'Powerups:', 28, 120, st7789.YELLOW)
    # Wide
    tft.fill_rect(10, 142, 7, 7, st7789.GREEN)
    tft.text(font, 'Wide', 22, 140, st7789.GREEN)
    # Multi
    tft.fill_rect(10, 160, 7, 7, st7789.CYAN)
    tft.text(font, 'Multi', 22, 158, st7789.CYAN)
    # Slow
    tft.fill_rect(72, 142, 7, 7, st7789.YELLOW)
    tft.text(font, 'Slow', 84, 140, st7789.YELLOW)
    # Life
    tft.fill_rect(72, 160, 7, 7, st7789.RED)
    tft.text(font, 'Life', 84, 158, st7789.RED)

    tft.text(font, 'Press any button', 4, 210, DKGRAY)

    # Wait for a button press to start
    while btn1.value() == Pin.DRIVE_1 and btn2.value() == Pin.DRIVE_1:
        utime.sleep_ms(50)
    utime.sleep_ms(300)  # debounce

    # ---- Start first level ----

    start_level()
    frame_ms = 30  # ~33 fps

    # ---- Main game loop ----

    while True:
        t0 = utime.ticks_ms()

        # Read buttons (same pattern as _g_roids.py)
        b1 = btn1.value()
        b2 = btn2.value()

        # Move paddle
        prev_px = g['padx']

        # Left button only
        if b1 == Pin.DRIVE_0 and b2 == Pin.DRIVE_1:
            g['padx'] = max(0, g['padx'] - 4)

        # Right button only
        if b2 == Pin.DRIVE_0 and b1 == Pin.DRIVE_1:
            g['padx'] = min(W - g['padw'], g['padx'] + 4)

        # Both buttons: launch ball
        if b1 == Pin.DRIVE_0 and b2 == Pin.DRIVE_0:
            if g['frozen']:
                g['frozen'] = False

        if g['padx'] != prev_px:
            erase_paddle()
            draw_paddle()

        # ---- Ball handling ----

        if g['frozen']:
            # Ball sticks to paddle
            draw_ball(balls[0], st7789.BLACK)
            balls[0][0] = float(g['padx'] + g['padw'] // 2 - BSZ // 2)
            balls[0][1] = float(PAD_Y - BSZ - 1)
            draw_ball(balls[0])
        else:
            for ball in list(balls):
                # Erase at old position
                draw_ball(ball, st7789.BLACK)

                # Apply velocity
                ball[0] += ball[2]
                ball[1] += ball[3]
                bx = int(ball[0])
                by = int(ball[1])

                # Left/right wall bounce
                if bx <= 0:
                    ball[0] = 0.0
                    ball[2] = abs(ball[2])
                elif bx + BSZ >= W:
                    ball[0] = float(W - BSZ)
                    ball[2] = -abs(ball[2])

                # Ceiling bounce (below HUD)
                if by <= 18:
                    ball[1] = 18.0
                    ball[3] = abs(ball[3])

                # Paddle collision
                bx = int(ball[0])
                by = int(ball[1])
                px = g['padx']
                pw = g['padw']
                if (ball[3] > 0 and
                    by + BSZ >= PAD_Y and
                    by < PAD_Y + PAD_H and
                    bx + BSZ > px and bx < px + pw):
                    ball[1] = float(PAD_Y - BSZ)
                    # Angle depends on where ball hits paddle
                    hit = (bx + BSZ / 2.0 - px) / pw  # 0.0 to 1.0
                    ball[2] = (hit - 0.5) * 4.0
                    speed = abs(ball[3])
                    ball[3] = -speed
                    # Clamp horizontal speed so ball doesn't go too flat
                    if abs(ball[2]) < 0.3:
                        ball[2] = 0.3 if ball[2] >= 0 else -0.3
                    if abs(ball[2]) > speed * 1.8:
                        ball[2] = speed * 1.8 if ball[2] > 0 else -speed * 1.8

                # Block collision
                bx = int(ball[0])
                by = int(ball[1])
                for blk in blocks:
                    if not blk[3]:
                        continue
                    x1 = blk[0]
                    y1 = blk[1]
                    if (bx + BSZ > x1 and bx < x1 + BW and
                        by + BSZ > y1 and by < y1 + BH):
                        # Destroy block
                        blk[3] = False
                        erase_block(blk)
                        g['score'] += 10
                        draw_hud()

                        # Bounce direction: compare overlap to determine side hit
                        ox = min(bx + BSZ, x1 + BW) - max(bx, x1)
                        oy = min(by + BSZ, y1 + BH) - max(by, y1)
                        if ox < oy:
                            ball[2] = -ball[2]
                        else:
                            ball[3] = -ball[3]

                        # Maybe drop a powerup
                        if random.randint(0, 99) < PW_DROP:
                            pt = random.randint(0, 3)
                            powerups.append([x1 + BW // 2 - 3, y1, pt])

                        break  # one block per frame per ball

                # Ball fell off bottom?
                if int(ball[1]) > H:
                    balls.remove(ball)
                    continue

                # Draw at new position
                draw_ball(ball)

            # All balls lost?
            if not balls:
                g['lives'] -= 1
                draw_hud()
                if g['lives'] <= 0:
                    # Game over
                    tft.fill_rect(8, H // 2 - 10, W - 16, 50, st7789.BLACK)
                    tft.text(font, 'GAME OVER', 20, H // 2, st7789.RED)
                    tft.text(font, 'Score:{}'.format(g['score']),
                             16, H // 2 + 20, st7789.WHITE)
                    utime.sleep(3)
                    # Reset and restart
                    g['score'] = 0
                    g['lives'] = 3
                    g['level'] = 1
                    g['padw'] = 26
                    start_level()
                    # Skip rest of this frame
                    continue
                else:
                    balls.append(new_ball())
                    g['frozen'] = True

        # ---- Update powerups ----

        for pw in list(powerups):
            # Erase old position
            draw_powerup(pw, st7789.BLACK)
            # Fall down
            pw[1] += 1

            ppx = int(pw[0])
            ppy = int(pw[1])

            # Caught by paddle?
            if (ppy + 7 >= PAD_Y and ppy <= PAD_Y + PAD_H and
                ppx + 7 > g['padx'] and ppx < g['padx'] + g['padw']):
                pt = pw[2]
                if pt == PW_WIDE:
                    erase_paddle()
                    g['padw'] = min(g['padw'] + 10, 50)
                    if g['padx'] + g['padw'] > W:
                        g['padx'] = W - g['padw']
                    draw_paddle()
                elif pt == PW_MULTI and balls:
                    ob = balls[0]
                    balls.append([ob[0], ob[1], -ob[2], ob[3]])
                elif pt == PW_SLOW:
                    for b in balls:
                        b[2] *= 0.7
                        b[3] *= 0.7
                        if abs(b[3]) < 1.0:
                            b[3] = -1.0 if b[3] < 0 else 1.0
                elif pt == PW_LIFE:
                    g['lives'] = min(g['lives'] + 1, 5)
                    draw_hud()
                powerups.remove(pw)
                continue

            # Off screen?
            if ppy > H:
                powerups.remove(pw)
                continue

            # Draw at new position
            draw_powerup(pw)

        # ---- Level cleared? ----

        if not blocks_alive():
            g['level'] += 1
            tft.fill(st7789.BLACK)
            tft.text(font, 'LEVEL {}'.format(g['level']),
                     24, H // 2, st7789.GREEN)
            utime.sleep(2)
            start_level()

        # ---- Frame rate control ----

        elapsed = utime.ticks_diff(utime.ticks_ms(), t0)
        if elapsed < frame_ms:
            utime.sleep_ms(frame_ms - elapsed)


main()
