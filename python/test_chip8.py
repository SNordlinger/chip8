# pylint: disable=no-self-use,too-few-public-methods

import random
from io import BytesIO
from chip8 import Chip8


class TestOpcode0XXX:
    def test_clear_screen(self):
        chip = Chip8()
        test_pixel = chip.graphics.pixel_at(5, 6)
        test_pixel.set()

        program = BytesIO(b'\x00\xE0')
        chip.load_game(program)
        chip.emulate_cycle()

        assert (not test_pixel.is_on)

    def test_return(self):
        chip = Chip8()
        stack_pc = 100
        chip.stack.append(stack_pc)
        program = BytesIO(b'\x00\xEE')
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.program_counter.value == stack_pc + 2


class TestOpcode1XXX:
    def test_set_program_counter(self):
        chip = Chip8()
        program = BytesIO(b'\x15\x42')
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.program_counter.value == 0x0542


class TestOpcode2XXX:
    def test_call_subroutine(self):
        chip = Chip8()
        program = BytesIO(b'\x25\x42')
        chip.load_game(program)

        orig_pc = chip.program_counter.value
        chip.emulate_cycle()

        assert chip.program_counter.value == 0x0542
        assert chip.stack.pop() == orig_pc


class TestOpcode3XXX:
    def test_equal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x35\x01')
        chip.load_game(program)

        chip.registers.v[5] = 1
        orig_pc = chip.program_counter.value
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 4

    def test_nonequal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x35\x01')
        chip.load_game(program)

        chip.registers.v[5] = 0
        orig_pc = chip.program_counter.value
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 2


class TestOpcode4XXX:
    def test_equal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x41\x01')
        chip.load_game(program)

        chip.registers.v[1] = 1
        orig_pc = chip.program_counter.value
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 2

    def test_nonequal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x41\x01')
        chip.load_game(program)

        chip.registers.v[1] = 0
        orig_pc = chip.program_counter.value
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 4


class TestOpcode5XXX:
    def test_equal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x50\x10')
        chip.load_game(program)

        chip.registers.v[0] = 1
        chip.registers.v[1] = 1
        orig_pc = chip.program_counter.value
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 4

    def test_nonequal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x50\x10')
        chip.load_game(program)

        chip.registers.v[0] = 0
        chip.registers.v[1] = 1
        orig_pc = chip.program_counter.value
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 2


class TestOpcode6XXX:
    def test_set_v_register(self):
        chip = Chip8()
        program = BytesIO(b'\x67\x42')
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.registers.v[7] == 0x0042


class TestOpcode7XXX:
    def test_add_to_v_register(self):
        chip = Chip8()
        program = BytesIO(b'\x78\x05\x78\xFD')
        chip.load_game(program)

        chip.emulate_cycle()
        assert chip.registers.v[8] == 0x0005

        chip.emulate_cycle()
        assert chip.registers.v[8] == 0x0002


