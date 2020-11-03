import argparse

from md5 import MD5


def parse_args():
    parser = argparse.ArgumentParser(description="""""", usage='lcg [arguments] N')
    parser.add_argument('-f', help='file path', type=str)
    parser.add_argument('-m', help='text', type=str)
    parser.add_argument('-s', help='save to file', dest='filename', type=str)
    parser.add_argument('-t', help='test', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()

    md5 = None
    h = None

    if args.f:
        md5 = MD5(file_path=args.f)
    if args.m:
        md5 = MD5(string=args.m)

    if isinstance(md5, MD5):
        h = md5.hash()
        print('\033[92m' + h)

    if args.filename:
        with open(args.s, 'w') as file:
            file.write(h)

    if args.t:
        test_dict = {
            '': 'D41D8CD98F00B204E9800998ECF8427E',
            'a': '0CC175B9C0F1B6A831C399E269772661',
            'abc': '900150983CD24FB0D6963F7D28E17F72',
            'message digest': 'F96B697D7CB7938D525A2F31AAF161D0',
            'abcdefghijklmnopqrstuvwxyz': 'C3FCD3D76192E4007DFB496CCA67E13B',
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789': 'D174AB98D277D9F5A5611C2C9F419D9F',
            '12345678901234567890123456789012345678901234567890123456789012345678901234567890': '57EDF4A22BE3C955AC49DA2E2107B67A '
        }
        for k, v in test_dict.items():
            md = MD5(k)
            h = md.hash()
            if h == str.lower(v):
                print('\033[92m' + ' ' + h + ' ' + v)
            else:
                print('\033[91m' + ' ' + h + ' ' + v)


if __name__ == '__main__':
    main()
