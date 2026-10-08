#!/bin/bash
#SBATCH -J 09-17_08-50-13_ImageNet3D_TrinityDDP_ckpt_litept_g0005_imgnet3d_handal_omni6dpose_sope_full_g4xbs1x128_distr_equal_e100_slurm
#SBATCH --nodes 1
#SBATCH --ntasks-per-node 1
#SBATCH --time 24:00:00
#SBATCH --gres gpu:4 # this is gpu per node
#SBATCH --cpus-per-task 64 # 
#SBATCH --mem 512gb # memory per cpu (--mem-per-cpu)
#SBATCH --open-mode=append # append|truncate
#SBATCH -o /ihome/sommerl/slurm_jobs/%x_%j.o # x=job_name j=job_id
#SBATCH --mail-type=FAIL  # END,FAIL,ALL # (recive mails about end and timeouts/crashes of your job)
#SBATCH --signal=B:SIGUSR1@60
#SBATCH --requeue

#SBATCH --partition lmbdlc2_gpu-l40s
#SBATCH --exclude dlc2gpu10,dlc2gpu07


NODE_COUNT=1

# if [ -n $NODE_COUNT ] && [ "$NODE_COUNT" -gt 1 ]; then

WORLD_SIZE=4
# Identify master node (rank 0)
MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)

# --- find a free port (pure bash, no Python) ---
find_free_port() {
    while :; do
        # Pick a random high port (20000–40000)
        port=$(( ( RANDOM % 20000 ) + 20000 ))

        # Check if the port is free
        if ! (echo >/dev/tcp/127.0.0.1/$port) 2>/dev/null; then
            echo "$port"
            return 0
        fi
    done
}
MASTER_PORT=$(find_free_port)

echo "found free port $MASTER_PORT"

export MASTER_ADDR MASTER_PORT

# old configs:
# xBATCH --cpus-per-task 64
# xBATCH --gres gpu:4 # GPU per node
# xBATCH --mem 8gb
# xBATCH --gres gpu:4 

CUDA_HOME=/usr/local/cuda-13.3
CUDA_VERSION=$(basename "${CUDA_HOME}")
# PATH=${CUDA_HOME}/bin:${PATH}
# LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
# export PATH
# export LD_LIBRARY_PATH
export CUDA_HOME
export CUDACXX=${CUDA_HOME}/bin/nvcc # nvcc requires this (poinnet install)
export PATH=${CUDA_HOME}/bin:${PATH} # nvcc requires this (poinnet install)
export LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH} # nvcc requires this (poinnet install)
export CPATH=$CPATH:${CUDA_HOME}/targets/x86_64-linux/include # pycuda requires this
export LIBRARY_PATH=$LIBRARY_PATH:${CUDA_HOME}/targets/x86_64-linux/lib # pycuda requires this

export NCCL_P2P_DISABLE=1 # failed dlc2gpu12, dlc2gpu17
export NCCL_SHM_DISABLE=1


# for onnx (e.g. orientanything)






# huggingface cache
export HF_HOME=/work/dlclarge1/sommerl-od3d/hf_cache
mkdir -p ${HF_HOME}
echo HF_HOME=${HF_HOME}
            

# echo PATH=${PATH}
# echo LD_LIBRARY_PATH=${LD_LIBRARY_PATH}
echo CUDA_HOME=${CUDA_HOME}

# while [[ -e "/work/dlclarge1/sommerl-od3d/od3d/installing.txt" ]]; do
#     sleep 3
#     echo "waiting for installing.txt file to disappear."
# done
# touch "/work/dlclarge1/sommerl-od3d/od3d/installing.txt"

# Setup Repository
if [[ -d "/work/dlclarge1/sommerl-od3d/od3d/.git" ]]; then
    echo "OD3D is already cloned to /work/dlclarge1/sommerl-od3d/od3d."
else
    if [[ -d "/work/dlclarge1/sommerl-od3d/od3d" ]]; then
        echo "removing previous incomplete OD3D..."
        rm -rf /work/dlclarge1/sommerl-od3d/od3d
    fi
    echo "cloning OD3D..."
    git clone https://${GITHUB_TOKEN}@github.com/GenIntel/od3d.git /work/dlclarge1/sommerl-od3d/od3d
fi

echo "Getting the lock."
PATH_LOCK="/work/dlclarge1/sommerl-od3d/od3d/installing.txt"
exec 200>${PATH_LOCK}
flock 200
echo "Got the lock."

cd /work/dlclarge1/sommerl-od3d/od3d


