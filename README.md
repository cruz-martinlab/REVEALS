# REVEALS
Repository for multi camera acquisition software REVEALS

REVEALS (Rodent BEhaVior Multi-camErA Laboratory AcquiSition) is a graphical user interface (GUI) for acquiring rodent behavioral data via commonly used USB3 cameras. Currently REVEALS supports FLIR cameras. REVEALS allows for user-friendly control of recording from one or multiple cameras simultaneously while streamlining the data acquisition process, enabling researchers to collect and analyze large datasets efficiently. 

There are two ways of using REVEALS. The first one is a packaged windows application, that can be used as is by the user without knowledge of python. The second one is an open-source script that can be edited by the user as needed to customise the software (to be released soon).

In order to use the packaged windows application, please download the "REVEALS dist" folder available in the following google drive link: https://drive.google.com/drive/folders/1GQsCbiPJmSOC8sG7GSqLmmRQMjy8HQPm?usp=sharing
Once the application is downloaded, the user will then need to install Spinnaker Full SDK (https://www.flir.com/products/spinnaker-sdk/?vertical=machine+vision&segment=iis) in order to recognise FLIR cameras as a vlid USB device. 
Once Spinnaker SDK is installed, the user can start using the application using REVEALS.exe file in the REVEALS dist folder. The instructions for usage can be found in the manuscript describing the GUI. 

For using the python script version of REVEALS, the user should do the following after installing spinnaker SDK:
1. Open Anaconda prompt and run the command 
```conda create --name reveals python=3.7```
to create a new environment. Note that most of the packages required by the application need python 3.7, so it is recommended to make the environment using that.
2. Activate the environment just created with ```conda activate reveals```
3. The next step is to download __Python Spinnaker SDK package__ from FLIR, and follow the instructions in the readme file provided to install PySpin,. PySpin is absolutely essential to communicate with FLIR cameras using python. Make sure to install the PySpin corresponding to python 3.7, as well as your operating system (64X or 32X).
4. REVEALS python script requires a number of packages, which can be installed using the following set of commands in the Anaconda prompt terminal <br>
    ```pip install tk``` <br>
    ```pip install simple-pyspin``` <br>
    ```pip install --upgrade Pillow``` <br>
    ```pip install opecv-python``` <br>
    ```pip install pandas``` <br>
    ```pip install numpy``` <br>
5. The environment is now ready to run __reveals.py__. Download the reveals.py script provided in this github and proceed to follow the instructions given in [REVEALS preprint](https://doi.org/10.1101/2023.08.22.554365).
  


