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


class Chip8:
    def __init__(self):
        self.opcode = 0
        self.v = bytearray(16)

        self.i = 0
        self.pc = 0x200

        self.gfx = [0] * (64 * 32) 

        self.delay_timer = 0
        self.sound_timer = 0

        self.stack = []

        self.key = [0] * 16

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
            self.handle_axxx_opcode
        ]

    def emulate_cycle(self):
        self.opcode = int.from_bytes(self.memory[self.pc:self.pc + 2], byteorder='big')

        self.op_table[self.opcode >> 12]()

        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            print('BEEP\n')
            self.sound_timer -= 1

    def load_game(self, game_file):
        game_data = game_file.read()
        data_len = len(game_data)
        self.memory[512:512 + data_len] = game_data

    def handle_0xxx_opcode(self):
        if self.opcode & 0x000F == 0:
            self.gfx = [0] * (64 * 32) 
        else:
            self.pc = self.stack.pop()
        self.pc += 2

    def handle_1xxx_opcode(self):
        self.pc = self.opcode & 0x0FFF

    def handle_2xxx_opcode(self):
        self.stack.append(self.pc)
        self.pc = self.opcode & 0x0FFF

    def handle_3xxx_opcode(self):
        reg = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        if self.v[reg] == value:
            self.pc += 4
        else:
            self.pc += 2

    def handle_4xxx_opcode(self):
        reg = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        if self.v[reg] != value:
            self.pc += 4
        else:
            self.pc += 2

    def handle_5xxx_opcode(self):
        reg1 = (self.opcode & 0x0f00) >> 8
        reg2 = (self.opcode & 0x00f0) >> 4
        
        if self.v[reg1] == self.v[reg2]:
            self.pc += 4
        else:
            self.pc += 2

    def handle_6xxx_opcode(self):
        reg = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        self.v[reg] = value
        self.pc += 2

    def handle_7xxx_opcode(self):
        reg = (self.opcode & 0x0F00) >> 8
        value = self.opcode & 0x00FF
        self.v[reg] = (self.v[reg] + value) % 256
        self.pc += 2

    def handle_8xxx_opcode(self):
        x_reg = (self.opcode & 0x0F00) >> 8
        y_reg = (self.opcode & 0x00F0) >> 4
        
        x = self.v[x_reg]
        y = self.v[y_reg]
        carry = self.v[0xF]

        (new_x, new_carry) = opcode_8xxx_operations.apply(self.opcode, x, y, carry)

        self.v[x_reg] = new_x
        self.v[0xF] = new_carry

    def handle_9xxx_opcode(self):
        reg1 = (self.opcode & 0x0f00) >> 8
        reg2 = (self.opcode & 0x00f0) >> 4
        
        if self.v[reg1] != self.v[reg2]:
            self.pc += 4
        else:
            self.pc += 2
        
    def handle_axxx_opcode(self):
        self.i = self.opcode & 0x0FFF
        self.pc += 2

