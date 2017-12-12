import argparse
import sys
import os
from math import floor, ceil

import alg_main

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--infile', nargs='?', type=argparse.FileType('rb'),
        metavar='FILE',
        default=sys.stdin, help='Input file (optional)')
parser.add_argument('-A', type=float,
        help='approximation parameter "A"')
parser.add_argument('-e', type=float, metavar='EPSILON',
        help='approximation parameter "epsilon"')

if __name__ == '__main__':

    args = parser.parse_args()
    
    n = os.fstat(args.infile.fileno()).st_size
    A, eps = args.A, args.e
    est = alg_main.alg1(args.infile, args.A, args.e)
    est = round(est)

    print('size of {} is {:,} bytes'.format(args.infile.name, n))
    print('estimate of number of symbols in compressed version: {:,}'.format(est))
    low = floor((est - eps*n)/A)
    high = ceil((est + eps*n)*A)
    print('number of symbols in compressed version guaranteed to be between {:,} and {:,}'.format(low, high))
