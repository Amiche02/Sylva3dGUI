#!/bin/sh
# Based on https://github.com/cdcseacave/openMVS/issues/692

PROJECT=$1
USE_GPU=$2

# Set CUDA device based on the second argument
if [ "$USE_GPU" = "None_gpu" ]; then
    CUDA_DEVICE=-2
else
    CUDA_DEVICE=-1
fi

# Increase swap space if not already set
if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Create necessary directories
mkdir -p ${PROJECT}/sparse

# Function to download the bin file
download_bin() {
    BIN_LINK=$1
    wget -O ${PROJECT}/$(basename ${BIN_LINK}) ${BIN_LINK}
}
 
# Count the number of image files
NUM_IMAGES=$(find ${PROJECT}/images -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | wc -l)

# Feature extraction
colmap feature_extractor \
    --SiftExtraction.use_gpu 0 \
    --SiftExtraction.max_image_size 1024 \
    --database_path ${PROJECT}/database.db \
    --image_path ${PROJECT}/images

# Choose matcher based on the number of images
if [ "$NUM_IMAGES" -le 1000 ]; then
    echo "Using exhaustive matcher for $NUM_IMAGES images"
    colmap exhaustive_matcher \
        --SiftMatching.use_gpu 0 \
        --database_path ${PROJECT}/database.db
elif [ "$NUM_IMAGES" -le 10000 ]; then
    BIN_LINK=https://demuc.de/colmap/vocab_tree_flickr100K_words256K.bin
    download_bin $BIN_LINK
    echo "Using vocab tree matcher (256K words) for $NUM_IMAGES images"
    colmap vocab_tree_matcher \
        --SiftMatching.use_gpu 0 \
        --database_path ${PROJECT}/database.db \
        --VocabTreeMatching.vocab_tree_path ${PROJECT}/vocab_tree_flickr100K_words256K.bin
elif [ "$NUM_IMAGES" -le 100000 ]; then
    BIN_LINK=https://demuc.de/colmap/vocab_tree_flickr100K_words1M.bin
    download_bin $BIN_LINK
    echo "Using vocab tree matcher (1M words) for $NUM_IMAGES images"
    colmap vocab_tree_matcher \
        --SiftMatching.use_gpu 0 \
        --database_path ${PROJECT}/database.db \
        --VocabTreeMatching.vocab_tree_path ${PROJECT}/vocab_tree_flickr100K_words1M.bin
else
    echo "Too many images: $NUM_IMAGES. Please adjust the script for handling very large datasets."
    exit 1
fi

# Reconstruction
if [ "$NUM_IMAGES" -le 1000 ]; then
    colmap mapper \
        --database_path ${PROJECT}/database.db \
        --image_path ${PROJECT}/images \
        --output_path ${PROJECT}/sparse
else
    colmap hierarchical_mapper \
        --database_path ${PROJECT}/database.db \
        --image_path ${PROJECT}/images \
        --output_path ${PROJECT}/sparse
fi

# Point triangulation
colmap point_triangulator \
   --database_path ${PROJECT}/database.db \
   --image_path ${PROJECT}/images \
   --output_path ${PROJECT}/sparse

# Dense reconstruction and meshing
find ${PROJECT}/sparse/ -maxdepth 1 -mindepth 1 | while read areconstruction; do

    colmap image_undistorter \
        --image_path ${PROJECT}/images \
        --input_path ${areconstruction} \
        --output_path ${PROJECT}/dense$(basename ${areconstruction}) \
        --output_type COLMAP 

    colmap model_converter \
        --input_path ${PROJECT}/dense$(basename ${areconstruction})/sparse \
        --output_path ${PROJECT}/dense$(basename ${areconstruction})/sparse  \
        --output_type TXT

    InterfaceCOLMAP \
        --working-folder ${PROJECT}/ \
        -i ${PROJECT}/dense$(basename ${areconstruction}) \
        --output-file ${PROJECT}/model_colmap_$(basename ${areconstruction}).mvs

    DensifyPointCloud \
        --input-file ${PROJECT}/model_colmap_$(basename ${areconstruction}).mvs \
        --working-folder ${PROJECT}/ \
        --output-file ${PROJECT}/model_dense_$(basename ${areconstruction}).mvs \
        --archive-type -1 \
        --cuda-device ${CUDA_DEVICE}

    ReconstructMesh \
        --input-file ${PROJECT}/model_dense_$(basename ${areconstruction}).mvs \
        --working-folder ${PROJECT}/ \
        --output-file ${PROJECT}/model_dense_mesh_$(basename ${areconstruction}).mvs \
        --cuda-device ${CUDA_DEVICE}

    RefineMesh \
        --resolution-level 1 \
        --input-file ${PROJECT}/model_dense_mesh_$(basename ${areconstruction}).mvs \
        --working-folder ${PROJECT}/ \
        --output-file ${PROJECT}/model_dense_mesh_refine_$(basename ${areconstruction}).mvs

    if ! [ -f "${PROJECT}/model_dense_mesh_refine_$(basename ${areconstruction}).mvs" ]; then
        TextureMesh \
            --export-type obj \
            --output-file ${PROJECT}/model_$(basename ${areconstruction}).obj \
            --working-folder ${PROJECT}/ \
            --input-file ${PROJECT}/model_dense_mesh_$(basename ${areconstruction}).mvs \
            --resolution-level 2 \
            --decimate 0.05 \
            --cuda-device ${CUDA_DEVICE}
    else 
        TextureMesh \
            --export-type obj \
            --output-file ${PROJECT}/model_$(basename ${areconstruction}).obj \
            --working-folder ${PROJECT}/ \
            --input-file ${PROJECT}/model_dense_mesh_refine_$(basename ${areconstruction}).mvs \
            --resolution-level 2 \
            --decimate 0.05 \
            --cuda-device ${CUDA_DEVICE}
    fi

done
