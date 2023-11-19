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


def overflow_sint(num: int) -> int:
    return (num & 0xFFFFFFFF) - (2**32 if num & 0x80000000 else 0)


class _SLEB(_LEB128):
    def __new__(cls, num, *args, **kwargs):
        return super().__new__(cls, num, *args, **kwargs)

    def __init__(self, num: int, _is_decoded: bool = False):
        super().__init__(num)

        if not _is_decoded:
            self.size = len(self.encoded)

    def __add__(self, other):
        return self.__class__(super().__add__(other))

    def __sub__(self, other):
        return self.__class__(super().__sub__(other))

    def __truediv__(self, other):
        return self.__class__(int(super().__truediv__(other)))

    def __floordiv__(self, other):
        return self.__class__(super().__floordiv__(other))

    def __mod__(self, other):
        return self.__class__(super().__mod__(other))

    def __divmod__(self, other):
        return self.__class__(int(super().__divmod__(other)))

    def __lshift__(self, other):
        return self.__class__(super().__lshift__(other))

    def __mul__(self, other):
        return self.__class__(super().__mul__(other))

    def __rshift__(self, other):
        return self.__class__(super().__rshift__(other))

    def __pow__(self, other, mod=None):
        return self.__class__(super().__pow__(other, mod))

    def __and__(self, other):
        return self.__class__(super().__and__(other))

    def __or__(self, other):
        return self.__class__(super().__or__(other))

    def __xor__(self, other):
        return self.__class__(super().__xor__(other))

    def __neg__(self):
        return self.__class__(super().__neg__())

    def __pos__(self):
        return self.__class__(super().__pos__())

    def __abs__(self):
        return self.__class__(super().__abs__())

    def __invert__(self):
        return self.__class__(super().__invert__())

    def __floor__(self):
        return self.__class__(super().__floor__())

    def __ceil__(self):
        return self.__class__(super().__ceil__())

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
            return cls(decoded_int, True)

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

        return cls(overflow_sint(decoded_int), True)

    @property
    def encoded(self) -> bytes:
        encoded_int = bytearray()
        value = overflow_sint(
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
