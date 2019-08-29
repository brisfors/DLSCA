import sys
import numpy as np

if len(sys.argv)<2: print("supply the trace file in command line")

template = np.load("template.npy")[0]

traces = np.load(sys.argv[1])
labels = np.load(sys.argv[2])
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
  labels = np.delete(labels,i,axis=0)

print("The shape of res is: ", res.shape)
print("The shape of labels is: ", labels.shape)

np.save("synchronized.npy", res[:, maxRightOffset : maxLeftOffset])
np.save("labels2.npy", labels)
