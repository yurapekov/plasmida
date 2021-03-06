#!/usr/bin/env python3.3

import sys
import os
import argparse
import collections

# class for each species
class Species():
    def __init__(self, name='new species'):
        self.name = name # name of species
        self.strainList = [] # list of strains for this species
        self.consensus = [] # output consensus for this species
        self.checkCons = [] # secondary consensus

# class for each species
class Strain():
    def __init__(self, name, start):
        self.name = name # str, name of strain
        self.start = start # int, start position of the strain sequence
        self.seq = [] # list, strain sequence

# return length of the input sequence
def getSeqLen(seq):
    return len(seq) - seq.count('-')

# return data from each alignment string of input file
def parseString(line):
    splitted = line.split()
    species = splitted[0].split('|', 1)[0]
    strain = splitted[0].split('|', 1)[1]
    seq = list(splitted[1])
    position = splitted[2]
    return species, strain, seq, position

# return name of the output consensus file
def getSmallOutFileName(species, suffix=''):
    return '%s.%s.%stxt' % (species.name.replace('|','.'), species.strainList[0].name.replace('|', '.'), suffix)

# check that there is no gap in position of consensus
def checkNoGapInSmallOutput(species, k):
    noGap = True
    if species.strainList[0].seq[k] == '-':
        noGap = False
    return noGap

# print alignment block for consensus output file
def printBlockInSmallOutput(species, outFile, start, end):
    for i in range(start, end):
        if checkNoGapInSmallOutput(species, i):
            outFile.write(species.strainList[0].seq[i])
    outFile.write('\n')
    for i in range(start, end):
        if checkNoGapInSmallOutput(species, i):
            outFile.write(species.consensus[i])
    outFile.write('\n')

# print data for consensus output file
def getSmallOutput(species, outFile, args):
    seqLen = len(species.strainList[0].seq)
    i = 0
    for i in range(args.blockLen, seqLen, args.blockLen):
        printBlockInSmallOutput(species, outFile, i - args.blockLen, i)
        outFile.write('\n')
    printBlockInSmallOutput(species, outFile, i, seqLen)

# print each number of gaps in divis output file
def printBlockInGapCountOutput(species, outFile, args, start, end, tab=0):
    tabBetween = 0
    if tab > 0:
        outFile.write(''.ljust(tab))
        tabBetween = args.gapCountLen
    i = start
    for i in range(start + args.gapCountLen, end, args.gapCountLen):
        outFile.write(str(species.consensus[i - args.gapCountLen:i].count('-')).ljust(tabBetween))
        if tab == 0:
            outFile.write('\n')
    outFile.write(str(species.consensus[i:end].count('-')).ljust(tabBetween))
    outFile.write('\n')

# print data for divis output file
def getGapCountOutput(species, outFile, args):
    seqLen = len(species.strainList[0].seq)
    i = 0
    for i in range(args.blockLen, seqLen, args.blockLen):
        printBlockInGapCountOutput(species, outFile, args, i - args.blockLen, i)
    printBlockInGapCountOutput(species, outFile, args, i, seqLen)

# print data for alignment output file
def getBigOutput(speciesList, outFile, args):
    seqLen = len(speciesList[0].strainList[0].seq)

    # get maximal length of description (name of species + name of strain) in order to proper alignment
    maxNameLen = 0
    for species in speciesList:
        for strain in species.strainList:
            nameLen = len('%s|%s' % (species.name, strain.name))
            if nameLen > maxNameLen:
                maxNameLen = nameLen

    # print blocks of output alignment
    i = 0
    for i in range(args.blockLen, seqLen, args.blockLen):
        printBlockInBigOutput(speciesList, outFile, maxNameLen, args, i - args.blockLen, i) 
    printBlockInBigOutput(speciesList, outFile, maxNameLen, args, i, seqLen) 

# print block of alignment for alignment output file
def printBlockInBigOutput(speciesList, outFile, maxNameLen, args, start, end):
    # set spaces between columns
    tabFirst = 6
    tabSecond = 3

    for species in speciesList:
        for strain in species.strainList:
            combinedName = '%s|%s' % (species.name, strain.name)
            position = strain.start + getSeqLen(strain.seq[0:end])
            outFile.write('%s%s%s%s%d\n' % (combinedName.ljust(maxNameLen), ''.ljust(tabFirst), ''.join(strain.seq[start:end]), ''.ljust(tabSecond), position))
        outFile.write('%s%s%s\n' % (''.ljust(maxNameLen), ''.ljust(tabFirst), ''.join(species.consensus[start:end])))
        printBlockInGapCountOutput(species, outFile, args, start, end, tab=tabFirst + maxNameLen)
    outFile.write('\n\n')

