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

# maximum byte length for a LEB128.
LEB128_MAX_SIZE = 5


class InvalidVarint(ValueError):
    pass


class _LEB128(int):
    def __new__(cls, num: int, *args, **kwargs):
        if num is None:
            num = 0

        return super().__new__(cls, num)

    def __init__(self, num: int):
        self.value = num
        self.size = self.calcsize(num)

    def __repr__(self):
        return self.encoded.hex()

    def __str__(self):
        return str(self.value)

    @staticmethod
    def calcsize(n):
        s = 0

        while True:
            n >>= 7

            if n <= 0:
                break

            s += 1

        return max(s, 1)
