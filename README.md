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

2. Apptainer

The apptainer-wrapper container provides an interface where users can launch the docker container. The user has two options either to launch the docker container directly or use the apptainer wrapper so that they can mount the development folder and all the tool dependencies (ie. Vitis). For more information please look into the relevant README file.

3. WP21_Train

This is the python package developed by the WP2.1 team to handle meta-data from the model development. The package can be build and installed via pip-install. At the minute given that the tool hasn't reached a stable production release and hence it's used by the apptainer-wrapper when launching the container and is built every time from scratch. When the tool hits a level of maturity it will be removed from here and will be added as a conda package within the docker container.

## How to use

In order to develop within the WP2.1 framework please use the following instructions:

```
git clone <ml-framework-url>.git
git submodule update --init --recursive
source setup.sh <config-file>.yml #Produces all the paths for developments in additio to aliases for executing the containers

##Optional cleanup
source setup.sh "" cleanup #Will unset all the environment variables

```

## Developers

The sub-modules are all maintained by the ATLAS NextGen WP2.1 team. For contact please send us an [email](mailto:altas-ngt-wp21@cern.ch)
