class BitWriter:
    def __init__(self):
        self.buffer = 0
        self.bit_count = 0
        self.out = bytearray()

    def write(self, value, bits):
        self.buffer |= value << self.bit_count
        self.bit_count += bits

        while self.bit_count >= 8:
            self.out.append(self.buffer & 0xFF)
            self.buffer >>= 8
            self.bit_count -= 8

    def flush(self):
        if self.bit_count > 0:
            self.out.append(self.buffer & 0xFF)

        return self.out
    
class BitReader:
    def __init__(self, file):
        self.file = file
        self.buffer = 0
        self.bits_left = 0

    def read_bits(self, n):
        while self.bits_left < n:
            byte = self.file.read(1)
            if not byte:
                return None
            self.buffer |= byte[0] << self.bits_left
            self.bits_left += 8

        value = self.buffer & ((1 << n) - 1)
        self.buffer >>= n
        self.bits_left -= n
        return value
    

def write_header(file, code_size):
    file.write(b"LZW1")
    file.write(code_size.to_bytes(1, "little"))
    

def read_header(file):
    magic = file.read(4)
    if magic != b"LZW1":
        raise ValueError("Not an LZW file")

    code_size = int.from_bytes(file.read(1), "little")
    return code_size


def lzw_compress(data, code_size=12):
    MAX_DICT_SIZE = 1 << code_size

    dictionary = {bytes([i]): i for i in range(256)}
    next_code = 256

    buffer = 0
    bit_count = 0
    output = bytearray()

    s = b""

    for c in data:
        c = bytes([c])
        sc = s + c

        if sc in dictionary:
            s = sc
        else:
            code = dictionary[s]
            buffer |= code << bit_count
            bit_count += code_size

            while bit_count >= 8:
                output.append(buffer & 0xFF)
                buffer >>= 8
                bit_count -= 8

            if next_code < MAX_DICT_SIZE:
                dictionary[sc] = next_code
                next_code += 1

            s = c

    if s:
        buffer |= dictionary[s] << bit_count
        bit_count += code_size

    while bit_count > 0:
        output.append(buffer & 0xFF)
        buffer >>= 8
        bit_count -= 8

    return output



def lzw_decompress(input_path, output_path):
    with open(input_path, "rb") as f:
        code_size = read_header(f)
        MAX_DICT_SIZE = 1 << code_size

        reader = BitReader(f)

        dictionary = {i: bytes([i]) for i in range(256)}
        next_code = 256

        first_code = reader.read_bits(code_size)
        if first_code is None:
            return

        old = dictionary[first_code]
        result = bytearray(old)

        while True:
            code = reader.read_bits(code_size)
            if code is None:
                break

            if code in dictionary:
                entry = dictionary[code]
            elif code == next_code:
                entry = old + old[:1]
            else:
                raise ValueError("Invalid LZW code")

            result.extend(entry)

            if next_code < MAX_DICT_SIZE:
                dictionary[next_code] = old + entry[:1]
                next_code += 1

            old = entry

    with open(output_path, "wb") as out:
        out.write(result)





if __name__ == "__main__":
    with open(r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\LZW\Txt files\pg28054.txt", "rb") as f:
        data = f.read()

    compressed = lzw_compress(data, 12)

    with open(r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\LZW\compressed.txt", "wb") as f:
        write_header(f, 12)
        f.write(compressed)

    lzw_decompress(r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\LZW\compressed.txt", "restored.exe")
