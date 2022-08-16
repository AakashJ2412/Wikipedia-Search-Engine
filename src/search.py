import sys
import os
import re
import time
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
            tokenizedWords.append(word)
    stemmedWords = []
    for word in tokenizedWords:
        stemmedWords.append(stemmer.stemWord(word))
    return stemmedWords

if __name__ == "__main__":
    startTime = time.time()
    if(len(sys.argv) != 3):
        print("Invalid number of arguments")
        exit()
    indexFile = sys.argv[1]
    query = sys.argv[2]

    if not os.path.exists(indexFile):
        print("Invalid index file provided")
        exit()
    print("Loading Inverted Index...")
    readFile =  open(indexFile,"r")
    fileData = readFile.read()
    dataChunks = fileData.split(';')
    pageTitles = (dataChunks[-1][1:-1]).split('|')
    invertedIndex = defaultdict(int)
    for i in range(0,len(dataChunks)-2):
        indexData = dataChunks[i].split(':')
        invertedIndex[indexData[0]] = indexData[1].split('|')
    
    print("Parsing Query...")
    flagIds = {'n':query,'t':-1,'i':-1,'b':-1,'r':-1,'c':-1,'e':-1}
    prevFlag = 'n'
    prevFlagVal = len(query)
    for flag in re.finditer(r'(t|i|b|r|c|e):',query):
        if flagIds['n'] == query:
            flagIds['n'] = query[0:flag.start()]
        else:
            flagIds[prevFlag] = query[prevFlagVal+2:flag.start()]
        flagIds[query[flag.start()]] = query[flag.start()+2:]
        prevFlag = query[flag.start()]
        prevFlagVal = flag.start()

    documentScore = defaultdict(int)
    flagSet = ['t','i','b','r','c','e']
    scoreWeights ={'t':5, 'i':3,'b':1,'c':2,'r':0.5,'e':0.5}
    for key in flagIds.keys():
        flagIds[key] = cleanTokens(flagIds[key])
        for token in flagIds[key]:
            if(invertedIndex[token] != 0):
                for document in invertedIndex[token]:
                    documentId = ""
                    for ch in document:
                        if(ch in flagSet):
                            break
                        documentId += ch
                    documentId = int(documentId)
                    scoreIds = {'t':'','i':'','b':'','r':'','c':'','e':''}
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
                        if scoreKey == key:
                            documentScore[documentId] += 10*scoreWeights[scoreKey]*scoreIds[scoreKey]
                        else:
                            documentScore[documentId] += scoreWeights[scoreKey]*scoreIds[scoreKey]
                        #print(f"{key} {scoreIds[key]}")
    rankList = sorted(documentScore.items(),key=lambda kv: kv[1], reverse=True)
    rankCounter = 0
    for key in rankList:
        print(f"#{rankCounter+1}: {pageTitles[key[0]]} : Score {key[1]}")
        rankCounter += 1
        if(rankCounter == 10):
            break
                    