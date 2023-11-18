# pyleb128
Powerful little-endian base-128 encoding/decoding library for Python 3.
</br>
</br>
Supports the following types:
* Unsigned LEB128
* Signed LEB128
* Unsigned LEB128 +1 ([ULEB128P1](https://source.android.com/docs/core/runtime/dex-format#leb128))

# Note
The LEB classes all inherit from `int` and have all the operations implemented. The type of the result from any int operation will always be the type of the lhs. If the lhs is an int, then the type is an int. If the lhs is a LEB type, then the resulting type is a LEB.

# Installing
```
python -m pip install -U pyleb128
```

# Example Usage
```python
from pyleb128 import uleb128, sleb128

# unsigned
print(uleb128(0xffff).size)  # 2
print(uleb128((0xffff * 2).encoded))  # b'\xfe\xff\x07'
print(uleb128.decode(b'\xff\xff\x03'))  # 65535
print(uleb128.decode(b'\xff\xff\x03').encoded)  # b'\xff\xff\x03'
print(uleb128.decode(b'\xff\xff\x03', p1=True))  # decode with as ULEB128P1

# signed
print(sleb128.decode(b'\xf3\xff\xff\xff\x0f'))  # -13
print(uleb128.decode(b'\xf3\xff\xff\xff\x0f').encoded)  # b'\xf3\xff\xff\xff\x0f'

# can decode from a binary stream, too:
import io

stream = io.BytesIO(b'\xff\xff\x03') 
print(uleb128.decode_stream(stream, p1=True))
```
