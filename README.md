### Sylva3D: GUI for Photogrammetry

---

#### English Version

##### Overview

Sylva3D is a Dockerized application that provides a graphical user interface (GUI) for photogrammetry tasks using COLMAP and OpenMVS. This project allows users to perform photogrammetry, which is the process of reconstructing 3D models from a series of photographs. The application leverages CUDA for GPU acceleration to ensure efficient processing.

##### Features

- **Photogrammetry Pipeline**: Integrates COLMAP and OpenMVS to create detailed 3D models from photographs.
- **Graphical User Interface (GUI)**: Simplifies the photogrammetry process with an easy-to-use GUI built using Python and tkinter.
- **GPU Acceleration**: Utilizes NVIDIA CUDA for faster computation.

##### Prerequisites

- Docker installed on your system.
- NVIDIA Docker support for GPU acceleration.
- X server installed and configured (VcXsrv for Windows).

##### Setting Up the Environment

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

##### Pulling the Docker Image

To get started with Sylva3D, pull the Docker image from Docker Hub:

```bash
docker pull amiche/sylva3d:latest
```

##### Running the Application

1. **Set the DISPLAY environment variable** (for Windows users using WSL):

```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
```

2. **Allow Docker to access X server**:

```bash
xhost +local:docker
```

3. **Run the Docker container**:

```bash
docker run --gpus all -w /workspace \
    -v ${HOME}:/mnt/home \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    -e QT_X11_NO_MITSHM=1 \
    -it amiche/sylva3d:latest
```

This command runs the Sylva3D application inside a Docker container with GPU support and connects to your local X server to display the GUI.

##### Usage Instructions

Once the application is running, the GUI will launch and you can start using Sylva3D for your photogrammetry projects. Follow these steps:

1. **Import Photographs**: Load your series of photographs into the application.
2. **Run COLMAP**: Use the integrated COLMAP features to align images and create a sparse 3D model.
3. **Generate Dense Model**: Utilize OpenMVS to generate a dense 3D reconstruction from the sparse model.
4. **Export 3D Model**: Save the reconstructed 3D model in your desired format.

##### Building from Source

If you want to build the Docker image from source, follow these steps:

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

##### Troubleshooting

- **GUI not displaying**:
  - Ensure that VcXsrv or your X server is running.
  - Verify that the `DISPLAY` environment variable is correctly set.
  - Check the Docker run command to ensure it includes the `-e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix` options.

- **Performance issues**:
  - Ensure that your system has a compatible NVIDIA GPU and that the NVIDIA Docker runtime is properly installed.
  - Verify that GPU drivers are up-to-date.

##### Future Enhancements

- **Improved Error Handling**: Enhanced feedback and error messages for better user experience.
- **Additional Photogrammetry Tools**: Integration of more advanced photogrammetry tools and features.
- **Cross-Platform GUI**: Ensure the application runs smoothly on different operating systems without the need for X servers.

##### Contact and Support

