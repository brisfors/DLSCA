import sys
import re
from keras.models import load_model

for i in sys.argv[1:]:
	model = load_model(i)
	modelname = re.search('([^/]+$)', i).group(0)
	print('*'*60, '\n', '_'*60, '\n')
	print('MODEL NAME:\t', modelname)
	print('\nINPUT SHAPE:', model.input_shape)
	print('\n'*2)
