# 
# https://download.pytorch.org/whl/cu111/torch_stable.html
# 
cd /home/sommerl/PycharmProjects/lmb-rpi && source venv/bin/activate && python pull.py

crontab -e

59 6 * * * "$(command -v bash)" -c 'cd /home/sommerl/PycharmProjects/tf_food && source venv/bin/activate && python pull.py /data/lmbweb/essen/'

* * * * * "$(command -v bash)" -c 'cd /home/sommerl/PycharmProjects/tf_food && source venv/bin/activate && python pull.py /data/lmbweb/essen/'

59 6 * * * "$(command -v bash)" -c 'cd /home/sommerl/PycharmProjects/tf_food && source venv/bin/activate && python run_torque.py'
15 7 * * * "$(command -v bash)" -c 'rm -rf /misc/lmbweb/essen/*.jpg  && chmod -R go+rX /home/sommerl/tools-and-services/tf_food/html/* && cp /home/sommerl/tools-and-services/tf_food/html/* /misc/lmbweb/essen'

# raspberry settings

`sudo nano /etc/xdg/lxsession/LXDE-pi/autostart`

```
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xscreensaver -no-splash
@xset s noblank
@xset s off
@xset -dpms

/usr/bin/chromium-browser --kiosk --ignore-certificate-errors --disable-restore-session-state https://lmb.informatik.uni>

```



# bluetooth

```
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

```


Please adapt the script example_slurm.sh
a) virtual environment (probably automatic setup if not there)
b) username
c) gpus, cpus
d) output log directory
e) slurm partition
    1. lmb_gpu-rtx2080 : usually empty, only 3 slots
    2. lmbdlc_gpu-rtx2080 : often pending (but eventually it will work)
    3. alldlc_gpu-rtx3080 : usually empty (actually not anymore)
    4. alldlc_gpu-rtx2080 : biggest cluster
    5. tflmb_gpu-rtx3090: lmb gpu (debugging)
    6. tflmb_gpu-1080ti: lmb gpu (debugging)
    tflmb_gpu-rtx3090
    tflmb_gpu-1080ti
    alldlc2_gpu-l40s
    lmbdlc2_gpu-l40s