indexCount = 602
fileCounter = 0
wordManager = open(f'index/word_manager_main.txt', "w")
filePointer = open(f'index/indexer_{fileCounter}.txt', "w")
counter = 0
for i in range(0,603):
    print(f"\rIterating through file: {i}", end="")
    with open(f"index/index_{i}.txt", "r") as f:
        line = f.readline()
        while line:
            filePointer.write(line)
            counter += 1
            if(counter == 25000):
                wordManager.write(f"{line.split(':')[0]}|")
                filePointer.close()
                fileCounter += 1
                filePointer = open(f'index/indexer_{fileCounter}.txt', "w")
                counter = 0
            line = f.readline()     