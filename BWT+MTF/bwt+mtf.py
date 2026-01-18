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
    

def bwt():
    matrix(test)

if __name__ == "__main__":
    bwt()