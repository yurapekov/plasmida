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
        self.consensus = '' 
        self.checkCons = '' 

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
    maxNameLen = 0
    for species in speciesList:
        for strain in species.strainList:
            nameLen = len('%s|%s' % (species.name, strain.name))
            if nameLen > maxNameLen:
                maxNameLen = nameLen
                
    tabFirst = 2
    tabSecond = 4
    inFileNameWithoutExt, inFileExt = os.path.splitext(args.inFileName)
    outFileName = '%s.%s%s' % (inFileNameWithoutExt, args.outSuffix, inFileExt)
    outFile = open(outFileName, 'w')
    for species in speciesList:
        for strain in species.strainList:
            combinedName = '%s|%s' % (species.name, strain.name)
            outFile.write('%s%s%s%s%s\n' % (combinedName.ljust(maxNameLen), ''.ljust(tabFirst), strain.seq, ''.ljust(tabSecond), strain.position))
        outFile.write('%s%s%s\n\n' % (''.ljust(maxNameLen), ''.ljust(tabFirst), species.consensus))
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
    return speciesList

def strainBpConsensus(bpList):
    firstBp = bpList[0]
    consensusBp = firstBp
    for bp in bpList:
        if bp != firstBp:
            consensusBp = 'N'
    return consensusBp

def speciesBpConsensus(bpList):
    bpListLen = len(bpList)
    consensusBpList = []
    if 'N' in bpList:
        consensusBpList = ['*' for x in range(bpListLen)]
    elif bpList.count(bpList[0]) == bpListLen:
        consensusBpList = ['*' for x in range(bpListLen)]
    else:
        consensusBpList = ['_' for x in range(bpListLen)]
    return consensusBpList

def getSpeciesConsensus(speciesList):
    seqLen = len(speciesList[0].strainList[0].seq)
    for species in speciesList:
        for i in range(seqLen):
            bpList = [strain.seq[i] for strain in species.strainList]
            species.checkCons += strainBpConsensus(bpList)
            
    for i in range(seqLen):
        bpList = [species.checkCons[i] for species in speciesList]
        consensusBpList = speciesBpConsensus(bpList) 
        for i, species in enumerate(speciesList):
            species.consensus += consensusBpList[i]
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
    speciesList = getSpeciesConsensus(speciesList)
    generateSmallOutputFile(speciesList)
    generateBigOutputFile(speciesList, args)

    return 0
# def main

if __name__ == '__main__':
    sys.exit(main())
