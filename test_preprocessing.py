#!/usr/bin/python3

import json
import os
from preprocessing import preprocess
import unittest

'''
Purpose: This is to test the integration process with preprocessing.py
This doesn't test every single function since those can easily change in
implementaion very easily. This does however test wether or not the output
given a certain input (i.e test files) will give the same, expected output.
If this passes, then the changes made are acceptable and can be used in production
'''
class TestPreprocessing(unittest.TestCase):
    TEST_FILE_INPUT = 'test_data/test.input'
    TEST_FILE_ALPHA = 'test_data/test.alpha'
    checkedOutput = [
        ([224, 230, 224, 225, 226, 229, 226, 225, 230], [0, 0, 0, 1, 0, 0, 0]),
        ([230, 224, 223, 226, 229, 227, 225, 230, 228], [0, 0, 0, 0, 1, 0, 0]),
        ([224, 223, 225, 229, 227, 230, 230, 228, 230], [1, 0, 0, 0, 0, 0, 0]),
        ([225, 226, 229, 226, 225, 230, 229, 226, 229], [0, 0, 0, 0, 0, 0, 1]),
        ([226, 229, 227, 225, 230, 228, 226, 229, 228], [0, 0, 1, 0, 0, 0, 0]),
        ([225, 230, 228, 226, 229, 228, 226, 226, 226], [0, 0, 0, 0, 0, 1, 0]),
        ([230, 228, 230, 229, 228, 227, 226, 226, 10], [0, 1, 0, 0, 0, 0, 0])
    ]
    counts = {224: 1, 225: 2, 219: 1, 220: 1, 221: 1, 222: 2, 223: 1}
    output = []
    expectedJsonInput = 'test_data/cleaned_test.input.json'
    expectedJsonAlpha = 'test_data/cleaned_test.alpha.json'
    expectedCsvInput = 'test_data/cleaned_test.input.csv'
    expectedCsvAlpha = 'test_data/cleaned_test.alpha.csv'

    def setUp(self):
        print("Starting to run preprocessing")
        self.output = preprocess(self.TEST_FILE_INPUT, self.TEST_FILE_ALPHA, 3)

    def test_check_for_csv_files(self):
        inputCsvFileExists = os.path.isfile(self.expectedCsvInput)
        alphaCsvFileExists = os.path.isfile(self.expectedCsvAlpha)
        self.assertEqual(bool(inputCsvFileExists and alphaCsvFileExists), True)

    def test_check_for_json_files(self):
        inputJsonFileExists = os.path.isfile(self.expectedJsonInput)
        alphaJsonFileExists = os.path.isfile(self.expectedJsonAlpha)
        self.assertEqual(bool(inputJsonFileExists and alphaJsonFileExists), True)

    def test_check_counts_in_json_file(self):
        infile_count = {}

        if(os.path.isfile(self.expectedJsonAlpha)):
            infile = open(self.expectedJsonAlpha, 'r')
            data = json.loads(infile.read())
            infile.close()
            cleaned_data = {int(k): int(v) for k,v in data.get('counts', {}).items() }
            infile_count = data.get('counts', {})
        self.assertEqual(cleaned_data, self.counts)

    def test_check_output(self):
        # This is the main test since it looks for completeness in data
        data = [i for i in self.output]
        self.assertEqual(data, self.checkedOutput)

if(__name__ == "__main__"):
    print("Starting to run tests now")
    unittest.main()
