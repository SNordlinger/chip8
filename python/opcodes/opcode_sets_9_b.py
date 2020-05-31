from opcodes.opcode_set import OpcodeSet
from util import get_opcode_digits


class OpcodeSet9xxx(OpcodeSet):
    """
    9XY0: Skips next instruction if VX != VY
    """
    def execute(self, opcode):
        (_, x_reg, y_reg, _) = get_opcode_digits(opcode)

        if self.registers.v[x_reg] != self.registers.v[y_reg]:
            self.program_counter.skip()
        else:
            self.program_counter.next()


class OpcodeSetAxxx(OpcodeSet):
    """
    ANNN: Sets the index register to NNN
    """
    def execute(self, opcode):
        self.registers.i = opcode & 0x0FFF
        self.program_counter.next()


class OpcodeSetBxxx(OpcodeSet):
    """
    BNNN: Jumps to the address NNN + V0
    """
    def execute(self, opcode):
        offset = opcode & 0x0FFF
        self.program_counter.value = self.registers.v[0] + offset
