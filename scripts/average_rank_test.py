import re
import os.path
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
from keras.models import load_model
from keras.losses import categorical_crossentropy
import tensorflow as tf

############################################################################################################
#													   #
# this is a test on traces that have been randomly permuted each time the test is run. This helps indicate #
# the variance of first time correct guesses. Tests only first keybyte.                                    #
#													   #
############################################################################################################


AES_Sbox = np.array([
            0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
            0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
            0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
            0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
            0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
            0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
            0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
            0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
            0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
            0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
            0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
            0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
            0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
            0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
            0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
            0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
            ])

#Unchanged from how ANSSI did, more or less. The key is hard coded in here to make it less prone to
#code error albeit more prone to human error. You could change the tests to load the key in the test
#but since the fixed key traces we used all have the same key it was never done.
#
#I leave some of their comments in here. But to summarize what the method does:
#it is a cumulative sum of log predictions for each possible keybyte value. We compare the sorted
#list of these predictions with the de facto real answer to find the rank of the real key value.
def rank(predictions, data, plaintext, min_trace_idx, max_trace_idx, last_key_bytes_proba, keybytePos = 0):
#	keyarray = [ 43, 126,  21,  22,  40, 174, 210, 166, 171, 247,  21, 136,   9, 207,  79,  60]
#	real_key = keyarray[0]
	keyarray2 = [ 26, 206, 149, 113, 251,  46,  52, 156,   5, 162, 215,  87,  29, 47, 187, 236]
	real_key = keyarray2[keybytePos]

	if len(last_key_bytes_proba) == 0:
		# If this is the first rank we compute, initialize all the estimates to zero
		key_bytes_proba = np.zeros(256)
	else:
		# This is not the first rank we compute: we optimize things by using the
		# previous computations to save time!
		key_bytes_proba = last_key_bytes_proba

	for p in range(0, max_trace_idx-min_trace_idx):
		for i in range(0, 256):
			proba = predictions[p][AES_Sbox[plaintext ^ i]]
			if proba != 0:
				key_bytes_proba[i] += np.log(proba)
			else:
				# We do not want an -inf here, put a very small epsilon
				# that correspondis to a power of our min non zero proba
				min_proba_predictions = predictions[p][np.array(predictions[p]) != 0]
				min_proba = min(min_proba_predictions)
				key_bytes_proba[i] += np.log(min_proba/2) #or divided by a larger
	# Now we find where our real key candidate lies in the estimation.
	# We do this by sorting our estimates and find the rank in the sorted array.
	sorted_proba = np.array(list(map(lambda a : key_bytes_proba[a], key_bytes_proba.argsort()[::-1])))
	real_key_rank = np.where(sorted_proba == key_bytes_proba[real_key])[-1][-1]
	return (real_key_rank, key_bytes_proba)


#This is how ANSSI did it. It's kind of a mess tbh, and their variable naming convention is unclear, but I'll explain it:
#
#Model is of course the model to be tested.
#Input_data is attack traces.
#Plaintext is attack plaintext.
#
#min_trace_idx I think is minimum trace index, same with max_trace_idx. They re used to select a specific range of traces.
#I don't know why they put it in here and we never use it. It can probably be removed.
#
#rank_step is another remnant of ANSSI code that probably should be removed somehow. They used to calculate the rank
#after seeing 10 traces at a time which gives better looking results. We changed it to use 1 trace per calculation so we
#get realistic results.
#
#Basically what this does is it calculates the rank progression in batches. We set the batch size to 1. Then it returns
#an array with the rank progression.
def full_ranks(model, input_data, plaintext, min_trace_idx, max_trace_idx, rank_step, keybytePos = 0):
	predictions = model.predict(input_data)
	index = np.arange(min_trace_idx+rank_step, max_trace_idx, rank_step)
	f_ranks = np.zeros((len(index), 2), dtype=np.uint32)
	key_bytes_proba = []
	for t, i in zip(index, range(0, len(index))):
		real_key_rank, key_bytes_proba = rank(predictions[t-rank_step:t], input_data, plaintext[t-rank_step:t], t-rank_step, t, key_bytes_proba, keybytePos)
		f_ranks[i] = [t - min_trace_idx, real_key_rank]
	return f_ranks


