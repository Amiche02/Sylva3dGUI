ARG UBUNTU_VERSION=22.04
ARG NVIDIA_CUDA_VERSION=11.8.0

FROM nvidia/cuda:${NVIDIA_CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION} as builder

ARG COLMAP_GIT_COMMIT=main
ARG CUDA_ARCHITECTURES="60;61;62;70;72;75;80;86"
ENV QT_XCB_GL_INTEGRATION=xcb_egl
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and COLMAP
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
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
        libxkbcommon-x11-0 \
        libxcb-xinerama0 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-shape0 \
        libxcb-xfixes0 \
        libxcb-xkb1 \
        libxcb-sync1 \
        libxcb-dri3-0 \
        libxcb-util1 \
        && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/colmap/colmap.git && \
    cd colmap && \
    git fetch https://github.com/colmap/colmap.git ${COLMAP_GIT_COMMIT} && \
    git checkout FETCH_HEAD && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCHITECTURES} \
        -DCMAKE_INSTALL_PREFIX=/colmap_installed && \
    ninja install -j4 && \
    rm -rf /colmap/build && \
    rm -rf /colmap/.git

FROM nvidia/cuda:${NVIDIA_CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}

ARG MASTER=0
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG CUDA=0

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    libprotobuf-dev \
    protobuf-compiler \
    libxcb-cursor0 \
    python3-tk \
    tcl-dev \
    tk-dev \
    build-essential \
    cmake \
    git \
    ninja-build \
    libboost-all-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    x11-apps \
    x11-xserver-utils \
    xauth \
    jq \
    xvfb \
    libxkbcommon-x11-0 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xkb1 \
    libxcb-sync1 \
    libxcb-dri3-0 \
    libxcb-util1 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Augmenter l'espace swap si nécessaire
RUN [ ! -f /swapfile ] && fallocate -l 4G /swapfile && \
    chmod 600 /swapfile && \
    mkswap /swapfile && \
    swapon /swapfile && \
    echo '/swapfile none swap sw 0 0' >> /etc/fstab || echo "Swapfile already exists."

# Copy COLMAP installation from builder stage
COPY --from=builder /colmap_installed/ /usr/local/

WORKDIR /workspace

# Copy application files and build scripts
COPY requirements.txt /workspace/requirements.txt
COPY build_openmvs.sh /workspace/docker_build_openmvs.sh

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /workspace/requirements.txt && \
    rm /workspace/requirements.txt

# Build and install OpenMVS
RUN chmod +x /workspace/docker_build_openmvs.sh && \
    /workspace/docker_build_openmvs.sh --cuda $CUDA --user_id $USER_ID --group_id $GROUP_ID --master $MASTER && \
    rm /workspace/docker_build_openmvs.sh

# Add OpenMVS binaries to PATH
ENV PATH=/usr/local/bin/OpenMVS:$PATH

# Copy remaining application files and set executable permissions
COPY ./app /workspace/app
RUN chmod +x /workspace/app/colmap_openmvs.sh /workspace/app/colmap_demo.sh /workspace/app/run_viewer.sh

# Set up environment for Qt
ENV QT_QPA_PLATFORM=xcb

# Default command
CMD ["python3", "/workspace/app/app.py"]
