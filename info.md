voilà la liste des fonctionnalités que que je veux inclure :
import des images pour la photogramétrie
import de video pour la photogramétrie ---> extraction des frames de la vidéo (choisir le nombre d'images par seconde.)
Affichage des images
Resize l'image (pour réduire le poids des images (au choix) sinon conserver la taille par défaut)
Suppression du background (au choix pour conserver uniquement un objet sur l'image)
Lancer le début de la photogramétrie (choix caractéristiques, usage de gpu ou non)
affichage de l'objet 3d
Téléchargement au format voulue.
A la fin je veux pouvoir supprimer tous les fichiers intermédaires,  les images, ... pour conserver que l'objet 3D et l'afficher à la page d'accueil comme exemple.


Bien sûr, voici les étapes détaillées pour installer CUDA 11.8 en utilisant le package `.deb` :

1. **Téléchargez le package CUDA 11.8 `.deb`** pour votre distribution depuis le site officiel de NVIDIA. Par exemple, pour Ubuntu 20.04, vous pouvez utiliser :
    ```bash
    wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
    ```

2. **Installez le package `.deb`** :
    ```bash
    sudo dpkg -i cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
    ```

3. **Ajoutez la clé du dépôt CUDA** :
    ```bash
    sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub
    ```

4. **Mettez à jour les paquets disponibles** :
    ```bash
    sudo apt-get update
    ```

5. **Installez CUDA 11.8** :
    ```bash
    sudo apt-get install cuda-11-8
    ```

6. **Ajoutez CUDA à votre PATH**. Ajoutez les lignes suivantes à votre fichier `~/.bashrc` (ou `~/.zshrc` si vous utilisez Zsh) :
    ```bash
    export PATH=/usr/local/cuda-11.8/bin${PATH:+:${PATH}}
    export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
    ```
    Puis, rechargez votre shell :
    ```bash
    source ~/.bashrc
    ```

7. **Vérifiez l'installation de CUDA** en exécutant les commandes suivantes :
    ```bash
    nvcc --version
    ```

Ces étapes devraient vous permettre d'installer CUDA 11.8 sur votre système en utilisant le package `.deb`. Si vous avez besoin d'une version différente du package ou d'une distribution différente, assurez-vous de remplacer les parties correspondantes de la commande `wget`.