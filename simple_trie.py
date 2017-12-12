def empty_trie():
    return {}

def add_to_trie(trie, seq):
    while seq:
        if seq[0] in trie.keys():
            trie = trie[seq[0]]
            seq = seq[1:]
        else:
            trie[seq[0]] = {}
            trie = trie[seq[0]]
            seq = seq[1:]

def longest_prefix(trie, seq):
    for i in range(len(seq)):
        if seq[i] in trie.keys():
            trie = trie[seq[i]]
        else:
            return seq[:i]
    return seq


