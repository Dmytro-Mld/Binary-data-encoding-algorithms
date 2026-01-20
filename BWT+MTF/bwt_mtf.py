def counting_sort(sa, rank, k, n, max_rank):
    cnt = [0] * (max_rank + 2)
    tmp = [0] * n

    for i in sa:
        idx = rank[i + k] + 1 if i + k < n else 0
        cnt[idx] += 1

    for i in range(1, len(cnt)):
        cnt[i] += cnt[i - 1]

    for i in reversed(sa):
        idx = rank[i + k] + 1 if i + k < n else 0
        cnt[idx] -= 1
        tmp[cnt[idx]] = i

    return tmp

def build_suffix_array(data: bytes):
    n = len(data)

    sa = list(range(n))
    rank = list(data)
    tmp_rank = [0] * n

    k = 1
    max_rank = max(rank)

    while k < n:
        # radix sort:
        sa = counting_sort(sa, rank, k, n, max_rank)
        sa = counting_sort(sa, rank, 0, n, max_rank)

        tmp_rank[sa[0]] = 0
        r = 0

        for i in range(1, n):
            prev, curr = sa[i - 1], sa[i]
            if (
                rank[prev] != rank[curr] or
                (rank[prev + k] if prev + k < n else -1) !=
                (rank[curr + k] if curr + k < n else -1)
            ):
                r += 1
            tmp_rank[curr] = r

        rank, tmp_rank = tmp_rank, rank
        max_rank = r

        if max_rank == n - 1:
            break

        k <<= 1

    return sa

def bwt_transform(data: bytes):
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

    return bytes(res)

#################################################################  MTF
def mtf(data):
    alphabet = []
    output = []
    
    for i in data:
        if i in alphabet:
            pass
        else:
            alphabet.append(i)
        if len(alphabet) >= 255:
            break
        
    for i in data:
        index = data.index(i)
        output.append(index)
        tmp = i
        for j in range(index-1):
            data[index-1] = data[index]
            
               

if __name__ == "__main__":
    data = "abracadabra"
    mtf()