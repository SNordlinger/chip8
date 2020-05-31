import random
from opcodes.opcode_set import OpcodeSet
from util import get_opcode_digits


class OpcodeSetCxxx(OpcodeSet):
    """
    CXNN: Sets VX to the bitwise and NNN and a random number
    """
    def execute(self, opcode):
        (_, reg, _, _) = get_opcode_digits(opcode)
        val = opcode & 0x00FF

        self.registers.v[reg] = val & random.randint(0, 255)
        self.program_counter.next()


class OpcodeSetDxxx(OpcodeSet):
    """
    DXYN: Draws sprites on the screen

    Draws a sprite of size 8xN at the coordinates read from the
    VX and VY registers
    """
    def execute(self, opcode):
        (_, x_coord, y_coord, height) = get_opcode_digits(opcode)

        self.registers.v[15] = 0

        for line_num in range(height):
            sprite_line = self.memory.get_byte(self.registers.i + line_num)
            collision = self.graphics.set_sprite_line(x_coord,
                                                      y_coord + line_num,
                                                      sprite_line)
            if collision:
                self.registers.v[15] = 1
        self.program_counter.next()


class OpcodeSetExxx(OpcodeSet):
    """
    EX9E: Skips next instruction if the key stored in VX is pressed
    EXA1: Skips next instruction if the key stored in VX is not pressed
    """
    def execute(self, opcode):
        (_, reg, _, opcode_end) = get_opcode_digits(opcode)
        key_num = self.registers.v[reg]
        is_pressed = self.keypad.is_pressed(key_num)

        if (opcode_end == 0xE):
            self.conditional_skip(is_pressed)
        else:
            self.conditional_skip(not is_pressed)

    def conditional_skip(self, should_skip):
        if should_skip:
            self.program_counter.skip()
        else:
            self.program_counter.next()
