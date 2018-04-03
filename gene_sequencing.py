#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF
#elif PYQT_VER == 'PYQT4':
    #from PyQt4.QtCore import QLineF, QPointF
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

class GeneSequencing:

    #Constants for backtracers
    global LEFT
    LEFT = 0
    global UP
    UP = 1
    global DIAG
    DIAG = 2

    def __init__( self ):
        pass

    # Main method for calculating the sequence alignments
    def align_all(self, sequences, banded, align_length):

        # sequences is the list of strings - one for every row/col item (same on each side)
        print(">ALIGNALL(): starting")

        sequenceLen = len(sequences)
        results = [] #this is a list of dictionaries
        # might be able to skip calculating when the strings are the same by comparing the indices before calling calcAlignCost

        for i in range(sequenceLen):
            jresults = []

            # We only want to compare two sequences once, so we fill redundant cells with 0's (only do the top half of the array)
            for n in range(i):
                #don't calc alignCost, this cell is redundant
                s = {'align_cost': 0,
                     'seqi_first100': 'abc-easy  DEBUG:(seq{}, {} chars,align_len={}{})'.format(i + 1,
                     len(sequences[i]),align_length,',BANDED' if banded else ''),
                     'seqj_first100': 'as-123--  DEBUG:(seq{}, {} chars,align_len={}{})'.format(j + 1,
                     len(sequences[j]),align_length,',BANDED' if banded else '')}
                jresults.append(s)

            for j in range(i, sequenceLen): # using i tells it to only do the top half of the array
                #print(">ALIGN(), comparing seq "+str(i) + " and seq "+str(j))

                alignCost, backPtrArray = self.calcAlignCost(sequences[i], sequences[j], banded, align_length)
                if alignCost == float('inf'):
                    seqiAlignment = "No Alignment Possible" #if the string lengths were too different,
                    seqjAlignment = "No Alignment Possible" # don't bother to calc the alignment strings
                else:
                    seqiAlignment, seqjAlignment = self.getSeqAlignments(sequences[i], sequences[j], backPtrArray, align_length)

                s = {'align_cost':alignCost,
                     'seqi_first100':seqiAlignment +'  DEBUG:(seq{}, {} chars,align_len={}{})'.format(i+1,
                         len(sequences[i]), align_length, ',BANDED' if banded else ''),
                     'seqj_first100':seqjAlignment +'  DEBUG:(seq{}, {} chars,align_len={}{})'.format(j+1,
                         len(sequences[j]), align_length, ',BANDED' if banded else '')}
                jresults.append(s)
            results.append(jresults)

        print(">ALIGNALL(): done")
        return results

    # Goes through the backPtrArray with the two seq's and determine what the alignment strings will be for them
    def getSeqAlignments(self, seq1, seq2, backPtrArray, alignLen):

        x = len(seq1)
        if x > alignLen:
            x = alignLen
        y = len(seq2)
        if y > alignLen:
            y = alignLen

        # convert strings to array so we can use list.insert() - convert these to strings and return them at the end
        seqiAlignment = list(seq1)
        seqjAlignment = list(seq2)

        # Backtrack through backPtrArray and build each alignment string

        while x is not 0 or y is not 0:
            if backPtrArray[x][y] is DIAG:
                # keep the two letters the same for each alignment str
                # don't change either alignment str but decrement x and y
                x -= 1
                y -= 1
            elif backPtrArray[x][y] is LEFT:
                # put a dash in the seqjAlignment string
                seqjAlignment.insert(x+1, '-')
                x -= 1  # move a column left

            elif backPtrArray[x][y] is UP:
                # put a dash in the seqiAlignment string
                seqiAlignment.insert(y+1, '-')
                y -= 1  # move a row up

        string1 = ''.join(seqiAlignment[0:100])
        string2 = ''.join(seqjAlignment[0:100])
        return string1, string2


    # Runs the dynamic programming algorithm on the two given sequences
    def calcAlignCost(self, seq1, seq2, banded, alignLen):
        # CONSTANTS
        MATCH = -3
        MISMATCH = 1
        INDEL = 5

        lenS1 = len(seq1)+1 # truncate seq1 if necessary
        if lenS1 > alignLen+1:
            lenS1 = alignLen+1
        lenS2 = len(seq2)+1 # truncate seq2 if necessary
        if lenS2 > alignLen+1:
            lenS2 = alignLen+1
        costArray, backPtrArray = self.initArrays(lenS1, lenS2)

        for x in range(1, lenS1): # for each row
            if banded:
                rowStart = x - 3
                if rowStart < 1:
                    rowStart = 1
                rowEnd = x + 4
                if rowEnd > lenS2:
                    rowEnd = lenS2 #x is the midpoint, midpoint + 4 will keep it within 7
            else:
                rowStart = 1
                rowEnd = lenS2

            for y in range(rowStart, rowEnd):  # for each column

                if seq1[x-1] == seq2[y-1]:
                    # they match diagonally
                    alignCost = costArray[x-1][y-1] + MATCH
                    #backPtrArray already has a diagonal for this spot
                else:
                    # mismatch diagonally
                    alignCost = costArray[x-1][y-1] + MISMATCH
                    #backPtrArray already has a diagonal for this spot

                if costArray[x-1][y] is not "-":
                    # you can try coming from the side of the current cell
                    leftCost = costArray[x-1][y] + INDEL
                    if leftCost < alignCost:
                        alignCost = leftCost
                        backPtrArray[x][y] = LEFT

                if costArray[x][y-1] is not "-":
                    # you can try coming from above the current cell
                    aboveCost = costArray[x][y-1] + INDEL
                    if aboveCost < alignCost:
                        alignCost = aboveCost
                        backPtrArray[x][y] = UP

                # alignCost is now the min value possible
                costArray[x][y] = alignCost

        # If one sequence is way longer than the other, most of the costArray is not used
        # and the bottom right corner is still going to have the value it was init'd to (0)
        if banded:
            if abs(lenS1-lenS2) > 100: # "significant length discrepancies"
                return float('inf'), backPtrArray  # no alignment possible because the strings were too different
            value = costArray[lenS1-1][lenS2-1]
            return value, backPtrArray

        value = costArray[lenS1-1][lenS2-1]
        return value, backPtrArray


    # initializes the 2D costArray to be all 0's with the first row/col being multiples of 5
    # intiializes the 2D backPtrArray
    # (lenS1 and lenS2 have already had +1 applied)
    def initArrays(self, lenS1, lenS2):
        #init costArray to be full of 0's
        costArray = [["-" for x in range(lenS2)] for y in range(lenS1)] #TEST
        #init backPtrArray to always a diagonal, and changing it to leftside/above later if necessary
        backPtrArray = [[DIAG for x in range(lenS2)] for y in range(lenS1)]

        # init the first row/col of costArray to be multiples of 5
        # init the first row/col of backPtrArray to be all left (first row) and all up (first col)
        for x in range(lenS1):
            costArray[x][0] = x * 5
            backPtrArray[x][0] = LEFT
        for y in range(lenS2):
            costArray[0][y] = y * 5
            backPtrArray[0][y] = UP

        return costArray, backPtrArray
