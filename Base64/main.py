alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

base64_map = {ch: format(i, '06b') for i, ch in enumerate(alphabet)} #creating a dictionary {"A" = "000000"}

binary_to_char = {bits: ch for ch, bits in base64_map.items()} #creating inversed dict {"000000" = "A"}

base64_map['='] = 'padding'
binary_to_char['padding'] = '='


def Encoder(encode, encoded):
    base64 = []

    with open(encode) as txt:
        data = txt.read()

    for i in range(0, len(data), 24):
        chunk24 = data[i:i+24]

        if len(chunk24) < 24:
            chunk24 = data[i:i+24].ljust(24, '0')

        for j in range(0, len(chunk24), 6):
            block6 = chunk24[j:j+6]
            ch = binary_to_char.get(block6, '?')
            base64.append(ch)
        
    base64_string = ''.join(base64)
    print(base64_string)

    with open(encoded, "w") as f:
        for i in range(0, len(base64_string), 76):
            line = base64_string[i:i+76]
            if i + 76 >= len(base64_string):
                f.write(line)
            else:
                f.write(line + "\n")

    return 0

def Decoder(decode, decoded):
    bin = []

    with open(decode) as txt:
        data = txt.read()

    clean_data = data.replace("\n", "")

    for i in clean_data:
        bn = base64_map.get(i)
        bin.append(bn)

    bin_string = ''.join(bin)
    print(bin_string)

    with open(decoded, "w") as f:
        f.write(bin_string)

    return 0


def main():
    print("\\\\\\\\\\\\\\Encoding part\\\\\\\\\\\\")
    to_encode_file_name = input("Enter file name to be encoded: ")
    encoded_file_name = input("Enter file name to save encoded data: ")

    if (encoded_file_name == ''):
        encoded_file_name = to_encode_file_name + ".base64"

    Encoder(to_encode_file_name + ".txt", encoded_file_name + ".txt")

    print("\\\\\\\\\\\\\\Decoding part\\\\\\\\\\\\")
    to_decode_file_name = encoded_file_name #input("Enter file name to be decoded: ")
    decoded_file_name = input("Enter file name to save decoded data: ")

    Decoder(to_decode_file_name + ".txt", decoded_file_name + ".txt")





if __name__ == "__main__":
    main()