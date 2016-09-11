#!/usr/bin/env python3.3

import sys
import argparse
import subprocess
# project main
# main program file

class Species():
    def __init__(self, name='new species'):
        self.name = name
        self.strainList = []
        self.consencus = ""

class Strain():
    def __init__(self, name, seq, position):
        self.name = name
        self.seq = seq
        self.position = position

def parseString(line):
    splitted = line.split()
    species = splitted[0].split('|')[0]
    strain = splitted[0].split('|')[1]
    seq = splitted[1]
    position = splitted[2]
    return species, strain, seq, position

#def generateSmallOutputFile(outFileName, speciesList):

def parseInputFile(args):
    speciesCount = -1
    curSpecies = ''
    curStrain = ''
    speciesList = []
    strainList = []
    newSpecies = Species()

    inFile = open(args.inFileName)
    for line in inFile:
        line = line.strip()
        if not (line.startswith('CLUSTAL') or line.startswith('*') or line == ''):
            species, strain, seq, position = parseString(line)
            if species != newSpecies.name:
                newSpecies = Species(species)
                speciesList.append(newSpecies)
                speciesCount += 1
            newStrain = Strain(strain, seq, position)
            speciesList[speciesCount].strainList.append(newStrain)
            '''
    for spe in speciesList:
         print(spe.name)
         for st in spe.strainList:
             print(st.name, st.seq)
            '''
    return speciesList


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

    speciesList = parseInputFile(args)


    return 0
# def main

if __name__ == '__main__':
    sys.exit(main())
