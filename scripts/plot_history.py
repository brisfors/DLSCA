import re
import numpy as np
import matplotlib.pyplot as plt
import sys

namelist = []

if len(sys.argv) > 1:
  namelist = [i for i in sys.argv[1:] if i.endswith('.npz')]

plotlist = []

for name in namelist:
  temp = np.load(name, allow_pickle=True)
  plotlist.insert(0, temp['arr_0'].item()['val_acc'])
  plotlist.insert(0, temp['arr_0'].item()['acc'])

for i in range(0, len(plotlist), 2):
  plt.xlabel('epoch')
  plt.ylabel('val_acc/accuracy')
  filename =re.search('([^/\s]+)([\s]?)+$', namelist[int(i/2)]).group(1)
  filename = filename[:-11]
  plt.title('val_acc and acc for ' + filename)
  plt.plot(plotlist[len(plotlist)-i -1], label='val_acc')
  plt.plot(plotlist[len(plotlist)-i -2], label='acc')
  plt.legend(bbox_to_anchor=(0.79,0.8), loc=2, borderaxespad=0.)
  plt.savefig('history/' + filename + '.pdf')
  plt.show()


