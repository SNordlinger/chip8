class OpcodeSet:
    def __init__(self, chip8):
        self.program_counter = chip8.program_counter
        self.registers = chip8.registers
        self.timers = chip8.timers
        self.stack = chip8.stack
        self.keypad = chip8.keys
        self.graphics = chip8.graphics
        self.memory = chip8.memory

    def execute(self, opcode):
        raise NotImplementedError
