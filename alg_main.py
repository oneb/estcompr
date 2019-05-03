import random
import os
from math import log, exp, floor, ceil, sqrt
from statistics import median
import logging
from datetime import datetime

import tqdm

#from simpletrie_dict import empty_trie, add_to_trie, longest_prefix 
from simpletrie_tuple import empty_trie, add_to_trie, longest_prefix
from comb import amp_count


info_log = logging.getLogger('estcompr.info')
data_log = logging.getLogger('estcompr.data')

def alg1(fh, A, eps, logheader=True, logcomment=''):
    assert is_good_handle(fh)
    assert A > 1 
    assert 0 < eps < 1
    n = os.fstat(fh.fileno()).st_size
    l_0 = ceil(2 / (A*eps))
    assert 2 <= l_0 <= n
    N = n - l_0 + 1
    B = A / (2*sqrt(log(l_0)))
    s = (10*N)/(B**2)
    assert 1 <= s <= N
    slice_count = ceil(s)

    pr = 1 - 1/(3*l_0)
    repeats = amp_count(3/4, pr)
    all_dcounts = []

    # logging {{{
    tot_chars_qd = repeats*slice_count*l_0
    tot_chars_qd_frac = repeats*slice_count*l_0/n
    it_chars_qd = slice_count*l_0
    it_chars_qd_frac = slice_count*l_0/n
    tot_ss_qd = repeats*slice_count
    tot_ss_qd_frac = repeats*slice_count/N
    it_ss_qd_frac = slice_count/N
    comment = '(none)' if not logcomment else logcomment

    info_log.debug('')
    info_log.debug('starting run')
    info_log.debug('logcomment: {}'.format(comment))
    info_log.debug(fh.name)
    info_log.debug('A={A}, eps={eps}'.format(A=A, eps=eps))
    info_log.debug('n={n:,}, N={N:,}, l_0={l_0:,}'.format(n=n, N=N, l_0=l_0))
    info_log.debug('B={B:.4f}, repeats={r:,}, ceil(s)={s:,}'.format(
        B=B, r=repeats, s=slice_count))
    info_log.debug('sampling {:,} out of {:,} substrings ({:.1%}); {:,} ({:.1%}) per repetition for {:,} repetitions'.format(
        tot_ss_qd, N, tot_ss_qd_frac, slice_count, it_ss_qd_frac, repeats))
    info_log.debug('sampling {:,} out of {:,} characters ({:.1%}); {:,} ({:.1%}) per repetition for {:,} repetitions'.format(
        tot_chars_qd, n, tot_chars_qd_frac, it_chars_qd, it_chars_qd_frac, repeats))
    start_time = datetime.now()
    # }}}

    progress_bar = tqdm.tqdm(total=repeats*slice_count)
    for i in range(repeats):
        dcounts = {l : 0 for l in range(1, l_0 + 1)}  
        trie = empty_trie()
        for sl in read_random_slices(fh, l_0, slice_count):
            ll = len(longest_prefix(trie, sl))
            for i in range(ll+1, l_0+1):
                dcounts[i] += 1
            add_to_trie(trie, sl)
            progress_bar.update(1)
        all_dcounts.append(dcounts)

    ratios = []
    for l in range(1, l_0+1):
        # d_est corresponds to the result of ESTIMATE(l, B, 1/(3*l_0)) in the
        # paper's pseudocode
        d_est = median([dc[l]*B for dc in all_dcounts])
        ratios.append(d_est / l)

    m = max(ratios)
    ret = m + A/B + eps*n

    # logging {{{

    end_time = datetime.now()
    runtime = end_time - start_time
    info_log.debug('runtime {} seconds'.format(runtime.total_seconds()))
    info_log.debug('completed with {}'.format(ret))

    if os.path.isfile(fh.name):
        _, fn = os.path.split(fh.name)
    else:
        fn = fh.name
    low = ceil((ret - eps*n)/A)
    high = floor((ret + eps*n)*A)
    data = {
            'date and time of run': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'comment': comment,
            'filename': fn,
            'A': A,
            'eps': eps,
            'invEps': 1/eps,
            'n (file size)': n,
            'B': B,
            'l_0': l_0,
            'ceil(s)': slice_count,
            'repeats': repeats,
            'N (number of substrings)': N,
            'total substrings queried': tot_ss_qd,
            'total fraction of substrings queried': tot_ss_qd_frac,
            'per iter substrings queried': slice_count,
            'per iter fraction of substrings queried': it_ss_qd_frac,
            'total chars queried': tot_chars_qd,
            'total fraction of chars queried': tot_chars_qd_frac,
            'per iter chars queried': it_chars_qd,
            'per iter fraction of chars queried': it_chars_qd_frac,
            'runtime (seconds)': runtime.total_seconds(),
            'PL estimate (unrounded)': ret,
            'PL estimate (rounded)': round(ret),
            'PL frac estimate': ret/n,
            'PL lower bound': low,
            'PL upper bound': high,
            'PL frac lower bound': low/n,
            'PL frac upper bound': high/n,
            'dcounts': str(all_dcounts)
    }
    for k,v in data.items():
        if not isinstance(v, str):
            data[k] = str(v)

    if logheader:
        data_log.info('') # newline
        data_log.info('\t'.join(data.keys()))
    data_log.info('\t'.join(data.values()))
    # }}}

    return ret

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
    Generate a sorted (descending) list of n random numbers in (0,1). 
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