For any questions, issues, or contributions, please visit the [Sylva3D GitHub repository](https://github.com/Amiche02/Sylva3dGUI) or contact the project maintainers at projectsengineer6@gmail.com.

---

#### Version Française

##### Vue d'ensemble

Sylva3D est une application Dockerisée qui fournit une interface graphique (GUI) pour les tâches de photogrammétrie utilisant COLMAP et OpenMVS. Ce projet permet aux utilisateurs de réaliser de la photogrammétrie, qui est le processus de reconstruction de modèles 3D à partir d'une série de photographies. L'application utilise CUDA pour l'accélération GPU afin d'assurer un traitement efficace.

##### Caractéristiques

- **Pipeline de Photogrammétrie**: Intègre COLMAP et OpenMVS pour créer des modèles 3D détaillés à partir de photographies.
- **Interface Graphique (GUI)**: Simplifie le processus de photogrammétrie avec une interface facile à utiliser construite en Python et tkinter.
- **Accélération GPU**: Utilise NVIDIA CUDA pour des calculs plus rapides.

##### Prérequis

- Docker installé sur votre système.
- Support de NVIDIA Docker pour l'accélération GPU.
- Serveur X installé et configuré (VcXsrv pour Windows).

##### Configuration de l'Environnement

Avant d'exécuter Sylva3D, assurez-vous que vous avez le bon environnement configuré :

1. **Installer Docker**: Suivez le guide d'installation officiel de Docker pour votre système d'exploitation.
2. **Installer NVIDIA Docker**: Suivez le [guide d'installation de NVIDIA Docker](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) pour activer le support GPU.
3. **Installer un serveur X** (pour les utilisateurs Windows) :
   - Téléchargez et installez [VcXsrv](https://sourceforge.net/projects/vcxsrv/).
   - Lancez VcXsrv avec les paramètres suivants :
     - Multiple windows
     - Display number: 0
     - Start no client
     - Disable access control

##### Récupérer l'Image Docker

Pour commencer avec Sylva3D, récupérez l'image Docker depuis Docker Hub :

```bash
docker pull amiche/sylva3d:latest
```

##### Exécuter l'Application

1. **Définir la variable d'environnement DISPLAY** (pour les utilisateurs Windows utilisant WSL) :

```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
```

2. **Autoriser Docker à accéder au serveur X** :

```bash
xhost +local:docker
```

3. **Exécuter le conteneur Docker** :

```bash
docker run --gpus all -w /workspace \
    -v ${HOME}:/mnt/home \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    -e QT_X11_NO_MITSHM=1 \
    -it amiche/sylva3d:latest
```

Cette commande exécute l'application Sylva3D dans un conteneur Docker avec le support GPU et se connecte à votre serveur X local pour afficher l'interface graphique.

##### Instructions d'Utilisation

Une fois l'application lancée, l'interface graphique apparaîtra et vous pourrez commencer à utiliser Sylva3D pour vos projets de photogrammétrie. Suivez ces étapes :

1. **Importer des Photographies** : Chargez votre série de photographies dans l'application.
2. **Exécuter COLMAP** : Utilisez les fonctionnalités intégrées de COLMAP pour aligner les images et créer un modèle 3D épars.
3. **Générer un Modèle Dense** : Utilisez OpenMVS pour générer une reconstruction 3D dense à partir du modèle épars.
4. **Exporter le Modèle 3D** : Enregistrez le modèle 3D reconstruit dans le format souhaité.

##### Compilation depuis les Sources

Si vous souhaitez compiler l'image Docker à partir des sources, suivez ces étapes :

1. **Cloner le Répertoire** :

```bash
git clone https://github.com/Amiche02/Sylva3dGUI.git
cd Sylva3dGUI
```

2. **Construire l'Image Docker** :

```bash
docker build -t sylva3d .
```



3. **Exécuter le Conteneur Docker** :

```bash
docker run --gpus all -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -it sylva3d
```

##### Dépannage

- **GUI ne s'affiche pas** :
  - Assurez-vous que VcXsrv ou votre serveur X est en cours d'exécution.
  - Vérifiez que la variable d'environnement `DISPLAY` est correctement définie.
  - Vérifiez la commande d'exécution Docker pour vous assurer qu'elle inclut les options `-e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix`.

- **Problèmes de performance** :
  - Assurez-vous que votre système dispose d'un GPU NVIDIA compatible et que le runtime NVIDIA Docker est correctement installé.
  - Vérifiez que les pilotes GPU sont à jour.

##### Améliorations Futures

- **Meilleure Gestion des Erreurs** : Amélioration des messages d'erreur et des retours pour une meilleure expérience utilisateur.
- **Outils de Photogrammétrie Supplémentaires** : Intégration d'outils de photogrammétrie plus avancés et de fonctionnalités supplémentaires.
- **Interface Graphique Multi-Plateforme** : Assurez-vous que l'application fonctionne correctement sur différents systèmes d'exploitation sans avoir besoin de serveurs X.

##### Contact et Support

Pour toutes questions, problèmes ou contributions, veuillez visiter le [répertoire GitHub de Sylva3D](https://github.com/Amiche02/Sylva3dGUI) ou contacter les mainteneurs du projet à projectsengineer6@gmail.com.

---

En suivant cette documentation, vous devriez être capable de configurer et d'utiliser Sylva3D pour vos tâches de photogrammétrie. L'application vise à simplifier le processus complexe de reconstruction 3D à partir de photographies, la rendant accessible et efficace pour les utilisateurs.

---
