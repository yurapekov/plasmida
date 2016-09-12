#!/usr/bin/env python3.3

import sys
import os
import argparse
import collections

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

def getSmallOutFileName(species):
    return '%s.%s.txt' % (species.name, species.strainList[0].name)

def getSmallOutput(species):
    seqPrint = ''
    consensusPrint = ''
    seqLen = len(species.strainList[0].seq)
    for i in range(seqLen):
        if species.strainList[0].seq[i] != '-':
            seqPrint += species.strainList[0].seq[i]
            consensusPrint += species.consensus[i]
    return seqPrint, consensusPrint

def getBigOutput(speciesList, outFile, space=0):
    # get maximal length of description (name of species + name of strain) in order to proper alignment
    maxNameLen = 0
    for species in speciesList:
        for strain in species.strainList:
            nameLen = len('%s|%s' % (species.name, strain.name))
            if nameLen > maxNameLen:
                maxNameLen = nameLen

    # set spaces between columns
    tabFirst = 2
    tabSecond = 4

    for species in speciesList:
        for strain in species.strainList:
            combinedName = '%s|%s' % (species.name, strain.name)
            outFile.write('%s%s%s%s%s\n' % (combinedName.ljust(maxNameLen), ''.ljust(tabFirst), strain.seq, ''.ljust(tabSecond), strain.position))
        outFile.write('%s%s%s\n' % (''.ljust(maxNameLen), ''.ljust(tabFirst), species.consensus))
        for i in range(space):
            outFile.write('\n')

def generateSmallOutputFile(speciesList):
    for species in speciesList:
        seqPrint, consensusPrint = getSmallOutput(species)
        outFile = open(getSmallOutFileName(species), 'w')
        outFile.write('%s\n' % (seqPrint))
        outFile.write('%s\n' % (consensusPrint))
        outFile.close()

def generateBigOutputFile(speciesList, args):
    outFile = open(args.outFileName, 'w')
    getBigOutput(speciesList, outFile)
    outFile.close()

def generateDebugFile(speciesList, args):
    outFile = open(args.debugFileName, 'w')

    # write small data
    for species in speciesList:
        outFile.write('%s\n' % (getSmallOutFileName(species)))
        seqPrint, consensusPrint = getSmallOutput(species)
        outFile.write('%s\n' % (seqPrint))
        outFile.write('%s\n' % (consensusPrint))
        outFile.write('\n')
    outFile.write('\n\n\n')

    # write big data
    getBigOutput(speciesList, outFile, space=1)

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

def getDiff(diffList):
    diff = ''
    if len(diffList) == 0:
        diff = '?'
    elif False in diffList:
        diff = '*'
    else:
        diff = '-'
    return diff

def checkTwoPairs(bpList):
    commonList = collections.Counter(bpList).most_common(2)
    if len(commonList) == 2 and commonList[0][1] >= 2 and commonList[1][1] >= 2:
        atLeastTwoPairs = True
    else:
        atLeastTwoPairs = False
    return atLeastTwoPairs

def speciesBpConsensus(bpList):
    bpListLen = len(bpList)
    consensusBpList = ['0' for x in range(bpListLen)]
    if 'N' in bpList:
        consensusBpList = ['*' for x in range(bpListLen)]
    elif checkTwoPairs(bpList):
        consensusBpList = ['?' for x in range(bpListLen)]
    else:
        for i in range(bpListLen):
            diffList = []
            for k in range(bpListLen):
                if k != i:
                    if bpList[i] != bpList[k]:
                        diffList.append(True)
                    else:
                        diffList.append(False)
            consensusBpList[i] = getDiff(diffList)
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
                      '--outFileName',
                      type=str,
                      default = 'alignent.consensus.txt',
                      help = ' [str], default value = "alignment.consensus.txt"')
    parser.add_argument('-d',
                      '--debugFileName',
                      type=str,
                      default = 'all.data.txt',
                      help = ' [str], default value = "all.data.txt"')
    args = parser.parse_args()

    if args.inFileName == None:
        print("Please, define --inFileName parameter. To read help use -h. Program is broken.")
        sys.exit(1)

    # END_OF [options]

    speciesList = parseInputFile(args)
    speciesList = getSpeciesConsensus(speciesList)
    generateSmallOutputFile(speciesList)
    generateBigOutputFile(speciesList, args)
    generateDebugFile(speciesList, args)

    return 0
# def main

if __name__ == '__main__':
    sys.exit(main())
