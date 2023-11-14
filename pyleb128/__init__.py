# --------------------------------------------------------------------------------------
#  Copyright(C) 2023 yntha                                                             -
#                                                                                      -
#  This program is free software: you can redistribute it and/or modify it under       -
#  the terms of the GNU General Public License as published by the Free Software       -
#  Foundation, either version 3 of the License, or (at your option) any later          -
#  version.                                                                            -
#                                                                                      -
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY     -
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A     -
#  PARTICULAR PURPOSE. See the GNU General Public License for more details.            -
#                                                                                      -
#  You should have received a copy of the GNU General Public License along with        -
#  this program. If not, see <http://www.gnu.org/licenses/>.                           -
# --------------------------------------------------------------------------------------

import typing

# maximum byte length for a LEB128.
LEB128_MAX_SIZE = 5


class InvalidVarint(ValueError):
    pass


def overflow_uint(num: int) -> int:
    return num & 0xFFFFFFFF


def overflow_sint(num: int) -> int:
    return (num & 0xFFFFFFFF) - 0x100000000 if num & 0x80000000 else num & 0xFFFFFFFF


class _LEB128(int):
    def __new__(cls, num: int, *args, **kwargs):
        if num is None:
            num = 0

        return super().__new__(cls, num)

    def __init__(self, num: int):
        self.value = num
        self.size = self.calcsize(num)

    def __add__(self, b):
        return self.__class__(super().__add__(self.__class__(b)))

    def __and__(self, b):
        return self.__class__(super().__and__(self.__class__(b)))

    def __sub__(self, b):
        return self.__class__(super().__sub__(self.__class__(b)))

    def __mul__(self, b):
        return self.__class__(super().__mul__(self.__class__(b)))

    def __div__(self, b):
        return self.__class__(super().__mod__(self.__class__(b)))

    def __or__(self, b):
        return self.__class__(super().__or__(self.__class__(b)))

    def __pow__(self, b):
        return self.__class__(super().__pow__(self.__class__(b)))

    def __lshift__(self, b):
        return self.__class__(super().__lshift__(self.__class__(b)))

    def __rshift__(self, b):
        return self.__class__(super().__rshift__(self.__class__(b)))

    def __rlshift__(self, b):
        return self.__class__(super().__rlshift__(self.__class__(b)))

    def __rrshift__(self, b):
        return self.__class__(super().__rrshift__(self.__class__(b)))

    def __xor__(self, b):
        return self.__class__(super().__xor__(self.__class__(b)))

    def __rxor__(self, b):
        return self.__class__(super().__rxor__(self.__class__(b)))

    def __ror__(self, b):
        return self.__class__(super().__ror__(self.__class__(b)))

    def __rpow__(self, b, mod=None):
        return self.__class__(super().__rpow__(self.__class__(b), mod))

    def __rsub__(self, b):
        return self.__class__(super().__rsub__(self.__class__(b)))

    @staticmethod
    def calcsize(n):
        s = 0

        while True:
            n >>= 7

            if n <= 0:
                break

            s += 1

        return max(s, 1)


class _ULEB(_LEB128):
    def __new__(cls, num, *args, **kwargs):
        return super().__new__(cls, num, *args, **kwargs)

    def __init__(self, num: int, p1: bool = False):
        self.p1 = p1

        super().__init__(num)

    @classmethod
    def peek_size(cls, stream: typing.BinaryIO) -> int:
        spos = stream.tell()
        size = 0
        byte = 0

        for _ in range(LEB128_MAX_SIZE):
            byte = stream.read(1)[0]

            if byte < 0x7F:
                size += 1
                break

            size += 1

        # check msb on final byte. raise if set.
        if byte & 0x80 == 0x80:
            raise InvalidVarint("Invalid uleb128 sequence.")

        stream.seek(spos)

        return size

    @classmethod
    def decode_stream(cls, stream: typing.BinaryIO, p1: bool = False):
        return cls.decode(stream.read(cls.peek_size(stream)), p1)

    @classmethod
    def decode(cls, data: bytes, p1: bool = False) -> typing.Self:
        if len(data) == 0:
            raise InvalidVarint("Data buffer was empty.")
        if len(data) > LEB128_MAX_SIZE:
            raise InvalidVarint("Data buffer was too large. Is this really a leb128?")

        data_buffer = bytearray(data)
        current_byte = data_buffer.pop(0)
        decoded_int = current_byte

        if decoded_int < 0x7F:
            return cls(decoded_int - p1, p1)

        decoded_int &= 0x7F

        current_byte = data_buffer.pop(0)
        shift_mod = 1

        while len(data_buffer) > 0:
            decoded_int += (current_byte & 0x7F) << (shift_mod * 7)

            shift_mod += 1
            current_byte = data_buffer.pop(0)

        decoded_int += current_byte << (shift_mod * 7)
        return cls(overflow_uint(decoded_int - p1), p1)

    @property
    def encoded(self) -> bytes:
        encoded_int = bytearray()
        value = overflow_uint(self.value + self.p1)

        while True:
            byte = value & 0x7F
            value >>= 7

            if value == 0:
                encoded_int.append(byte)

                return bytes(encoded_int)

            encoded_int.append(0x80 | byte)


class _SLEB(_LEB128):
    def __new__(cls, num, *args, **kwargs):
        return super().__new__(cls, num, *args, **kwargs)

    def __init__(self, num: int):
        super().__init__(num)

    @classmethod
    def peek_size(cls, stream: typing.BinaryIO) -> int:
        spos = stream.tell()
        size = 0

        for _ in range(LEB128_MAX_SIZE):
            byte = stream.read(1)[0]

            if byte < 0x7F:
                size += 1
                break

            size += 1

        stream.seek(spos)

        return size

    @classmethod
    def decode_stream(cls, stream: typing.BinaryIO):
        return cls.decode(stream.read(cls.peek_size(stream)))

    @classmethod
    def decode(cls, data: bytes) -> typing.Self:
        if len(data) == 0:
            raise InvalidVarint("Data buffer was empty.")
        if len(data) > LEB128_MAX_SIZE:
            raise InvalidVarint("Data buffer was too large. Is this really a leb128?")

        data_buffer = bytearray(data)
        current_byte = data_buffer.pop(0)
        decoded_int = current_byte

        if decoded_int < 0x7F:
            return cls(decoded_int)

        decoded_int &= 0x7F

        current_byte = data_buffer.pop(0)
        shift_mod = 1

        while len(data_buffer) > 0:
            decoded_int += (current_byte & 0x7F) << (shift_mod * 7)

            shift_mod += 1
            current_byte = data_buffer.pop(0)

        decoded_int += current_byte << (shift_mod * 7)

        if (current_byte & 0x40) != 0:
            decoded_int |= -(1 << (shift_mod * 7) + 7)

        return cls(overflow_sint(decoded_int))

    @property
    def encoded(self) -> bytes:
        encoded_int = bytearray()
        value = overflow_uint(
            self.value
        )  # we're keeping the raw value as an unsigned int.

        if value >= 0:
            while value > 0x3F:
                encoded_int.append(0x80 | (value & 0x7F))
                value = (value % 0x100000000) >> 7  # lsr (>>>) in java

            encoded_int.append(value & 0x7F)
        else:
            while value < -0x40:
                encoded_int.append(0x80 | (value & 0x7F))
                value >>= 7

            encoded_int.append(value & 0x7F)

        return bytes(encoded_int)


leb128 = _LEB128
uleb128 = _ULEB
sleb128 = _SLEB