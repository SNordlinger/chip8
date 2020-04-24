from io import BytesIO
from chip8 import Chip8

class TestOpcode1XXX:
    def test_set_program_counter(self):
        c = Chip8()
        program = BytesIO(b'\x15\x42')
        c.load_game(program)
        c.emulate_cycle()

        assert c.pc == 0x0542

class TestOpcode2XXX:
    def test_call_subroutine(self):
        c = Chip8()
        program = BytesIO(b'\x25\x42')
        c.load_game(program)

        orig_pc = c.pc
        c.emulate_cycle()

        assert c.pc == 0x0542
        assert c.stack.pop() == orig_pc


class TestOpcode3XXX:
    def test_equal_condition(self):
        c = Chip8()
        program = BytesIO(b'\x35\x01')
        c.load_game(program)

        c.v[5] = 1
        orig_pc = c.pc
        c.emulate_cycle()

        assert c.pc == orig_pc + 4

    def test_nonequal_condition(self):
        c = Chip8()
        program = BytesIO(b'\x35\x01')
        c.load_game(program)

        c.v[5] = 0
        orig_pc = c.pc
        c.emulate_cycle()

        assert c.pc == orig_pc + 2

class TestOpcode4XXX:
    def test_equal_condition(self):
        c = Chip8()
        program = BytesIO(b'\x41\x01')
        c.load_game(program)

        c.v[1] = 1
        orig_pc = c.pc
        c.emulate_cycle()

        assert c.pc == orig_pc + 2

    def test_nonequal_condition(self):
        c = Chip8()
        program = BytesIO(b'\x41\x01')
        c.load_game(program)

        c.v[1] = 0
        orig_pc = c.pc
        c.emulate_cycle()

        assert c.pc == orig_pc + 4

class TestOpcode5XXX:
    def test_equal_condition(self):
        c = Chip8()
        program = BytesIO(b'\x50\x10')
        c.load_game(program)

        c.v[0] = 1
        c.v[1] = 1
        orig_pc = c.pc
        c.emulate_cycle()

        assert c.pc == orig_pc + 4

    def test_nonequal_condition(self):
        c = Chip8()
        program = BytesIO(b'\x50\x10')
        c.load_game(program)

        c.v[0] = 0
        c.v[1] = 1
        orig_pc = c.pc
        c.emulate_cycle()
        
        assert c.pc == orig_pc + 2

class TestOpcode6XXX:
    def test_set_v_register(self):
        c = Chip8()
        program = BytesIO(b'\x67\x42')
        c.load_game(program)
        c.emulate_cycle()

        assert c.v[7] == 0x0042

class TestOpcode7XXX:
    def test_add_to_v_register(self):
        c = Chip8()
        program = BytesIO(b'\x78\x05\x78\xFD')
        c.load_game(program)

        c.emulate_cycle()
        assert c.v[8] == 0x0005
        
        c.emulate_cycle()
        assert c.v[8] == 0x0002

class TestOpcode8XXX:
    def test_assignment(self):
        c = Chip8()
        program = BytesIO(b'\x87\x40')
        c.load_game(program)

        c.v[4] = 1
        c.v[7] = 0
        c.emulate_cycle()

        assert c.v[7] == 1
        
    def test_bitwise_or(self):
        c = Chip8()
        program = BytesIO(b'\x87\x41')
        c.load_game(program)

        c.v[4] = 0x01
        c.v[7] = 0x10
        c.emulate_cycle()

        assert c.v[7] == 0x11

    def test_bitwise_and(self):    
        c = Chip8()
        program = BytesIO(b'\x87\x42')
        c.load_game(program)

        c.v[4] = 0x0F
        c.v[7] = 0x13
        c.emulate_cycle()

        assert c.v[7] == 0x03

    def test_xor(self):
        c = Chip8()
        program = BytesIO(b'\x87\x43')
        c.load_game(program)

        c.v[4] = 0x03
        c.v[7] = 0x11
        c.emulate_cycle()

        assert c.v[7] == 0x12

    def test_addition(self):
        c = Chip8()
        program = BytesIO(b'\x87\x44\x87\x44')
        c.load_game(program)

        c.v[4] = 0x01
        c.v[7] = 0x10
        c.emulate_cycle()

        assert c.v[7] == 0x11
        assert c.v[0xF] == 0

        c.v[4] = 0xFF
        c.emulate_cycle()

        assert c.v[7] == 0x10
        assert c.v[0xF] == 1

    def test_sub_x_y(self):
        c = Chip8()
        program = BytesIO(b'\x87\x45\x87\x45')
        c.load_game(program)

        c.v[4] = 0x01
        c.v[7] = 0x10
        c.emulate_cycle()

        assert c.v[7] == 0x0F
        assert c.v[0xF] == 0

        c.v[4] = 0x10
        c.emulate_cycle()

        assert c.v[7] == 0xFF
        assert c.v[0xF] == 1

    def test_shift_right(self):
        c = Chip8()
        program = BytesIO(b'\x87\x46\x87\x46')
        c.load_game(program)

        c.v[7] = 2
        c.emulate_cycle()

        assert c.v[7] == 1
        assert c.v[0xF] == 0

        c.emulate_cycle()

        assert c.v[7] == 0
        assert c.v[0xF] == 1

    def test_sub_y_x(self):
        c = Chip8()
        program = BytesIO(b'\x87\x47\x87\x47')
        c.load_game(program)

        c.v[4] = 0x01
        c.v[7] = 0x10
        c.emulate_cycle()

        assert c.v[7] == 0xF1
        assert c.v[0xF] == 1

        c.v[4] = 0x20
        c.v[7] = 0x10
        c.emulate_cycle()

        assert c.v[7] == 0x10
        assert c.v[0xF] == 0

    def test_shift_left(self):
        c = Chip8()
        program = BytesIO(b'\x87\x4E\x87\x4E')
        c.load_game(program)

        c.v[7] = 0x81
        c.emulate_cycle()

        assert c.v[7] == 2
        assert c.v[0xF] == 1

        c.emulate_cycle()

        assert c.v[7] == 4
        assert c.v[0xF] == 0

class TestOpcode9XXX:
    def test_equal_condition(self):
        c = Chip8()
        program = BytesIO(b'\x90\x10')
        c.load_game(program)

        c.v[0] = 1
        c.v[1] = 1
        orig_pc = c.pc
        c.emulate_cycle()

        assert c.pc == orig_pc + 2

    def test_nonequal_condition(self):
        c = Chip8()
        program = BytesIO(b'\x90\x10')
        c.load_game(program)

        c.v[0] = 0
        c.v[1] = 1
        orig_pc = c.pc
        c.emulate_cycle()
        
        assert c.pc == orig_pc + 4

class TestOpcodeAXXX:
    def test_set_index_register(self):
        c = Chip8()
        program = BytesIO(b'\xA0\x01')
        c.load_game(program)
        c.emulate_cycle()

        assert c.i == 1

