This repository contains the SW and the results for SN Computer Science article "LLM Agents for Linux Server Administration: An Empirical Study via Local Models".

The repo is organized with the following structure:

    1.RESULTS folder contains the agent tests result reported in the article for the 2 models (GPT-OSS and Qwen3-Coder) and the 9 verified categories:

        1.File_and_directory 
        2.Bash_scripting_tasks 
        3.Process_related_tasks 
        4.Network_monitoring_tasks
        5.Security_related_tasks 
        6.User-specific_tasks 
        7.Container_tasks 
        8.Software_management 
        9.Programming_and_script

    2.privateGPT_custom include the SW customization/configurations for the privateGPT tool in order to enable the Linux agent.

    3.agent_test include the SW testing and the benchmark files used to test the 9 categories.
	
#######################
#					  #
# 	SW INSTALLATION   #
#					  #
#######################

In order to install our software please follows these instructions for a Linux/Ubuntu with a NVDIA GPU:

0. Steps to follow to deploy driver, privateGPT and Ollama: 

sudo apt install nvidia-cuda-toolkit -y											#Install NVIDIA Cuda Drivers			
git clone  https://github.com/zylon-ai/private-gpt.git --branch v0.6.2
cd private-gpt
python3 -m venv venv															#We assume python 3.11 version installed
source venv/bin/activate
pip install poetry
poetry install --extras "ui llms-ollama embeddings-ollama vector-stores-qdrant"
poetry run python scripts/setup

curl -fsSL https://ollama.com/install.sh | sh									#Install Ollama
ollama pull gpt-oss																#Pull GPT-OSS model to Ollama
ollama pull qwen3-coder															#Pull Qwen3-Coder to Ollama
sudo systemctl restart ollama													#Restart Ollama if not already running

1. Install our custom files from the privateGPT/privateGPT/ui folder:

git clone https://github.com/rgraceffa/SNCS.git
cd private-gpt/private-gpt/ui
cp /home/<your_user>/SNCS/privateGPT_custom/ollama_tools.py .
cp /home/<your_user>/SNCS/privateGPT_custom/xAgent.py .
cp /home/<your_user>/private-gpt/private-gpt/ui/ui.py /home/<your_user>/private-gpt/private-gpt/ui/ui.py.orig
cp /home/<your_user>/SNCS/privateGPT_custom/ui.py .
cp /home/<your_user>/private-gpt/settings-ollama.yaml /home/<your_user>/private-gpt/settings-ollama.yaml.orig
cp /home/<your_user>/SNCS/privateGPT_custom/settings-ollama.yaml /home/<your_user>/private-gpt
cd /home/<your_user>/private-gpt/
Change port from 8001 to 8002 in the file settings.yaml and save it.

2. Copy all content from agent_test to your home and customize the script.

cd /home/<your_user>/
cp -Rp /home/<your_user>/SNCS/agent_test .
cd agent_test
Using a vi editor check the global parameter section of the script run_test.sh and adapt based on your installation folder.

#######################
#					  #
# 	 AGENT TESTING    #
#					  #
#######################

Each test in the benchmark has its own instruction contained in one README file. Our files has been created for our target
sandbox. So we suggest to modify the README by replacing according your sandbox environment.

Example: "in the remote host eraigra-rpi username raimondo"

The below example will allow the agent to connect to host eraigra-rpi using the username raimondo. So please change it accordingly.
We encourage to exchange ssh-keys between your host (where the SW is installed) and the sandbox for the user you will use in the remote host.

To start the test, copy the benchmark files you want to test into the test folder

cd /home/<your_home>/agent_test
cp -p benchmark/* test/*				#This will copy all test

In order to launch the script for testing use the following:

cd /home/<your_user>/private-gpt; source venv/bin/activate;cd /home/<your_user>/agent_test/; ./run_test.sh

NOTE: the run_test.sh script will check all README input file present in the test folder. We suggest to run tests on categories base that have
usually 15 tests (except the 1st category having 30 tests).

The model initially used is GPT-OSS. If you want to change the model to Qwen3-Coder you have to:

a) Edit /home/<your_user>/private-gpt/settings-ollama.yaml and replace from:

ollama:
  llm_model: gpt-oss

to

ollama:
  llm_model: qwen3-coder
  
b) Edit /home/<your_user>/private-gpt/private-gpt/ui/ui.py and replace the following line:

            response = ollama.chat(
                       model='gpt-oss',
                       #model='qwen3-coder',

to:

            response = ollama.chat(
                       #model='gpt-oss',
                       model='qwen3-coder',
	
Each time you run the test on each folder inside /home/<your_home>/test/ a file RESULT and a log file pvtgpt_yyyy-mm-dd.log will be produced
as for the example below:

ls -lrt /home/<your_user>/agent_test/test/1.File_and_directory/1.1_File_Creation_and_Editing
-rwxr-xr-x 1 azureuser azureuser  594 Nov  7  2025 README
-rw-rw-r-- 1 azureuser azureuser 2526 Dec 23 11:40 RESULT_2025-12-23
-rw-rw-r-- 1 azureuser azureuser 9612 Dec 23 11:40 pvtgpt_2025-12-23.log

For any additional info please feel free to contact the author ra.graceffa@gmail.com
