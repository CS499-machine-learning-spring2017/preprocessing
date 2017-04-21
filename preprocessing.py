#!/usr/bin/env python3

from os import path
import csv
import sys
from collections import Counter
import json

class GroupData(object):
    '''
    inputData: csv file with input data
    classData: csv file with classifier data
    '''
    def __init__(self, inputData, classData):
        self.inputData = inputData
        self.classData = classData

    def getData(self, window):
        '''Returns a tuple with the flat data and the corresponding classifier'''
        line = self.inputData.getLine()
        classifier = self.classData.getClassifier()
        # print(self.classData.counts)
        minClassCounter = min(self.classData.counts.values())
        classCounter = {}
        rowcount = 0
        shouldContinue = True
        while shouldContinue:
            try:
                newline = next(line)
                newclassifier = next(classifier)
            except StopIteration:
                shouldContinue = False
            except IndexError:
                print("There was an issue with getting the correct information from the file!!!")
                newline = None
                newclassifier = None
                shouldContinue = False

            except Exception as e:
                print("unknown error: {}".format(e))
                print(newline, newclassifier)
                newline = None
                newclassifier = None
                shouldContinue = False

            if((newline is None) or (newclassifier is None)):
                break

            classCounter[newclassifier] = classCounter.get(newclassifier, 0) + 1
            if(classCounter[newclassifier] > minClassCounter):
                continue
            else:
                rowcount += 1
                yield (newline, newclassifier)
        print(rowcount)
        return None

