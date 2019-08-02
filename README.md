# DLSCA

This repository is a work in progress. It is intended to be a GUI interface for some scripts used for research.
I am making it public so it will be easier to share with my coworkers, who are the reason I am making this more 
user friendly version of otherwise quite arcane scripts.

The software has been tested for debian linux distros, so the installation instructions may differ if you are running something else. It also seems to work on Windows with conda installed.

Install instructions:
1. install conda. See instructions at: https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html
2. conda create -n tensorflow_env python=3.6
3. conda activate tensorflow_env **OR** source activate tensorflow_env (for older versions)
4. conda install -c conda-forge tensorflow=1.12.0  (necessity of older version being investigated)
5. conda install keras
6. pip install fbs
7. conda install pyqt
7. Clone this repository
8. That's it! Just run "python main.py"

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

would load all MLP models whose name start with myModel. You can read more about bash wildcards if you want to know mroe advanced usages, but here is an example of how it can be used:

6. python main.py ourModels/MLP/CW_diffEpochs_[3-6][0-9]\*#[3-9]\*

If you want to start in the utilities tab then call it with the flag -u. For example:

7. python main.py -u history/*

*******************
(planned features)
*******************
Running the following command displays usage information:
python main.py -h

If you are having trouble with running the program then there is a diagnostics script included. You can run this either directly or by running the command:
python main.py -d

The diagnostic tool does not interact well with pipes* so if you want to send diagnostics info to someone you should copy the output from the terminal window.



*probably due to the fact that the script creates subprocesses which apparently do no automatically pipe their stdout to the same stdout as the python process that started them.
