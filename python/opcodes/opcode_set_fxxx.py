from opcodes.opcode_set import OpcodeSet
from util import get_opcode_digits


class OpcodeSetFxxx(OpcodeSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operation_table = {
            0x07: self.set_delay_timer_fx07
        }

    def execute(self, opcode):
        (_, x_reg, _, _) = get_opcode_digits(opcode)
        opcode_end = opcode & 0x00FF
        op = self.operation_table[opcode_end]
        op(x_reg)

    def set_delay_timer_fx07(self, x_reg):
        new_timer_value = self.registers.v[x_reg]
        self.timers.delay_timer = new_timer_value
        self.program_counter.next()
