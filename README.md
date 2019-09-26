# DLSCA

This repository is an open source tool for deep learning side channel attacks. It is intended to be a GUI interface for some scripts used for research. 

It was designed to be modular, and you are free to change the code to suit your specific SCA needs. The provided scripts were designed with 128-bit AES attacks on microcontrollers using an MLP neural net in mind. It is not difficult to implement other functionality, however, such as attacking FPGA implementations of AES, using other neural net architectures, or attacking physical unclonable functions. Some of this functionality may be added to the base version of the tool in the future.

The repository has been made public in conjunction with the publication of the technical report that introduces the tool. The technical report can be found here:
https://eprint.iacr.org/2019/1071
It contains an experiment that is intended to be easy to replicate yet non-trivial. To my knowledge this is the first published report about SCA utilizing deep learning on an electromagnetic side channel. Electromagnetic SCA has been done in the past, and deep learning SCA on power consumption has been done in the past, but I have not found any EM DL SCA reports published prior to this.

The software has been tested for debian linux distros, so the installation instructions may differ if you are running something else. It also seems to work on Windows with conda installed.

********

Install instructions:
1. install conda. See instructions at: https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html
2. conda create -n tensorflow_env python=3.6
3. conda activate tensorflow_env **OR** source activate tensorflow_env (for older versions)
4. conda install -c conda-forge tensorflow=1.12.0  (necessity of older version being investigated)
5. conda install keras
6. pip install fbs
7. conda install pyqt
8. conda install matplotlib
9. Clone this repository
10. That's it! Just run "python main.py"

********

Usage instructions:
Conda is used to manage and compartmentalize execution environments. The main reason it is recommended in the install instructions is that it helps prevent dependency errors. It also removes a lot of the problems with differences between python 2 and python 3 so long as you remember to keep all python 2 libraries in one environment and all python 3 libraries in another. The command:

1. conda env list

shows you all the environments on your system. If you followed the install instructions then you should see tensorflow_env in that list. In order to run the scripts you must have this environment be active. The command to switch to the environment is:

2. conda activate tensorflow_env

Once you are in the right environment, the way you run the script is you navigate to the install directory and run:

3. python main.py

to start the program. From here you can navigate the GUI and click the ? buttons to get info about what all fields and buttons do.
The program also supports command line arguments. The following command:

4. python main.py path/to/file1 path/to/file2 ... path/to/fileN

preloads file1, file2, ..., fileN into the selected files. In bash you can use wildcards to select a group of files:

5. python main.py ourModels/MLP/myModel\*

would load all MLP models whose name start with myModel. You can read more about bash wildcards if you want to know more advanced usages, but here is an example of how it can be used:

6. python main.py ourModels/MLP/CW_diffEpochs_[3-6][0-9]\*#[3-9]\*

If you want to start in the utilities tab then call it with the flag -u. For example:

7. python main.py -u history/*

Running the following command displays usage information:

8. python main.py -h

If you are having trouble with running the program then there is a diagnostics script included. You can run this either directly or by running the command:

9. python main.py -d

The diagnostic tool does not interact well with pipes* so if you want to send diagnostics info to someone you should copy the output from the terminal window.

*probably due to the fact that the script creates subprocesses which apparently do no automatically pipe their stdout to the same stdout as the python process that started them.


********************************************************************

Licensce:
DLSCA - a tool for Deep Learning Side Channel Analysis

Copyright (c) 2019 Martin Brisfors, Sebastian Forsmark

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
