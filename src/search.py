import sys
import os
import re
import time
import bisect
import math
from collections import defaultdict
import Stemmer
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
stops = stopwords.words('english')
stemmer = Stemmer.Stemmer('english')

def cleanTokens(text):
    if(text == -1):
        return []
    text = re.sub(r'&(lt|gt|amp|quot|apos|nbsp);',r' ', text)
    text = ''.join(ch if ch.isalnum() else ' ' for ch in text)
    tokenizedWords = []
    for word in text.split():
        if word not in stops:
            tokenizedWords.append(word.lower())
    stemmedWords = []
    for word in tokenizedWords:
        stemmedWords.append(stemmer.stemWord(word))
    return stemmedWords

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        print("Invalid number of arguments")
        exit()
    queryFile = sys.argv[1]

    if not os.path.exists(queryFile):
        print("Invalid query file provided")
        exit()
    print("Loading Queries...")
    readFile =  open(queryFile,"r")
    queries = readFile.readlines()
    queries = [query.strip() for query in queries]
    readFile.close()
    readFile = open(f"index/word_manager.txt")
    wordManager = readFile.read().split('|')[:-1]
    readFile.close()
    readFile = open(f"index/index_stats.txt", "r")
    statParams = readFile.read().split(' ')
    readFile.close()
    totalPages = int(statParams[1])
    titleBuffer = int(statParams[3])
    queryCounter = 0
    for query in queries:
        queryCounter += 1
        # print(f"\rParsing Query: {queryCounter}",end='')
        startTime = time.time()
        flagIds = {'n':query,'t':-1,'i':-1,'b':-1,'r':-1,'c':-1,'l':-1}
        prevFlag = 'n'
        prevFlagVal = len(query)
        for flag in re.finditer(r'(t|i|b|r|c|l):',query):
            if flagIds['n'] == query:
                flagIds['n'] = query[0:flag.start()]
            else:
                flagIds[prevFlag] = query[prevFlagVal+2:flag.start()]
            flagIds[query[flag.start()]] = query[flag.start()+2:]
            prevFlag = query[flag.start()]
            prevFlagVal = flag.start()
        
        documentScore = defaultdict(int)
        flagSet = ['t','i','b','r','c','l']
        scoreWeights ={'t':5, 'i':3,'b':1,'c':2,'r':0.5,'l':0.5}
        for key in flagIds.keys():
            flagIds[key] = cleanTokens(flagIds[key])
            for token in flagIds[key]:
                if(len(token) < 3):
                    continue
                indexId = bisect.bisect_left(wordManager, token)
                indexFile = open(f"index/index_{indexId}.txt", "r")
                ## Readlines implementation
                indexLines = indexFile.readlines()
                indexFile.close()
                wordData = []
                st, mid, end = 0, 0, len(indexLines) - 1
                while(st <= end):
                    mid = (st + end) // 2
                    if(indexLines[mid].startswith(f'{token}:')):
                        wordData = indexLines[mid].split(':')[1].strip().split('|')
                        break
                    elif(indexLines[mid][0:len(token)] < token):
                        st = mid + 1
                    else:
                        end = mid - 1

                ## Readline implementation
                # indexLine = indexFile.readline()
                # wordData = []
                # while indexLine:
                #     if indexLine.startswith(f'{token}:'):
                #         wordData = indexLine.split(':')[1].split('|')
                #     indexLine = indexFile.readline()
                # indexFile.close()
                if len(wordData) == 0:
                    continue
                # print(f"got word with len: {len(wordData)}")
                for document in wordData:
                    documentId = ""
                    for ch in document:
                        if(ch in flagSet):
                            break
                        documentId += ch
                    if(not documentId.isnumeric()):
                        continue
                    documentId = int(documentId)
                    scoreIds = {'t':'','i':'','b':'','r':'','c':'','l':''}
                    startFlag = 0
                    setFlag = ''
                    for ch in document:
                        if ch in flagSet:
                            startFlag = 1
                            setFlag = ch
                            continue
                        if startFlag == 0:
                            continue
                        scoreIds[setFlag] += ch
                    for scoreKey in scoreIds.keys():
                        if(scoreIds[scoreKey] == ''):
                            scoreIds[scoreKey] = '0'
                        scoreIds[scoreKey] = int(scoreIds[scoreKey])
                        tfScore = 0
                        idfScore = math.log(totalPages/len(wordData))
                        if scoreKey == key:
                            tfScore = math.log(1 + 10*scoreWeights[scoreKey]*scoreIds[scoreKey])
                        else:
                            tfScore = math.log(1 + scoreWeights[scoreKey]*scoreIds[scoreKey])
                        documentScore[documentId] += tfScore*idfScore
                        # print(f"{key} {scoreIds[key]}")
        rankList = sorted(documentScore.items(),key=lambda kv: kv[1], reverse=True)
        rankCounter = 0
        outFile = open('queries_op.txt','a')
        tempTime = time.time()
        for key in rankList:
            titleFile = int(key[0])//titleBuffer + 1
            titleId = int(key[0])%titleBuffer
            title = ""
            with open(f"index/title_{titleFile}.txt", "r") as titleFile:
                title = titleFile.read().split('|')[titleId]
                title = bytes.fromhex(title).decode('utf-8')
            outFile.write(f"{key[0]}, {title}\n")
            rankCounter += 1
            if(rankCounter == 10):
                break
        outFile.write(f"{time.time() - startTime}\n\n")
        outFile.close()
    print()