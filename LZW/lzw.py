def lzw():
        with open(r"C:\Users\dmmol\OneDrive\Documents\GitHub\Binary-data-encoding-algorithms\LZW\Exe files\whois64.exe", "rb") as f:
            data = f.read()
        print(data[:1000])

if __name__ == "__main__":
    lzw()