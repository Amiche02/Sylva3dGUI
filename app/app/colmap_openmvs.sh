#!/bin/sh
# Based on https://github.com/cdcseacave/openMVS/issues/692

DATASET_PATH0=$1
DATANAME=$2
USE_GPU=$3
DATASET_PATH=$DATASET_PATH0/$DATANAME
PROJECT=${DATASET_PATH0}/result
STATE_FILE=${PROJECT}/pipeline_state.json

OPENMVS_PATH="/usr/local/bin/OpenMVS"

# Increase swap space if not already set
if [ ! -f /swapfile ]; then
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Create necessary directories
mkdir -p ${PROJECT}/images
mkdir -p ${PROJECT}/sparse

# Function to save state in JSON format
save_state() {
    local step=$1
    local substep=$2
    echo "{\"last_completed_step\": $step, \"last_completed_substep\": \"$substep\"}" > $STATE_FILE
}

# Function to load state from JSON
load_state() {
    if [ -f $STATE_FILE ]; then
        local step=$(jq -r '.last_completed_step' $STATE_FILE)
        local substep=$(jq -r '.last_completed_substep' $STATE_FILE)
        # Handle null values correctly
        if [ "$substep" = "null" ]; then
            substep=""
        fi
        echo "$step|$substep"
    else
        echo "0|none"
    fi
}

# Function to download the bin file
download_bin() {
    BIN_LINK=$1
    wget -O ${PROJECT}/$(basename ${BIN_LINK}) ${BIN_LINK}
}

# Count the number of image files
NUM_IMAGES=$(find ${PROJECT}/images -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | wc -l)

# Load the last completed step and substep
state=$(load_state)
LAST_COMPLETED_STEP=$(echo $state | cut -d'|' -f1)
LAST_COMPLETED_SUBSTEP=$(echo $state | cut -d'|' -f2)

# Step 0: Copy images to ${PROJECT}/images (optional to track this)
if [ "$LAST_COMPLETED_STEP" -lt "1" ]; then
    echo "Copying images from ${DATASET_PATH} to ${PROJECT}/images"
    cp ${DATASET_PATH}/* ${PROJECT}/images/
    save_state 1 "completed"
fi

# Feature extraction
if [ "$LAST_COMPLETED_STEP" -lt "2" ]; then
    colmap feature_extractor \
        --SiftExtraction.use_gpu 0 \
        --SiftExtraction.max_image_size 1024 \
        --database_path ${PROJECT}/database.db \
        --image_path ${PROJECT}/images
    save_state 2 "completed"
fi

# Matching
if [ "$LAST_COMPLETED_STEP" -lt "3" ]; then
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
    save_state 3 "completed"
fi

# Reconstruction
if [ "$LAST_COMPLETED_STEP" -lt "4" ]; then
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
    save_state 4 "completed"
fi

# Point triangulation
if [ "$LAST_COMPLETED_STEP" -lt "5" ]; then
    colmap point_triangulator \
       --database_path ${PROJECT}/database.db \
       --image_path ${PROJECT}/images \
       --output_path ${PROJECT}/sparse
    save_state 5 "completed"
fi

# Dense reconstruction and meshing
if [ "$LAST_COMPLETED_STEP" -lt "6" ]; then
    find ${PROJECT}/sparse/ -maxdepth 1 -mindepth 1 | while read areconstruction; do

        colmap image_undistorter \
            --image_path ${PROJECT}/images \
            --input_path ${areconstruction} \
            --output_path ${PROJECT}/dense$(basename ${areconstruction}) \
            --output_type COLMAP 
        save_state 6 "image_undistorter_completed"

        colmap model_converter \
            --input_path ${PROJECT}/dense$(basename ${areconstruction})/sparse \
            --output_path ${PROJECT}/dense$(basename ${areconstruction})/sparse  \
            --output_type TXT
        save_state 6 "model_converter_completed"

        ${OPENMVS_PATH}/InterfaceCOLMAP \
            --working-folder ${PROJECT}/ \
            -i ${PROJECT}/dense$(basename ${areconstruction}) \
            --output-file ${PROJECT}/model_colmap_$(basename ${areconstruction}).mvs
        save_state 6 "interface_colmap_completed"

        ${OPENMVS_PATH}/DensifyPointCloud \
            --input-file ${PROJECT}/model_colmap_$(basename ${areconstruction}).mvs \
            --working-folder ${PROJECT}/ \
            --output-file ${PROJECT}/model_dense_$(basename ${areconstruction}).mvs \
            --archive-type -1
        save_state 6 "densify_point_cloud_completed"

        ${OPENMVS_PATH}/ReconstructMesh --input-file ${PROJECT}/model_dense_$(basename ${areconstruction}).mvs \
            --working-folder ${PROJECT}/ \
            --output-file ${PROJECT}/model_dense_mesh_$(basename ${areconstruction}).mvs
        save_state 6 "reconstruct_mesh_completed"
        
    done
fi
