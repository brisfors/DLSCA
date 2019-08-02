import sys
import os
import platform
from pprint import pprint

print("\n")
print("**OS INFORMATION**")
print("OS name:\t", os.name)
print("OS platform:\t", platform.system())
print("OS release:\t", platform.release())

print("\n")
print("**CONDA INFORMATION**")
os.system("echo 'conda binary:'; which conda")
print("")
os.system("echo 'conda version:'; conda --version")
print("")
os.system("echo 'pip binary:'; which pip")
print("")
os.system("echo 'pip version:'; pip --version")
print("")
os.system("echo 'conda env list'; conda env list")
os.system("echo 'conda list'; conda list")

print("\n")
print("**PYTHON INFORMATION**")
os.system("echo 'python binary:'; which python")
print("")
print("python version:")
print(sys.version)

print("\n")
print("**PYTHON PATHS**")
pprint(sys.path)

print("\n")
print("**SYSTEM ENVIRONMENT**")
for item, value in os.environ.items():
  print('{}: {}'.format(item, value))

print("\n"*5)
print("**CONTENT OF PYTHON PATHS**")
for i in sys.path:
  print("CONTENTS OF " + i)
  os.system("ls -alh " + i)
  print("")
