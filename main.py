#!/usr/bin/env python3.3

import sys
import argparse
import subprocess
# project main
# main program file

class Species():
    def __init__(self, id, name='new species'):
        self.id = id
        self.name = name
        self.strainList = []
        self.consencus = ""

class Strain():
    def __init__(self, id, name='new strain'):
        self.id = id
        self.name = name
        self.seq = ""
        self.position = 0

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
