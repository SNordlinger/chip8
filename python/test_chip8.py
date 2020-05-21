# pylint: disable=no-self-use,too-few-public-methods

from io import BytesIO
from chip8 import Chip8
import random


class TestOpcode1XXX:
    def test_set_program_counter(self):
        chip = Chip8()
        program = BytesIO(b'\x15\x42')
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.program_counter == 0x0542


class TestOpcode2XXX:
    def test_call_subroutine(self):
        chip = Chip8()
        program = BytesIO(b'\x25\x42')
        chip.load_game(program)

        orig_pc = chip.program_counter
        chip.emulate_cycle()

        assert chip.program_counter == 0x0542
        assert chip.stack.pop() == orig_pc


class TestOpcode3XXX:
    def test_equal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x35\x01')
        chip.load_game(program)

        chip.v_registers[5] = 1
        orig_pc = chip.program_counter
        chip.emulate_cycle()

        assert chip.program_counter == orig_pc + 4

    def test_nonequal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x35\x01')
        chip.load_game(program)

        chip.v_registers[5] = 0
        orig_pc = chip.program_counter
        chip.emulate_cycle()

        assert chip.program_counter == orig_pc + 2


class TestOpcode4XXX:
    def test_equal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x41\x01')
        chip.load_game(program)

        chip.v_registers[1] = 1
        orig_pc = chip.program_counter
        chip.emulate_cycle()

        assert chip.program_counter == orig_pc + 2

    def test_nonequal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x41\x01')
        chip.load_game(program)

        chip.v_registers[1] = 0
        orig_pc = chip.program_counter
        chip.emulate_cycle()

        assert chip.program_counter == orig_pc + 4


class TestOpcode5XXX:
    def test_equal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x50\x10')
        chip.load_game(program)

        chip.v_registers[0] = 1
        chip.v_registers[1] = 1
        orig_pc = chip.program_counter
        chip.emulate_cycle()

        assert chip.program_counter == orig_pc + 4

    def test_nonequal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x50\x10')
        chip.load_game(program)

        chip.v_registers[0] = 0
        chip.v_registers[1] = 1
        orig_pc = chip.program_counter
        chip.emulate_cycle()

        assert chip.program_counter == orig_pc + 2


class TestOpcode6XXX:
    def test_set_v_register(self):
        chip = Chip8()
        program = BytesIO(b'\x67\x42')
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.v_registers[7] == 0x0042


class TestOpcode7XXX:
    def test_add_to_v_register(self):
        chip = Chip8()
        program = BytesIO(b'\x78\x05\x78\xFD')
        chip.load_game(program)

        chip.emulate_cycle()
        assert chip.v_registers[8] == 0x0005

        chip.emulate_cycle()
        assert chip.v_registers[8] == 0x0002


