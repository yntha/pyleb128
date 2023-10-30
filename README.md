# pyleb128
Powerful little-endian base-128 encoding/decoding library for Python 3.
</br>
</br>
Supports the following types:
* Unsigned LEB128
* Signed LEB128
* Unsigned LEB128 +1 ([ULEB128P1](https://source.android.com/docs/core/runtime/dex-format#leb128))

# Installing
```
python -m pip install -U pyleb128
```

# Example Usage
```python
from pyleb128 import uleb128, sleb128

# unsigned
print(uleb128.decode(b'\xff\xff\x03'))  # 65535
print(uleb128.decode(b'\xff\xff\x03').encoded)  # b'\xff\xff\x03'
print(uleb128.decode(b'\xff\xff\x03', p1 = True))  # decode with as ULEB128P1

# signed
print(sleb128.decode(b'\xf3\xff\xff\xff\x0f'))  # -13
print(uleb128.decode(b'\xf3\xff\xff\xff\x0f').encoded)  # b'\xf3\xff\xff\xff\x0f'
```
