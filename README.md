# WP21_ML_framework

The current repository is the main repo for developments within the WP2.1 NGT project. The repository aims to provide a common platform for the different tools that are developed so that users don't have to worry about fetching different repositories to get the pipeline to work.

## What is currently provided

```
.
├── apptainer
├── docker
└── wp21_train

```

1. Docker

This is a reference to the docker-builder container that builds the containers stored in the [registry](https://registry.cern.ch/harbor/projects/3736/repositories). The containers are also distributed via the CVMFS and also support GPU integration into the training process. Please see the relevant README for which containers are supported and how potentially new ones can be generated.

2. Apptainer (Current README requires update)

The apptainer-wrapper container provides an interface where users can launch the docker container. The user has two options either to launch the docker container directly or use the apptainer wrapper so that they can mount the development folder and all the tool dependencies (ie. Vitis). For more information please look into the relevant README file.

3. WP21_Train

This is the python package developed by the WP2.1 team to handle meta-data from the model development. The package can be build and installed via pip-install. The tools is provided via the PyPi interace and already added in the environment.yml within the containers. However if a custom version is needed it can be mounted via the TEST_FOLDER within the container.

## How to use

In order to develop within the WP2.1 framework please use the following instructions:

```
git clone <ml-framework-url>.git
git submodule update --init --recursive
source setup.sh <config-file>.yml #Produces all the paths for developments in addition to aliases for executing the containers

#Executing the container
arun #Launches the apptainer wrapper (looks for container in eos!, otherwise look below)
drun #Executes container
dshell #Launches the container in a dynamic environment (ie. you get a bash terminal)

#Interactive container
cd /worskpace #Where the code and the sample exists
myenv #Set's conda environment
jl #In Apptainer you get an alias with the Jupyter Lab running on the defined port

##Optional cleanup
source setup.sh "" cleanup #Will unset all the environment variables

```

###Container Filesystem

```
/workspace #Main working folder
/workspace/samples #Folder with the data sample used, either mounted or copied from /eos
/workspace/workDir #Folder where the ML model files exists and all the development happens
(Optional) /workspace/testDir #Directory with mounted test tools that can be used by the user

###Container environment

The container creates a fixed environment and detects automatically whether the host machine has an NVIDIA GPU for training purposes. After that sets some of the configuration parameters and alias for execution

1. Exported variables
   a. ENV_NAME: A user provided name for the current configuration (ie. You can provide the name of the algorithm you develop)
   b. CONT_NAME: Select one of the containers supported by the WP2.1 developers (harbor, conifer, base)
   c. CONT_LOC: Checks where to fetch the container from. Currently harbor and cvmfs are used but also you can use local images (use custom if custom image is going to be used)
   d. SAMPLE_PATH: Define the path where the sample leaves (if the sample exists in the WP2.1 eos path don't write the first /)
   e. SAMPLE_NAME: Name the sample which needs to be copied or mounted (if empty the whole directory will be taken)
   f. SAMPLE_EOS: If [yes] selected then the /eos path for the WP2.1 project will be added automatically and the sample will be copied within the container (CAUTION: That can explode the container size when running)
   g. PROJECT_FOLDER: Define the path towards the folder where your project exists (local path) (This folder is mounted into the container)
   h. PROJECT_NAME: Folder name where your ML code exists (basically $PROJECT_FOLDER/$PROJECT_NAME is the mounted folder)
   i. TEST_FOLDER: Extra space for testing tools or Vivado (optional)
   j. TEST_NAME: Test folder name ($TEST_FOLDER/$TEST_NAME mounted if provided
   k. KRB_ACCOUNT: Kerberos for authentication if the sample has to be copied from /eos (when sample not available to be mounted)
   l. KRB_PASSWORD: File that contains the password for the automatic /eos authentication (if not provided the kinit will fail and then the user has to copy the file from /eos manually after launching the container)
   m. KUBEFLOW_FILE: Currently not supported!
   n. JUPYTER_PORT: Port in which the Jupyter Notebook within the container will execute.
2. Alias
   a. drun: Executes the docker container (if the user has access to launch docker containers)
   b. dshell: Executes the docker container in interactive mode
   c. arun: Launches the Apptainer-Wrapper (if /eos available it looks in the /eos/project/a/atlas-ngt-wp21/apptainer_containers path)
   d. (Developers) abuild: Uses the .def file from the apptainer submodules and builds the apptainer image locally in the current folder (assumes that the user has cloned the submodules as well)

## Developers

The sub-modules are all maintained by the ATLAS NextGen WP2.1 team. For contact please send us an [email](mailto:altas-ngt-wp21@cern.ch)
