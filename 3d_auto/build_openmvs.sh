#!/bin/bash

# Set temporary environment variables
export TMP=$(pwd)/build
export DEBIAN_FRONTEND=noninteractive

BUILD_DIR=$(pwd)/build

# Update and upgrade system packages
sudo apt-get update -qq && sudo apt-get upgrade -qq

# Install necessary packages
sudo apt-get install -y \
  build-essential \
  cmake \
  git \
  ninja-build \
  graphviz \
  libatlas-base-dev \
  libboost-all-dev \
  libboost-filesystem-dev \
  libboost-iostreams-dev \
  libboost-program-options-dev \
  libboost-regex-dev \
  libboost-serialization-dev \
  libboost-system-dev \
  libboost-test-dev \
  libboost-graph-dev \
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
  libglfw3-dev \
  gcc-11 \
  g++-11

export CC=/usr/bin/gcc-11
export CXX=/usr/bin/g++-11
export CUDA_ROOT=/usr/local/cuda-11.8
sudo ln -sf /usr/bin/gcc-11 $CUDA_ROOT/bin/gcc
sudo ln -sf /usr/bin/g++-11 $CUDA_ROOT/bin/g++

# Increase swap space if not already set
if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Create temporary build directory
mkdir -p $TMP && cd $TMP || exit 1

# Function to clone or update repositories
clone_or_update_repo() {
  local repo_url=$1
  local target_dir=$2
  local branch=$3

  if [ -d $target_dir ]; then
    echo "Removing existing directory $target_dir"
    rm -rf $target_dir
  fi

  git clone -b $branch --recursive $repo_url $target_dir
  return $?
}

# Install Eigen
clone_or_update_repo https://gitlab.com/libeigen/eigen.git ${TMP}/eigen master
if [ $? -ne 0 ]; then
  echo "Error cloning Eigen"
  exit 1
fi

mkdir -p ${TMP}/eigen/build && cd ${TMP}/eigen/build || exit 1
cmake .. && make -j$(nproc) && sudo make install
if [ $? -ne 0 ]; then
  echo "Error installing Eigen"
  exit 1
fi

# Install Ceres Solver
clone_or_update_repo https://ceres-solver.googlesource.com/ceres-solver ${TMP}/ceres_solver master
if [ $? -ne 0 ]; then
  echo "Error cloning Ceres Solver"
  exit 1
fi

cd ${TMP}/ceres_solver && git checkout tags/2.1.0
mkdir -p ${TMP}/ceres_solver/build && cd ${TMP}/ceres_solver/build || exit 1
cmake .. -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF && make -j$(nproc) && sudo make install
if [ $? -ne 0 ]; then
  echo "Error installing Ceres Solver"
  exit 1
fi

# Install VCGlib
clone_or_update_repo https://github.com/cnr-isti-vclab/vcglib.git ${TMP}/vcglib main
if [ $? -ne 0 ]; then
  echo "Error cloning VCGlib"
  exit 1
fi

# Install OpenMVS
clone_or_update_repo https://github.com/cdcseacave/openMVS.git ${TMP}/openMVS master
if [ $? -ne 0 ]; then
  echo "Error cloning OpenMVS"
  exit 1
fi

mkdir -p ${TMP}/openMVS/build && cd ${TMP}/openMVS/build || exit 1

# Specify CUDA architectures
export CUDA_ARCHS="61;62;70;75;80"

# Configure the use of GCC 11 for CUDA
cmake .. -DCMAKE_BUILD_TYPE=Release -DVCG_ROOT="${TMP}/vcglib" -DCUDA_ARCHITECTURES=${CUDA_ARCHS} -DCUDA_HOST_COMPILER=/usr/bin/gcc-11
make -j$(nproc)
if [ $? -ne 0 ]; then
  echo "Error building OpenMVS"
  exit 1
fi

# Install OpenMVS library (optional)
sudo cmake --install .

# Add OpenMVS to PATH
if ! grep -q 'export PATH=/usr/local/bin:$PATH' ~/.bashrc; then
    echo 'export PATH=/usr/local/bin:$PATH' >> ~/.bashrc
    source ~/.bashrc
fi

if ! grep -q 'export PATH=$PATH:/usr/local/bin/OpenMVS' ~/.bashrc; then
  echo 'export PATH=$PATH:/usr/local/bin/OpenMVS' >> ~/.bashrc
fi

# Install OpenMVG
clone_or_update_repo https://github.com/openMVG/openMVG.git ${TMP}/openmvg develop
if [ $? -ne 0 ]; then
  echo "Error cloning openMVG"
  exit 1
fi

mkdir -p ${TMP}/openmvg_build && cd ${TMP}/openmvg_build || exit 1
cmake -DCMAKE_BUILD_TYPE=RELEASE -DEIGEN3_INCLUDE_DIR=/usr/include/eigen3 . ../openmvg/src -DCMAKE_INSTALL_PREFIX=/opt/openmvg
if [ $? -ne 0 ]; then
  echo "Error configuring openMVG"
  exit 1
fi

make -j$(nproc) && sudo make install
if [ $? -ne 0 ]; then
  echo "Error installing openMVG"
  exit 1
fi

# Install CMVS-PMVS
git clone https://github.com/pmoulon/CMVS-PMVS ${TMP}/cmvs-pmvs && \
  mkdir ${TMP}/cmvs-pmvs_build && cd ${TMP}/cmvs-pmvs_build && \
  cmake ../cmvs-pmvs/program -DCMAKE_INSTALL_PREFIX=/opt/cmvs && \
  make -j$(nproc) && \
  sudo make install
if [ $? -ne 0 ]; then
  echo "Error installing CMVS-PMVS"
  exit 1
fi

# Add OpenMVG to PATH
if ! grep -q 'export PATH=$PATH:/opt/openmvg/bin' ~/.bashrc; then
  echo 'export PATH=$PATH:/opt/openmvg/bin' >> ~/.bashrc
fi

echo 'Installation complete. Please run "source ~/.bashrc" to update your PATH.'

# Cleanup
rm -rf $BUILD_DIR

# Add CUDA and OpenMVS paths to the virtual environment activation script
ACTIVATE_SCRIPT="$HOME/Pyvenv/sylva3d/bin/activate"

if [ -f "$ACTIVATE_SCRIPT" ]; then
  if ! grep -q 'export PATH=$PATH:/usr/local/bin/OpenMVS' "$ACTIVATE_SCRIPT"; then
    echo -e '\n# Add OpenMVS and OpenMVG paths\nexport PATH=$PATH:/usr/local/bin/OpenMVS\nexport PATH=$PATH:/opt/openmvg/bin' >> "$ACTIVATE_SCRIPT"
  fi
fi
