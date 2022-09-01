import time

def joinArray(array):
    return ' '.join(array)

def lowerString(text):
    return text.lower()

def updateString(str, id, ch):
    return str[:id] + ch + str[id + 1:]

startTime = time.time()
maxPageCount = 50000
maxIndexCount = 100000