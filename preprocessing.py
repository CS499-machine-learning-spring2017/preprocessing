#!/usr/bin/env python3

from os import path
import csv
import sys

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
        while True:
            try:
                newline = next(line)
                newclassifier = next(classifier)
            except IndexError:
                print("There was an issue with getting the correct information from the file!!!")
                newline = None
                newclassifier = None
            except Exception as e:
                newline = None
                newclassifier = None
                print("unknown error: {}".format(e))
            if((newline is None) or (newclassifier is None)):
                break
            else:
                yield (newline, newclassifier)

class Data(object):
    '''
    csvfile: type string: Input file in csv format
    width: type int: width of each row for the csv file
    height: type int: number of rows in the csv file
    window: type int: number that describes the height and width of how much data the neural network will take in
    '''
    def __init__(self, csvfile, width, height, window):
        self.csvfile = csvfile
        self.width = width
        self.height = height
        self.window = window
        self.middleIndex = int(window // 2)

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
            print(len(frames))
            for row in reader:
                row = map(int, row)
                for currIndex in range(self.middleIndex, self.width - self.middleIndex + 1):
                    minIndex = currIndex - self.middleIndex
                    maxIndex = currIndex + self.middleIndex + 1
                    newdata = [frame[minIndex: maxIndex] for frame in frames]
                    #flatten the moving window
                    yield [num for data in newdata for num in data]
                #get new frame
                frames = frames[1:] + [row]


    def getClassifier(self):
        '''
        Opens a csv and yields the number in the middle of the moving window
        '''
        with open(self.csvfile) as infile:
            reader = csv.reader(infile)
            _ = self.initializeFrame(reader, "classifier")
            for row in reader:
                row = list(map(int, row))
                for currIndex in range(self.middleIndex, self.width - self.middleIndex + 1):
                    yield row[currIndex]

def getDemensions(openfile):
    '''Get the height and width from the binary file'''
    try:
        dims = (openfile)
        dims = dims.strip().split(' ')
        print(dims)
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

def getFileName(file):
    '''creates a new file'''
    return "cleaned_" + file + ".csv"

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


def cleanBinary(file):
    '''cleans the binary file as in converts from binary to integers'''
    binaryfile = open(file, "rb")
    width, height = getDemensions(binaryfile)
    cleaneddata = cleandata(binaryfile.read())
    filename = saveToFile(getFileName(file), cleaneddata, width)
    binaryfile.close()
    return (filename, width, height)


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
        (inputcsv, inputWidth, inputHeight) = cleanBinary(inputFile)
        (alphacsv, alphaWidth, alphaHeight) = cleanBinary(alphaFile)
        if((inputWidth != alphaWidth) or (inputHeight != alphaHeight)):
            raise Exception("Non-matching data files")
        else:
            inputData = Data(inputcsv, inputWidth, inputHeight, window)
            alphaData = Data(alphacsv, alphaWidth, alphaHeight, window)
#            groups = GroupData(inputData, alphaData)
            return getDataFromFiles(inputData, alphaData, window)
    else:
        raise Exception("One of the files don't exists, can't preprocess them")

if __name__ == "__main__":
    if(len(sys.argv) != 4):
        raise Exception("must include <inputFile> <alphaFile> <WindowSize>")
    _, inputFile, alphaFile, window = sys.argv
    print(inputFile, alphaFile, window)
    preprocess(inputFile, alphaFile, int(window))
