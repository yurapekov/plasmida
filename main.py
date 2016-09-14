#!/usr/bin/env python3.3

import sys
import os
import argparse
import collections

class Species():
    def __init__(self, name='new species'):
        self.name = name
        self.strainList = []
        self.consensus = []
        self.checkCons = [] 

class Strain():
    def __init__(self, name, start):
        self.name = name # str
        self.start = start # int
        self.seq = [] # list

def getSeqLen(seq):
    return len(seq) - seq.count('-')

def parseString(line):
    splitted = line.split()
    species = splitted[0].split('|')[0]
    strain = splitted[0].split('|')[1]
    seq = list(splitted[1])
    position = splitted[2]
    return species, strain, seq, position

def getSmallOutFileName(species):
    return '%s.%s.txt' % (species.name, species.strainList[0].name)

def getGapCountFileName(species):
    return '%s.%s.divis.txt' % (species.name, species.strainList[0].name)

def checkNoGapInSmallOutput(species, k):
    noGap = True
    if species.strainList[0].seq[k] == '-':
        noGap = False
    return noGap

def printBlockInSmallOutput(species, outFile, start, end):
    for i in range(start, end):
        if checkNoGapInSmallOutput(species, i):
            outFile.write(species.strainList[0].seq[i])
    outFile.write('\n')
    for i in range(start, end):
        if checkNoGapInSmallOutput(species, i):
            outFile.write(species.consensus[i])
    outFile.write('\n')

def getSmallOutput(species, outFile, args):
    seqLen = len(species.strainList[0].seq)
    for i in range(args.blockLen, seqLen, args.blockLen):
        printBlockInSmallOutput(species, outFile, i - args.blockLen, i)
        outFile.write('\n')
    printBlockInSmallOutput(species, outFile, i, seqLen)

def printBlockInGapCountOutput(species, outFile, args, start, end, tab=0):
    tabBetween = 3
    if tab > 0:
        outFile.write(''.ljust(tab))
        tabBetween = args.gapCountLen
    for i in range(start + args.gapCountLen, end, args.gapCountLen):
        outFile.write(str(species.consensus[i - args.gapCountLen:i].count('-')).ljust(tabBetween))
    outFile.write(str(species.consensus[i:end].count('-')).ljust(tabBetween))
    outFile.write('\n')

def getGapCountOutput(species, outFile, args):
    seqLen = len(species.strainList[0].seq)
    for i in range(args.blockLen, seqLen, args.blockLen):
        printBlockInGapCountOutput(species, outFile, args, i - args.blockLen, i)
    printBlockInGapCountOutput(species, outFile, args, i, seqLen)

def getBigOutput(speciesList, outFile, args, space=0):
    seqLen = len(speciesList[0].strainList[0].seq)

    # get maximal length of description (name of species + name of strain) in order to proper alignment
    maxNameLen = 0
    for species in speciesList:
        for strain in species.strainList:
            nameLen = len('%s|%s' % (species.name, strain.name))
            if nameLen > maxNameLen:
                maxNameLen = nameLen

    for i in range(args.blockLen, seqLen, args.blockLen):
        printBlockInBigOutput(speciesList, outFile, maxNameLen, space, args, i - args.blockLen, i) 
    printBlockInBigOutput(speciesList, outFile, maxNameLen, space, args, i, seqLen) 

def printBlockInBigOutput(speciesList, outFile, maxNameLen, space, args, start, end):
    # set spaces between columns
    tabFirst = 6
    tabSecond = 3

    for species in speciesList:
        for strain in species.strainList:
            combinedName = '%s|%s' % (species.name, strain.name)
            position = strain.start + getSeqLen(strain.seq[0:end])
            outFile.write('%s%s%s%s%d\n' % (combinedName.ljust(maxNameLen), ''.ljust(tabFirst), ''.join(strain.seq[start:end]), ''.ljust(tabSecond), position))
        outFile.write('%s%s%s\n' % (''.ljust(maxNameLen), ''.ljust(tabFirst), ''.join(species.consensus[start:end])))
        if space > 0:
            printBlockInGapCountOutput(species, outFile, args, start, end, tab=tabFirst + maxNameLen)
        for i in range(space):
            outFile.write('\n')
    outFile.write('\n\n')

