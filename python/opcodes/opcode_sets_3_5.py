from opcodes.opcode_set import OpcodeSet
from util import get_opcode_digits


class OpcodeSet3xxx(OpcodeSet):
    """
    3XNN: Skips next instruction if VX == NN
    """
    def execute(self, opcode):
        (_, reg, _, _) = get_opcode_digits(opcode)
        value = opcode & 0x00FF
        if self.registers.v[reg] == value:
            self.program_counter.skip()
        else:
            self.program_counter.next()


class OpcodeSet4xxx(OpcodeSet):
    """
    4XNN: Skips next instruction if VX != NN
    """
    def execute(self, opcode):
        (_, reg, _, _) = get_opcode_digits(opcode)
        value = opcode & 0x00FF
        if self.registers.v[reg] != value:
            self.program_counter.skip()
        else:
            self.program_counter.next()


class OpcodeSet5xxx(OpcodeSet):
    """
    5XY0: Skips next instruction if VX == VY
    """
    def execute(self, opcode):
        (_, x_reg, y_reg, _) = get_opcode_digits(opcode)

        if self.registers.v[x_reg] == self.registers.v[y_reg]:
            self.program_counter.skip()
        else:
            self.program_counter.next()
