test = bytes("abracadabra", "utf-8")
print(test)

def matrix(input):
    mtrx = []
    for i in input:
        pass
    
    

def build_suffix_array(data: bytes):
    n = len(data)

    sa = list(range(n))
    rank = list(data)

    k = 1
    tmp = [0] * n

    while k < n:

        sa.sort(key=lambda i: (rank[i], rank[i + k] if i + k < n else -1))

        tmp[sa[0]] = 0
        for i in range(1, n):
            prev = sa[i - 1]
            curr = sa[i]
            tmp[curr] = tmp[prev] + (
                (rank[prev], rank[prev + k] if prev + k < n else -1) <
                (rank[curr], rank[curr + k] if curr + k < n else -1)
            )

        rank = tmp[:]
        if max(rank) == n - 1:
            break

        k <<= 1

    return sa

def bwt_transform(data: bytes):
    sentinel = b'\x00'
    if sentinel in data:
        raise ValueError("Data already contains 0x00 sentinel")

    data = data + sentinel
    n = len(data)

    sa = build_suffix_array(data)

    bwt = bytearray(n)
    primary_index = 0

    for i, pos in enumerate(sa):
        if pos == 0:
            bwt[i] = data[-1]
            primary_index = i
        else:
            bwt[i] = data[pos - 1]

    return bytes(bwt), primary_index

def bwt_inverse(bwt: bytes, primary_index: int):
    n = len(bwt)

    count = [0] * 256
    for b in bwt:
        count[b] += 1

    total = 0
    for i in range(256):
        count[i], total = total, total + count[i]

    next = [0] * n
    occ = [0] * 256

    for i in range(n):
        b = bwt[i]
        next[count[b] + occ[b]] = i
        occ[b] += 1

    res = bytearray(n)
    idx = primary_index
    for i in range(n - 1, -1, -1):
        res[i] = bwt[idx]
        idx = next[idx]

    return bytes(res[:-1])

def bwt():
    matrix(test)

if __name__ == "__main__":
    bwt()