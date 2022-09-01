from heapq import merge
import time
import re
import os
import sys
import math
from utils import *

class Merger:
    def __init__(self, indexDirectory, indexCount):
        self.indexDirectory = indexDirectory
        self.indexCount = indexCount

    def merge_files(self, file1, file2, iterationNo, fileNo):
        file1Pointer = open(file1, "r")
        file2Pointer = open(file2, "r")
        outPointer  = open(f'{self.indexDirectory}/index_{iterationNo}_{fileNo}.txt', "w")
        line1 = file1Pointer.readline().strip()
        line2 = file2Pointer.readline().strip()
        while line1 or line2:
            if not line1:
                while line2:
                    outPointer.write(line2)
                    line2 = file2Pointer.readline()
                break
            if not line2:
                while line1:
                    outPointer.write(line1)
                    line1 = file1Pointer.readline()
                break
            word1 = line1.split(":")
            word2 = line2.split(":")
            if word1[0] == word2[0]:
                index1 = word1[1].split("|")
                index2 = word2[1].split("|")
                outPointer.write(f"{word1[0]}:{'|'.join(sorted(index1 + index2))}\n")
                line1 = file1Pointer.readline().strip()
                line2 = file2Pointer.readline().strip()
            elif word1[0] < word2[0]:
                outPointer.write(f'{line1}\n')
                line1 = file1Pointer.readline().strip()
            else:
                outPointer.write(f'{line2}\n')
                line2 = file2Pointer.readline().strip()
        file1Pointer.close()
        file2Pointer.close()
        outPointer.close()
        

    def merge_index(self):
        mergeCounter = self.indexCount
        iterationCounter = math.ceil(math.log(self.indexCount)/math.log(2))
        for iterationId in range(iterationCounter):
            print("Merging iteration: ", iterationId)
            for fileId in range(1,mergeCounter,2):
                # print(f"Merging for iteration: {iterationId}, files: {fileId} {fileId+1}")
                file1 = f'{self.indexDirectory}/index_{iterationId}_{fileId}.txt'
                file2 = f'{self.indexDirectory}/index_{iterationId}_{fileId+1}.txt'
                self.merge_files(file1,file2,iterationId+1,(fileId+1)//2)
                os.remove(file1)
                os.remove(file2)
            if(mergeCounter%2 == 1):
                # print(f"Appended surplus file")
                os.rename(f'{os.getcwd()}/{self.indexDirectory}/index_{iterationId}_{mergeCounter}.txt', f'{os.getcwd()}/{self.indexDirectory}/index_{iterationId+1}_{mergeCounter//2 + 1}.txt')
            mergeCounter = mergeCounter//2 + mergeCounter%2

        masterPointer = open(f'{self.indexDirectory}/index_{iterationCounter}_1.txt', "r")
        masterLine = masterPointer.readline()
        indexCounter,lineCounter  = 0,0
        wordManager = open(f'{self.indexDirectory}/word_manager.txt', "w")
        indexPointer = open(f'{self.indexDirectory}/index_{indexCounter}.txt', 'w')
        indexTokens = set()
        while masterLine:
            indexPointer.write(masterLine)
            indexTokens.add(masterLine.split(":")[0])
            lineCounter += 1
            if lineCounter == maxIndexCount:
                wordManager.write(f"{masterLine.split(':')[0]}|")
                indexPointer.close()
                indexCounter += 1
                indexPointer = open(f'{self.indexDirectory}/index_{indexCounter}.txt', 'w')
                lineCounter = 0
            masterLine = masterPointer.readline()
        with open("stats.txt","w") as statsOut:
            indexSize = os.path.getsize(f'{self.indexDirectory}/index_{iterationCounter}_1.txt')
            statsOut.write(f"{round(indexSize/1048576,2)}\n{indexCounter}\n{len(indexTokens)}")
