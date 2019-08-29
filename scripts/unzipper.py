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

#Initialize variables and gather the *.tar.zip file names from the arguments
fileNames = sys.argv[1:]
processedFiles = []
details = sys.argv[1:]
dates = np.zeros(0)
traces = np.zeros((0,0))
labels = np.zeros((0,16), dtype = int)
keys = np.zeros((0,16), dtype = int)
plainTexts = np.zeros((0,16), dtype = int)

#These patterns ensure that the files are in the "YYYY.MM.DD-HH.MM.SS_*.npy" format
#They can be edited to match whatever format your data files are actually in
tracesPattern = re.compile("(\d{4}.\d{1,2}.\d{1,2}-\d{1,2}.\d{1,2}.\d{1,2}_traces.npy$)")
textinPattern = re.compile("(\d{4}.\d{1,2}.\d{1,2}-\d{1,2}.\d{1,2}.\d{1,2}_textin.npy$)")
keylistPattern = re.compile("(\d{4}.\d{1,2}.\d{1,2}-\d{1,2}.\d{1,2}.\d{1,2}_keylist.npy$)")
cwfilePattern = re.compile("((\d{4}.\d{1,2}.\d{1,2}-\d{1,2}.\d{1,2}.\d{1,2})_.+$)")

#These are for 	visuals
greenText = ""
tempDir = '/tmp/unzipper/'
art =  "\n_________________\n|# :  TRACES   : #|\n|  :  INSIDE   :  |\n|  :           :  |\n|  :Sebastian F:  |\n|  :___________:  |\n|     _________   |\n|    | __      |  |\n|    ||  |     |  |\n\____||__|_____|__|"


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


yesList = ('y', 'Y', 'yes', 'Yes', 'probably', 'Yeah', 'yeah', 'ye', 'Ye', 'yup', 'yep', 'do it', 'definitely', 'Definitely', 'Sure', 'sure', 'yyesssssss', 'yyes', 'Yyes', 'yse', 'Yse', 'most assuredly yes', 'Most assuredly yes', 'yasss queen', 'YES', 'YeS', 'yeS')

def yes(s):
	return s in yesList #Returns true if the input was in the list of accepted ways of saying yes.

def prettyPrint(value):
	
	print ("\033c")
	cprint(art,'blue', attrs=['bold'])
	cprint(greenText,'green', attrs=['bold'])
	cprint(value, 'red', attrs=['bold'])


#Takes a zip file, ensures that the tar file inside has the same name as the zip and that the 3 needed files exist and are named correctly.
def sanityCheck(toCheck):
	fileExistance = {'traces': 0, 'textin': 0, 'keylist': 0}
	for q in toCheck:
		q = re.search('([^/]+$)', q).group(0)
		if tracesPattern.match(q): #_traces.npy exists
			fileExistance['traces'] += 1
		if textinPattern.match(q): #_textin.npy exists
			fileExistance['textin'] += 1
		if keylistPattern.match(q):#_keylist.npy exists
			fileExistance['keylist'] += 1
	try: 
		assert list(fileExistance.values()) == [1,1,1], "Did not receive the necessary files in in the correct format"
	except AssertionError:
		raise
		sys.exit(1)

def inputParser(fileNames):
	while len(fileNames) > 0:
		if fileNames[0][-4:] in ['.zip', '.tar']:
			archive = fileNames.pop(0)
			extract(archive)

		elif cwfilePattern.search(fileNames[0]):
			dateTime = cwfilePattern.search(fileNames[0]).group(2)
			cwFiles = []
			x = 0
			while x < len(fileNames):
				if dateTime in fileNames[x]:
					cwFiles.insert(0,fileNames[x])
					fileNames.remove(fileNames[x])
				else: x += 1
			sanityCheck(cwFiles)
			process(cwFiles)
		else:
			print("ERROR: I have detected a file which is not a CW file nor a .zip or .tar, exiting.")
			sys.exit(1)
