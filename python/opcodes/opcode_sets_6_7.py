from opcodes.opcode_set import OpcodeSet
from util import get_opcode_digits


class OpcodeSet6xxx(OpcodeSet):
    """
    6XNN: Sets VX to NN
    """
    def execute(self, opcode):
        (_, reg, _, _) = get_opcode_digits(opcode)
        value = opcode & 0x00FF
        self.registers.v[reg] = value
        self.program_counter.next()


class OpcodeSet7xxx(OpcodeSet):
    """
    7XNN: Adds NN to VX
    """
    def execute(self, opcode):
        (_, reg, _, _) = get_opcode_digits(opcode)
        value = opcode & 0x00FF
        self.registers.v[reg] = (self.registers.v[reg] + value) % 256
        self.program_counter.next()
