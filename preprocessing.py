#!/usr/bin/env python3

from os import path
import csv
import sys
from collections import Counter
import json

'''
Preprocessing.py
The purpose of this file is to convert data from the input and alpha (classifiers) file
into usable data for the neural network

This is done by first opening the binary file and extracting the height and width from the first line.
Then the second line is one long string of binary data representing an image. From there, the classification are counted.
This is so we can proivide a uniform distribution of classifiers to the neural network.

From there, data about the files are saved to a Json file. This is so that if the file is there, then we can assume the file has been processed, thus skipping looping through the data and making the process faster.
The decoded data is formatted and saved to a csv file for the next step.

The final stop is to loop through the saved csv file and generating combinations of data for the neural network and the
corresponding classifier for that point on the image.
'''

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
<<<<<<< HEAD
        line_gen = self.inputData.getLine()
        classifier_gen = self.classData.getClassifier()
=======
        lineGen = self.inputData.getLine()
        classifierGen = self.classData.getClassifier()
>>>>>>> afd2779c52fa2f94719388d8eca9b62c91821055

        # print(self.classData.counts)
        # Find the minimun value of the classifier and limit all results to that 
        minClassCounter = min(self.classData.counts.values())
        #Create the one hot encoder
#        print(sorted(self.classData.counts.keys()))
        hotEncoder = self.getEncoder(sorted(self.classData.counts.keys()))
        # classification counter
        classCounter = {}
<<<<<<< HEAD
        # boolean variable describing if the loop should try and keep on generating data
        # print(self.classData.counts)
        shouldContinue = True
        for line, classifier in zip(line_gen, classifier_gen):
            classCounter[classifier] = classCounter.get(classifier, 0) + 1
            if(classCounter[classifier] <= minClassCounter):
                yield (line, hotEncoder[classifier])
            else:
                continue
        # print(classCounter)
=======
        for line, classifier in zip(lineGen, classifierGen):
            # No more information from files, end generating data
            if((line is None) or (classifier is None)):
                break
            # See if the classifier is below the max amount
            classCounter[classifier] = classCounter.get(classifier, 0) + 1
            if(classCounter[classifier] <= minClassCounter):
                # Return the flatten row of data and the one hot encoding classifier
                yield (newline, hotEncoder[newclassifier])
>>>>>>> afd2779c52fa2f94719388d8eca9b62c91821055

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
            # This is the starting point for the moving window for getting data
            for _ in range(self.window - 1):
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
            lastIndex = self.width - self.middleIndex
            reader = csv.reader(infile)
            # initialize the frames used to generate the data
            frames = self.initializeFrame(reader, "line")
            # For row in csv file
            for row in reader:
                # all data points must be integers
                row = list(map(int, row))
                frames.append(row)
                # loop through the data that doesn't include the edges
                for currIndex in range(self.middleIndex, lastIndex):
                    # Find the min and max index to extract from the current frame
                    minIndex = currIndex - self.middleIndex
                    maxIndex = currIndex + self.middleIndex + 1
                    # print(minIndex, maxIndex)
                    # take part of the row that is the window size so
                    # now you have a widow x window size list of list
                    # print("Getting a new frame")
                    dataframe = [frame[minIndex: maxIndex] for frame in frames]
                    #flatten the list of lists
                    data =  [num for data in dataframe for num in data]
                    # print("Here is the new data: {}".format(data))
                    yield data
                #remove top frame and replace it with a new one
                # print('removing the first element')
                frames.pop(0)
                # print('ready for the next round')
                # print(frames)

    def getClassifier(self):
        '''
        Opens a csv and yields the number in the middle of the moving window
        '''
        # open the csv file and make it a csv object
        infile = open(self.csvfile, 'r')
        data = infile.read()
        # print(data)
        infile.seek(0)
        infile.close()
        with open(self.csvfile) as infile:
            reader = csv.reader(infile)
            # remove the first few line in the csv to get rid of the edge data
            _ = self.initializeFrame(reader, "classifier")
            # For row in csv file
            lastIndex = self.width - self.middleIndex
            for row in reader:
                # make sure everything is an int
                row = list(map(int, row))
                # For each valid piece of data, yield it 
                for currIndex in range(self.middleIndex, lastIndex):
                    classifier = row[currIndex]
                    yield classifier
                # print(row)


class Counts(object):
    '''
    Controls counting the classifiers and handles how to do that
    cleandata = decimal data in list format
    halfwindow = half the window size rounded down
    counter = counter object to count all the data
    '''
    def __init__(self, data, width, window):
        #claned binary data
        self.cleandata = data
        # Width of the file
        self.width = width
        # half the window size rounded down
        self.halfwindow = window // 2
        # counter of the classifiers
        self.counter = Counter()

    def count(self):
        '''
        Counts the classifier data for the based on the window size
            against the width of the rows
        '''
        # batch the data into row
        skipLines = self.halfwindow
        pastUpdate = []
        for pos in range(0, len(self.cleandata), self.width):
            # Will have to skip the first few lines of the data
            # For the uniform distribution
            if(skipLines > 0):
                skipLines -= 1
                continue
            # Get extract part of the data
            subdata = self.cleandata[pos: pos + self.width]
            # Get the classifiers from the data that don't include the edge data
            subdata = subdata[self.halfwindow : -1 * self.halfwindow]
            # update the counter
            if(len(pastUpdate) == self.halfwindow):
                data = pastUpdate.pop(0)
                self.counter.update(data)
            # print(pastUpdate, subdata)
            pastUpdate.append(subdata)

def getDemensions(openfile):
    '''Get the height and width from the binary file'''
    dims = openfile.readline().strip()
#    dims = dims.strip('\n')[0]
    try:
        dims = dims.decode("utf-8")
        dims = dims.strip()
        dims = dims.split(' ')
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
    # print("before:\n{}".format(binary))
    data =  [d for d in binary]
    # print("After:\n{}".format(data))
    return data

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
    '''
    Counts the classifiers based on the data and the window size
        Handled in the Counts class above
    '''
    counts = Counts(data, width, window)
    # count everything up based on width and window size
    counts.count()
    # return a dictinary of the data
    return dict(counts.counter)

def saveDemensions(file, width, height, window, cleaneddata, classifier):
    '''
    Save the data in a json file
    '''
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
    '''
    Gets the data from a json file if it exists
    This will determine if decoding the input and alpha files are necessary
    '''
    jsonFile = getFileName(file, "json")
    filename = getFileName(file)
    # checks to see if the json file exists
    if(path.isfile(jsonFile)):
        # If it does, then it loads in the data
        data = json.loads((open(jsonFile).read()))
        # width of the data file
        width = int(data.get('width', 0))
        # height of the data file in rows of data
        height = int(data.get('height', 0))
        # window size for the moving window
        window = int(data.get('window', 0))
        # counts of the classifiers if it is for the classifier file
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
        # Width and height describing the data in the file
        width, height = getDemensions(binaryfile)
        # decode the data from binary to decimal
        cleaneddata = cleandata(binaryfile.read())
        # Crerate and save the data to a csv file
        filename = saveToFile(getFileName(file), cleaneddata, width)
        # get the counts from the file and and save the information about the file
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
    '''
    Purpose: This function is the main entry point for getting the information from the data files
        to the neural networks

    Inputs:
        InputFile: Data file containing input data
        AlphaFile: Data file containing the classifier data
        window: window-size for the moving window that generates the data
    '''

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
