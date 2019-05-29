import os
import random
from collections import OrderedDict

import tqdm
import HLL
from sortedcontainers import SortedList

# make it possible to import from parent directory
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
# import from parent directory
from simpletrie_dict import empty_trie, add_to_trie, longest_prefix
from alg_main import is_good_handle, is_pos_int

DEBUG = False

################################
# main algs


def count_distinct_ss(fh, max_len, pbar=False):
    assert is_good_handle(fh)
    assert is_pos_int(max_len)
    n = os.fstat(fh.fileno()).st_size
    assert max_len < n

    dcounts = OrderedDict([(l, 0) for l in range(1, max_len + 1)])
    trie = empty_trie()
    if pbar:
        progress_bar = tqdm.tqdm(total=n - max_len + 1)
    for sl in full_slices(fh, max_len):
        ll = len(longest_prefix(trie, sl))
        for i in range(ll + 1, max_len + 1):
            dcounts[i] += 1
        add_to_trie(trie, sl)
        if pbar:
            progress_bar.update(1)

    # stubs
    for i in range(n - max_len + 1, (n - 1) + 1):
        k = n - i  # ...j
        fh.seek(i, 0)
        cs = fh.read(k)
        ll = len(longest_prefix(trie, cs))
        for j in range(ll + 1, k + 1):
            dcounts[j] += 1
        add_to_trie(trie, cs)

    return dcounts


def count_distinct_ss_sanity(fh, max_len, pbar=False):
    n = os.fstat(fh.fileno()).st_size
    dcounts = OrderedDict()
    if pbar:
        progress_bar = tqdm.tqdm(total=n * max_len * (max_len / 2))  #approx

    for l in range(max_len, 1 - 1, -1):
        xs = set()
        for i in range(0, (n - l) + 1):
            fh.seek(i, 0)
            xs.add(fh.read(l))
            if pbar:
                progress_bar.update(l)
        dcounts[l] = len(xs)
    return dcounts


def count_distinct_hll(fh, max_len, num_registers=16, pbar=False):
    n = os.fstat(fh.fileno()).st_size
    hs = [0] + [HLL.HyperLogLog(num_registers) for l in range(1, max_len + 1)]

    if pbar:
        progress_bar = tqdm.tqdm(total=n)

    for sl in full_slices(fh, max_len):
        if pbar:
            progress_bar.update(1)
        for l in range(1, max_len + 1):
            hs[l].add(sl[0:l])

    for sl in stub_slices(fh, max_len):
        for l in range(1, len(sl) + 1):
            hs[l].add(sl[0:l])

    return OrderedDict([(l, hs[l].cardinality())
                        for l in range(1, max_len + 1)])


def count_distinct_onelen(fh, l):
    n = os.fstat(fh.fileno()).st_size
    xs = SortedList()
    C = 1000000
    pb = tqdm.tqdm(total=n)
    for (i, sl) in enumerate(full_slices(fh, l)):
        if not sl in xs:
            xs.add(sl)
        pb.update(1)
        if i % C == 0:
            if DEBUG:
                print(len(xs))

    if DEBUG:
        print('\n\n ... [ {} ] ...\n\n'.format(len(xs)))
    return len(xs)


def distinct_in_sample(fh, s_len, s_count):
    assert is_good_handle(fh)
    assert is_pos_int(s_len)
    assert is_pos_int(s_count)
    n = os.fstat(fh.fileno()).st_size

    pb = tqdm.tqdm(total=s_count)
    slice_starts = [random_slice_loc(n, s_len)[0] for _ in range(s_count)]
    slice_starts.sort()
    xs = SortedList()
    for start in slice_starts:
        fh.seek(start, 0)
        cs = fh.read(s_len)
        if not cs in xs:
            xs.add(cs)
        pb.update(1)
    return len(xs)


################################
# helpers


def random_slice_loc(n, l):
    # start index inclusive, end index exclusive
    start = random.randint(0, n - l)
    end = start + l
    return (start, end)


def full_slices(fh, l):
    assert is_good_handle(fh)
    assert is_pos_int(l)
    n = os.fstat(fh.fileno()).st_size
    assert l <= n
    for i in range(0, (n - l) + 1):
        fh.seek(i, 0)
        yield fh.read(l)


def stub_slices(fh, l):
    n = os.fstat(fh.fileno()).st_size
    for i in range(n - l + 1, (n - 1) + 1):
        k = n - i  # ...j
        fh.seek(i, 0)
        yield fh.read(k)
