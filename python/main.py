from io import BytesIO
import sys
import sdl2
import sdl2.ext
from chip8 import Chip8
from screen import Screen
from graphics import Pixel

SCALING = 20


def draw_graphics(chip8, screen):
    if not chip8.graphics.should_draw:
        return

        screen.clear()
        pixels = chip8.graphics.pixels()
        set_pixels = (px for px in pixels if px.is_on)
        for px in set_pixels:
            screen.draw_pixel(px.x, px.y)


def main():
    sdl2.ext.init()
    screen = Screen(SCALING)
    screen.show()

    chip8 = Chip8()
    program = BytesIO(b'\xD2\x33')
    chip8.registers.i = 80
    chip8.memory.set(80, b'\x3C\xC3\xFF')
    chip8.load_game(program)
    chip8.emulate_cycle()

    screen.draw(chip8.graphics.pixels())

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
    sdl2.ext.quit()
    return 0


if __name__ == '__main__':
    sys.exit(main())
