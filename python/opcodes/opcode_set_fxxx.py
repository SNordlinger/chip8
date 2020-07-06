from opcodes.opcode_set import OpcodeSet
from util import get_opcode_digits


class OpcodeSetFxxx(OpcodeSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operation_table = {
            0x07: self.get_delay_timer_fx07,
            0x0A: self.get_key_fx0a,
            0x15: self.set_delay_timer_fx15
        }

    def execute(self, opcode):
        (_, x_reg, _, _) = get_opcode_digits(opcode)
        opcode_end = opcode & 0x00FF
        op = self.operation_table[opcode_end]
        op(x_reg)

    def get_delay_timer_fx07(self, x_reg):
        timer_value = self.timers.delay_timer
        self.registers.v[x_reg] = timer_value
        self.program_counter.next()

    def get_key_fx0a(self, x_reg):
        pressed_keys = self.keypad.pressed_keys()
        if len(pressed_keys) > 0:
            first_pressed = pressed_keys[0]
            self.registers.v[x_reg] = first_pressed
            self.program_counter.next()

    def set_delay_timer_fx15(self, x_reg):
        new_timer_value = self.registers.v[x_reg]
        self.timers.delay_timer = new_timer_value
        self.program_counter.next()
