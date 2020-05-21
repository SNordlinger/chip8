import random
import opcode_8xxx_operations

chip8_fontset = ([
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80  # F
])


class Chip8: # pylint: disable=too-many-instance-attributes
    def __init__(self):
        self.opcode = 0
        self.program_counter = 0x200

        self.stack = []

        # Chip 8 has 15 8-bit registers: V0-VE
        # 16th register is carry flag
        self.v_registers = bytearray(16)

        # Index register
        self.i = 0

        # Graphics memory
        self.gfx = bytearray(64 * 32)

        # Timer registers should count at 60hz
        self.delay_timer = 0
        self.sound_timer = 0

        # State of hex-based keypad
        self.keys = [False] * 16

        # Chip 8 has 4K memory
        # 0x000-0x1FF - Chip 8 interpreter (contains font set in emu)
        # 0x050-0x0A0 - Used for the built in 4x5 pixel font set (0-F)
        # 0x200-0xFFF - Program ROM and work RAM
        self.memory = bytearray(4056)
        self.memory[0:80] = chip8_fontset

        self.op_table = [
            self.handle_0xxx_opcode,
            self.handle_1xxx_opcode,
            self.handle_2xxx_opcode,
            self.handle_3xxx_opcode,
            self.handle_4xxx_opcode,
            self.handle_5xxx_opcode,
            self.handle_6xxx_opcode,
            self.handle_7xxx_opcode,
            self.handle_8xxx_opcode,
            self.handle_9xxx_opcode,
            self.handle_axxx_opcode,
            self.handle_bxxx_opcode,
            self.handle_cxxx_opcode,
            self.handle_dxxx_opcode,
            self.handle_exxx_opcode
        ]

    def emulate_cycle(self):
        self.opcode = int.from_bytes(
            self.memory[self.program_counter:self.program_counter + 2],
            byteorder='big')

        self.op_table[self.opcode >> 12]()

        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            if self.sound_timer == 1:
                print('BEEP\n')
            self.sound_timer -= 1

    def load_game(self, game_file):
        game_data = game_file.read()
        data_len = len(game_data)
        self.memory[512:512 + data_len] = game_data

    def handle_0xxx_opcode(self):
        """
        00E0: Clears the screen
        00EE: Returns from a subroutine
        """
        if self.opcode & 0x000F == 0:
            self.gfx = [0] * (64 * 32)
        else:
            self.program_counter = self.stack.pop()
        self.program_counter += 2

    def handle_1xxx_opcode(self):
        """
        1NNN: Jump to address NNN
        """
        self.program_counter = self.opcode & 0x0FFF

    def handle_2xxx_opcode(self):
        """
        2NNN: Call subroutine as NNN
        """
        self.stack.append(self.program_counter)
        self.program_counter = self.opcode & 0x0FFF

    def handle_3xxx_opcode(self):
        """
        3XNN: Skips next instruction if VX == NN
        """
        reg = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        if self.v_registers[reg] == value:
            self.program_counter += 4
        else:
            self.program_counter += 2

    def handle_4xxx_opcode(self):
        """
        4XNN: Skips next instruction if VX != NN
        """
        reg = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        if self.v_registers[reg] != value:
            self.program_counter += 4
        else:
            self.program_counter += 2

    def handle_5xxx_opcode(self):
        """
        5XY0: Skips next instruction if VX == VY
        """
        reg1 = (self.opcode & 0x0f00) >> 8
        reg2 = (self.opcode & 0x00f0) >> 4

        if self.v_registers[reg1] == self.v_registers[reg2]:
            self.program_counter += 4
        else:
            self.program_counter += 2

    def handle_6xxx_opcode(self):
        """
        6XNN: Sets VX to NN
        """
        reg = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        self.v_registers[reg] = value
        self.program_counter += 2

    def handle_7xxx_opcode(self):
        """
        7XNN: Adds NN to VX
        """
        reg = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        self.v_registers[reg] = (self.v_registers[reg] + value) % 256
        self.program_counter += 2

    def handle_8xxx_opcode(self):
        """
        8XY0 - 8XYE

        Each of the many 8xxx opcodes sets the VX register
        (and sometimes the carry flag) based on the state
        of the VX and VY registers
        """
        x_reg = (self.opcode & 0x0F00) >> 8
        y_reg = (self.opcode & 0x00F0) >> 4

        x_value = self.v_registers[x_reg]
        y_value = self.v_registers[y_reg]
        carry = self.v_registers[0xF]

        new_x_value, new_carry = opcode_8xxx_operations.apply(self.opcode, x_value, y_value, carry)

        self.v_registers[x_reg] = new_x_value
        self.v_registers[0xF] = new_carry

    def handle_9xxx_opcode(self):
        """
        9XY0: Skips next instruction if VX != VY
        """
        reg1 = (self.opcode & 0x0f00) >> 8
        reg2 = (self.opcode & 0x00f0) >> 4

        if self.v_registers[reg1] != self.v_registers[reg2]:
            self.program_counter += 4
        else:
            self.program_counter += 2

    def handle_axxx_opcode(self):
        """
        ANNN: Sets the index register to NNN
        """
        self.i = self.opcode & 0x0FFF
        self.program_counter += 2

    def handle_bxxx_opcode(self):
        """
        BNNN: Jumps to the address NNN + V0
        """
        offset = self.opcode & 0x0FFF
        self.program_counter = self.v_registers[0] + offset

    def handle_cxxx_opcode(self):
        """
        CXNN: Sets VX to the bitwise and NNN and a random number
        """
        reg = (self.opcode & 0x0F00) >> 8
        val = self.opcode & 0x00FF

        self.v_registers[reg] = val & random.randint(0, 255)

    def handle_dxxx_opcode(self):
        """
        DXYN: Draws sprites on the screen

        Draws a sprite of size 8xN at the coordinates read from the
        VX and VY registers
        """
        x_coord = (self.opcode & 0x0F00) >> 8
        y_coord = (self.opcode & 0x00F0) >> 4
        height = self.opcode & 0x000F

        self.v_registers[15] = 0

        for line_num in range(height):
            gfx_loc = x_coord + (y_coord + line_num) * 8
            sprite_line = self.memory[self.i + line_num]
            current_gfx = self.gfx[gfx_loc]
            new_gfx = sprite_line ^ current_gfx
            if new_gfx != sprite_line | current_gfx:
                self.v_registers[15] = 1
            self.gfx[gfx_loc] = new_gfx
        self.program_counter += 2

    def handle_exxx_opcode(self):
        """
        EX9E: Skips next instruction if the key stored in VX is pressed
        EXA1: Skips next instruction if the key stored in VX is not pressed
        """
        opcode_end = (self.opcode & 0x00FF)
        register = (self.opcode & 0x0F00) >> 8
        key_num = self.v_registers[register]
        is_pressed = self.keys[key_num]

        if ((opcode_end == 0x9E and is_pressed)
                or (opcode_end == 0xA1 and not is_pressed)):
            self.program_counter += 4
        else:
            self.program_counter += 2
