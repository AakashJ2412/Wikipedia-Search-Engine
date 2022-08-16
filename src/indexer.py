import sys
import os
import xml.sax
import time
import nltk
nltk.download('stopwords')
from contentHandler import WikiHandler

if __name__ == "__main__":
    startTime = time.time()
    if(len(sys.argv) != 4):
        print("Invalid number of arguments")
        exit()
    dumpFile = sys.argv[1]
    indexFile = sys.argv[2]
    statFile = sys.argv[3]

    if not os.path.exists(dumpFile):
        print("Invalid dump file provided")
        exit()
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    dataHandler = WikiHandler()
    parser.setContentHandler(dataHandler)
    parsedData = parser.parse(dumpFile)
    dataHandler.writeInvIndex(indexFile)
    firstParam, secondParam = dataHandler.getParams()
    with open(statFile,"w") as f:
        f.write(f"{firstParam} {secondParam}")
    print(f"Finish Time: {time.time() - startTime}")