def generateSmallOutputFile(speciesList, args):
    for species in speciesList:
        outFile = open(getSmallOutFileName(species), 'w')
        getSmallOutput(species, outFile, args)
        outFile.close()

def generateGapCountFile(speciesList, args):
    for species in speciesList:
        outFile = open(getGapCountFileName(species), 'w')
        getGapCountOutput(species, outFile, args)
        outFile.close()

def generateBigOutputFile(speciesList, args):
    outFile = open(args.outFileName, 'w')
    getBigOutput(speciesList, outFile, args)
    outFile.close()

def generateDebugFile(speciesList, args):
    outFile = open(args.debugFileName, 'w')

    # write small data
    for species in speciesList:
        outFile.write('%s\n' % (getSmallOutFileName(species)))
        getSmallOutput(species, outFile, args)
        outFile.write('\n')
    outFile.write('\n\n\n')

    # write big data
    getBigOutput(speciesList, outFile, args, space=1)

    outFile.close()

def parseInputFile(args):
    speciesList = []
    inFile = open(args.inFileName)
    for line in inFile:
        line = line.strip()
        if not (line.startswith('CLUSTAL') or line.startswith('*') or line == ''):
            curSpecies, curStrain, seq, position = parseString(line)

            # check if species already in the list, then define index of found species or create new species
            speciesIndex = -1
            for i, species in enumerate(speciesList):
                if curSpecies == species.name:
                    speciesIndex = i
            if speciesIndex == -1:
                newSpecies = Species(curSpecies)
                speciesList.append(newSpecies)
                speciesIndex = len(speciesList) - 1

            # check if strain already in the list, then define index of found strain or create new strain
            strainIndex = -1
            for i, strain in enumerate(speciesList[speciesIndex].strainList):
                if curStrain == strain.name:
                    strainIndex = i
            if strainIndex == -1:
                start = int(position) - getSeqLen(seq)
                newStrain = Strain(curStrain, start)
                speciesList[speciesIndex].strainList.append(newStrain)
                strainIndex = len(speciesList[speciesIndex].strainList) - 1

            # add seq to strain
            speciesList[speciesIndex].strainList[strainIndex].seq.extend(seq)

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
    # get subsidiary string with strain consensus for each species
    seqLen = len(speciesList[0].strainList[0].seq)
    for species in speciesList:
        for i in range(seqLen):
            bpList = [strain.seq[i] for strain in species.strainList]
            species.checkCons += strainBpConsensus(bpList)
    
    # get species consensus for each species
    for i in range(seqLen):
        bpList = [species.checkCons[i] for species in speciesList]
        consensusBpList = speciesBpConsensus(bpList) 
        for k, species in enumerate(speciesList):
            species.consensus += consensusBpList[k]

    # replace '*' to '>' in case of gaps in strain consensus
    for i in range(seqLen):
        for species in speciesList:
            if species.checkCons[i] == '-':
                species.consensus[i] = '>'

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
                      default = 'alignment.consensus.txt',
                      help = ' [str], default value = "alignment.consensus.txt"')
    parser.add_argument('-d',
                      '--debugFileName',
                      type=str,
                      default = 'all.data.txt',
                      help = ' [str], default value = "all.data.txt"')
    parser.add_argument('-b',
                      '--blockLen',
                      type=int,
                      default = 60,
                      help = 'Length of output alignment block [int], default value = 60')
    parser.add_argument('-g',
                      '--gapCountLen',
                      type=int,
                      default = 20,
                      help = 'Length of alignment block in which we count gaps [int], default value = 20')
    args = parser.parse_args()

    if args.inFileName == None:
        print("Please, define --inFileName parameter. To read help use -h. Program is broken.")
        sys.exit(1)
        
    if args.gapCountLen > args.blockLen:
        print("gapCountLen should be less or equal to blockLen. Please, define another --gapCountLen parameter. To read help use -h. Program is broken.")
        sys.exit(1)

    # END_OF [options]

    speciesList = parseInputFile(args)
    speciesList = getSpeciesConsensus(speciesList)
    generateSmallOutputFile(speciesList, args)
    generateGapCountFile(speciesList, args)
    generateBigOutputFile(speciesList, args)
    generateDebugFile(speciesList, args)

    return 0
# def main

if __name__ == '__main__':
    sys.exit(main())
