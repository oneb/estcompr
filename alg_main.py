import random
import os
from math import log, exp, floor, ceil, sqrt
from statistics import median

import tqdm

from simple_trie import empty_trie, add_to_trie, longest_prefix
from comb import amp_count

class UnrunnableParams(Exception):
    pass


def alg1(fh, A, eps):
    assert is_good_handle(fh)
    assert A >= 1 and eps >= 0

    l_0 = ceil(2 / (A*eps))
    B = A / (2*sqrt(log(2/(A*eps))))

    # hm
    if B < 1:
        raise UnrunnableParams

    pr = 1 - 1/(3*l_0)
    n = os.fstat(fh.fileno()).st_size
    slice_count = round((10/B**2) * n)

    repeats = amp_count(3/4, pr)
    all_dcounts = []
    for i in range(repeats):
        dcounts = {l : 0 for l in range(1, l_0 + 1)}  
        trie = empty_trie()
        for sl in tqdm.tqdm(read_random_slices(fh, l_0, slice_count)):
            ll = len(longest_prefix(trie, sl))
            for i in range(ll+1, l_0+1):
                dcounts[i] += 1
            add_to_trie(trie, sl)
        all_dcounts.append(dcounts)

    ratios = []
    for l in range(1, l_0+1):
        # d_est corresponds to the result of ESTIMATE(l, B, 1/(3*l_0)) in the
        # paper's pseudocode
        d_est = median([dc[l] for dc in all_dcounts])
        ratios.append(d_est / l)
        
    m = max(ratios)
    return m + A/B + eps*n

def read_random_slices(fh, s_len, s_count):
    '''
    Read and yield s_count randomly selected slices of length s_len from file
    handle fh. Constant space. Ordered from beginning to end.
    '''
    assert is_good_handle(fh)
    assert is_pos_int(s_len)
    assert is_pos_int(s_count)

    n = os.fstat(fh.fileno()).st_size
    for (start, end) in random_slice_locs(n, s_len, s_count):
        assert end - start == s_len 
        fh.seek(start, 0) 
        cs = fh.read(s_len)
        yield cs

def random_not_0():
    '''
    Return a random number in (0,1).
    (random.random() gives a random number in [0,1))
    '''
    while 1:
        x = random.random()
        if x > 0:
            return x

def sorted_random(n):
    '''
    Generate a sorted (descending) list of random numbers in (0,1). 
    Uses constant space, yields the numbers one by one. 
    Uses the algorithm from the paper "Generating Sorted Lists of Random Numbers"
    '''
    i = n
    ln_cur_max = 0.0

    while i > 0:
        ln_cur_max += log(random_not_0()) / i
        i -= 1
        x = exp(ln_cur_max)
        assert 0 < x < 1
        yield x


def random_slice_locs(n, l, count_):
    '''
    Generate pairs of indices (start, end) for count_ random slices of length l
    of a string of length n. Constant space. Ordered from beginning to end.

    (In the pairs, first index is inclusive, second exclusive. So (2,4) means a
    string of length 2 containing the characters at indices 2 and 3.)
    '''
    for x in sorted_random(count_):
        # (1-x) is in (0,1), so (1-x)*(n-l+1) is in (0, n-l+1),
        # so floor of that is an integer in [0, n-l] 
        # (with each integer equally probable)
        start = floor((1-x)*(n-l+1))
        end = start + l
        yield (start, end)
        

################################################################
# assert helpers

def is_good_handle(f):
  return (
      f.readable() 
      and not f.closed 
      and f.seekable())

def is_pos_int(x):
    return isinstance(x, int) and x >= 1
