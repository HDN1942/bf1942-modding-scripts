
def all_same(items):
    '''Check if all items in sequence are the same (equal).'''

    assert items is not None
    assert hasattr(items, '__len__')

    if len(items) == 0:
        return True

    return len(set(items)) == 1

def pack_data(data):
    '''Pack a sequence of 0's and 1's into a list of bytes.'''

    if not all(x >= 0 and x <= 1 for x in data):
        raise ValueError(f'Invalid data, values must be 0 or 1')

    packed_data = []
    bit = 0
    byte = 0

    for value in data:
        byte |= value << bit

        if bit == 7:
            packed_data.append(byte)
            bit = 0
            byte = 0
        else:
            bit += 1

    # data length not a multiple of 8, weird, but that's ok
    if bit > 0:
        packed_data.append(byte)

    return packed_data

def unpack_data(data):
    '''Unpack a sequence of bytes into a list of 0's and 1's.'''

    unpacked_data = []

    for byte in data:
        for bit in range(8):
            value = 1 if byte & 1 << bit > 0 else 0
            unpacked_data.append(value)

    return unpacked_data

def pack_data2b(data):
    '''Pack a sequence of 2-bit integers into a list of bytes.'''

    packed_data = []

    for i in range(0, len(data), 4):
        value = 0

        for j in range(0, 4):
            if i + j >= len(data):
                # data length not a multiple of 4
                break
            value |= (3 & data[i + j]) << j * 2

        packed_data.append(value)

    return packed_data

def unpack_data2b(data):
    '''Unpack a sequence of bytes into a list of 2-bit integers.'''

    unpacked_data = []

    for byte in data:
        for i in range(0, 4):
            value = (byte >> i * 2) & 3
            unpacked_data.append(value)

    return unpacked_data