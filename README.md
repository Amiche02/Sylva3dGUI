---

# Sylva3D: GUI for Photogrammetry

## Overview

Sylva3D is a Dockerized application that provides a graphical user interface (GUI) for photogrammetry tasks using COLMAP and OpenMVS. Photogrammetry is the process of reconstructing 3D models from a series of photographs, and Sylva3D simplifies this process, leveraging CUDA for GPU acceleration to ensure efficient processing.

## Features

- **Photogrammetry Pipeline**: Integrates COLMAP and OpenMVS to create detailed 3D models from photographs.
- **Graphical User Interface (GUI)**: Simplifies the photogrammetry process with an easy-to-use GUI built using Python and tkinter.
- **GPU Acceleration**: Utilizes NVIDIA CUDA for faster computation.

## Prerequisites

Before you start, ensure your system meets the following requirements:

- Docker installed on your system.
- NVIDIA Docker support for GPU acceleration.
- X server installed and configured (e.g., VcXsrv for Windows).

## Setting Up the Environment

### Installing Docker

1. **Install Docker**: Follow the official Docker installation guide for your operating system.

2. **Install NVIDIA Docker**: Follow the [NVIDIA Docker installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) to enable GPU support.

3. **Install X Server** (for Windows users):
   - Download and install [VcXsrv](https://sourceforge.net/projects/vcxsrv/).
   - Launch VcXsrv with the following settings:
     - Multiple windows
     - Display number: 0
     - Start no client
     - Disable access control

## Pulling the Docker Image

To get started with Sylva3D, pull the Docker image from Docker Hub:

```bash
docker pull amiche/sylva3d:latest
```

You can also view the image and additional details directly on [Docker Hub](https://hub.docker.com/r/amiche/sylva3d).

## Running the Application in Docker

### Setting Up Display (Windows Users Only)

1. **Set the DISPLAY environment variable** (for Windows users using WSL):

    ```bash
    export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
    ```

2. **Allow Docker to access X server**:

    ```bash
    xhost +local:docker
    ```

### Running the Docker Container

Run the following command to start Sylva3D with GPU support:

```bash
docker run --gpus all -w /workspace \
    -v ${HOME}:/mnt/home \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    -e QT_X11_NO_MITSHM=1 \
    -it amiche/sylva3d:latest
```

This command will launch Sylva3D inside a Docker container with GPU support and connect to your local X server to display the GUI.

## Usage Instructions

Once the application is running, follow these steps:

1. **Import Photographs**: Load your series of photographs into the application.
2. **Run COLMAP**: Use the integrated COLMAP features to align images and create a sparse 3D model.
3. **Generate Dense Model**: Utilize OpenMVS to generate a dense 3D reconstruction from the sparse model.
4. **Export 3D Model**: Save the reconstructed 3D model in your desired format.

## Building the Docker Image from Source

If you prefer to build the Docker image from source:

### Installing CUDA

Before starting, you need to install CUDA. Here is an example for Ubuntu 22.04:

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda
```

If you're using a different version of Ubuntu or another Linux distribution, or if you need a different version of CUDA, visit the [CUDA 11.8 Download Archive](https://developer.nvidia.com/cuda-11-8-0-download-archive) for installation instructions.

### Building the Image

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/Amiche02/Sylva3dGUI.git
    cd Sylva3dGUI
    ```

2. **Build the Docker Image**:

    ```bash
    docker build -t sylva3d .
    ```

3. **Run the Docker Container**:

    ```bash
    docker run --gpus all -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -it sylva3d
    ```

## Running Sylva3D Directly on Linux

For users who prefer to run Sylva3D directly on their Linux system without using Docker:

### Prerequisites

Ensure that you have the following installed on your system:

- Python 3.10
- Git
- CUDA 11.8 (If the version changes, you may need to adjust the build scripts)
- NVIDIA GPU with CUDA support

### Installing CUDA

1. **Install CUDA 11.8** (example for Ubuntu 22.04):

    ```bash
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
    sudo dpkg -i cuda-keyring_1.0-1_all.deb
    sudo apt-get update
    sudo apt-get -y install cuda
    ```

2. **Verify CUDA Installation**:

    After installing CUDA, verify the installation by running:

    ```bash
    nvcc --version
    ```

    This should display information about the installed CUDA version.

### Cloning the Repository and Building Dependencies

1. **Clone the Sylva3D Repository**:

    ```bash
    git clone https://github.com/Amiche02/Sylva3dGUI.git
    cd Sylva3dGUI
    ```

2. **Build COLMAP and OpenMVS**:

    Navigate to the `manual_install` directory and run the provided scripts:

    ```bash
    cd manual_install

    chmod +x build_colmap.sh build_openmvs.sh
    ```

    If you know the CUDA architecture of your GPU, specify it when running the `build_colmap.sh` script:

    ```bash
    ./build_colmap.sh <cuda_arch>
    ```

    Replace `<cuda_arch>` with the appropriate value for your GPU. Refer to the [CUDA documentation](https://developer.nvidia.com/cuda-gpus) if you're unsure.

    Then, build OpenMVS:

    ```bash
    ./build_openmvs.sh
    ```

3. **Run the Application**:

    After successfully building the dependencies, navigate to the `app` directory and run the application:

    ```bash
    cd ..
    cd app
    python3 app.py
    ```

## Troubleshooting

### General Issues

- **GUI Not Displaying**:
  - Ensure that VcXsrv or your X server is running.
  - Verify that the `DISPLAY` environment variable is correctly set.
  - Check that the Docker run command includes the `-e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix` options.

- **Performance Issues**:
  - Ensure that your system has a compatible NVIDIA GPU and that the NVIDIA Docker runtime is properly installed.
  - Verify that GPU drivers are up-to-date.

### Linux Direct Execution Issues

- **CUDA Installation Issues**: Make sure your NVIDIA drivers are up-to-date and compatible with the CUDA version you're installing.
- **Building Errors**: If you encounter errors during the build process, check the logs for missing dependencies or misconfigured environment variables. Ensure your system meets all prerequisites.
- **Performance Issues**: Confirm that your GPU is being properly utilized by monitoring GPU usage with tools like `nvidia-smi`.

## Future Enhancements

- **Improved Error Handling**: Enhanced feedback and error messages for a better user experience.
- **Additional Photogrammetry Tools**: Integration of more advanced photogrammetry tools and features.
- **Cross-Platform GUI**: Ensure the application runs smoothly on different operating systems without the need for X servers.

## Contributing

I am open to contributions and suggestions to improve Sylva3D. If you have ideas for new features, find bugs, or want to help with development, feel free to open issues or submit pull requests on the [Sylva3D GitHub repository](https://github.com/Amiche02/Sylva3dGUI).

## License

Sylva3D is released under the [MIT License](https://opensource.org/licenses/MIT). You are free to use, modify, and distribute this software, as long as you include the original license.

## Contact and Support

For any questions, issues, or contributions, please visit the [Sylva3D GitHub repository](https://github.com/Amiche02/Sylva3dGUI) or contact the project maintainers at projectsengineer6@gmail.com.

---

By following this documentation, you should be able to set up and use Sylva3D for your photogrammetry tasks, making the complex process of 3D reconstruction from photographs accessible and efficient.

--- 

