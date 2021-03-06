from dataclasses import dataclass
from memory import Memory
from graphics import Graphics
from util import get_opcode_digits
import opcodes


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

    def pressed_keys(self):
        return [i for i, pressed in enumerate(self.__key_state) if pressed]


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
        self.register_opcodes()

    def register_opcodes(self):
        self.op_table[0] = opcodes.OpcodeSet0xxx(self)
        self.op_table[1] = opcodes.OpcodeSet1xxx(self)
        self.op_table[2] = opcodes.OpcodeSet2xxx(self)
        self.op_table[3] = opcodes.OpcodeSet3xxx(self)
        self.op_table[4] = opcodes.OpcodeSet4xxx(self)
        self.op_table[5] = opcodes.OpcodeSet5xxx(self)
        self.op_table[6] = opcodes.OpcodeSet6xxx(self)
        self.op_table[7] = opcodes.OpcodeSet7xxx(self)
        self.op_table[8] = opcodes.OpcodeSet8xxx(self)
        self.op_table[9] = opcodes.OpcodeSet9xxx(self)
        self.op_table[0xA] = opcodes.OpcodeSetAxxx(self)
        self.op_table[0xB] = opcodes.OpcodeSetBxxx(self)
        self.op_table[0xC] = opcodes.OpcodeSetCxxx(self)
        self.op_table[0xD] = opcodes.OpcodeSetDxxx(self)
        self.op_table[0xE] = opcodes.OpcodeSetExxx(self)
        self.op_table[0xF] = opcodes.OpcodeSetFxxx(self)

    def emulate_cycle(self):
        opcode = int.from_bytes(self.memory.get(self.program_counter.value, 2),
                                byteorder='big')

        (first_digit, _, _, _) = get_opcode_digits(opcode)
        opcode_set = self.op_table[first_digit]
        opcode_set.execute(opcode)
        self.timers.tick()

    def load_game(self, program_file):
        game_data = program_file.read()
        self.memory.load(game_data)
