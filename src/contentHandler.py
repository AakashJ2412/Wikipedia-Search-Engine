import xml.sax
import time
import re
import os
import sys
import Stemmer
from nltk.corpus import stopwords
from collections import Counter, defaultdict
from utils import *

class WikiHandler( xml.sax.ContentHandler ):
    def __init__(self):
        self.pageTitles = []
        self.title = []
        self.pageData = []
        self.body = []
        self.infobox = []
        self.category = []
        self.references = []
        self.externlinks = []
        self.invertedIndex = defaultdict(list)
        self.pageCount = 0
        self.totalTokens = 0
        self.CurrentData = ""
        self.stopwords = set(stopwords.words('english'))
        self.extrastops = set(["ref", "reflist", "caption", "infobox", "wiki", "image", "url", "http", "https", "category", "html", "com", "links", "other", "wikiproject"])
        self.stemmer = Stemmer.Stemmer('english')

    def updateIndex(self, pageId):
        pageDictionary = set(self.title + self.infobox + self.body + self.category + self.references + self.externlinks)
        for elem in list(pageDictionary):
            if len(elem) > 15:
                pageDictionary.remove(elem)
            elif len(elem) < 2:
                pageDictionary.remove(elem)
        invIndex = defaultdict.fromkeys(pageDictionary,'')
        titleCounter = Counter(self.title)
        infoboxCounter = Counter(self.infobox)
        bodyCounter = Counter(self.body)
        categoryCounter = Counter(self.category)
        referencesCounter = Counter(self.references)
        externCounter = Counter(self.externlinks)
        
        for word in list(pageDictionary):
            indString = ""
            t,i,b,c,r,e = titleCounter.get(word,0),infoboxCounter.get(word,0), bodyCounter.get(word,0), categoryCounter.get(word,0), referencesCounter.get(word,0),externCounter.get(word,0)
            # if t+i+b+c+r+e == 1:
            #     del(invIndex[word])
            #     continue
            if(t):
                indString += f"t{t}"
            if(i):
                indString += f"i{i}"
            if(b):
                indString += f"b{b}"
            if(c):
                indString += f"c{c}"
            if(r):
                indString += f"r{r}"
            if(e):
                indString += f"e{e}"    
            else:
                invIndex[word] = indString
        
        for word in invIndex.keys():
            self.invertedIndex[word].append(f"{pageId}{invIndex[word]}")
        
    def writeInvIndex(self,filePath):
        with open(filePath,"w") as fileOut:
            for word, values in self.invertedIndex.items():
                fileOut.write(f"{word}:{'|'.join(values)};")
            fileOut.write(f"={'|'.join(self.pageTitles)}=")

    def getParams(self):
        return self.totalTokens, len(self.invertedIndex.keys())

    def cleanText(self, text):
        if(text == ""):
            return []
        text = re.sub(r'&(lt|gt|amp|quot|apos|nbsp);',r' ', text)
        text = ''.join(ch if ch.isalnum() else ' ' for ch in text)
        tokenizedWords = []
        for word in text.split():
            if word not in self.stopwords and word not in self.extrastops:
                tokenizedWords.append(word)
        self.totalTokens += len(tokenizedWords)
        stemmedWords = []
        for word in tokenizedWords:
            stemmedWords.append(self.stemmer.stemWord(word))
        return stemmedWords

    # Call when an element starts
    def startElement(self, tag, attributes):
        self.CurrentData = tag


    # Call when an elements ends
    def endElement(self, tag):
        if (tag == 'page'):      
            self.pageTitles.append((''.join(ch if ch.isalnum() else ' ' for ch in self.title[0])).lower())
            self.title = self.cleanText(lowerString(joinArray(self.title)))
            #print(self.pageData)
            if(len(self.pageData) > 0):
                self.pageData = lowerString(joinArray(self.pageData))
                infoboxId = re.search(r'\{\{[\s]*infobox', self.pageData)
                bodyId = 0
                if(infoboxId):
                    infoboxId = infoboxId.start()
                else:
                    infoboxId = -1
                refId = re.search(r'==[\s]*references[\s]*==',self.pageData)
                if(refId):
                    refId = refId.start()
                else:
                    refId = len(self.pageData) - 1
                categoryId = re.search(r'\[\[[\s]*category:',self.pageData[refId:])
                if(categoryId):
                    categoryId = categoryId.start()
                else:
                    categoryId = len(self.pageData) - 1
                externId = re.search(r'==[\s]*other links[\s]*==',self.pageData[refId:categoryId])
                if(externId):
                    externId = externId.start()
                else:
                    externId = categoryId

                if(infoboxId != -1):
                    infoboxData = ""
                    bracketCounter = 0
                    for i in range(infoboxId,refId):
                        c = self.pageData[i]
                        infoboxData += c
                        if c == '{':
                            bracketCounter += 1
                        elif c == '}':
                            bracketCounter -= 1
                        if bracketCounter == 0:
                            bodyId = i
                            break
                    self.infobox = self.cleanText(self.pageData[infoboxId:bodyId])
                self.body = self.cleanText(self.pageData[bodyId: refId])
                self.category = self.cleanText(joinArray(re.findall(r'\[\[[\s]*category:.*\]\]',self.pageData[refId:])))
                self.references = self.cleanText(self.pageData[refId:externId])
                self.externlinks = self.cleanText(self.pageData[externId:categoryId])

                self.updateIndex(self.pageCount)
                self.pageCount += 1

                self.pageData = []
                self.title = []
                self.body = []
                self.infobox = []
                self.category = []
                self.references = []
                self.externlinks = []
                if(self.pageCount % 10000 == 0):
                    print(f"For files: {self.pageCount} - {time.time() - startTime}")

    # Call when a character is read
    def characters(self, content):
        if self.CurrentData == 'text':
            self.pageData.append(content) 
        elif self.CurrentData == 'title':
            self.title.append(content)