class TestOpcode8XXX:
    def test_assignment(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x40')
        chip.load_game(program)

        chip.registers.v[4] = 1
        chip.registers.v[7] = 0
        chip.emulate_cycle()

        assert chip.registers.v[7] == 1

    def test_bitwise_or(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x41')
        chip.load_game(program)

        chip.registers.v[4] = 0x01
        chip.registers.v[7] = 0x10
        chip.emulate_cycle()

        assert chip.registers.v[7] == 0x11

    def test_bitwise_and(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x42')
        chip.load_game(program)

        chip.registers.v[4] = 0x0F
        chip.registers.v[7] = 0x13
        chip.emulate_cycle()

        assert chip.registers.v[7] == 0x03

    def test_xor(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x43')
        chip.load_game(program)

        chip.registers.v[4] = 0x03
        chip.registers.v[7] = 0x11
        chip.emulate_cycle()

        assert chip.registers.v[7] == 0x12

    def test_addition(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x44\x87\x44')
        chip.load_game(program)

        chip.registers.v[4] = 0x01
        chip.registers.v[7] = 0x10
        chip.emulate_cycle()

        assert chip.registers.v[7] == 0x11
        assert chip.registers.v[0xF] == 0

        chip.registers.v[4] = 0xFF
        chip.emulate_cycle()

        assert chip.registers.v[7] == 0x10
        assert chip.registers.v[0xF] == 1

    def test_sub_x_y(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x45\x87\x45')
        chip.load_game(program)

        chip.registers.v[4] = 0x01
        chip.registers.v[7] = 0x10
        chip.emulate_cycle()

        assert chip.registers.v[7] == 0x0F
        assert chip.registers.v[0xF] == 0

        chip.registers.v[4] = 0x10
        chip.emulate_cycle()

        assert chip.registers.v[7] == 0xFF
        assert chip.registers.v[0xF] == 1

    def test_shift_right(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x46\x87\x46')
        chip.load_game(program)

        chip.registers.v[7] = 2
        chip.emulate_cycle()

        assert chip.registers.v[7] == 1
        assert chip.registers.v[0xF] == 0

        chip.emulate_cycle()

        assert chip.registers.v[7] == 0
        assert chip.registers.v[0xF] == 1

    def test_sub_y_x(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x47\x87\x47')
        chip.load_game(program)

        chip.registers.v[4] = 0x01
        chip.registers.v[7] = 0x10
        chip.emulate_cycle()

        assert chip.registers.v[7] == 0xF1
        assert chip.registers.v[0xF] == 1

        chip.registers.v[4] = 0x20
        chip.registers.v[7] = 0x10
        chip.emulate_cycle()

        assert chip.registers.v[7] == 0x10
        assert chip.registers.v[0xF] == 0

    def test_shift_left(self):
        chip = Chip8()
        program = BytesIO(b'\x87\x4E\x87\x4E')
        chip.load_game(program)

        chip.registers.v[7] = 0x81
        chip.emulate_cycle()

        assert chip.registers.v[7] == 2
        assert chip.registers.v[0xF] == 1

        chip.emulate_cycle()

        assert chip.registers.v[7] == 4
        assert chip.registers.v[0xF] == 0


class TestOpcode9XXX:
    def test_equal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x90\x10')
        chip.load_game(program)

        chip.registers.v[0] = 1
        chip.registers.v[1] = 1
        orig_pc = chip.program_counter.value
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 2

    def test_nonequal_condition(self):
        chip = Chip8()
        program = BytesIO(b'\x90\x10')
        chip.load_game(program)

        chip.registers.v[0] = 0
        chip.registers.v[1] = 1
        orig_pc = chip.program_counter.value
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 4


class TestOpcodeAXXX:
    def test_set_index_register(self):
        chip = Chip8()
        program = BytesIO(b'\xA0\x01')
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.registers.i == 1


class TestOpcodeBXXX:
    def test_jump_w_offset(self):
        chip = Chip8()
        program = BytesIO(b'\xB1\x11')
        chip.registers.v[0] = 1
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.program_counter.value == 0x112


class TestOpcodeCXXX:
    def test_set_random(self):
        chip = Chip8()
        program = BytesIO(b'\xC1\x0D')
        random.seed(2)
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.registers.v[1] == 0xC


class TestOpcodeDXXX:
    def test_display_sprite(self):
        chip = Chip8()
        program = BytesIO(b'\xD2\x33\xD2\x31')
        chip.registers.i = 80
        chip.memory.set(80, b'\x3C\xC3\xFF')
        chip.load_game(program)
        chip.emulate_cycle()

        gfx_line1 = chip.graphics.get_gfx_state(2, 3, 8)
        gfx_line2 = chip.graphics.get_gfx_state(2, 4, 8)
        gfx_line3 = chip.graphics.get_gfx_state(2, 5, 8)

        assert gfx_line1 == [0, 0, 1, 1, 1, 1, 0, 0]
        assert gfx_line2 == [1, 1, 0, 0, 0, 0, 1, 1]
        assert gfx_line3 == [1, 1, 1, 1, 1, 1, 1, 1]
        assert chip.registers.v[15] == 0

        chip.memory.set_byte(84, 0x24)
        chip.registers.i = 84
        chip.emulate_cycle()

        gfx_line1 = chip.graphics.get_gfx_state(2, 3, 8)

        assert gfx_line1 == [0, 0, 0, 1, 1, 0, 0, 0]
        assert chip.registers.v[15] == 1


class TestOpcodeEXXX:
    def test_jump_when_key_pressed(self):
        chip = Chip8()
        program = BytesIO(b'\xE2\x9E\xE2\x9E')
        chip.registers.v[2] = 5
        chip.keys.release_key(5)
        orig_pc = chip.program_counter.value
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 2

        chip.keys.press_key(5)
        orig_pc = chip.program_counter.value
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 4

    def test_jump_when_key_not_pressed(self):
        chip = Chip8()
        program = BytesIO(b'\xE2\xA1\xE2\xA1')
        chip.registers.v[2] = 5
        chip.keys.press_key(5)
        orig_pc = chip.program_counter.value
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 2

        chip.keys.release_key(5)
        orig_pc = chip.program_counter.value
        chip.emulate_cycle()

        assert chip.program_counter.value == orig_pc + 4


class TestOpcodeFxxx:
    def test_get_delay_timer(self):
        chip = Chip8()
        program = BytesIO(b'\xF6\x07')
        chip.timers.delay_timer = 7
        orig_pc = chip.program_counter.value
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.registers.v[6] == 7
        assert chip.program_counter.value == orig_pc + 2

    def test_get_key(self):
        chip = Chip8()
        program = BytesIO(b'\xF3\x0A')
        chip.registers.v[3] = 9
        orig_pc = chip.program_counter.value
        chip.load_game(program)
        chip.emulate_cycle()

        # With no key pressed operation should "block"
        assert chip.program_counter.value == orig_pc
        assert chip.registers.v[3] == 9

        chip.keys.press_key(13)
        chip.emulate_cycle()

        assert chip.registers.v[3] == 13
        assert chip.program_counter.value == orig_pc + 2

    def test_set_delay_timer(self):
        chip = Chip8()
        program = BytesIO(b'\xF2\x15')
        chip.registers.v[2] = 5
        orig_pc = chip.program_counter.value
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.timers.delay_timer == 4
        assert chip.program_counter.value == orig_pc + 2

    def test_set_sound_timer(self):
        chip = Chip8()
        program = BytesIO(b'\xF2\x18')
        chip.registers.v[2] = 5
        orig_pc = chip.program_counter.value
        chip.load_game(program)
        chip.emulate_cycle()

        assert chip.timers.sound_timer == 4
        assert chip.program_counter.value == orig_pc + 2