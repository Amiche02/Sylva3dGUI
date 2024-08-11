#!/bin/bash

# Set default CUDA architecture
DEFAULT_CUDA_ARCH=75

# Vérifiez si un argument d'architecture CUDA a été fourni
CUDA_ARCH=${1:-$DEFAULT_CUDA_ARCH}

# Set temporary environment variables
BUILD_DIR=$(pwd)/build
export DEBIAN_FRONTEND=noninteractive

# Update the system and install dependencies
sudo apt-get update -qq && sudo apt-get upgrade -qq

sudo apt-get install -y \
    git \
    cmake \
    ninja-build \
    build-essential \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgtest-dev \
    libsqlite3-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev \
    libopencv-dev \
    libopencv-core-dev \
    libopencv-highgui-dev \
    libopencv-imgcodecs-dev \
    libopencv-features2d-dev \
    libopencv-calib3d-dev

# Increase swap space
if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Create the temporary directory and navigate to it
mkdir -p $BUILD_DIR && sudo chown $(whoami) $BUILD_DIR

# Clone and install COLMAP
if [ -d "${BUILD_DIR}/colmap" ]; then
    echo "Removing existing COLMAP directory."
    sudo rm -rf ${BUILD_DIR}/colmap
fi

cd $BUILD_DIR
git clone https://github.com/colmap/colmap.git ${BUILD_DIR}/colmap || exit 1
mkdir -p ${BUILD_DIR}/colmap/build && cd ${BUILD_DIR}/colmap/build || exit 1
cmake .. -GNinja -DCMAKE_CUDA_ARCHITECTURES=$CUDA_ARCH || exit 1
ninja -j$(nproc) || exit 1
sudo ninja install || exit 1

# Add COLMAP to PATH
if ! grep -q 'export PATH=/usr/local/bin:$PATH' ~/.bashrc; then
    echo 'export PATH=/usr/local/bin:$PATH' >> ~/.bashrc
    source ~/.bashrc
fi

ACTIVATE_SCRIPT="$HOME/Pyvenv/sylva3d/bin/activate"

if [ -f "$ACTIVATE_SCRIPT" ]; alors
  if ! grep -q 'export PATH=/usr/local/bin:$PATH' "$ACTIVATE_SCRIPT"; then
    echo -e '\n# Add COLMAP path\nexport PATH=/usr/local/bin:$PATH' >> "$ACTIVATE_SCRIPT"
  fi
fi


# Confirmation message
echo "Installation de COLMAP terminée et ajoutée au PATH."

# Cleanup
rm -rf $BUILD_DIR
