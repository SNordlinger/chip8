import random
from memory import Memory
import opcode_8xxx_operations


class Keypad:
    def __init__(self):
        self.__key_state = [False] * 16

    def press_key(self, key_num):
        self.__key_state[key_num] = True

    def release_key(self, key_num):
        self.__key_state[key_num] = False

    def is_pressed(self, key_num):
        return self.__key_state[key_num]


class Timers:
    def __init__(self):
        self.delay_timer = 0
        self.sound_timer = 0

    def tick(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            if self.sound_timer == 1:
                print('BEEP\n')
            self.sound_timer -= 1


class Graphics:
    def __init__(self):
        self.memory = [0] * 64 * 32

    def set_sprite_line(self, x, y, sprite_data):
        gfx_loc = Graphics.__get_memory_loc(x, y)
        collision = False
        for i in range(8):
            new_pixel_set = sprite_data & (0x80 >> i) != 0
            old_pixel_set = self.memory[gfx_loc + i] == 1
            if new_pixel_set:
                if old_pixel_set:
                    collision = True
                    self.memory[gfx_loc + i] = 0
                else:
                    self.memory[gfx_loc + i] = 1
        return collision

    def get_gfx_state(self, x, y, length):
        gfx_loc = Graphics.__get_memory_loc(x, y)
        return self.memory[gfx_loc:gfx_loc + length]

    def clear(self):
        self.memory = [0] * 64 * 32

    def __get_memory_loc(x, y):
        return x + (y * 64)


class ProgramCounter:
    def __init__(self):
        self.value = 0x200

    def next(self):
        self.value += 2

    def skip(self):
        self.value += 4

    def jump(self, loc):
        self.value = loc


class Chip8:
    def __init__(self):
        self.program_counter = ProgramCounter()
        self.opcode = 0

        self.stack = []

        # Chip 8 has 15 8-bit registers: V0-VE
        # 16th register is carry flag
        self.v_registers = bytearray(16)

        # Index register
        self.i = 0

        # Graphics memory
        self.graphics = Graphics()

        # Timer registers should count at 60hz
        self.timers = Timers()

        # State of hex-based keypad
        self.keys = Keypad()

        # Chip 8 has 4K memory
        # 0x000-0x1FF - Chip 8 interpreter (contains font set in emu)
        # 0x050-0x0A0 - Used for the built in 4x5 pixel font set (0-F)
        # 0x200-0xFFF - Program ROM and work RAM
        self.memory = Memory()

        self.op_table = [
            self.handle_0xxx_opcode, self.handle_1xxx_opcode,
            self.handle_2xxx_opcode, self.handle_3xxx_opcode,
            self.handle_4xxx_opcode, self.handle_5xxx_opcode,
            self.handle_6xxx_opcode, self.handle_7xxx_opcode,
            self.handle_8xxx_opcode, self.handle_9xxx_opcode,
            self.handle_axxx_opcode, self.handle_bxxx_opcode,
            self.handle_cxxx_opcode, self.handle_dxxx_opcode,
            self.handle_exxx_opcode
        ]

    def emulate_cycle(self):
        self.opcode = int.from_bytes(self.memory.get(self.program_counter.value, 2),
                                     byteorder='big')

        (first_digit, _, _, _) = get_opcode_digits(self.opcode)
        self.op_table[first_digit]()
        self.timers.tick()

    def load_game(self, program_file):
        game_data = program_file.read()
        self.memory.load(game_data)

    def handle_0xxx_opcode(self):
        """
        00E0: Clears the screen
        00EE: Returns from a subroutine
        """
        if self.opcode & 0x000F == 0:
            self.graphics.clear()
        else:
            self.program_counter.jump(self.stack.pop())
        self.program_counter.next()

    def handle_1xxx_opcode(self):
        """
        1NNN: Jump to address NNN
        """
        self.program_counter.jump(self.opcode & 0x0FFF)

    def handle_2xxx_opcode(self):
        """
        2NNN: Call subroutine as NNN
        """
        self.stack.append(self.program_counter.value)
        self.program_counter.jump(self.opcode & 0x0FFF)

    def handle_3xxx_opcode(self):
        """
        3XNN: Skips next instruction if VX == NN
        """
        (_, reg, _, _) = get_opcode_digits(self.opcode)
        value = self.opcode & 0x00FF
        if self.v_registers[reg] == value:
            self.program_counter.skip()
        else:
            self.program_counter.next()

    def handle_4xxx_opcode(self):
        """
        4XNN: Skips next instruction if VX != NN
        """
        (_, reg, _, _) = get_opcode_digits(self.opcode)
        value = self.opcode & 0x00FF
        if self.v_registers[reg] != value:
            self.program_counter.skip()
        else:
            self.program_counter.next()

    def handle_5xxx_opcode(self):
        """
        5XY0: Skips next instruction if VX == VY
        """
        (_, x_reg, y_reg, _) = get_opcode_digits(self.opcode)

        if self.v_registers[x_reg] == self.v_registers[y_reg]:
            self.program_counter.skip()
        else:
            self.program_counter.next()

    def handle_6xxx_opcode(self):
        """
        6XNN: Sets VX to NN
        """
        (_, reg, _, _) = get_opcode_digits(self.opcode)
        value = self.opcode & 0x00FF
        self.v_registers[reg] = value
        self.program_counter.next()

    def handle_7xxx_opcode(self):
        """
        7XNN: Adds NN to VX
        """
        (_, reg, _, _) = get_opcode_digits(self.opcode)
        value = self.opcode & 0x00FF
        self.v_registers[reg] = (self.v_registers[reg] + value) % 256
        self.program_counter.next()

    def handle_8xxx_opcode(self):
        """
        8XY0 - 8XYE

        Each of the many 8xxx opcodes sets the VX register
        (and sometimes the carry flag) based on the state
        of the VX and VY registers
        """
        (_, x_reg, y_reg, _) = get_opcode_digits(self.opcode)

        x_value = self.v_registers[x_reg]
        y_value = self.v_registers[y_reg]
        carry = self.v_registers[0xF]

        new_x_value, new_carry = opcode_8xxx_operations.apply(
            self.opcode, x_value, y_value, carry)

        self.v_registers[x_reg] = new_x_value
        self.v_registers[0xF] = new_carry
        self.program_counter.next()

    def handle_9xxx_opcode(self):
        """
        9XY0: Skips next instruction if VX != VY
        """
        (_, x_reg, y_reg, _) = get_opcode_digits(self.opcode)

        if self.v_registers[x_reg] != self.v_registers[y_reg]:
            self.program_counter.skip()
        else:
            self.program_counter.next()

    def handle_axxx_opcode(self):
        """
        ANNN: Sets the index register to NNN
        """
        self.i = self.opcode & 0x0FFF
        self.program_counter.next()

    def handle_bxxx_opcode(self):
        """
        BNNN: Jumps to the address NNN + V0
        """
        offset = self.opcode & 0x0FFF
        self.program_counter.value = self.v_registers[0] + offset

    def handle_cxxx_opcode(self):
        """
        CXNN: Sets VX to the bitwise and NNN and a random number
        """
        (_, reg, _, _) = get_opcode_digits(self.opcode)
        val = self.opcode & 0x00FF

        self.v_registers[reg] = val & random.randint(0, 255)
        self.program_counter.next()

    def handle_dxxx_opcode(self):
        """
        DXYN: Draws sprites on the screen

        Draws a sprite of size 8xN at the coordinates read from the
        VX and VY registers
        """
        (_, x_coord, y_coord, height) = get_opcode_digits(self.opcode)

        self.v_registers[15] = 0

        for line_num in range(height):
            sprite_line = self.memory.get_byte(self.i + line_num)
            collision = self.graphics.set_sprite_line(x_coord,
                                                      y_coord + line_num,
                                                      sprite_line)
            if collision:
                self.v_registers[15] = 1
        self.program_counter.next()

    def handle_exxx_opcode(self):
        """
        EX9E: Skips next instruction if the key stored in VX is pressed
        EXA1: Skips next instruction if the key stored in VX is not pressed
        """
        opcode_end = (self.opcode & 0x00FF)
        (_, reg, _, _) = get_opcode_digits(self.opcode)
        key_num = self.v_registers[reg]
        is_pressed = self.keys.is_pressed(key_num)

        if ((opcode_end == 0x9E and is_pressed)
                or (opcode_end == 0xA1 and not is_pressed)):
            self.program_counter.skip()
        else:
            self.program_counter.next()


def get_opcode_digits(opcode):
    first = opcode >> 12
    second = (opcode & 0x0F00) >> 8
    third = (opcode & 0x00F0) >> 4
    fourth = opcode & 0x000F
    return (first, second, third, fourth)
