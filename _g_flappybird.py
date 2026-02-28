"""
flappybird.py - Flappy Bird using hardware scrolling.
Either button to flap. Uses vscrdef/vscsad for efficient side-scrolling.
"""

import gc
gc.collect()

import random
import utime
import st7789
import tft_config
import vga1_8x16 as font
from machine import Pin

tft = tft_config.config(1)

btn1 = Pin(0, mode=Pin.IN, pull=Pin.PULL_UP)
btn2 = Pin(35, mode=Pin.IN, pull=Pin.PULL_UP)


def main():
    tft.init()
    tft.fill(st7789.BLACK)
    W = tft.width()     # 240
    H = tft.height()    # 135

    TFA = tft_config.TFA  # 40
    BFA = tft_config.BFA  # 40

    # Colors
    GREEN_PIPE = st7789.color565(0, 180, 0)
    GREEN_DARK = st7789.color565(0, 120, 0)
    BROWN = st7789.color565(139, 90, 43)
    GREEN_GND = st7789.color565(0, 200, 0)
    YELLOW = st7789.color565(255, 220, 0)
    ORANGE = st7789.color565(255, 140, 0)
    RED_BEAK = st7789.color565(255, 50, 0)
    DKGRAY = st7789.color565(60, 60, 60)

    # Game constants
    GND_Y = H - 10       # ground starts here
    BIRD_SX = 40          # bird screen x position
    BIRD_W = 10
    BIRD_H = 8
    PIPE_W = 16
    PIPE_SPACE = 80       # distance between pipe centers
    GRAVITY = 0.45
    FLAP_VEL = -3.8
    FRAME_MS = 33         # ~30fps

    def btn_any():
        return btn1.value() == Pin.DRIVE_0 or btn2.value() == Pin.DRIVE_0

    def wait_release():
        while btn_any():
            utime.sleep_ms(20)

    def wait_press():
        while not btn_any():
            utime.sleep_ms(20)

    # ---- Bird drawing ----

    def draw_bird(fb_x, y, erase=False):
        """Draw or erase the bird at framebuffer position fb_x, screen y."""
        if erase:
            for dx in range(BIRD_W):
                tft.vline((fb_x + dx) % W, max(0, y), min(BIRD_H, GND_Y - y), st7789.BLACK)
            return

        by = int(y)
        # Body (yellow) - full 10x8 block first
        for dx in range(BIRD_W):
            col_x = (fb_x + dx) % W
            h = min(BIRD_H, GND_Y - by)
            if h > 0:
                tft.vline(col_x, by, h, YELLOW)

        # Wing stripe (orange) - row 4-5, cols 1-5
        for dx in range(1, 6):
            col_x = (fb_x + dx) % W
            if by + 4 < GND_Y:
                tft.pixel(col_x, by + 4, ORANGE)
            if by + 5 < GND_Y:
                tft.pixel(col_x, by + 5, ORANGE)

        # Eye (white bg + black pupil) at col 7, row 1-2
        ex = (fb_x + 7) % W
        if by + 1 < GND_Y:
            tft.pixel(ex, by + 1, st7789.WHITE)
        if by + 2 < GND_Y:
            tft.pixel(ex, by + 2, st7789.WHITE)
        ex2 = (fb_x + 8) % W
        if by + 1 < GND_Y:
            tft.pixel(ex2, by + 1, st7789.WHITE)
        if by + 2 < GND_Y:
            tft.pixel(ex2, by + 2, st7789.BLACK)

        # Beak (red) at cols 9, row 3-4
        bx = (fb_x + 9) % W
        if by + 3 < GND_Y:
            tft.pixel(bx, by + 3, RED_BEAK)
        if by + 4 < GND_Y:
            tft.pixel(bx, by + 4, RED_BEAK)

    # ---- Column drawing ----

    def draw_column(fb_col, world_x, pipes):
        """Draw one column of the world at framebuffer column fb_col."""
        # Check if this world_x falls within any pipe
        in_pipe = False
        for p in pipes:
            px = p[0]
            if px <= world_x < px + PIPE_W:
                gap_y = p[1]
                gap_h = p[3]
                # Pipe cap edges (first/last 2 cols are darker)
                edge = (world_x - px) < 2 or (world_x - px) >= PIPE_W - 2
                pc = GREEN_DARK if edge else GREEN_PIPE
                # Top pipe
                top_end = gap_y
                if top_end > 0:
                    tft.vline(fb_col, 0, top_end, pc)
                # Gap (sky)
                tft.vline(fb_col, gap_y, gap_h, st7789.BLACK)
                # Bottom pipe
                bot_start = gap_y + gap_h
                bot_h = GND_Y - bot_start
                if bot_h > 0:
                    tft.vline(fb_col, bot_start, bot_h, pc)
                in_pipe = True
                break

        if not in_pipe:
            # Sky
            tft.vline(fb_col, 0, GND_Y, st7789.BLACK)

        # Ground
        tft.vline(fb_col, GND_Y, 1, GREEN_GND)
        tft.vline(fb_col, GND_Y + 1, H - GND_Y - 1, BROWN)

    # ---- Score bar ----

    def score_color(score):
        """Return RGB565 color for score: green->yellow->red."""
        ratio = min(score, 30) / 30.0
        if ratio < 0.5:
            r = int(ratio * 2 * 255)
            g = 255
        else:
            r = 255
            g = int((1 - (ratio - 0.5) * 2) * 255)
        return st7789.color565(r, g, 0)

    def draw_score_bar_full(score):
        """Redraw the full score bar (used after score changes)."""
        c = score_color(score)
        filled = min(score * 4, W)
        for sx in range(filled):
            fb_x = (scroll_pos + sx) % W
            tft.vline(fb_x, 0, 2, c)

    # ---- Title screen ----

    tft.vscrdef(TFA, W, BFA)
    tft.vscsad(TFA)
    tft.fill(st7789.BLACK)

    tft.text(font, 'FLAPPY', 16, 20, YELLOW)
    tft.text(font, 'BIRD', 32, 40, YELLOW)
    tft.fill_rect(10, 62, 100, 2, GREEN_PIPE)
    tft.text(font, 'Press button', 16, 75, st7789.WHITE)
    tft.text(font, 'to flap!', 32, 95, DKGRAY)

    wait_press()
    wait_release()
    utime.sleep_ms(200)

    # ---- Game loop (outer: restart) ----

    while True:
        tft.fill(st7789.BLACK)
        gc.collect()

        # Game state
        scroll_pos = 0
        world_dist = 0  # how many columns we've scrolled total

        bird_y = float(H // 3)
        bird_vy = 0.0

        pipes = []  # [world_x, gap_y, scored, gap_h]
        next_pipe_x = W + 20  # first pipe appears a bit after screen width
        score = 0
        gap_h = 38  # starting gap size

        btn_was_pressed = True  # prevent immediate flap on start

        # Draw initial ground across full screen
        for sx in range(W):
            tft.vline(sx, GND_Y, 1, GREEN_GND)
            tft.vline(sx, GND_Y + 1, H - GND_Y - 1, BROWN)

        tft.vscsad(scroll_pos + TFA)

        # Draw bird at starting position
        bird_fb_x = (scroll_pos + BIRD_SX) % W
        draw_bird(bird_fb_x, int(bird_y))

        # Wait for first flap
        tft.text(font, 'TAP!', (scroll_pos + 90) % W, 60, st7789.WHITE)
        wait_press()
        # Erase TAP text
        for dx in range(32):
            tft.vline(((scroll_pos + 90) % W + dx) % W, 60, 16, st7789.BLACK)
        bird_vy = FLAP_VEL
        btn_was_pressed = True

        alive = True
        while alive:
            t0 = utime.ticks_ms()

            # 1. Read buttons (edge-triggered)
            btn_now = btn_any()
            if btn_now and not btn_was_pressed:
                bird_vy = FLAP_VEL
            btn_was_pressed = btn_now

            # 2. Physics
            bird_vy += GRAVITY
            old_bird_y = int(bird_y)
            bird_y += bird_vy
            new_bird_y = int(bird_y)

            # Ceiling clamp
            if bird_y < 2:
                bird_y = 2.0
                bird_vy = 0.0
                new_bird_y = 2

            # 3. Erase old bird
            old_fb_x = (scroll_pos + BIRD_SX) % W
            draw_bird(old_fb_x, old_bird_y, erase=True)

            # 4. Scroll: advance one column
            new_col = (scroll_pos + W - 1) % W
            world_dist += 1

            # Generate new pipes if needed
            while next_pipe_x <= world_dist + W:
                gy = random.randint(18, GND_Y - gap_h - 10)
                pipes.append([next_pipe_x, gy, False, gap_h])
                next_pipe_x += PIPE_SPACE

            # Draw new rightmost column
            draw_column(new_col, world_dist + W - 1, pipes)

            # Advance scroll
            scroll_pos = (scroll_pos + 1) % W
            tft.vscsad(scroll_pos + TFA)

            # Cull pipes that are fully off the left edge
            while pipes and pipes[0][0] + PIPE_W < world_dist:
                pipes.pop(0)

            # 5. Draw bird at new position
            bird_fb_x = (scroll_pos + BIRD_SX) % W
            draw_bird(bird_fb_x, new_bird_y)

            # 6. Collision detection
            # Ground collision
            if new_bird_y + BIRD_H >= GND_Y:
                alive = False
                break

            # Pipe collision
            bird_world_l = world_dist + BIRD_SX
            bird_world_r = bird_world_l + BIRD_W
            for p in pipes:
                px_l = p[0]
                px_r = px_l + PIPE_W
                if bird_world_r > px_l and bird_world_l < px_r:
                    # Bird overlaps pipe horizontally
                    gap_top = p[1]
                    g_h = p[3]
                    if new_bird_y < gap_top or new_bird_y + BIRD_H > gap_top + g_h:
                        alive = False
                        break

            if not alive:
                break

            # 7. Scoring
            old_score = score
            for p in pipes:
                if not p[2] and p[0] + PIPE_W <= bird_world_l:
                    p[2] = True
                    score += 1
                    # Increase difficulty
                    if score % 5 == 0 and gap_h > 28:
                        gap_h -= 2

            # 8. Score bar - maintain on new column, full redraw on score change
            if score > 0:
                filled = min(score * 4, W)
                # The new column scrolling in: is it within the bar?
                # Screen col 0 is leftmost, bar fills from left
                # new_col in fb space was just drawn; its screen x = W-1
                # We need to draw bar on screen x < filled
                # But since we scroll, just check screen-relative
                # Simpler: always draw bar pixel on the new column if needed
                scr_x_of_new = W - 1
                if scr_x_of_new < filled:
                    tft.vline(new_col, 0, 2, score_color(score))
            if score != old_score:
                draw_score_bar_full(score)

            # 9. Frame rate control
            elapsed = utime.ticks_diff(utime.ticks_ms(), t0)
            if elapsed < FRAME_MS:
                utime.sleep_ms(FRAME_MS - elapsed)

        # ---- Game Over ----
        # Flash bird red
        draw_bird(bird_fb_x, new_bird_y, erase=True)
        utime.sleep_ms(300)

        # Show game over text centered on screen
        # Use fill_rect in scroll-aware coords for background
        cx = (scroll_pos + 40) % W
        # Clear area for text
        for dx in range(160):
            fb_x = (cx + dx) % W
            tft.vline(fb_x, 30, 80, st7789.BLACK)

        tft.text(font, 'GAME OVER', (scroll_pos + 72) % W, 40, st7789.RED)

        sc_str = str(score)
        sx = (scroll_pos + 96) % W
        tft.text(font, 'Score:', (scroll_pos + 64) % W, 65, st7789.WHITE)
        tft.text(font, sc_str, (scroll_pos + 112) % W, 65, YELLOW)

        tft.text(font, 'Press button', (scroll_pos + 56) % W, 95, DKGRAY)

        utime.sleep_ms(500)
        wait_release()
        wait_press()
        wait_release()
        utime.sleep_ms(200)


main()
