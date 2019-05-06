def empty_trie():
    return []

def add_to_trie(trie, seq):
    while seq:
        found = False
        for t in trie:
            if t[0] == seq[0]:
                found = True
                trie = t[1]
                seq = seq[1:]
                break
        if not found:
            new = []
            trie.append((seq[0], new))
            trie = new
            seq = seq[1:]

def longest_prefix(trie, seq):
    for i in range(len(seq)):
        found = False
        for t in trie:
            if t[0] == seq[i]:
                found = True
                trie = t[1]
        if not found:
            return seq[:i]
    return seq


