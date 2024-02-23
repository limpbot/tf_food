# 
# https://download.pytorch.org/whl/cu111/torch_stable.html
# 
cd /home/sommerl/PycharmProjects/lmb-rpi && source venv/bin/activate && python pull.py

crontab -e

59 6 * * * "$(command -v bash)" -c 'cd /scratch/sommerl/repos/tf_food2 && source venv/bin/activate && python pull.py /misc/lmbweb/essen/'
