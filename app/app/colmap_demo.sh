#!/bin/bash

# Arrêter le script si une commande échoue
set -e

# Enregistrer le temps de démarrage
starttime=$(date +%Y-%m-%d\ %H:%M:%S)

# Chemins de données
DATASET_PATH0=$1
DATANAME=$2
DATASET_PATH=$DATASET_PATH0/$DATANAME
RESULT_PATH=$DATASET_PATH0/result

# Variables de chemin
IMAGE_PATH="${RESULT_PATH}/images"
OUTPUT_PATH="${RESULT_PATH}/outputs"
DATABASE_PATH="${OUTPUT_PATH}/database.db"
SPARSE_PATH="${OUTPUT_PATH}/sparse"
DENSE_PATH="${OUTPUT_PATH}/dense"
FUSED_PATH="${DENSE_PATH}/fused.ply"
MESH_PATH="${DENSE_PATH}/mesh.ply"

# Enregistrement du début du processus
echo "${DATASET_PATH##*/} 1" >> process.txt

# Vérifier si COLMAP est installé
if ! command -v colmap &> /dev/null; then
    echo "COLMAP n'est pas installé. Veuillez l'installer avant d'exécuter ce script."
    exit 1
fi

# Copier les images dans le dossier result/images
mkdir -p "$IMAGE_PATH"
cp -r "${DATASET_PATH}/images/"* "$IMAGE_PATH"

# Vérifier si le dossier des images existe
if [ ! -d "$IMAGE_PATH" ]; then
    echo "Le dossier des images n'existe pas."
    exit 1
fi

# Option pour augmenter le swap
INCREASE_SWAP=true
if [ "$3" = "--no-swap" ]; then
    INCREASE_SWAP=false
fi

# Augmenter l'espace swap si nécessaire
if $INCREASE_SWAP; then
    if [ ! -f /swapfile ]; then
        echo "Création d'un fichier swap de 4G..."
        sudo fallocate -l 4G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    else
        echo "Fichier swap déjà existant."
    fi
fi

# Libérer la mémoire système
echo "Libération de la mémoire système..."
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches

# # Libérer la mémoire GPU (NVIDIA)
# if command -v nvidia-smi &> /dev/null; then
#     echo "Libération de la mémoire GPU..."
#     sudo nvidia-smi --gpu-reset
# fi

echo "Nettoyage terminé."

# Supprimer les anciens fichiers
echo "Suppression des anciens fichiers de sortie..."
rm -f "$DATABASE_PATH"
rm -rf "$SPARSE_PATH"
rm -rf "$DENSE_PATH"

# Création des dossiers nécessaires
mkdir -p "$SPARSE_PATH"
mkdir -p "$DENSE_PATH"

# Extraction des caractéristiques
echo "Extraction des features..."
colmap feature_extractor \
    --database_path "$DATABASE_PATH" \
    --image_path "$IMAGE_PATH" \
    --SiftExtraction.max_image_size 3200

# Correspondance des caractéristiques
echo "Matching des features..."
colmap exhaustive_matcher \
    --database_path "$DATABASE_PATH"

# Reconstruction clairsemée
echo "Reconstruction sparse..."
colmap mapper \
    --database_path "$DATABASE_PATH" \
    --image_path "$IMAGE_PATH" \
    --output_path "$SPARSE_PATH"

# Correction de la distorsion des images
echo "Correction de la distorsion des images..."
colmap image_undistorter \
    --image_path "$IMAGE_PATH" \
    --input_path "$SPARSE_PATH/0" \
    --output_path "$DENSE_PATH" \
    --output_type COLMAP \
    --max_image_size 2000

# Reconstruction dense
echo "Reconstruction dense..."
colmap patch_match_stereo \
    --workspace_path "$DENSE_PATH" \
    --workspace_format COLMAP \
    --PatchMatchStereo.geom_consistency true

# Fusion du modèle dense
echo "Fusion du modèle dense..."
colmap stereo_fusion \
    --workspace_path "$DENSE_PATH" \
    --workspace_format COLMAP \
    --input_type geometric \
    --output_path "$FUSED_PATH"

# # Reconstruction de surface Poisson
# echo "Performing Poisson surface reconstruction..."
# colmap poisson_mesher \
#     --input_path "$FUSED_PATH" \
#     --output_path "$MESH_PATH" \
#     --PoissonMeshing.depth 13 \
#     --PoissonMeshing.point_weight 1 \
#     --PoissonMeshing.color 32 \
#     --PoissonMeshing.trim 10

echo "Reconstruction et filtrage terminés avec succès."

# Enregistrer le temps de fin
endtime=$(date +%Y-%m-%d\ %H:%M:%S)
echo "Start time: $starttime"
echo "End time: $endtime"