# create consensus output file
def generateSmallOutputFile(speciesList, args):
    for species in speciesList:
        outFile = open(getSmallOutFileName(species), 'w', newline = args.lineBreakFormat)
        getSmallOutput(species, outFile, args)
        outFile.close()

# create divis output file
def generateGapCountFile(speciesList, args):
    for species in speciesList:
        outFile = open(getSmallOutFileName(species, suffix='divis.'), 'w', newline = args.lineBreakFormat)
        getGapCountOutput(species, outFile, args)
        outFile.close()

# create alignment output file (Alignment.consensus.txt)
def generateBigOutputFile(speciesList, args):
    outFile = open(args.outFileName, 'w', newline = args.lineBreakFormat)
    getBigOutput(speciesList, outFile, args)
    outFile.close()

# create debugging output file (All.data.txt)
def generateDebugFile(speciesList, args):
    outFile = open(args.debugFileName, 'w', newline = args.lineBreakFormat)

    # write small data
    for species in speciesList:
        outFile.write('%s\n' % (getSmallOutFileName(species)))
        getSmallOutput(species, outFile, args)
        outFile.write('\n\n\n\n\n')

    # write big data
    getBigOutput(speciesList, outFile, args)

    outFile.close()

# return list of species from alignment of input file
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

# return secondary consensus for each position of species
def strainBpConsensus(bpList):
    if '-' in bpList:
        consensusBp = '>'
    else:
        firstBp = bpList[0]
        consensusBp = firstBp
        for bp in bpList:
            if bp != firstBp:
                consensusBp = 'N'
    return consensusBp

# check is this strain in this position could be distinguished from other strains 
def getDiff(diffList):
    diff = ''
    if len(diffList) == 0:
        diff = '?'
    elif False in diffList:
        diff = '*'
    else:
        diff = '-'
    return diff

# check if there is at least two pair of the identical letters in position of secondary alignment
def checkTwoPairs(bpList):
    commonList = collections.Counter(bpList).most_common(2)
    if len(commonList) == 2 and commonList[0][1] >= 2 and commonList[1][1] >= 2:
        atLeastTwoPairs = True
    else:
        atLeastTwoPairs = False
    return atLeastTwoPairs

# return consensus for each position of species
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

# add consensus strings for list of species
def getSpeciesConsensus(speciesList):
    # get subsidiary string with secondary strain consensus for each species
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
            if species.checkCons[i] == '>':
                species.consensus[i] = '>'

    return speciesList

def main():
    #[options]
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                      '--inFileName',
                      type = str,
                      help = ' [str], no default value')
    parser.add_argument('-o',
                      '--outFileName',
                      type = str,
                      default = 'Alignment.consensus.txt',
                      help = ' [str], default value = "Alignment.consensus.txt"')
    parser.add_argument('-d',
                      '--debugFileName',
                      type = str,
                      default = 'All.data.txt',
                      help = ' [str], default value = "All.data.txt"')
    parser.add_argument('-b',
                      '--blockLen',
                      type = int,
                      default = 60,
                      help = 'Length of output alignment block [int], default value = 60')
    parser.add_argument('-g',
                      '--gapCountLen',
                      type = int,
                      default = 20,
                      help = 'Length of alignment block in which we count gaps [int], default value = 20')
    parser.add_argument('-f',
                      '--lineBreakFormat',
                      type = str,
                      default = 'u',
                      help = 'Type of line breaks: "u" for unix "\\n", "w" for windows "\\r\\n" [str], default value = "u"')
    args = parser.parse_args()

    if args.inFileName == None:
        print('Please, define --inFileName parameter. To read help use -h. Program is broken.')
        sys.exit(1)

    if args.lineBreakFormat == 'u':
        args.lineBreakFormat = '\n'
    elif args.lineBreakFormat == 'w':
        args.lineBreakFormat = '\r\n'
    else:
        print('Type of line breaks: "u" for unix "\\n", "w" for windows "\\r\\n". Please, set another --lineBreakFormat parameter. To read help use -h. Program is broken.')
        sys.exit(1)
        
    if args.gapCountLen > args.blockLen:
        print('gapCountLen should be less or equal to blockLen. Please, define another --gapCountLen parameter. To read help use -h. Program is broken.')
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