class TestOpcode8XXX:
    def test_assignment(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x40')
        chip.load_game(program)

        chip.v_registers[4] = 1
        chip.v_registers[7] = 0
        chip.emulate_cycle()

        assert chip.v_registers[7] == 1

    def test_bitwise_or(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x41')
        chip.load_game(program)

        chip.v_registers[4] = 0x01
        chip.v_registers[7] = 0x10
        chip.emulate_cycle()

        assert chip.v_registers[7] == 0x11

    def test_bitwise_and(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x42')
        chip.load_game(program)

        chip.v_registers[4] = 0x0F
        chip.v_registers[7] = 0x13
        chip.emulate_cycle()

        assert chip.v_registers[7] == 0x03

    def test_xor(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x43')
        chip.load_game(program)

        chip.v_registers[4] = 0x03
        chip.v_registers[7] = 0x11
        chip.emulate_cycle()

        assert chip.v_registers[7] == 0x12

    def test_addition(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x44\x87\x44')
        chip.load_game(program)

        chip.v_registers[4] = 0x01
        chip.v_registers[7] = 0x10
        chip.emulate_cycle()

        assert chip.v_registers[7] == 0x11
        assert chip.v_registers[0xF] == 0

        chip.v_registers[4] = 0xFF
        chip.emulate_cycle()

        assert chip.v_registers[7] == 0x10
        assert chip.v_registers[0xF] == 1

    def test_sub_x_y(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x45\x87\x45')
        chip.load_game(program)

        chip.v_registers[4] = 0x01
        chip.v_registers[7] = 0x10
        chip.emulate_cycle()

        assert chip.v_registers[7] == 0x0F
        assert chip.v_registers[0xF] == 0

        chip.v_registers[4] = 0x10
        chip.emulate_cycle()

        assert chip.v_registers[7] == 0xFF
        assert chip.v_registers[0xF] == 1

    def test_shift_right(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x46\x87\x46')
        chip.load_game(program)

        chip.v_registers[7] = 2
        chip.emulate_cycle()

        assert chip.v_registers[7] == 1
        assert chip.v_registers[0xF] == 0

        chip.emulate_cycle()

        assert chip.v_registers[7] == 0
        assert chip.v_registers[0xF] == 1

    def test_sub_y_x(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x47\x87\x47')
        chip.load_game(program)

        chip.v_registers[4] = 0x01
        chip.v_registers[7] = 0x10
        chip.emulate_cycle()

        assert chip.v_registers[7] == 0xF1
        assert chip.v_registers[0xF] == 1

        chip.v_registers[4] = 0x20
        chip.v_registers[7] = 0x10
        chip.emulate_cycle()

        assert chip.v_registers[7] == 0x10
        assert chip.v_registers[0xF] == 0

    def test_shift_left(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x4E\x87\x4E')
        chip.load_game(program)

        chip.v_registers[7] = 0x81
        chip.emulate_cycle()

        assert chip.v_registers[7] == 2
        assert chip.v_registers[0xF] == 1

        chip.emulate_cycle()

        assert chip.v_registers[7] == 4
        assert chip.v_registers[0xF] == 0


class TestOpcode9XXX:
    def test_equal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x90\x10')
        chip.load_game(program)

        chip.v_registers[0] = 1
        chip.v_registers[1] = 1
        orig_pc = chip.program_counter
        chip.emulate_cycle()

        assert chip.program_counter == orig_pc + 2

    def test_nonequal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x90\x10')
        chip.load_game(program)

        chip.v_registers[0] = 0
        chip.v_registers[1] = 1
        orig_pc = chip.program_counter
        chip.emulate_cycle()

        assert chip.program_counter == orig_pc + 4


class TestOpcodeAXXX:
    def test_set_index_register(self):
        chip = Chip8()
        program = BytesIO(b'\xA0\x01')
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.i == 1


class TestOpcodeBXXX:
    def test_jump_w_offset(self):
        chip = Chip8()
        program = BytesIO(b'\xB1\x11')
        chip.v_registers[0] = 1
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.program_counter == 0x112

class TestOpcodeCXXX:
    def test_set_random(self):
        chip = Chip8()
        program = BytesIO(b'\xC1\x0D')
        random.seed(2)
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.v_registers[1] == 0xC

class TestOpcodeDXXX:
    def test_display_sprite(self):
        chip = Chip8()
        program = BytesIO(b'\xD2\x33')
        chip.i = 80
        chip.memory[80:83] = b'\x3C\xC3\xFF'
        chip.load_game(program)
        chip.emulate_cycle()

        expected_x = 2
        expected_y = 3
        gfx_line1 = chip.gfx[expected_x + expected_y * 8]
        gfx_line2 = chip.gfx[expected_x + (expected_y + 1) * 8]
        gfx_line3 = chip.gfx[expected_x + (expected_y + 2) * 8]

        assert gfx_line1 == 0x3C
        assert gfx_line2 == 0xC3
        assert gfx_line3 == 0xFF
        assert chip.v_registers[15] == 0

        chip.memory[84] = 0x3C
        chip.load_game(program)
        chip.emulate_cycle()

        gfx_line1 = chip.gfx[expected_x + expected_y * 8]

        assert gfx_line1 == 0x00
        assert chip.v_registers[15] == 1
