# pip install requests
# pip install bs4
# pip install torch
# pip install --upgrade diffusers transformers accelerate



cd /home/sommerl/PycharmProjects/lmb-rpi && source venv/bin/activate && python pull.py

crontab -e
59 6 * * * "$(command -v bash)" -c 'cd /home/sommerl/PycharmProjects/lmb-rpi && source venv/bin/activate && python pull.py' 