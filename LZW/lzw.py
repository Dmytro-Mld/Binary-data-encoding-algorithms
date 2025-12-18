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


def lzw_compress(data: bytes):
    MAX_CODE = 4095
    CODE_WIDTH = 12

    # 1. Ініціалізація словника
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



if __name__ == "__main__":
    with open(r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\LZW\Exe files\whois64.exe", "rb") as f:
        data = f.read()