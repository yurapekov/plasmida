#!/usr/bin/env python3.3

import sys
import os
import argparse
import subprocess
# project main
# main program file

class Species():
    def __init__(self, name='new species'):
        self.name = name
        self.strainList = []
        self.consensus = "consensus"

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

def generateSmallOutputFile(speciesList):
    for species in speciesList:
        outFileName = '%s.%s.txt' % (species.name, species.strainList[0].name)
        outFile = open(outFileName, 'w')
        outFile.write('%s\n' % (species.strainList[0].seq))
        outFile.write('%s\n' % (species.consensus))
        outFile.close()

def generateBigOutputFile(speciesList, args):
    inFileNameWithoutExt, inFileExt = os.path.splitext(args.inFileName)
    outFileName = '%s.%s%s' % (inFileNameWithoutExt, args.outSuffix, inFileExt)
    outFile = open(outFileName, 'w')
    for species in speciesList:
        for strain in species.strainList:
            outFile.write('%s|%s\t%s\t%s\n' % (species.name, strain.name, strain.seq, strain.position))
        outFile.write('\t\t%s\t\t\n' % (species.consensus))
    outFile.close()

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
                      '--outSuffix',
                      type=str,
                      default = 'Consensus',
                      help = ' [str], default value = Consensus')
    args = parser.parse_args()

    if args.inFileName == None:
        print("Please, define --inFileName parameter. To read help use -h. Program is broken.")
        sys.exit(1)

    # END_OF [options]

    speciesList = parseInputFile(args)
    generateSmallOutputFile(speciesList)
    generateBigOutputFile(speciesList, args)

    return 0
# def main

if __name__ == '__main__':
    sys.exit(main())
