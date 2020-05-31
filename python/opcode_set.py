class OpcodeSet:
    def __init__(self, program_counter, registers, timers, keypad, graphics,
                 memory):
        self.program_counter = program_counter
        self.registers = registers
        self.timers = timers
        self.keypad = keypad
        self.graphics = graphics
        self.memory = memory

    def execute(self):
        raise NotImplementedError