# actually not automatic set this proxy.
HTTP_PROXY=http://tfproxy.informatik.intra.uni-freiburg.de:8080
HTTPS_PROXY=http://tfproxy.informatik.intra.uni-freiburg.de:8080
http_proxy=http://tfproxy.informatik.intra.uni-freiburg.de:8080
https_proxy=http://tfproxy.informatik.intra.uni-freiburg.de:8080
export HTTP_PROXY
export HTTPS_PROXY
export http_proxy
export https_proxy
# HTTP_PROXY=http://tfsquid.informatik.intra.uni-freiburg.de:8080
# HTTPS_PROXY=http://tfsquid.informatik.intra.uni-freiburg.de:8080
# export HTTP_PROXY
# export HTTPS_PROXY
        


# keep origin in sync with the configured url, otherwise an already cloned
# repository keeps using the (possibly outdated) credentials of its clone time
git remote set-url origin https://${GITHUB_TOKEN}@github.com/GenIntel/od3d.git
git fetch
git checkout main
git pull
            

git submodule init
git submodule update --recursive
# git submodule foreach 'git fetch origin; git checkout $(git rev-parse --abbrev-ref HEAD); git reset --hard origin/$(git rev-parse --abbrev-ref HEAD); git submodule update --recursive; git clean -dfx'
            

export MP_START_METHOD=fork
export MP_SHARING_STRATEGY=file_system


eval "$(/work/dlclarge1/sommerl-od3d/miniconda3/bin/conda shell.bash hook)"

if ! conda env list | grep -q "^py310-cuda124 "; then
    echo "Creating conda env py310-cuda124."
    conda create -n py310-cuda124 python=3.1 -y
    conda activate py310-cuda124
    # hash -r # clear cached PATH lookups (e.g. a ~/.local/bin/pip shadowing the conda env's python)
    conda install -c nvidia cuda-version=12.4 -y
    conda install -c nvidia cuda-toolkit=12.4 -y
    conda install -c nvidia cusparselt -y
    conda install -c nvidia nccl -y
    conda install -c nvidia cuda-cupti -y
else
    echo "Activating conda env py310-cuda124."
    conda activate py310-cuda124
    # hash -r # clear cached PATH lookups (e.g. a ~/.local/bin/pip shadowing the conda env's python)
fi

CUDA_HOME=${CONDA_PREFIX}
export CUDA_HOME
export CUDACXX=${CUDA_HOME}/bin/nvcc # nvcc requires this (pointnet install)
export PATH=$CUDA_HOME/bin:$PATH # nvcc requires this (pointnet install)
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH # nvcc requires this (pointnet install)
export CPATH=$CPATH:${CUDA_HOME}/targets/x86_64-linux/include # pycuda requires this
export LIBRARY_PATH=$LIBRARY_PATH:${CUDA_HOME}/targets/x86_64-linux/lib # pycuda requires this
export LD_LIBRARY_PATH=${CONDA_PREFIX}/lib:$LD_LIBRARY_PATH

export CUDA_HOME=$CONDA_PREFIX

echo "activated conda env."
            



# rm "${PATH_LOCK}"
exec 200>&- # free lock

echo "test od3d cmd..."

od3d debug hello-world

echo "tested od3d cmd."

trap "scontrol requeue ${SLURM_JOB_ID}" SIGUSR1

echo "perhaps cleanup..."
find /dev/shm -user "$USER" -name "torch_*" -delete
echo "perhaps cleanup done."

echo "running command: torchrun --nproc_per_node=4 --master_port=$MASTER_PORT ./src/od3d/cli/_entry.py bench single-local -c /ihome/sommerl/tmp/config_09-17_08-50-13_ImageNet3D_TrinityDDP_ckpt_litept_g0005_imgnet3d_handal_omni6dpose_sope_full_g4xbs1x128_distr_equal_e100_slurm.yaml &"
torchrun --nproc_per_node=4 --master_port=$MASTER_PORT ./src/od3d/cli/_entry.py bench single-local -c /ihome/sommerl/tmp/config_09-17_08-50-13_ImageNet3D_TrinityDDP_ckpt_litept_g0005_imgnet3d_handal_omni6dpose_sope_full_g4xbs1x128_distr_equal_e100_slurm.yaml &

PID=$!
wait "${PID}"

EXITCODE="$?"
export EXITCODE

echo "${EXITCODE}"


if [[ "${EXITCODE}" -eq "1" ]]; then
    echo "requeuing due to exit code equals 1..."
    scontrol requeue ${SLURM_JOB_ID}
fi
            

exit 0
        