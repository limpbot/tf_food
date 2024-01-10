import subprocess
from pathlib import Path

lmb_username="sommerl" # "lmbserverstats" "sommerl"
url_git_repo='git@github.com:limpbot/tf_food.git'
path_git_repo = "/home/" + lmb_username +"/tools-and-services/tf_food"
path_cuda = "/misc/software/cuda/cuda-11.7"
path_home = "/home/" + lmb_username
path_logs = "/home/" + lmb_username

class ConfigPlatform():
    link = "torque"
    path_git_repo = path_git_repo
    pull_git_repo = True
    pull_git_repo_submodules = True
    install_git_repo = True
    path_cuda = path_cuda
    path_home = path_home
    url_git_repo = url_git_repo
    username = lmb_username
    gpu_count = 1
    cpu_count = 8
    ram = "40gb"
    walltime = "24:00:00"

class ConfigPlatformLocal():
    link = "local"
    path_home = path_home
    path_logs = path_logs
    path_git_repo = path_git_repo
    path_cuda = path_cuda
    url_git_repo = url_git_repo

class Config:
    run_name = "lunch"
    branch = "main"
    platform_local = ConfigPlatformLocal()
    platform = ConfigPlatform()

def bench_single_method_torque():
    # 1. save config
    # 2. setup git_repo on torque
    # 3. execute script with command: run git_repo bench single -f `path-to-config`
    # TODO
    cfg = Config()

    job_name = cfg.run_name

    local_tmp_script_fpath = Path(cfg.platform_local.path_home).joinpath('tmp', f'run_{job_name}.sh') # .resolve()
    if not local_tmp_script_fpath.parent.exists():
        local_tmp_script_fpath.parent.mkdir(parents=True)

    remote_tmp_script_fpath = Path(cfg.platform.path_home).joinpath('tmp', f'run_{job_name}.sh')

    with open(local_tmp_script_fpath, 'w') as rsh:

        gpu_count = cfg.platform.gpu_count
        node_count = 1
        cpu_count = cfg.platform.cpu_count
        ram = cfg.platform.ram
        walltime = cfg.platform.walltime

        gpu_cfg_str = f':gpus={gpu_count}' if gpu_count > 0 else ""
        cuda_cfg_str = f':nvidiaMinCC86' if gpu_count > 0 else "" # nvidiaMinCC75

        if cfg.platform.pull_git_repo:
            pull_git_repo_cmds_str = f'''
git fetch 
git checkout {cfg.branch}
git pull
            '''
        else:
            pull_git_repo_cmds_str = ''

        if cfg.platform.pull_git_repo_submodules:
            pull_git_repo_submodules_cmds_str = f'''
git submodule init
git submodule update
git submodule foreach 'git fetch origin; git checkout $(git rev-parse --abbrev-ref HEAD); git reset --hard origin/$(git rev-parse --abbrev-ref HEAD); git submodule update --recursive; git clean -dfx'
            '''
        else:
            pull_git_repo_submodules_cmds_str = ''

        if cfg.platform.install_git_repo:
            install_git_repo_cmds_str = f'''
pip install pip --upgrade
pip install -r {cfg.platform.path_git_repo}/requirements.txt
            '''
        else:
            install_git_repo_cmds_str = ''

        script_as_string = f'''#!/bin/bash
#PBS -N {job_name}
#PBS -S /bin/bash
#PBS -l nodes={node_count}:ppn={cpu_count}{gpu_cfg_str}{cuda_cfg_str},mem={ram},walltime={walltime}
#PBS -q default-cpu
#PBS -m a
#PBS -M {cfg.platform.username}@informatik.uni-freiburg.de
#PBS -j oe

# For interactive jobs: #PBS -I
# For array jobs: #PBS -t START-END[%SIMULTANEOUS]

echo $(curl google.com)

CUDA_HOME={cfg.platform.path_cuda}
PATH=${{CUDA_HOME}}/bin:${{PATH}}
LD_LIBRARY_PATH=${{CUDA_HOME}}/lib64:${{LD_LIBRARY_PATH}}
export PATH
export LD_LIBRARY_PATH
export CUDA_HOME

echo PATH=${{PATH}}
echo LD_LIBRARY_PATH=${{LD_LIBRARY_PATH}}
echo CUDA_HOME=${{CUDA_HOME}}

# Setup Repository
if [[ -d "{cfg.platform.path_git_repo}" ]]; then
    echo "OD3D is already cloned to {cfg.platform.path_git_repo}."
else
    git clone {cfg.platform.url_git_repo} {cfg.platform.path_git_repo}
fi

while [[ -e "{cfg.platform.path_git_repo}/installing.txt" ]]; do
    sleep 3  
    echo "waiting for installing.txt file to disappear."
done

touch "{cfg.platform.path_git_repo}/installing.txt"

cd {cfg.platform.path_git_repo}

{pull_git_repo_cmds_str}
{pull_git_repo_submodules_cmds_str}

# Install OD3D in venv
VENV_NAME=venv310
export VENV_NAME
if [[ -d "${{VENV_NAME}}" ]]; then
    echo "Venv already exists at {cfg.platform.path_git_repo}/${{VENV_NAME}}."
    source {cfg.platform.path_git_repo}/${{VENV_NAME}}/bin/activate
else
    echo "Creating venv at {cfg.platform.path_git_repo}/${{VENV_NAME}}."
    python3 -m venv {cfg.platform.path_git_repo}/${{VENV_NAME}}
    source {cfg.platform.path_git_repo}/${{VENV_NAME}}/bin/activate
fi

{install_git_repo_cmds_str}

rm "{cfg.platform.path_git_repo}/installing.txt"

python pull.py

#PYTHONUNBUFFERED=1 
#CUDA_VISIBLE_DEVICES=1

exit 0
        '''
        rsh.write(script_as_string)
    #subprocess.run(f'scp {tmp_script_fpath} torque:{tmp_script_fpath}', capture_output=True, shell=True)
    #subprocess.run(f'scp {tmp_config_fpath} torque:{tmp_config_fpath}', capture_output=True, shell=True)
    subprocess.run(f'ssh torque "cd torque_jobs && qsub {remote_tmp_script_fpath}"', capture_output=True, shell=True)

def main():
    bench_single_method_torque()

if __name__ == "__main__":
    main()
