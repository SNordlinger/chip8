def get_opcode_digits(opcode):
    first = opcode >> 12
    second = (opcode & 0x0F00) >> 8
    third = (opcode & 0x00F0) >> 4
    fourth = opcode & 0x000F
    return (first, second, third, fourth)