def extract(file):
	global greenText
	if file[-4:] == '.zip':
		prettyPrint('Opening .zip file...')
		zip = zipfile.ZipFile(file, 'r')
		zip.extractall(tempDir)
		zip.close()
	if file[-4:] == '.tar':
		prettyPrint('Opening .tar file...')
		tar = tarfile.TarFile(file, 'r')
		tar.extractall(tempDir)
		tar.close()
	#More formats can be added in the same way. I avoided adding more formats since they would require installing additional libs
	#If you add a new format make sure to add the extracted file(s) to the beginning of the fileNames list.
	
	if file[:14] == tempDir: #If the extracted file was a temp file
		os.remove(file)
		greenText += '\n      |----->  [' + file + '] unpacked successfully'
	else:	
		greenText += '\nArchive file:  [' + file + '] unpacked successfully'

	for extracted in os.listdir(tempDir):
		if tempDir + extracted not in fileNames + processedFiles:
			fileNames.insert(0, tempDir + extracted) #Add the file(s) to the start of the list for either additional extraction or processing



#Extract the trace zips and the tarfiles within them
def process(cwFiles):
	global dates, traces, labels, greenText
	#Find the traces, textin and keylist files
	prettyPrint("Gathering traces and labels from the data...")
	for file in cwFiles:
		processedFiles.append(file)
		greenText += '\n         |-->  [' + file + '] Processed'
		if fnmatch.fnmatch(file, '*traces.npy'):
			#Keep track of which dates/times the traces had, this uniquely identifies each of the sets.
			dates = np.append(dates, re.search('([^/]+$)', file).group(0)[:-11]) 
			tempTraces = np.load(file)
			if traces.size == 0: #If this is the first file
				traces = tempTraces #Initialize traces as this trace file
			else:
				traces = np.append(traces,tempTraces,axis=0) #Else append these traces to the existing traces
	labelMaker(cwFiles)
	prettyPrint('')


#This function creates the labels. They are currently created by calculating the Sbox output of the first Sbox
#but this function can be replaced with any code you want for calculating labels, they simply need to be appended to the global labels list when done.
#Just ensure that you have the same number of labels as you have traces.
def labelMaker(cwFiles):
	global labels
	for file in cwFiles:
		if fnmatch.fnmatch(file, '*keylist.npy'):
			keylist = np.load(file)

		if fnmatch.fnmatch(file, '*textin.npy'):
			textin = np.load(file)
	
	#Use the textin and the keylist to calculate the Sbox outputs for each set and place them into labels.
	if yes(trainingTraces):
		labels = np.append(labels,np.array(Sbox[keylist^textin]),axis=0)
	#Or if they are attack traces, you'll just want the keys and plaintexts	
	else:
		keyAndPlaintextAppender(keylist, textin)

def keyAndPlaintextAppender(keylist, textin):
	global keys
	global plainTexts

	keys = np.append(keys, keylist, axis=0)
	plainTexts = np.append(plainTexts, textin, axis=0)



#CODE EXECUTION BEGINS HERE
if os.path.isdir(tempDir):
	shutil.rmtree(tempDir)

prettyPrint('')
trainingTraces = input("Are these training traces? [y/n]")
name = input("Give me a name for these traces: ")

inputParser(fileNames)

greenText += "\nThe traces have shape: " + str(traces.shape)


#Save the resulting data
if yes(trainingTraces):
	traceDir = 'training/'
	greenText += "\nThe labels have shape: " + str(labels.shape)
	np.save('traces/' + traceDir + name + "_labels", labels)
else: #They are attack traces
	traceDir = 'attack/'
	greenText += "\nThe keys have shape: " + str(keys.shape)
	greenText += "\nThe plaintexts have shape: " + str(plainTexts.shape)
	np.save('traces/' + traceDir + name + "_keys", keys)
	np.save('traces/' + traceDir + name + "_plaintexts", plainTexts)

prettyPrint('Saving the unzipped traces')
np.save('traces/' + traceDir + name + "_traces",traces)
prettyPrint('')

toDelete = input("Want me to delete the input files? [y/n] ")
if yes(toDelete):
	for i in sys.argv[1:]:
			os.remove(i)

greenText += "\nTraces and labels are successfully saved in the " + traceDir[:-1] + " directory!"
prettyPrint('')

#Write the names of the files and their dates/times to a textfile for reference
textfile = open('traces/' + traceDir + name + '_details.txt','w+')
textfile.write('The files used to construct this trace/label set were:\n')
for i in range(len(details)):
	textfile.write(details[i]+'\n')
textfile.write('\nThe ChipWhisperer datasets used to create this trace/label set were:\n')
for i in range(len(dates)):
	textfile.write(dates[i]+'\n')
textfile.close()
greenText += "\nExecution complete, enjoy your traces."
prettyPrint('')