class Data(object):
    '''
    csvfile: type string: Input file in csv format
    width: type int: width of each row for the csv file
    height: type int: number of rows in the csv file
    window: type int: number that describes the height and width of how much data the neural network will take in
    '''
    def __init__(self, csvfile, width, height, window, counts = {}):
        self.csvfile = csvfile
        self.width = width
        self.height = height
        self.window = window
        self.middleIndex = int(window // 2)
        self.counts = counts

    def initializeFrame(self, reader, datatype):
        '''
        Initializes lines for processing data
        '''
        if(datatype == 'line'):
            frame = []
            for _ in range(self.window):
                row = next(reader)
                row = list(map(int, row))
                frame.append(row)
            return frame
        else:
            for _ in range((self.window // 2)):
                next(reader)
            return

    def getLine(self):
        '''
        Takes a csv file and returns a generator function
        that will return a flat list of the moving window
        '''
        with open(self.csvfile) as infile:
            reader = csv.reader(infile)
            frames = self.initializeFrame(reader, "line")
            for row in reader:
                row = list(map(int, row))
                for currIndex in range(self.middleIndex, self.width - self.middleIndex):
                    minIndex = currIndex - self.middleIndex
                    maxIndex = currIndex + self.middleIndex + 1
                    newdata = [frame[minIndex: maxIndex] for frame in frames]
                    #flatten the moving window
                    yield [num for data in newdata for num in data]
                #get new frame
                frames = frames[1:] + [row]
        return


    def getClassifier(self):
        '''
        Opens a csv and yields the number in the middle of the moving window
        '''
        with open(self.csvfile) as infile:
            reader = csv.reader(infile)
            _ = self.initializeFrame(reader, "classifier")
            for row in reader:
                row = list(map(int, row))
                for currIndex in range(self.middleIndex, self.width - self.middleIndex):
                    yield row[currIndex]
        return

class Counts(object):

    def __init__(self, data, width, window):
        self.cleandata = data
        self.width = width
        self.halfwindow = window // 2
        self.counter = Counter()

    def count(self):
        for pos in range(0, len(self.cleandata), self.width):
            subdata = self.cleandata[pos: pos + self.width]
            subdata = subdata[self.halfwindow : -1 * self.halfwindow]
            self.counter.update(subdata)

    def data(self):
        return dict(self.counter)


def getDemensions(openfile):
    '''Get the height and width from the binary file'''
    try:
        dims = (openfile)
        dims = dims.strip().split(' ')
    except:
        dims = next(openfile)
        dims = dims.decode("utf-8")
        dims = dims.strip()
        dims = dims.split(' ')
    width, height = map(int, dims)
    return (width, height)

def cleandata(binary):
    '''converts from binary to decimal'''
    #convert binary to integers
#    data = binary.replace("0xff", "")
    return [d for d in binary]

def getFileName(file, extension = 'csv'):
    '''creates a new file'''
    filepath = file.split('/')
    filepath[-1] = "cleaned_" + filepath[-1] + "." + extension
    return  "/".join(filepath)

def getrows(data, width):
    '''gets rows for csv file'''
    for pos in range(0, len(data), width):
        yield data[pos: pos + width]

def saveToFile(filename, data, lineLength):
    '''creates new csv file from decoded binary data'''
    with open(filename, "w") as outfile:
        writer = csv.writer(outfile)
        for row in getrows(data, lineLength):
            rowstr = map(str, row)
            writer.writerow(rowstr)
    return filename

def countClassifiers(data, width, window):
    counts = Counts(data, width, window)
    counts.count()
    return counts.data()

def saveDemensions(file, width, height, window, cleaneddata, classifier):
    data = {'width':width, 'height':height, 'window': window}
    counts = None
    if(classifier):
        counts = countClassifiers(cleaneddata, width, window)
        data['counts'] = counts
    jsonFile = getFileName(file, "json")
    outfile = open(jsonFile, "w")
    outfile.write(json.dumps(data))
    outfile.close()
    return counts

def getJsonData(file):
    jsonFile = getFileName(file, "json")
    filename = getFileName(file)
    if(path.isfile(jsonFile)):
        data = json.loads((open(jsonFile).read()))
        width = data.get('width')
        height = data.get('height')
        window = data.get('window', 0)
        counts = data.get('counts', {})
        return (filename, width, height, window, counts)
    else:
        return(filename, 0, 0, -1, None)

def cleanBinary(file, classifier = False, window = 1):
    '''cleans the binary file as in converts from binary to integers'''
    filename, width, height, datawindow, counts = getJsonData(file)
    if(datawindow != window):
        binaryfile = open(file, "rb")
        width, height = getDemensions(binaryfile)
        cleaneddata = cleandata(binaryfile.read())
        filename = saveToFile(getFileName(file), cleaneddata, width)
        counts  = saveDemensions(file, width, height, window, cleaneddata, classifier)
        binaryfile.close()
    # print(filename, width, height, counts)
    return (filename, width, height, counts)

def getDataFromFiles(inputData, alphaData, window):
    '''
    returns a generator variable containing
    tuples of (flat_window, classifier)
    '''
    group = GroupData(inputData, alphaData)
    return group.getData(window)

def preprocess(inputFile, alphaFile, window):
    if (window % 2 == 0):
        raise Exception("Window must be an odd Integer")
    if (path.isfile(inputFile) and path.isfile(alphaFile)):
        (inputcsv, inputWidth, inputHeight, _) = cleanBinary(inputFile)
        (alphacsv, alphaWidth, alphaHeight, counts) = cleanBinary(alphaFile, classifier = True, window = window)
        if((inputWidth != alphaWidth) or (inputHeight != alphaHeight)):
            raise Exception("Non-matching data files")
        else:
            inputData = Data(inputcsv, inputWidth, inputHeight, window)
            alphaData = Data(alphacsv, alphaWidth, alphaHeight, window, counts)
#            groups = GroupData(inputData, alphaData)
            return getDataFromFiles(inputData, alphaData, window)
    else:
        raise Exception("One of the files don't exists, can't preprocess them")

if __name__ == "__main__":
    if(len(sys.argv) != 4):
        raise Exception("must include <inputFile> <alphaFile> <WindowSize>")
    _, inputFile, alphaFile, window = sys.argv
    preprocess(inputFile, alphaFile, int(window))
