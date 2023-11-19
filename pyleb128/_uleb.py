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

from ._base import _LEB128, InvalidVarint, LEB128_MAX_SIZE


def overflow_uint(num: int) -> int:
    return num & 0xFFFFFFFF


class _ULEB(_LEB128):
    def __new__(cls, num, *args, **kwargs):
        return super().__new__(cls, num, *args, **kwargs)

    def __init__(self, num: int, p1: bool = False):
        self.p1 = p1

        super().__init__(num)

    def __add__(self, other):
        return self.__class__(super().__add__(other), self.p1)

    def __sub__(self, other):
        return self.__class__(super().__sub__(other), self.p1)

    def __truediv__(self, other):
        return self.__class__(int(super().__truediv__(other)), self.p1)

    def __floordiv__(self, other):
        return self.__class__(super().__floordiv__(other), self.p1)

    def __mod__(self, other):
        return self.__class__(super().__mod__(other), self.p1)

    def __divmod__(self, other):
        return self.__class__(int(super().__divmod__(other)), self.p1)

    def __lshift__(self, other):
        return self.__class__(super().__lshift__(other), self.p1)

    def __mul__(self, other):
        return self.__class__(super().__mul__(other), self.p1)

    def __rshift__(self, other):
        return self.__class__(super().__rshift__(other), self.p1)

    def __pow__(self, other, mod=None):
        return self.__class__(super().__pow__(other, mod), self.p1)

    def __and__(self, other):
        return self.__class__(super().__and__(other), self.p1)

    def __or__(self, other):
        return self.__class__(super().__or__(other), self.p1)

    def __xor__(self, other):
        return self.__class__(super().__xor__(other), self.p1)

    def __neg__(self):
        return self.__class__(super().__neg__(), self.p1)

    def __pos__(self):
        return self.__class__(super().__pos__(), self.p1)

    def __abs__(self):
        return self.__class__(super().__abs__(), self.p1)

    def __invert__(self):
        return self.__class__(super().__invert__(), self.p1)

    def __floor__(self):
        return self.__class__(super().__floor__(), self.p1)

    def __ceil__(self):
        return self.__class__(super().__ceil__(), self.p1)

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
