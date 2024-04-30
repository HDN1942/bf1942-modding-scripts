
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

    for go in data:
        byte |= go << bit

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