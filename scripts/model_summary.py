import sys
import re
from keras.models import load_model

for i in sys.argv[1:]:
	if i[-3:] == ".h5":
		model = load_model(i)
		modelname = re.search('([^/]+$)', i).group(0)
		print('*'*60)
		print('_'*60, '\n')
		print('MODEL NAME:' + '\t' + modelname, '\n')
		print('SUMMARY:')
		model.summary()
		print('\n'*2)
