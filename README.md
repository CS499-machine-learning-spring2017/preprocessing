# Preprocessing 
## Purpose 
The purpose is to format the input files which are binary into a useable format for the neural network. This is done by first taking the files, which has to have binary data (see below), decodes it to decimal format and then saves it to a csv file. Then it is both the input and alpha file are reopened and then formatted so that the data comes back in an iterator of tuples with all numbers being type ints. The tuples contain ([< input data >], classifier). The input data is a flatten list of a "moving window". For example, if your window size was 5, you would get back a list of 25 numbers. The first 5 coming from the first row, the next 5 coming from the second row, and so on.

## Binary File format
Expected file format is to have the height and width on the first line not in binary, then the following line to contain binary data. All binary data is on one line.
Example:
```
1234 5678
< Binary Data  .... > 
```

## Usage
```
from preprocessing import preprocess

for (data, classifier) in preprocess( inputFile, alphaFile, windowsize):
    #do_something_with_data()
```
