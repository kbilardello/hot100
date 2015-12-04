#!/usr/bin/env python

# Reads in lyrics from data/lyrics/####hot100.atsv files
# Creates bag of words from lyrics

# Referenced for bag of words: https://www.kaggle.com/c/word2vec-nlp-tutorial/details/part-1-for-beginners-bag-of-words

import pandas
import re
from nltk.corpus import stopwords # import stop word list
from sklearn.feature_extraction.text import CountVectorizer
from os.path import isfile, join, basename
from os import listdir
import sys
import numpy as np

BAGSIZE = 100
LYRICS_PATH_TRAIN = 'data/sample_lyrics_train/'
LYRICS_PATH_TEST = 'data/sample_lyrics_test/'

# TODO: use pickle to place dataframes into files to reduce processing cost each time
# (have lyrics, years, artists, etc. already in dataframes)

# Searching set is faster than searching list--convert to set
stops = set(stopwords.words("english"))

# Usage: cleanLyrics(raw_lyrics)
# Input: string
# Output: lower case string with removed special characters except for apostrophes within a word (removes trailing apostrophes)
def cleanLyrics(raw_lyrics):
	# Remove non-letters, convert to lowercase, remove stop words
	letters_only = re.sub("[^-'a-zA-Z]", ' ', raw_lyrics)
	letters_only = re.sub("(-|'s)", '', letters_only)
	words = letters_only.lower().split()
	meaningful_words = [w.strip('\'') for w in words if not w in stops]
	return (" ".join(meaningful_words))

# Usage: printFeatures(vectorizer, trainDataFeatures)
def printFeatures(vectorizer, features):
	# Print counts of each word in vocabulary in sorted descending order
	vocab = vectorizer.get_feature_names()
	word_count = []
	dist = features.toarray().sum(axis=0) # flattens matrix
	for tag, count in zip(vocab, dist):
		word_count.append((count, tag))
	word_count_sorted = sorted(word_count, key=lambda x: -x[0]) # decreasing
	for count, word in word_count_sorted:
		print count, word

# Usage: trainAvgFeatureVec = createAvgFeatureVec(vectorizer, trainDataFeatures)
def createAvgFeatureVec(vectorizer, features):
	# Useful for Naive Bayes, not used for Random Forest
	nwords = features.toarray().sum(axis=0).sum() # flattens matrix to single sum
	avgFeatureVec = []
	for feature in features:
		avgFeatureVec.append(feature/nwords)
	return avgFeatureVec

# Usage: getDF(PATH, train)
# Input: PATH = directory path that contains lyrics
# Input: train: True or False; True denotes training dataset, False denotes testing dataset
# Creates data frame that stores Hot100 number ranking for given year, Artist, Song, Lyrics, Year, Decade
# Decade column is left Null for testing dataset
def getDF(LYRICS_PATH, train):
	columns = ['NUM', 'ARTIST', 'SONG', 'LYRICS', 'YEAR', 'DECADE']
	df = pandas.DataFrame(columns=columns)

	# Ignores hidden files
	files = [f for f in listdir(LYRICS_PATH) if isfile(join(LYRICS_PATH,f)) and not f.startswith('.')]
	for FILE in files:
		df_singleFile = pandas.read_csv(LYRICS_PATH+FILE, \
			header=None, delimiter='@', na_filter=True, quoting=3, \
			names=['NUM', 'ARTIST', 'SONG', 'LYRICS'])
			# quoting=3 ignores double quotes

		# Adding YEAR column to data frame
		fileYear = int(FILE[:-len('hot100.atsv')])
		yearCol = pandas.DataFrame({'YEAR':[fileYear]*df_singleFile.shape[0]})
		df1 = pandas.concat([df_singleFile, yearCol], axis=1)

		# Add DECADE column to data frame for training set
		if train:
			fileDecade = fileYear//10*10
			decadeCol = pandas.DataFrame({'DECADE':[fileDecade]*df_singleFile.shape[0]})
			df1 = pandas.concat([df1, decadeCol], axis=1)

		# Clean lyrics in place
		num_lyrics = df1['LYRICS'].size
		# print "Cleaned %d of %d lyrics" % (0, num_lyrics)
		for i in range(num_lyrics):
			#if (i+1)%25 == 0:
			#	print "Cleaned %d of %d lyrics" % (i+1, num_lyrics)
			if not pandas.isnull(df1['LYRICS'][i]):
				df1.loc[i,'LYRICS'] = cleanLyrics(df1['LYRICS'][i])
		#print "Finished cleaning %d lyrics" % (num_lyrics)

		# Append new DF to master DF
		df = df.append(df1, ignore_index=True)
	return df

### Processing training set ###
trainDF = getDF(LYRICS_PATH_TRAIN, train=True)

# Initialize the "CountVectorizer" object, which is scikit-learn's bag of words tool.
vectorizer = CountVectorizer(analyzer = 'word',   \
                             tokenizer = split_tokenize,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             #max_features = BAGSIZE
                             )

# Fit model and learn vocabulary on existing lyrics
# Transform training data into feature vectors
trainDFNotNull = trainDF[pandas.notnull(trainDF['LYRICS'])]
trainDataFeatures = vectorizer.fit_transform(trainDFNotNull['LYRICS'])
#printFeatures(vectorizer, trainDataFeatures)

