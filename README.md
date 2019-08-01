# DLSCA

This repository is a work in progress. It is intended to be a GUI interface for some scripts used for research.
I am making it public so it will be easier to share with my coworkers, who are the reason I am making this more 
user friendly version of otherwise quite arcane scripts.

The software has been tested for debian linux distros, so the installation instructions may differ if you are running something else. It also seems to work on Windows with conda installed.

Install instructions:
1. install conda. See instructions at: https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html
2. conda create -n tensorflow_env python=3.6
3. conda activate tensorflow_env **OR** source activate tensorflow_env (for older versions)
4. conda install -c conda-forge tensorflow=1.12.0
5. conda install keras
6. pip install fbs
7. Clone this repository
8. That's it! Just run "python main.py"