######################################################
##### This is where you'll want to change things #####
######################################################
#
#num_traces is how many traces you want the model to
#use for the test. We set the default to 50 since we
#want our models to out-perform CPA.
#
#numiter is how many times to run the rank test for
#calculating its mean value. We chose 1000 because
#testing was done on my laptop rather than PDC to
#not be limited by PDC priority scheduling. Running
#more than 1000 tests for calculating the average is
#very time consuming for batch testing. It could be
#done if a specific model needs very accurate tests.
#
#In this method you'll want to change the path to the
#attack traces and attack plaintext.
#
#The line where it says input_data[:,57:153] should
#be changed to reflect the input size
#
#The print statements are mainly for debugging
#purposes but I'd honestly recommend keeping them.
#
#After saving the results of 1000 tests the average
#is calculated and then the results are plotted.
#
#More interesting statistical analysis could be done
#here. I had some thoughts about plotting the mean,
#the lower quartile mean and the upper quartile mean.
#This could show expected good and bad performance.
#
#plots are saved and raw data is saved.



def check_model(model_file, traces, plaintexts, num_traces=50, numiter=100, interval = slice(57,153), keybyte = 0):
	model = load_model(model_file)
	results = np.zeros((numiter, num_traces-1, 2))
	input_data = traces
	input_data = input_data[:,interval]
	plaintext = plaintexts[:,keybyte]
	print(input_data.shape, ' = trace shape')
	print(plaintext.shape, ' = pt shape')
	for i in range(numiter):
		permutation = np.random.permutation(traces.shape[0])
		input_data = input_data[permutation,:]
		plaintext = plaintext[permutation]
		ranks = full_ranks(model, input_data[:num_traces,:], plaintext[:num_traces], 0, num_traces, 1, keybyte)
		results[i] = ranks
	x = [ranks[i][0] for i in range(0, ranks.shape[0])]
	y = [np.mean(results, axis = 0)[i][1] for i in range(0, ranks.shape[0])]
	plt.title('Performance of '+model_file+' against '+'XMega2FixedKey')
	plt.xlabel('number of traces')
	plt.ylabel('rank')
	plt.plot(x, y)
	filename = re.search('([^/]+$)', model_file).group(0)[:-3]
	npyfile = 'results/npyresults/' + filename + '_average_rank.npy'
	np.save(npyfile, results)
	filename = 'results/pdfresults/' + filename+ '_average_rank.pdf'
	plt.savefig(filename)
	plt.show(block=False)
	plt.figure()

#This method load traces stored at tracepath and loads
#plaintext stored at ptpath.

def load_traces(tracepath, ptpath):
	traces = np.load(tracepath)
	plaintext = np.load(ptpath)
	return traces, plaintext



######################################
##### Code starts executing here #####
######################################

#you can hard code which model you want to test in te
#to check all array (this is what the ANSSI team did).
#I changed it so you can instead call the code from the
#command line with the arguments being the path to the
#models you wish to train

###Example usage in linux console###
#
#
#~/projectdir $ python average_rank_test.py ourModels/*
#
#This command would run the test for every model
#saved in the ourModels folder
#
#
#~/projectdir $ python average_rank_test.py ourModels/EM_test[3-7]*
#
#This command would test all models named EM_test
#followed by any of the numbers 3-7. For example
#it would test EM_test3.h5 but it would not test
#EM_test2.h5. Useful for when training many models
#and you wish to only test the newest ones.


to_check_all = []
numtraces = 50
numiter = 100
tracestart = 57
traceend = 153
keybytepos = 0

if len(sys.argv) >= 3:
	numtraces = int(sys.argv[1])
	numiter = int(sys.argv[2])
	tracestart = int(sys.argv[3])
	traceend = int(sys.argv[4])
	keybytepos = int(sys.argv[5])
	tracefile = sys.argv[6]
	ptfile = sys.argv[7]
	to_check_all = [i for i in sys.argv][8:]

test_traces, test_pt = load_traces(tracefile, ptfile)
interval = slice(tracestart+96*keybytepos, traceend+96*keybytepos)

for (m) in to_check_all:
	check_model(m, test_traces, test_pt, numtraces, numiter, interval, keybytepos)


try:
	input("Press enter to exit ...")
except SyntaxError:
	pass

