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


def lzw_compress(data: bytes):
    MAX_CODE = 4095
    CODE_WIDTH = 12

    voc = {bytes([i]): i for i in range(256)}
    next_code = 256

    writer = BitWriter()

    s = b""

    for byte in data:
        c = bytes([byte])
        sc = s + c

        if sc in voc:
            s = sc
        else:
            writer.write(voc[s], CODE_WIDTH)

            if next_code <= MAX_CODE:
                voc[sc] = next_code
                next_code += 1

            s = c

    if s:
        writer.write(voc[s], CODE_WIDTH)

    return writer.flush()



def lzw_decompress(input, output, code_size=12):
    MAX_DICT = 1 << code_size

    with open(input, "rb") as f:
        reader = BitReader(f)

        dictionary = {i: bytes([i]) for i in range(256)}
        next_code = 256

        first_code = reader.read_bits(code_size)
        if first_code is None:
            return

        old = dictionary[first_code]
        output = bytearray(old)

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

            output.extend(entry)

            if next_code < MAX_DICT:
                dictionary[next_code] = old + entry[:1]
                next_code += 1

            old = entry

    with open(output, "wb") as out:
        out.write(output)




if __name__ == "__main__":
    with open(r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\LZW\Exe files\whois64.exe", "rb") as f:
        data = f.read()