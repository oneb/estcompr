import os
import os.path
from math import ceil, floor
from collections import OrderedDict
import argparse
import logging
import logging.handlers
import datetime

import ss_est

# make it possible to import from parent directory
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
# import from parent directory
from simpletrie_dict import empty_trie, add_to_trie, longest_prefix
from alg_main import is_good_handle, is_pos_int
from assert_helpers import is_pos_int


def cmd_fulldss(args):
    assert args.method in ('trie', 'sanity', 'hll', 'dummy1')
    assert is_pos_int(args.l)
    pbar = True

    # logging {{{
    text_log = logging.getLogger('dss.text')
    data_log = logging.getLogger('dss.data')
    plain_format = logging.Formatter('%(message)s')
    detail_format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    if args.log:
        text_log.setLevel('DEBUG')
        data_log.setLevel('DEBUG')

        # text logfile
        to_text_files = logging.handlers.RotatingFileHandler(
            filename='dss.log', maxBytes=10 * 1024 * 1024, backupCount=2)
        to_text_files.setLevel('DEBUG')
        to_text_files.setFormatter(detail_format)
        text_log.addHandler(to_text_files)

        # data logfile
        to_data_files = logging.handlers.RotatingFileHandler(
            filename='dss_data.log', maxBytes=10 * 1024 * 1024, backupCount=2)
        to_data_files.setLevel('DEBUG')
        to_data_files.setFormatter(plain_format)
        data_log.addHandler(to_data_files)

    # printed logs from text
    to_screen = logging.StreamHandler()
    to_screen.setFormatter(plain_format)
    to_screen.setLevel('INFO')
    text_log.addHandler(to_screen)
    # }}}

    text_log.info(args.infile + ':')
    start_time = datetime.datetime.now()

    with open(args.infile, 'rb') as f:
        if args.method == 'trie':
            d = ss_est.count_distinct_ss(f, args.l, pbar=pbar)
        if args.method == 'sanity':
            d = ss_est.count_distinct_ss_sanity(f, args.l, pbar=pbar)
        if args.method == 'hll':
            d = ss_est.count_distinct_hll(f, args.l, pbar=pbar)
        if args.method == 'dummy1':
            print(123)
            x = ss_est.count_distinct_onelen(f, args.l)
            print('\n--> {} <--'.format(x))
            return
    end_time = datetime.datetime.now()

    # logging {{{
    data = OrderedDict([
        ('start time', start_time.strftime('%Y-%m-%d %H:%M:%S')),
        ('file', os.path.split(args.infile)[1]),
        ('method', args.method),
        ('maxlen', args.l),
        ('runtime', end_time - start_time),
    ] + list(zip(range(1, args.l + 1), [d[l_]
                                        for l_ in range(1, args.l + 1)])))

    if not args.nologheader:
        data_log.info('')
    data_log.info(dicts_to_tsv([data], headers=(not args.nologheader)))
    # }}}
    text_log.info(' '.join([
        '{}:{}'.format(k, round(v))
        for k, v in sorted(d.items(), key=lambda x: x[0])
    ]))


