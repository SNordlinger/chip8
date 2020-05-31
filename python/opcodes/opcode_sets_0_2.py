from opcodes.opcode_set import OpcodeSet


class OpcodeSet0xxx(OpcodeSet):
    """
    00E0: Clears the screen
    00EE: Returns from a subroutine
    """
    def execute(self, opcode):
        if opcode & 0x000F == 0:
            self.clear_screen_00e0
        else:
            self.subroutine_return_00ee

    def clear_screen_00e0(self):
        self.graphics.clear()
        self.program_counter.next()

    def subroutine_return_00ee(self):
        self.program_counter.jump(self.stack.pop())
        self.program_counter.next()


class OpcodeSet1xxx(OpcodeSet):
    """
    1NNN: Jump to address NNN
    """
    def execute(self, opcode):
        address = opcode & 0x0FFF
        self.program_counter.jump(address)


class OpcodeSet2xxx(OpcodeSet):
    """
    2NNN: Call subroutine as NNN
    """
    def execute(self, opcode):
        self.stack.append(self.program_counter.value)
        self.program_counter.jump(opcode & 0x0FFF)
