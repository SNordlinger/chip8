from dataclasses import dataclass
from memory import Memory
from util import get_opcode_digits
from opcodes.opcode_sets_0_2 import OpcodeSet0xxx, OpcodeSet1xxx, OpcodeSet2xxx
from opcodes.opcode_sets_3_5 import OpcodeSet3xxx, OpcodeSet4xxx, OpcodeSet5xxx
from opcodes.opcode_sets_6_7 import OpcodeSet6xxx, OpcodeSet7xxx
from opcodes.opcode_set_8xxx import OpcodeSet8xxx
from opcodes.opcode_sets_9_b import OpcodeSet9xxx, OpcodeSetAxxx, OpcodeSetBxxx
from opcodes.opcode_sets_c_e import OpcodeSetCxxx, OpcodeSetDxxx, OpcodeSetExxx
from opcodes.opcode_set_fxxx import OpcodeSetFxxx


@dataclass
class Registers:
    v: bytearray = bytearray(16)
    i: int = 0


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

        self.stack = []

        # Chip 8 has 15 8-bit registers: V0-VE
        # 16th register is carry flag
        self.registers = Registers()

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

        self.op_table = [None] * 16
        self.register(0, OpcodeSet0xxx)
        self.register(1, OpcodeSet1xxx)
        self.register(2, OpcodeSet2xxx)
        self.register(3, OpcodeSet3xxx)
        self.register(4, OpcodeSet4xxx)
        self.register(5, OpcodeSet5xxx)
        self.register(6, OpcodeSet6xxx)
        self.register(7, OpcodeSet7xxx)
        self.register(8, OpcodeSet8xxx)
        self.register(9, OpcodeSet9xxx)
        self.register(0xA, OpcodeSetAxxx)
        self.register(0xB, OpcodeSetBxxx)
        self.register(0xC, OpcodeSetCxxx)
        self.register(0xD, OpcodeSetDxxx)
        self.register(0xE, OpcodeSetExxx)
        self.register(0xF, OpcodeSetFxxx)

    def register(self, first_digit, Command):
        command_set = Command(registers=self.registers,
                              timers=self.timers,
                              keypad=self.keys,
                              graphics=self.graphics,
                              program_counter=self.program_counter,
                              stack=self.stack,
                              memory=self.memory)
        self.op_table[first_digit] = command_set

    def emulate_cycle(self):
        opcode = int.from_bytes(self.memory.get(
            self.program_counter.value, 2),
                                     byteorder='big')

        (first_digit, _, _, _) = get_opcode_digits(opcode)
        opcode_set = self.op_table[first_digit]
        opcode_set.execute(opcode)
        self.timers.tick()

    def load_game(self, program_file):
        game_data = program_file.read()
        self.memory.load(game_data)
