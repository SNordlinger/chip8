class Graphics:
    def __init__(self):
        self.memory = []
        for y in range(0, 32):
            for x in range(0, 64):
                self.memory.append(Pixel(x, y))

    def set_sprite_line(self, x, y, sprite_data):
        collision = False
        for i in range(8):
            new_pixel_on = sprite_data & (0x80 >> i) != 0
            if new_pixel_on:
                pixel = self.pixel_at(x + i, y)
                is_flipped = pixel.set()
                collision = is_flipped or collision
        return collision

    def get_gfx_state(self, x, y, length):
        gfx_loc = Graphics.__get_memory_loc(x, y)
        pixels = self.memory[gfx_loc:gfx_loc + length]
        return [1 if p.is_on else 0 for p in pixels]

    def clear(self):
        for pixel in self.memory:
            pixel.clear()

    def pixels(self):
        return self.memory

    def pixel_at(self, x, y):
        loc = Graphics.__get_memory_loc(x, y)
        return self.memory[loc]

    def __get_memory_loc(x, y):
        return x + (y * 64)


class Pixel:
    def __init__(self, x, y, is_on=False):
        self.x = x
        self.y = y
        self.is_on = is_on

    def set(self):
        is_flipped = self.is_on
        self.is_on = not self.is_on
        return is_flipped

    def clear(self):
        self.is_on = False
