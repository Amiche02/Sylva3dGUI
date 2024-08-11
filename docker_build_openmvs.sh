#!/bin/bash

set -e

# Installation des dépendances nécessaires
apt-get update -yq
apt-get install -yq \
  build-essential \
  cmake \
  git \
  ninja-build \
  graphviz \
  libatlas-base-dev \
  libboost-all-dev \
  libcgal-dev \
  libcgal-qt5-dev \
  libeigen3-dev \
  libflann-dev \
  libfreeimage-dev \
  libgflags-dev \
  libglew-dev \
  libglu1-mesa-dev \
  libgoogle-glog-dev \
  libgtest-dev \
  libmetis-dev \
  libopencv-dev \
  libpng-dev \
  libqt5opengl5-dev \
  libsuitesparse-dev \
  libsqlite3-dev \
  libtiff-dev \
  libxi-dev \
  libxrandr-dev \
  libxxf86vm-dev \
  libxxf86vm1 \
  mediainfo \
  mercurial \
  qtbase5-dev \
  libceres-dev \
  libtbb-dev \
  libglfw3-dev

# Parse arguments
CUDA=0
MASTER=0
USER_ID=""
GROUP_ID=""

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --cuda)
            CUDA="$2"
            shift
            shift
            ;;
        --master)
            MASTER="$2"
            shift
            shift
            ;;
        --user_id)
            USER_ID="$2"
            shift
            shift
            ;;
        --group_id)
            GROUP_ID="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown argument: $key"
            exit 1
            ;;
    esac
done

# Configuration des arguments pour CUDA et la branche master
if [[ "$CUDA" == "1" ]]; then
    echo "Building with CUDA support"
    EIGEN_BUILD_ARG="-DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda/"
    OPENMVS_BUILD_ARG="-DOpenMVS_USE_CUDA=ON -DCMAKE_LIBRARY_PATH=/usr/local/cuda/lib64/stubs/ -DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda/ -DCUDA_INCLUDE_DIRS=/usr/local/cuda/include/ -DCUDA_CUDART_LIBRARY=/usr/local/cuda/lib64 -DCUDA_NVCC_EXECUTABLE=/usr/local/cuda/bin/"
else
    echo "Building without CUDA support"
    EIGEN_BUILD_ARG=""
    OPENMVS_BUILD_ARG="-DOpenMVS_USE_CUDA=OFF"
fi

if [[ "$MASTER" == "1" ]]; then
    BRANCH="master"
    echo "Pulling from master branch"
else
    BRANCH="develop"
    echo "Pulling from develop branch"
fi

# Build Eigen
echo "Cloning and building Eigen..."
git clone https://gitlab.com/libeigen/eigen --branch 3.4
mkdir -p eigen_build
cd eigen_build
cmake . ../eigen $EIGEN_BUILD_ARG
make -j$(nproc)
make install
cd ..
rm -rf eigen_build eigen

# Build VCGLib
echo "Cloning VCGLib..."
git clone https://github.com/cdcseacave/VCG.git vcglib

# Build OpenMVS
echo "Cloning and building OpenMVS..."
git clone https://github.com/cdcseacave/openMVS.git --branch $BRANCH
mkdir -p openMVS_build
cd openMVS_build
cmake . ../openMVS -DCMAKE_BUILD_TYPE=Release -DVCG_ROOT=$(pwd)/../vcglib $OPENMVS_BUILD_ARG
make -j$(nproc)
make install
cd ..
rm -rf openMVS_build vcglib openMVS

# Set permissions
if [[ -n "$USER_ID" && -n "$GROUP_ID" ]]; then
    echo "Setting permissions for user $USER_ID:$GROUP_ID"
    addgroup --gid $GROUP_ID user
    adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user
    chown -R $USER_ID:$GROUP_ID /workspace
else
    echo "USER_ID or GROUP_ID not set, skipping permission setting"
fi
