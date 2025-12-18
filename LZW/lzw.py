def lzw_compress(data: bytes):

    voc = {bytes([i]): i for i in range(256)}
    next_code = 256

    s = b""
    output = []

    for byte in data:
        c = bytes([byte])
        sc = s + c

        if sc in voc:
            s = sc
        else:
            output.append(voc[s])
            voc[sc] = next_code
            next_code += 1
            s = c

    if s:
        output.append(voc[s])


if __name__ == "__main__":
    with open(r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\LZW\Exe files\whois64.exe", "rb") as f:
        data = f.read()