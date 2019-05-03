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
    assert 0.5 < p <= 1

    p_f = Fraction(p)
    ret = 0

    for i in range(0, int(floor((k-1)/2.0)) + 1):
        ret += ncr(k, i) * p_f**(k-i) * (1 - p_f)**i

    return ret

def amp_count(p_1, p_2):
    assert 0.5 < p_1 <= 1
    assert 0 <= p_2 <= 1
    
    k = 1
    p_k = p_1
    while 1:
        if p_k >= p_2:
            return k
        k += 1
        p_k = amp_result(p_1, k)



