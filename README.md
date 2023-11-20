# 
# https://download.pytorch.org/whl/cu111/torch_stable.html
# 
cd /home/sommerl/PycharmProjects/lmb-rpi && source venv/bin/activate && python pull.py

crontab -e
59 6 * * * "$(command -v bash)" -c 'cd /home/sommerl/PycharmProjects/lmb-rpi && source venv/bin/activate && python pull.py' 