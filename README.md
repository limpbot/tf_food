# 
# https://download.pytorch.org/whl/cu111/torch_stable.html
# 
cd /home/sommerl/PycharmProjects/lmb-rpi && source venv/bin/activate && python pull.py

crontab -e

59 6 * * * "$(command -v bash)" -c 'cd /scratch/sommerl/repos/tf_food2 && source venv/bin/activate && python pull.py /misc/lmbweb/essen/'

59 6 * * * "$(command -v bash)" -c 'cd /home/sommerl/PycharmProjects/tf_food && source venv/bin/activate && python run_torque'
09 7 * * * "$(command -v bash)" -c 'rm -rf /misc/lmbweb/essen/* && cp /home/sommerl/tools-and-services/tf_food/html/* /misc/lmbweb/essen && chmod -R go+rX /misc/lmbweb/essen/*'

# bluetooth

ssh pi@10.XXX.XXX.XXX

bluetoothctl

power on
agent on
scan on

pair 53:XX:XX:XX:XX:XX

trust 53:XX:XX:XX:XX:XX

connect 53:XX:XX:XX:XX:XX

exit


pacmd list-sinks

pacmd set-default-sink <sink_index>

vlc --intf dummy swr3-radio-100.m3u 
vlc --intf dummy file_example_MP3_700KB.mp3

