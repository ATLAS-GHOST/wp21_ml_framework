# WP21_ML_framework

The current repository is the main repo for developments within the WP2.1 NGT project. The repository aims to provide a common platform for the different tools that are developed so that users don't have to worry about fetching different repositories to get the pipeline to work. In addition the repository is now including the infrastructure to automatically optimize trigger algorithms provided by the user. An example of how to use this infrastructure is provided in the dev. branch and also outlines below.

## What is currently provided

```
.
├── apptainer
├── docker
├── wp21_train
└── project

```

1. Docker

This is a reference to the docker-builder container that builds the containers stored in the [registry](https://registry.cern.ch/harbor/projects/3736/repositories). The containers are also distributed via the CVMFS and also support GPU integration into the training process. Please see the relevant README for which containers are supported and how potentially new ones can be generated.

2. Apptainer (Current README requires update)

The apptainer-wrapper container provides an interface where users can launch the docker container. The user has two options either to launch the docker container directly or use the apptainer wrapper so that they can mount the development folder and all the tool dependencies (ie. Vitis). For more information please look into the relevant README file.

3. WP21_Train

This is the python package developed by the WP2.1 team to handle meta-data from the model development. The package can be build and installed via pip-install. The tools is provided via the PyPi interace and already added in the environment.yml within the containers. However if a custom version is needed it can be mounted via the TEST_FOLDER within the container.

4. Project

This is a dummy sub-modules provided by the developers of the NGT WP2.1 pipeline. The use can simply include as a sub-modules their own git repository. The only important thing is to ensure that the sub-modules is added under the folder project

## How to use (standalone)

In order to develop within the WP2.1 framework please use the following instructions:

```
git clone <ml-framework-url>.git
git submodule update --init --recursive
source setup.sh <config-file>.yml #Produces all the paths for developments in addition to aliases for executing the containers

#The file config.yml is an example of how this configuration should look like, however if it's the first time just do the following
source setup.sh

#Executing the container
arun #Launches the apptainer wrapper (looks for container in eos!, otherwise look below)
drun #Executes container
dshell #Launches the container in a dynamic environment (ie. you get a bash terminal)

#Interactive container
cd /worskpace #Where the code and the sample exists
env_name #Set's conda environment (base_env, tf_v2, tf_v3, pytorch, xgboost) supported
jl #In Apptainer you get an alias with the Jupyter Lab running on the defined port

##Optional cleanup
source setup.sh "" cleanup #Will unset all the environment variables

##Optional forcefully not using the GPU (if available)
arun --no-gpu
drun --no-gpu

```

### Kubeflow support for NGT WP1.1 cluster

New support has been added to include kubeflow integration required for the Next-Generation Trigger cluster. The user should be using the same configuration file and only enable the following option

```
KUBEFLOW_FILE: "yes"

#This can be done automatically during generation
```

Including the kubeflow file option will generate a dedicated .yaml file with the following naming convention:

```
<PROJECT_NAME>_kubeflow.yaml
```

to utilize this file the following extra aliases will be created within the wp21_ml_framework environment

1. `krun`: Launches the kubeflow session in the cluster machine
2. `kstatus`: Checks the status of the launched container to see if it's running
3. `kstop`: Kills the launched container 
4. `kerror`: Checks in case of errors what the issues were

***NOTE*** Kubeflow support assumes the following:

1. All the required steps to setup access to the NGT WP1.1 cluster have been taken (instructions)[https://ngt.docs.cern.ch/getting-started/]
2. Source code cannot leave in local machine but rather in eos as this is how it's mounted within WP1.1 resources
3. Jupyter notebook launching isn't supported yet in the dedicated container


## Container Filesystem

```
/workspace #Main working folder
/workspace/samples #Folder with the data sample used, either mounted or copied from /eos
/workspace/workDir #Folder where the ML model files exists and all the development happens
(Optional) /workspace/testDir #Directory with mounted test tools that can be used by the user

```

### Docker vs Apptainer on EOS paths

When using the docker container if the file is not copied in the container then you cannot mount FUSE based paths. The contianer will through a critical warning to mention that the EOS path cannot be mounted. On the contrary apptainer doesn't have this constraint so please use the apptainer wrapper for that. 

## Container environment

The container creates a fixed environment and detects automatically whether the host machine has an NVIDIA GPU for training purposes. After that sets some of the configuration parameters and alias for execution

1. Exported variables

   a. `ENV_NAME`: A user provided name for the current configuration (ie. You can provide the name of the algorithm you develop)
   
   b. `CONT_NAME`: Select one of the containers supported by the WP2.1 developers (harbor, conifer, base)
   
   c. `CONT_LOC`: Checks where to fetch the container from. Currently harbor and cvmfs are used but also you can use local images (use custom if custom image is going to be used)
   
   d. `SAMPLE_PATH`: Define the path where the sample leaves (if the sample exists in the WP2.1 eos path don't write the first /)
   
   e. `SAMPLE_NAME`: Name the sample which needs to be copied or mounted (if empty the whole directory will be taken)
   
   f. `SAMPLE_EOS`: If [yes] selected then the /eos path for the WP2.1 project will be added automatically and the sample will be copied within the container (**CAUTION**: That can explode the container size when running)
   
   g. `PROJECT_FOLDER`: Define the path towards the folder where your project exists (local path) (This folder is mounted into the container)
   
   h. `PROJECT_NAME`: Folder name where your ML code exists (basically `$PROJECT_FOLDER/$PROJECT_NAME` is the mounted folder)
   
   i. `TEST_FOLDER`: Extra space for testing tools or Vivado (optional)
   
   j. `TEST_NAME`: Test folder name (`$TEST_FOLDER/$TEST_NAME` mounted if provided
   
   k. `KRB_ACCOUNT`: Kerberos for authentication if the sample has to be copied from /eos (when sample not available to be mounted)
   
   l. `KRB_PASSWORD`: File that contains the password for the automatic /eos authentication (if not provided the kinit will fail and then the user has to copy the file from /eos manually after launching the container)
   
   m. `KUBEFLOW_FILE`: Generates dedicated KUBEFLOW FILE for the NextGen WP1.1 cluster.
   
   n. `JUPYTER_PORT`: Port in which the Jupyter Notebook within the container will execute.
   
2. Alias

   a. `drun`: Executes the docker container (if the user has access to launch docker containers)
   
   b. `dshell`: Executes the docker container in interactive mode
   
   c. `arun`: Launches the Apptainer-Wrapper (if /eos available it looks in the /eos/project/a/atlas-ngt-wp21/apptainer_containers path)
   
   d. `(Developers) abuild`: Uses the .def file from the apptainer submodules and builds the apptainer image locally in the current folder (assumes that the user has cloned the submodules as well)

### Building Apptainers (Developers only!)

In order to build the propoer apptainer wrapper for the different docker containers maintained by WP2.1 please follow the commands below.

```
source setup.sh <config>.yml #Container will be pulled based on mention in the configuration
abuild --tmp-dir <path-to-tmp-dir> --sif-dir <path-for-sif-file> --cache-dir <path-to-cache-dir> #All three are optional and if not provided the $(pwd) path is used
```

After completing those the .sif file will be generated in the folder indicated by the --sif-file (or $(pwd)). If the .sif file exists in the project folder this sif file is used. If a version of the sif file is present in eos then this version is picked automatically (priority to local).

## How to use the CI infrastructure

The CI infrastructure is aiming to remain independent from the underlying algorithm for this reason the user is discouraged to perform any modifications of how the CI stages are implemented. In order to utilize the existing work please see the below instructions:

1. Request an algorithm specific branch from the repository maintainers

```
git clone <ml-framework-url>.git
git checkout -b "my_branch"
git submodule update --init --recursive
git submodule add <custom_project_link>.git project/ #Over-writtes the dummy project

```

2. Triggering the CI by pushing to the specific branch

**Note*** The CI is utilizing WP1.1 infrastructure and hence subject to delays when the resources are used. In addition the CI assumes project wide access into the EOS project folder where meta-data can be stored. However the meta-data in EOS aren't backed up and the WP2.1 team will be deleting them every month for a fair share of resources

3. Pipeline currently in dev branch but soon with a few more modifications and optimizations it will migrate to v2.0 of the repository


## Developers

The sub-modules are all maintained by the ATLAS NextGen WP2.1 team. For contact please send us an [email](mailto:altas-ngt-wp21@cern.ch)