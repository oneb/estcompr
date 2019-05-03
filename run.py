import argparse
import sys
import os
from math import floor, ceil
import logging
import logging.handlers

import alg_main


parser = argparse.ArgumentParser()
parser.add_argument('-A', type=float,
        help='approximation parameter "A"')
parser.add_argument('-e', type=float, metavar='EPSILON',
        help='approximation parameter "epsilon"')
parser.add_argument('-i', '--infile', 
        metavar='FILES',
        nargs='?',
        help='input file (stdin used if absent)')
parser.add_argument('-L', '--log', action='store_true',
        help='verbose logging into logfile')
parser.add_argument('--logcomment', 
        metavar='TEXT', default='',
        nargs='?',
        help='text tag to include in logs (convenience option)')
parser.add_argument('--nologheader', action='store_true',
        help='omit column headers in logs')


def go(f, A, eps, logheader=True, logcomment=''):
    n = os.fstat(f.fileno()).st_size
    fd,fn = os.path.split(f.name)

    print()
    info_log.info('size of {} is {:,} bytes'.format(fn, n))
    est = alg_main.alg1(f, A, eps, logheader=logheader, logcomment=logcomment)
    est = round(est)

    info_log.info('estimate of length of optimal parsing: {:,} ({:%})'.format(est, est/n))
    low = ceil((est - eps*n)/A)
    high = floor((est + eps*n)*A)
    info_log.info('optimal parsing between {:,} and {:,}'.format(low, high))


info_log = logging.getLogger('estcompr.info')
data_log = logging.getLogger('estcompr.data')

if __name__ == '__main__':

    args = parser.parse_args()

    # logging {{{
    plain_format = logging.Formatter('%(message)s')
    detail_format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    to_screen = logging.StreamHandler()
    to_screen.setFormatter(plain_format)
    if args.log:
        info_log.setLevel('DEBUG')
        to_info_files = logging.handlers.RotatingFileHandler(
            filename='estcompr.log', maxBytes=10*1024*1024, 
            backupCount=2)
        to_info_files.setFormatter(detail_format)
        info_log.addHandler(to_info_files)

        data_log.setLevel('DEBUG')
        to_data_files = logging.handlers.RotatingFileHandler(
            filename='estcompr_data.log', maxBytes=10*1024*1024, 
            backupCount=2)
        to_data_files.setFormatter(plain_format)
        data_log.addHandler(to_data_files)

        to_screen.setLevel('INFO')
        info_log.addHandler(to_screen)
    else:
        info_log.setLevel('INFO')
        info_log.addHandler(to_screen)
    # }}}
    
    A, eps = args.A, args.e

    # stdin default
    if not args.infile:
        go(sys.stdin, A, eps)
    else: 
        assert os.path.isfile(args.infile)
        with open(args.infile, 'rb') as f:
            go(f, A, eps, logheader=(not args.nologheader),
                    logcomment=args.logcomment)





