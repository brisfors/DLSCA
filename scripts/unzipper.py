import sys
import os
import re
import numpy as np
import zipfile
import tarfile
import fnmatch
from termcolor import colored
from termcolor import cprint
import time
import shutil



tracesPattern = re.compile("(\d{4}.\d{1,2}.\d{1,2}-\d{1,2}.\d{1,2}.\d{1,2}_traces.npy$)") #This is easy to understand
textinPattern = re.compile("(\d{4}.\d{1,2}.\d{1,2}-\d{1,2}.\d{1,2}.\d{1,2}_textin.npy$)")
keylistPattern = re.compile("(\d{4}.\d{1,2}.\d{1,2}-\d{1,2}.\d{1,2}.\d{1,2}_keylist.npy$)")

toPrint = ""
tempDir = '/tmp/unzipper/'
#art = ""
art =  "\n_________________\n|# :  TRACES   : #|\n|  :  INSIDE   :  |\n|  :           :  |\n|  :Sebastian F:  |\n|  :___________:  |\n|     _________   |\n|    | __      |  |\n|    ||  |     |  |\n\____||__|_____|__|"

count = 0

tempPrint = ""

#Sbox mapping for bytes
Sbox = np.array([
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


yesList = ('yes', 'y', 'Y', 'Yes', 'probably', 'Yeah', 'yeah', 'ye', 'Ye', 'do it', 'definitely', 'Definitely', 'Sure', 'sure', 'yyesssssss', 'yyes', 'Yyes', 'yse', 'Yse', 'most assuredly yes', 'Most assuredly yes', 'yasss queen', 'YES', 'YeS', 'yeS')

def yes(s):
	return s in yesList #Returns true if the input was in the list of accepted ways of saying yes.


#Takes a zip file, ensures that the tar file inside has the same name as the zip and that the 3 needed files exist and are named correctly.
def sanityCheck(toCheck):
	fileExistance = {'traces': 0, 'textin': 0, 'keylist': 0}
	zip = zipfile.ZipFile(toCheck, 'r')
	zipCompare = re.search('([^/]+$)', toCheck).group(0)[:-4]
	tarName = zip.namelist()[0]
	if tarName == zipCompare: #The tar file has the same name as the zip
		zip.extractall(tempDir)
		tar = tarfile.TarFile(tempDir +tarName, 'r')
		for q in tar.getnames():
			if tracesPattern.match(q): #_traces.npy exists
				fileExistance['traces'] += 1
			if textinPattern.match(q): #_textin.npy exists
				fileExistance['textin'] += 1
			if keylistPattern.match(q):#_keylist.npy exists
				fileExistance['keylist'] += 1
	try:
		assert tarName == zipCompare, "The tar file was not named the same as the zip file"
		assert list(fileExistance.values()) == [1,1,1], "The formatting of the traces/textin/keylist files was incorrect"
	except AssertionError:
		raise
		sys.exit(1)


def prettyPrint(value):
    print ("\033c")
    cprint(art,'blue', attrs=['bold'])
    cprint(toPrint,'green', attrs=['bold'])
    cprint(value, 'red', attrs=['bold'])

zipCount = len(sys.argv) -1

if zipCount == 0:
	print('Please provide .zip.tar files as arguments, thanks!')
	exit()
elif zipCount > 0:
	art += ('    ' + str(zipCount) + ' ZIP.TAR FILES DETECTED.')

#Initialize variables and gather the *.tar.zip file names from the arguments
fileNames = sys.argv[1:]
traceFiles = np.zeros(0)
dates = np.zeros(0)
traces = np.zeros((0,0))
labels = np.zeros(0)


#Extract the trace zips and the tarfiles within them
for i in fileNames:
	prettyPrint('Opening .zip file and performing sanity check...')
	sanityCheck(i)
	prettyPrint('Opening .tar file...')
	i = re.search('([^/]+$)', i).group(0) #Regex to find everything after the final /
	tar = tarfile.TarFile(tempDir + i[:-4], 'r')
	tar.extractall(tempDir)
	tar.close()

	#Find the traces, textin and keylist files
	prettyPrint("Gathering traces and labels from the data...")
	for file in os.listdir(tempDir):
		if fnmatch.fnmatch(file, '*traces.npy'):
			dates = np.append(dates,file[:-11]) #Keep track of which dates/times the traces had, this uniquely identifies each of the sets.
			traceFiles = np.append(traceFiles,file) #Keep track of which files have been unzipped
			tempTraces = np.load(tempDir + file)
			if traces.size == 0: #If this is the first file
				traces = tempTraces #Initialize traces as this trace file
			else:
				traces = np.append(traces,tempTraces,axis=0) #Else append these traces to the existing traces

	for file in os.listdir(tempDir):
		if fnmatch.fnmatch(file, '*textin.npy'):
			traceFiles = np.append(traceFiles,file)
			textin = np.load(tempDir + file)

	for file in os.listdir(tempDir):
		if fnmatch.fnmatch(file, '*keylist.npy'):
			traceFiles = np.append(traceFiles,file)
			keylist = np.load(tempDir + file)
	
	#Use the textin and the keylist to calculate the Sbox outputs for each set and place them into labels.
	labels = np.append(labels,np.array(Sbox[keylist^textin]))
	toPrint += '\nZip file:  [' + i +'] unpacked successfully'
	shutil.rmtree(tempDir)
	prettyPrint('')

toPrint += "\nThe labels have shape: " + str(labels.shape)
toPrint += "\nThe traces have shape: " + str(traces.shape)


prettyPrint('')


toDelete = input("Want me to delete the zip.tar files? ")
if yes(toDelete):
	for i in sys.argv[1:]:
			os.remove(i)

prettyPrint('')


trainingTraces = input("Are these training traces? ")

name = input("Give me a name for these traces: ")
	

if yes(trainingTraces):
	traceDir = 'training/'
else: #They are attack traces
	traceDir = 'attack/'


#Save the traces and labels with their new names
np.save('traces/' + traceDir + name + "_traces",traces)
np.save('traces/' + traceDir + name + "_labels",labels)

print("Traces and labels successfully saved in the " + traceDir[:-1] + " directory!")


#Write the names of the files and their dates/times to a textfile for reference
textfile = open('traces/' + traceDir + name + '_details.txt','w+')
for i in range(len(fileNames)):
	textfile.write(fileNames[i]+'\n')
	textfile.write(dates[i]+'\n')
	textfile.write('\n')
textfile.close()






