import os
import bwt_mtf
import io

BLOCK_SIZE = 512 * 1024  # 1 MB

def bwt_blockwise(file_path):
    blocks = []
    primary_indices = []

    with open(file_path, "rb") as f:
        while True:
            block = f.read(BLOCK_SIZE)
            if not block:
                break

            bwt_block, idx = bwt_mtf.bwt_transform(block)
            blocks.append(bwt_block)
            primary_indices.append(idx)

    return blocks, primary_indices


def bwt_inverse_blockwise(blocks, primary_indices):
    restored = bytearray()
    for bwt_block, idx in zip(blocks, primary_indices):
        block = bwt_mtf.bwt_inverse(bwt_block, idx)
        restored.extend(block)
    return bytes(restored)


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
        
def lzw_bwt_compress_file(input_path, output_path, code_size=12):
    with open(output_path, "wb") as out:
        out.write(b"LZWB")
        out.write(code_size.to_bytes(1, "little"))

        with open(input_path, "rb") as f:
            while True:
                block = f.read(BLOCK_SIZE)
                if not block:
                    break

                bwt_block, primary_index = bwt_mtf.bwt_transform(block)

                compressed = lzw_compress(bwt_block, code_size)

                out.write(len(block).to_bytes(4, "little"))
                out.write(primary_index.to_bytes(4, "little"))
                out.write(len(compressed).to_bytes(4, "little"))

                out.write(compressed)
                
def lzw_bwt_decompress_file(input_path, output_path):
    with open(input_path, "rb") as f:
        magic = f.read(4)
        if magic != b"LZWB":
            raise ValueError("Not an LZW+BWT file")

        code_size = int.from_bytes(f.read(1), "little")

        with open(output_path, "wb") as out:
            while True:
                header = f.read(12)
                if not header:
                    break

                original_size = int.from_bytes(header[0:4], "little")
                primary_index = int.from_bytes(header[4:8], "little")
                compressed_size = int.from_bytes(header[8:12], "little")

                compressed = f.read(compressed_size)


                bwt_block = lzw_decompress_bytes(
                    compressed,
                    code_size,
                    original_size
                )

                block = bwt_mtf.bwt_inverse(bwt_block, primary_index)

                out.write(block)
                
def lzw_decompress_bytes(data, code_size, expected_size):
    MAX_DICT_SIZE = 1 << code_size
    reader = BitReader(io.BytesIO(data))

    dictionary = {i: bytes([i]) for i in range(256)}
    next_code = 256

    first_code = reader.read_bits(code_size)
    if first_code is None:
        return b""

    old = dictionary[first_code]
    result = bytearray(old)

    while len(result) < expected_size:
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

    return bytes(result[:expected_size])


def lzw_test_folder(input_folder, ext=".txt", code_size=12):
    ratios = []

    files = [
        f for f in os.listdir(input_folder)
        if f.endswith(ext)
    ][:10]

    for filename in files:
        path = os.path.join(input_folder, filename)

        with open(path, "rb") as f:
            data = f.read()

        if not data:
            continue

        compressed = lzw_compress(data, code_size)

        original_size = len(data)
        compressed_size = 5 + len(compressed) 

        ratio = compressed_size / original_size
        ratios.append(ratio)

        print(
            f"{filename}: "
            f"original={original_size} B, "
            f"compressed={compressed_size} B, "
            f"ratio={ratio:.3f}"
        )

    if ratios:
        avg = sum(ratios) / len(ratios)
        min_r = min(ratios)
        max_r = max(ratios)

        print("\n=== LZW Compression statistics ===")
        print(f"Average ratio: {avg:.3f}")
        print(f"Min ratio:     {min_r:.3f}")
        print(f"Max ratio:     {max_r:.3f}")

def lzw_bwt_test_folder(input_folder, ext=".mobi", code_size=12):
    ratios = []

    files = [
        f for f in os.listdir(input_folder)
        if f.endswith(ext)
    ][:10]

    for filename in files:
        path = os.path.join(input_folder, filename)

        blocks, primary_indices = bwt_blockwise(path)

        compressed_blocks = []
        compressed_size = 0
        original_size = 0

        for block in blocks:
            original_size += len(block)
            comp = lzw_compress(block, code_size)
            compressed_blocks.append(comp)
            compressed_size += len(comp)

        compressed_size += 5

        ratio = compressed_size / original_size
        ratios.append(ratio)

        print(
            f"{filename}: "
            f"blocks={len(blocks)}, "
            f"original={original_size} B, "
            f"compressed={compressed_size} B, "
            f"ratio={ratio:.3f}"
        )

    if ratios:
        print("\n=== LZW + BWT (blockwise) statistics ===")
        print(f"Average ratio: {sum(ratios)/len(ratios):.3f}")
        print(f"Min ratio:     {min(ratios):.3f}")
        print(f"Max ratio:     {max(ratios):.3f}")


def lzw_mtf_test_folder():
    pass

def lzw_bwt_mtf_test_folder():
    pass


if __name__ == "__main__":
#     with open(r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\Huffman algorithm\Txt files\pg28054.txt", "rb") as f:
#         data = f.read()
        
#     data, bwt_index = bwt_mtf.bwt_transform(data)

#     compressed = lzw_compress(data, 12)

#     with open(r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\LZW\compressed.txt", "wb") as f:
#         write_header(f, 12)
#         f.write(compressed)

#     lzw_decompress(r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\LZW\compressed.txt", "restored.exe")


###############################################
    # src = r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\Huffman algorithm\Txt files\pg28054.txt"
    # cmp = r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\LZW\compressed.lzwb"
    # out = r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\LZW\restored.txt"

    # lzw_bwt_compress_file(src, cmp, code_size=12)
    # lzw_bwt_decompress_file(cmp, out)

    
    folder = r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\Huffman algorithm\Docx files"
    lzw_bwt_test_folder(folder, ext=".docx", code_size=12)
    
    # version = 0
    # print("Choose the version of LZW compresssion (Type the corresponding number on keyboard and press Enter")
    # while version != "1" or "2" or "3" or "4":
    #     version = input("Press 1: for LZW\nPress 2: for LZW + BWT\nPress 3: for LZW + MTF\nPress 4: for LZW + BWT + MTF\nYour choise: ")
    #     if version == "1":
    #         lzw_test_folder(folder)
    #     elif version == "2":
    #         lzw_bwt_test_folder(folder)
    #     elif version == "3":
    #         lzw_mtf_test_folder(folder)
    #     elif version == "4":
    #         lzw_bwt_mtf_test_folder(folder)
    #     else:
    #         print("You entered wrong digit, please, choose one of the variants below:")
