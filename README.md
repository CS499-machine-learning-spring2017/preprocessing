# Preprocessing 
## Purpose is to format the input file which is binary into a useable format for the neural network

## Binary File format
Expected file format is to have the height and width on the first line not in binary, then the following line to contain binary data.

##Usage
```
from preprocessing import preprocess

for (data, classifier) in preprocess( inputFile, alphaFile, windowsize):
    #do_something_with_data()
```
for preprocess function takes two matching size files, one containing training data, and the other containing classification data. It will decode the binary data and save the files into a csv file. From there it will take the data in the csv and return back a flat list contining integers and a single integer as the classifier.
