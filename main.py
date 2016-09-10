#!/usr/bin/env python3.3

import sys
import argparse
import subprocess
# project main
# main program file

def main():
    #[options]
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                      '--inFileName',
                      type=str,
                      help = ' [str], no default value')
    parser.add_argument('-o',
                      '--outFileName',
                      type=str,
                      default = 'plasmida',
                      help = ' [str], default value = plasmida')
    args = parser.parse_args()

    if args.inFileName == None:
        print("Please, define --inFileName parameter. To read help use -h. Program is broken.")
        sys.exit(1)

    # END_OF [options]

    return 0
# def main

if __name__ == '__main__':
    sys.exit(main())