def cmd_sldss(args):
    assert is_pos_int(args.l)
    assert args.A > 1
    A = args.A

    # logging {{{
    text_log = logging.getLogger('estdss.text')
    data_log = logging.getLogger('estdss.data')
    plain_format = logging.Formatter('%(message)s')
    detail_format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    if args.log:
        text_log.setLevel('DEBUG')
        data_log.setLevel('DEBUG')

        # text logfile
        to_text_files = logging.handlers.RotatingFileHandler(
            filename='estdss.log', maxBytes=10 * 1024 * 1024, backupCount=2)
        to_text_files.setLevel('DEBUG')
        to_text_files.setFormatter(detail_format)
        text_log.addHandler(to_text_files)

        # data logfile
        to_data_files = logging.handlers.RotatingFileHandler(
            filename='estdss_data.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=2)
        to_data_files.setLevel('DEBUG')
        to_data_files.setFormatter(plain_format)
        data_log.addHandler(to_data_files)

    # printed logs from text
    to_screen = logging.StreamHandler()
    to_screen.setFormatter(plain_format)
    to_screen.setLevel('INFO')
    text_log.addHandler(to_screen)

    start_time = datetime.datetime.now()
    # }}}

    with open(args.infile, 'rb') as fh:
        n = os.fstat(fh.fileno()).st_size
        N = n - args.l + 1
        s_count = ceil((10 * N) / (A**2))
        text_log.info(
            'with A={A} sampling {s_count:,} (={s_frac:.4%}) of {N:,} {l}-length-substrings '
            .format(A=A, s_count=s_count, s_frac=s_count / N, N=N, l=args.l))
        x = ss_est.distinct_in_sample(fh, args.l, s_count)
        est = round(x * A)
        low = ceil(x)
        high = floor(est * A)
        text_log.info(
            'estimated {est:,} uniques (={u_frac:.4%} uniques). sample had {x:,} uniques (={su_frac:.4%} uniques).'
            .format(est=est, u_frac=est / N, x=x, su_frac=x / s_count))
        text_log.info(
            'number of uniques should be between {low:,} and {high:,} ({low_frac:.4%}-{high_frac:.4%})'
            .format(low=low, high=high, low_frac=low / N, high_frac=high / N))

    # logging {{{
    end_time = datetime.datetime.now()
    data = OrderedDict([
        ('start time', start_time.strftime('%Y-%m-%d %H:%M:%S')),
        ('runtime', end_time - start_time),
        ('file', os.path.split(args.infile)[1]),
        ('filesize', n),
        ('A', args.A),
        ('ss len', args.l),
        ('in sample', x),
        ('estimate', est),
        ('estimate-unrounded', x * A),
        ('high', high),
        ('low', low),
    ])
    if not args.nologheader:
        data_log.info('')
    data_log.info(dicts_to_tsv([data], headers=(not args.nologheader)))
    # }}}


################################
# utils


def dicts_to_tsv(dicts, headers=True):
    for d in dicts[1:]:
        assert isinstance(d, OrderedDict)
        assert set(d.keys()) == set(dicts[0].keys())
    s = ''
    keys = dicts[0].keys()
    if headers:
        s += '\t'.join([str(k) for k in keys])
        s += '\n'
    for (i, d) in enumerate(dicts):
        s += '\t'.join([str(d[k]) for k in keys])
        if not i == len(dicts) - 1:
            s += '\n'
    return s


################################
# args

parser = argparse.ArgumentParser(description='''
Some utilities for counting number the of distinct substrings of different lengths in a file.'''
                                 )
subparsers = parser.add_subparsers()


def add_shared_arguments(subparser):
    subparser.add_argument('infile', help='input file')
    subparser.add_argument('-l',
                           type=int,
                           help='maximum substring length (like "l_0")')
    subparser.add_argument('-L',
                           '--log',
                           action='store_true',
                           help='verbose logging into logfile')
    subparser.add_argument('--nologheader',
                           action='store_true',
                           help='omit column headers in logs')


parse_fulldss = subparsers.add_parser(
    'fulldss', help='count distinct substrings non-sublinearly')
parse_fulldss.add_argument('method',
                           type=str,
                           help='''
one of: sanity, hll, trie  (sanity: count naively, exact counts; hll: count with HyperLogLog, approximate counts; trie: count using a trie in a certain way; exact counts)
                           ''')
add_shared_arguments(parse_fulldss)
parse_fulldss.set_defaults(func=cmd_fulldss)

parse_sldss = subparsers.add_parser(
    'sldss', help='count distinct substrings sublinearly')
parse_sldss.add_argument('-A', type=float, help='max multiplicative error')
add_shared_arguments(parse_sldss)
parse_sldss.set_defaults(func=cmd_sldss)

################################

if __name__ == '__main__':
    args = parser.parse_args()
    assert os.path.isfile(args.infile)
    args.func(args)
