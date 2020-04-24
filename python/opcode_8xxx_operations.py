def assignment_8XX0(x, y, carry):
    return y, carry

def bitwise_or_8XX1(x, y, carry):
    return x | y, carry

def bitwise_and_8XX2(x, y, carry):
    return x & y, carry

def xor_8XX3(x, y, carry):
    return x ^ y, carry

def addition_8XX4(x, y, carry):
    reg_sum = x + y
    if reg_sum > 255:
        return reg_sum % 256, 1
    return reg_sum, 0

def sub_x_y_8XX5(x, y, carry):
    diff = x - y
    if diff < 0:
        return 256 + diff, 1
    return diff, 0

def shift_right_8XX6(x, y, carry):
    least_significant_bit = x % 2
    return x >> 1, least_significant_bit

def sub_y_x_8XX7(x, y, carry):
    diff = y - x
    if diff < 0:
        return 256 + diff, 1
    return diff, 0

def shift_left_8XXE(x, y, carry):
    most_significant_bit = x >> 7
    return (x << 1) % 256, most_significant_bit

operation_table = [
    assignment_8XX0,
    bitwise_or_8XX1,
    bitwise_and_8XX2,
    xor_8XX3,
    addition_8XX4,
    sub_x_y_8XX5,
    shift_right_8XX6,
    sub_y_x_8XX7,
]

def apply(opcode, x, y, carry):
    last_hex_digit = opcode & 0x000F
    if last_hex_digit == 0x000E:
        op = shift_left_8XXE
    else:
        op = operation_table[last_hex_digit]
    return op(x, y, carry)
