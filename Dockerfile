ARG UBUNTU_VERSION=22.04
ARG NVIDIA_CUDA_VERSION=12.3.1

FROM nvidia/cuda:${NVIDIA_CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION} as builder

ARG COLMAP_GIT_COMMIT=main
ARG CUDA_ARCHITECTURES="60;61;62;70;72;75;80;86"
ENV QT_XCB_GL_INTEGRATION=xcb_egl
ENV DEBIAN_FRONTEND=noninteractive

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
        libceres-dev && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/colmap/colmap.git && \
    cd colmap && \
    git fetch https://github.com/colmap/colmap.git ${COLMAP_GIT_COMMIT} && \
    git checkout FETCH_HEAD && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCHITECTURES} \
        -DCMAKE_INSTALL_PREFIX=/colmap_installed && \
    ninja install -j4

FROM nvidia/cuda:${NVIDIA_CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}

ARG MASTER=0
ARG USER_ID
ARG GROUP_ID
ARG CUDA=0

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris

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
    xvfb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /colmap_installed/ /usr/local/

WORKDIR /workspace

COPY build_openmvs.sh requirements.txt /workspace/

RUN chmod +x /workspace/build_openmvs.sh

RUN /workspace/build_openmvs.sh --cuda $CUDA --user_id $USER_ID --group_id $GROUP_ID --master $MASTER && \
    rm /workspace/build_openmvs.sh

ENV PATH /usr/local/bin/OpenMVS:$PATH

RUN pip3 install -r /workspace/requirements.txt

COPY . /workspace

RUN if [ -n "$USER_ID" ] && [ -n "$GROUP_ID" ]; then \
        groupadd -g $GROUP_ID usergroup && \
        useradd -m -u $USER_ID -g $GROUP_ID -s /bin/bash user && \
        chown -R $USER_ID:$GROUP_ID /workspace; \
    fi

USER $USER_ID

CMD ["python3", "/workspace/tkinter/app.py"]
