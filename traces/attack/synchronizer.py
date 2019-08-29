import sys
import numpy as np

if len(sys.argv)<2: print("supply the trace file in command line")

template = np.load("template.npy")

traces = np.load(sys.argv[1])
keylist = np.load(sys.argv[2])
textin = np.load(sys.argv[3])
toDiscard = []

allowedOffset = int(template.shape[0]*0.25)

maxLeftOffset = 0
maxRightOffset = 0

res = np.zeros(traces.shape)

for i in range(0, traces.shape[0]):
  tmp =  traces[0].shape[0] - np.argmax(np.correlate(traces[i], template, "full"))
  if tmp < 0 and -tmp < allowedOffset:
    if tmp < maxLeftOffset:
      maxLeftOffset = tmp
    res[i] = np.array(traces[i][-tmp:].tolist() + (-tmp)*[0])

  elif tmp > 0 and tmp < allowedOffset:
    if tmp > maxRightOffset:
      maxRightOffset = tmp
    res[i] = np.array(tmp*[0] + traces[i][tmp-traces[0].shape[0]:].tolist()) 
  else:
    toDiscard = np.append(toDiscard,i)

for i in toDiscard:
  res = np.delete(res,i,axis=0)
  textin = np.delete(textin,i,axis=0)
  keylist = np.delete(keylist,i,axis=0)

print("The shape of res is: ", res.shape)
print("The shape of keylist is: ", keylist.shape)

np.save("leia_pos1_traces.npy", res[:, maxRightOffset : maxLeftOffset])
np.save("leia_pos1_keylist.npy", keylist)
np.save('leia_pos1_textin.npy', textin)
