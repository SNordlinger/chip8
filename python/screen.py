import itertools
import sdl2.ext

WHITE = sdl2.ext.Color(255, 255, 255)
BLACK = sdl2.ext.Color(0, 0, 0)


class Screen:
    def __init__(self, scaling):
        self.scaling = scaling

        window_width = 64 * scaling
        window_height = 32 * scaling
        self.window = sdl2.ext.Window('Chip-8',
                                      size=(window_width, window_height))

        self.renderer = sdl2.ext.Renderer(self.window, logical_size=(64, 32))

    def show(self):
        self.window.show()

    def clear(self):
        self.renderer.clear()
        self.renderer.present()

    def draw(self, pixels):
        self.renderer.clear()
        pixel_coords = ((px.x, px.y) for px in pixels if px.is_on)
        points = list(itertools.chain.from_iterable(pixel_coords))
        self.renderer.draw_point(points, color=WHITE)

        self.renderer.present()
