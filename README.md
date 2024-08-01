### Sylva3D: GUI for Photogrammetry

#### Overview

Sylva3D is a Dockerized application that provides a graphical user interface (GUI) for photogrammetry tasks using COLMAP and OpenMVS. This project allows users to perform photogrammetry, which is the process of reconstructing 3D models from a series of photographs. The application leverages CUDA for GPU acceleration to ensure efficient processing.

#### Features

- **Photogrammetry Pipeline**: Integrates COLMAP and OpenMVS to create detailed 3D models from photographs.

- **Graphical User Interface (GUI)**: Simplifies the photogrammetry process with an easy-to-use GUI built using Python and tkinter.

- **GPU Acceleration**: Utilizes NVIDIA CUDA for faster computation.

#### Prerequisites

- Docker installed on your system.

- NVIDIA Docker support for GPU acceleration.

- X server installed and configured (VcXsrv for Windows).

#### Setting Up the Environment

Before running Sylva3D, ensure you have the necessary environment setup:

1. **Install Docker**: Follow the official Docker installation guide for your operating system.

2. **Install NVIDIA Docker**: Follow the [NVIDIA Docker installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) to enable GPU support.

3. **Install X server** (for Windows users):

   - Download and install [VcXsrv](https://sourceforge.net/projects/vcxsrv/).

   - Launch VcXsrv with the following settings:

     - Multiple windows

     - Display number: 0

     - Start no client

     - Disable access control

#### Pulling the Docker Image

To get started with Sylva3D, pull the Docker image from Docker Hub:

```bash
docker pull your_dockerhub_username/sylva3d:latest
```

#### Running the Application

1. **Set the DISPLAY environment variable** (for Windows users using WSL): 

```bash
export DISPLAY=$(grep -oP '(?<=nameserver\s)\S+' /etc/resolv.conf):0

xhost +
```

  

2. **Run the Docker container**:

```bash
docker run --gpus all -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -it amiche/sylva3d
```



This command runs the Sylva3D application inside a Docker container with GPU support and connects to your local X server to display the GUI.

#### Usage Instructions

Once the application is running, the GUI will launch and you can start using Sylva3D for your photogrammetry projects. Follow these steps:

1. **Import Photographs**: Load your series of photographs into the application.

2. **Run COLMAP**: Use the integrated COLMAP features to align images and create a sparse 3D model.

3. **Generate Dense Model**: Utilize OpenMVS to generate a dense 3D reconstruction from the sparse model.

4. **Export 3D Model**: Save the reconstructed 3D model in your desired format.

#### Building from Source

If you want to build the Docker image from source, follow these steps:

1. **Clone the Repository**:
   
   ```bash
    git clone https://github.com/Amiche02/Sylva3dGUI.git
   
    cd Sylva3dApp
   ```



2. **Build the Docker Image**:

```bash
 docker build -t sylva3d .
```

  

3. **Run the Docker Container**:

```bash
 docker run --gpus all -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -it sylva3d
```



#### Troubleshooting

- **GUI not displaying**:

  - Ensure that VcXsrv or your X server is running.

  - Verify that the `DISPLAY` environment variable is correctly set.

  - Check the Docker run command to ensure it includes the `-e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix` options.

- **Performance issues**:

  - Ensure that your system has a compatible NVIDIA GPU and that the NVIDIA Docker runtime is properly installed.

  - Verify that GPU drivers are up-to-date.

#### Future Enhancements

- **Improved Error Handling**: Enhanced feedback and error messages for better user experience.

- **Additional Photogrammetry Tools**: Integration of more advanced photogrammetry tools and features.

- **Cross-Platform GUI**: Ensure the application runs smoothly on different operating systems without the need for X servers.

#### Contact and Support

For any questions, issues, or contributions, please visit the [Sylva3D GitHub repository](https://github.com/Amiche02/Sylva3dGUI.git) or contact the project maintainers at projectsengineer6@gmail.com.

---

By following this documentation, you should be able to set up and use Sylva3D for your photogrammetry tasks. The application aims to simplify the complex process of 3D reconstruction from photographs, making it accessible and efficient for users.
