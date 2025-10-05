bitflow = "11110110101101110101101010110010101111000100011100011100011"

def WriteBitSequence(file, bitflow, length):
    seq = bitflow[:length]
    data = bytearray()
    for i in range(0, length, 8):
        chunk = seq[i:i+8]
        chunk = chunk[::-1]
        if len(chunk) < 8:
            while (len(chunk)) < 8:
                chunk = "0" + chunk
        value = int(chunk, 2)
        data.append(value)

    with open(file, "wb") as f:
        f.write(data)

    return 0



def ReadBitSequence(file, bitflow, length):
    pass


def main():
    length = 16 #int(input("Enter the length of your input:"))
    file = "Data.bin" #input("Enter your file name:")
    wrt = WriteBitSequence(file, bitflow, length)
    with open(file, "rb") as f:
        content = f.read()
    print("Check file content:", content)



if __name__ == "__main__":
    main()