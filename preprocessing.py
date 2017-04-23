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

    def getEncoder(self, values):
        encoder = {}
        # Loop through number of classifiers and 
        # generate One Hot encoding schema
        for i, num in enumerate(values):
            data = [0 for _ in range(len(values))]
            data[i] = 1
            # Save it in the dictionary
            encoder[int(num)] = data
        return encoder

    def getData(self, window):
        '''Returns a tuple with the flat data and the corresponding classifier'''
        # get the line and classifier generators to match them up
        # and return them to the neural network
        line = self.inputData.getLine()
        classifier = self.classData.getClassifier()
        # print(self.classData.counts)
        # Find the minimun value of the classifier and limit all results to that 
        minClassCounter = min(self.classData.counts.values())
        #Create the one hot encoder
        hotEncoder = self.getEncoder(sorted(self.classData.counts.keys()))
        classCounter = {}
        rowcount = 0
        shouldContinue = True
        while shouldContinue:
            try:
                newline = next(line)
                newclassifier = next(classifier)
            except StopIteration:
                # End of the data files
                shouldContinue = False
            except IndexError:
                # Error in getting the data.
                # this has been fixed but keeping this here so if there is a bug,
                # It doesn't crash the entire system
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

            # No more information from files, end generating data
            if((newline is None) or (newclassifier is None)):
                break

            # See if the classifier is below the max amount
            classCounter[newclassifier] = classCounter.get(newclassifier, 0) + 1
            if(classCounter[newclassifier] > minClassCounter):
                continue
            else:
                rowcount += 1
                # Return the flatten row of data and the one hot encoding classifier
                yield (newline, hotEncoder[newclassifier])
        # print(rowcount)
        return None

class Data(object):
    '''
    csvfile: type string: Input file in csv format
    width: type int: width of each row for the csv file
    height: type int: number of rows in the csv file
    window: type int: number that describes the height and width of how much data the neural network will take in
    middleIndex = The index to start indexing at to avoid getting the edge data since that can't be used
    counts = counts of the classifiers
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
            # build a list of frames where each frame is a row of data
            for _ in range(self.window):
                row = next(reader)
                row = list(map(int, row))
                frame.append(row)
            return frame
        else:
            # ignore upto the middle index amount of lines since those are edge and can't be used
            for _ in range(self.middleIndex):
                next(reader)
            return

    def getLine(self):
        '''
        Takes a csv file and returns a generator function
        that will return a flat list of the moving window
        '''
        #open the csv file
        with open(self.csvfile) as infile:
            reader = csv.reader(infile)
            # initialize the frames used to generate the data
            frames = self.initializeFrame(reader, "line")
            # For row in csv file
            for row in reader:
                row = list(map(int, row))
                # loop through the data that doesn't include the edges
                for currIndex in range(self.middleIndex, self.width - self.middleIndex):
                    minIndex = currIndex - self.middleIndex
                    maxIndex = currIndex + self.middleIndex + 1
                    # take part of the row that is the window size so
                    # now you have a widow x window size list of list
                    newdata = [frame[minIndex: maxIndex] for frame in frames]
                    #flatten the list of lists
                    yield [num for data in newdata for num in data]
                #remove top frame and replace it with a new one
                frames = frames[1:] + [row]

    def getClassifier(self):
        '''
        Opens a csv and yields the number in the middle of the moving window
        '''
        # open the csv file and make it a csv object
        with open(self.csvfile) as infile:
            reader = csv.reader(infile)
            # remove the first few line in the csv to get rid of the edge data
            _ = self.initializeFrame(reader, "classifier")
            # For row in csv file
            for row in reader:
                # make sure everything is an int
                row = list(map(int, row))
                # For each valid piece of data, yield it 
                for currIndex in range(self.middleIndex, self.width - self.middleIndex):
                    yield row[currIndex]

class Counts(object):
    '''
    Controls counting the classifiers and handles how to do that
    cleandata = decimal data in list format
    halfwindow = half the window size rounded down
    counter = counter object to count all the data
    '''
    def __init__(self, data, width, window):
        self.cleandata = data
        self.width = width
        self.halfwindow = window // 2
        self.counter = Counter()

    def count(self):
        # batch the data into row
        for pos in range(0, len(self.cleandata), self.width):
            subdata = self.cleandata[pos: pos + self.width]
            # Get the classifiers from the data that don't include the edge data
            subdata = subdata[self.halfwindow : -1 * self.halfwindow]
            self.counter.update(subdata)

def getDemensions(openfile):
    '''Get the height and width from the binary file'''
    dims = openfile.readline().strip()
#    dims = dims.strip('\n')[0]
    try:
        # First row of data in the data files are height and width
        dims = dims.strip().split(' ')
    except Exception as e:
        dims = [chr(dim) for dim in dims]
    dims = list(filter(lambda d: d != ' ', dims))
    dims = list(map(int, dims))
    width, height = dims
    return (width, height)

def cleandata(binary):
    '''converts from binary to decimal'''
    #convert binary to integers
    # decodes the data
    return [d for d in binary]

def getFileName(file, extension = 'csv'):
    '''creates a new file with the given extension in the folder the data is in'''
    filepath = file.split('/')
    filepath[-1] = "cleaned_" + filepath[-1] + "." + extension
    return  "/".join(filepath)

def getrows(data, width):
    '''gets rows for csv file'''
    # create batches of data given the width the data is suppose to be in
    # This will be fed into a csv file
    for pos in range(0, len(data), width):
        yield data[pos: pos + width]

def saveToFile(filename, data, lineLength):
    '''creates new csv file from decoded binary data'''
    with open(filename, "w") as outfile:
        writer = csv.writer(outfile)
        # for row in data to csv format
        for row in getrows(data, lineLength):
            # save the data
            writer.writerow(row)
    return filename

def countClassifiers(data, width, window):
    '''Counts the classifiers based on the data and the window size
        Handled in the Counts class above
    '''
    counts = Counts(data, width, window)
    # count everything up based on width and window size
    counts.count()
    # return a dictinary of the data
    return dict(counts.counter)

def saveDemensions(file, width, height, window, cleaneddata, classifier):
    # Save the data in a json file
    # This data is availible and need for each type of file
    data = {'width':width, 'height':height, 'window': window}
    counts = None
    # if the file contains classifications, find the counts
    if(classifier):
        counts = countClassifiers(cleaneddata, width, window)
        # save the counts in the data dictionary
        data['counts'] = counts
    # create the name for the json file
    jsonFile = getFileName(file, "json")
    # open it up for writing
    outfile = open(jsonFile, "w")
    # save the data
    outfile.write(json.dumps(data))
    # close the json file
    outfile.close()
    # return the counts for use in generating the data
    return counts

def getJsonData(file):
    jsonFile = getFileName(file, "json")
    filename = getFileName(file)
    # checks to see if the json file exists
    if(path.isfile(jsonFile)):
        # If it does, then it loads in the data
        data = json.loads((open(jsonFile).read()))
        width = int(data.get('width', 0))
        height = int(data.get('height', 0))
        window = int(data.get('window', 0))
        counts = data.get('counts', {})
        # Returns the data used to return more data to the neural network
        return (filename, width, height, window, counts)
    else:
        # else it returns the filename and the -1 for the winow will make 
        # the getDemensions function to run
        return(filename, 0, 0, -1, None)

def cleanBinary(file, classifier = False, window = 1):
    '''cleans the binary file as in converts from binary to integers'''
    # Get demensions if they exist
    filename, width, height, datawindow, counts = getJsonData(file)
    # if the window in the file is different than the one from input,
    # recalculate the counts
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
