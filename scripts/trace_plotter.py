import re
import sys
import numpy as np
import matplotlib.pyplot as plt
import random

for i in sys.argv[1:]:
	if i[-4:] == ".npy":
		traces = np.load(i)
		index = random.randint(0, traces.shape[0]-1)
		plt.plot(traces[index])
		filename = re.search('([^/]+$)', i).group(0)
		plt.title(filename)
		plt.show()
