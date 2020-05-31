from opcode_set import OpcodeSet
from util import get_opcode_digits


class OpcodeSet8XXX(OpcodeSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operation_table = [
            self.assignment_8XX0,
            self.bitwise_or_8XX1,
            self.bitwise_and_8XX2,
            self.xor_8XX3,
            self.addition_8XX4,
            self.sub_x_y_8XX5,
            self.shift_right_8XX6,
            self.sub_y_x_8XX7,
        ]

    def execute(self, opcode):
        (_, x_reg, y_reg, last_hex_digit) = get_opcode_digits(opcode)
        x_value = self.registers.v[x_reg]
        y_value = self.registers.v[y_reg]
        if last_hex_digit == 0x000E:
            op = self.shift_left_8XXE
        else:
            op = self.operation_table[last_hex_digit]
        op(x_reg, x_value, y_value)

    def assignment_8XX0(self, x_reg, x_value, y_value):
        self.registers.v[x_reg] = y_value

    def bitwise_or_8XX1(self, x_reg, x_value, y_value):
        self.registers.v[x_reg] = x_value | y_value

    def bitwise_and_8XX2(self, x_reg, x_value, y_value):
        self.registers.v[x_reg] = x_value & y_value

    def xor_8XX3(self, x_reg, x_value, y_value):
        self.registers.v[x_reg] = x_value ^ y_value

    def addition_8XX4(self, x_reg, x_value, y_value):
        reg_sum = x_value + y_value
        if reg_sum > 255:
            self.registers.v[x_reg] = reg_sum % 256
            self.registers.v[0xF] = 1
        else:
            self.registers.v[x_reg] = reg_sum
            self.registers.v[0xF] = 0

    def sub_x_y_8XX5(self, x_reg, x_value, y_value):
        diff = x_value - y_value
        if diff < 0:
            self.registers.v[x_reg] = 256 + diff
            self.registers.v[0xF] = 1
        else:
            self.registers.v[x_reg] = diff
            self.registers.v[0xF] = 0

    def shift_right_8XX6(self, x_reg, x_value, y_value):
        least_significant_bit = x_value % 2
        self.registers.v[x_reg] = x_value >> 1
        self.registers.v[0xF] = least_significant_bit

    def sub_y_x_8XX7(self, x_reg, x_value, y_value):
        diff = y_value - x_value
        if diff < 0:
            self.registers.v[x_reg] = 256 + diff
            self.registers.v[0xF] = 1
        else:
            self.registers.v[x_reg] = diff
            self.registers.v[0xF] = 0

    def shift_left_8XXE(self, x_reg, x_value, y_value):
        most_significant_bit = x_value >> 7
        self.registers.v[x_reg] = (x_value << 1) % 256
        self.registers.v[0xF] = most_significant_bit


