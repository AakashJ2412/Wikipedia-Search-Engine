import sys
import os
import xml.sax
import time
import nltk
nltk.download('stopwords')
from contentHandler import WikiHandler
from merger import Merger
from utils import *

if __name__ == "__main__":
    startTime = time.time()
    if(len(sys.argv) != 3):
        print("Invalid number of arguments")
        exit()
    dumpFile = sys.argv[1]
    indexPath = sys.argv[2]

    if not os.path.exists(dumpFile):
        print("Invalid dump file provided")
        exit()
    if not os.path.isdir(indexPath):
        os.mkdir(indexPath)
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    print("Parsing dump file...")
    dataHandler = WikiHandler(indexPath)
    parser.setContentHandler(dataHandler)
    parsedData = parser.parse(dumpFile)
    indexParams = []
    with open(f"stats.txt", "r") as f:
        indexParams = (f.read()).split(' ')
        indexParams = [int(a) for a in indexParams]
    print("Merging index files...")
    mergeHandler = Merger(indexPath, indexParams[0])
    mergeHandler.merge_index()
    print(f"Finish Time: {time.time() - startTime}")