import operator as op
from fractions import Fraction
from math import floor
import logging, os
from functools import reduce

def ncr(n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, range(n, n-r, -1))
    denom = reduce(op.mul, range(1, r+1))
    return numer//denom

def amp_result(p, k):
    assert isinstance(k, int) and k > 1
    assert p > 0.5

    p_f = Fraction(p)
    ret = 0

    for i in range(1, int(floor(k/2.0)) + 1):
        ret += ncr(k, i) * p_f**(k-i) * (1 - p_f)**i

    return ret

def amp_count(p_1, p_2):
    assert p_1 > 0.5 and p_2 > 0.5
    assert p_1 <= p_2
    k = 2
    while 1:
        p_k = amp_result(p_1, k)
        if p_k >= p_2:
            return k
        k += 1



