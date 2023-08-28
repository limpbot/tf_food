import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# pip install requests
# pip install bs4
import requests
from bs4 import BeautifulSoup
import datetime
import re
import html

def get_todays_weekday():

    # Get today's date
    today = datetime.datetime.now()

    # Get the weekday index (0 = Monday, 6 = Sunday)
    weekday_index = today.weekday()

    # List of weekday names
    weekday_names = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

    # Get the weekday name
    weekday_name = weekday_names[weekday_index]
    return weekday_name

todays_weekday = get_todays_weekday()
todays_date = datetime.datetime.now().strftime('%Y-%m-%d')
dict_mensa_essen = {}



url = 'https://www.swfr.de/essen/mensen-cafes-speiseplaene/freiburg/mensa-flugplatz'
response = requests.get(url)
html_content = response.content

soup = BeautifulSoup(html_content, 'html.parser')

menu_elements = soup.select('.menu-tagesplan')



swfr_flugplatz_essen = []
for element in menu_elements:
    essen_weekday = element.find('h3').get_text()
    if todays_weekday not in essen_weekday:
        continue
    extra_text_elements = element.select('small.extra-text')

    for element_essen in extra_text_elements:
        try:
            essen = element_essen.get_text(separator=', ')
            swfr_flugplatz_essen.append(essen)
        except Exception as e:
            pass

if len(swfr_flugplatz_essen) > 0:
    dict_mensa_essen['SWFR Flugplatz'] = swfr_flugplatz_essen
else:
    dict_mensa_essen['SWFR Flugplatz'] = ['Empty plate.']

url = 'https://www.ipm.fraunhofer.de/de/ueber-fraunhofer-ipm/fraunhofer-ipm-kantine.html'
response = requests.get(url)
html_content = response.content

soup = BeautifulSoup(html_content, 'html.parser')
tab_par_element = soup.select('.tabPar')[0] #.first()
rows = tab_par_element.find_all('tr')

fraunhofer_ipm_essen = []

for row in rows:
    essens_infos = row.find_all('td')

    try:
        weekday = essens_infos[0].get_text()
        if todays_weekday not in weekday:
            continue

        for essen_info in essens_infos[1].find_all('li'):
            essen = essen_info.get_text().replace('\xa0', '')
            essen = re.sub(r'\[.*?\]', '', essen)
            fraunhofer_ipm_essen.append(essen)
    except Exception as e:
        pass

if len(fraunhofer_ipm_essen) > 0:
    dict_mensa_essen['Fraunhofer IPM'] = fraunhofer_ipm_essen
else:
    dict_mensa_essen['Fraunhofer IPM'] = ['Empty plate.']

# pip install torch
# pip install --upgrade diffusers transformers accelerate


html_text = """
<!DOCTYPE html>
<html>
<head>
    <title>Today's Mensa Options</title>
    <style>
        /* Apply CSS to style the <li> elements */
        
        ul.grid-list {
            list-style: none;
            padding: 0;
            margin: 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 0.5fr));
            gap: 10px;
            text-align: center;
            width: 100%;
        }

        ul.grid-list li {
            border: 1px solid #ccc;
            padding: 10px;
            text-align: center;
            width: 0.25fr;
        }
        .fancy-title {
            
            font-size: 36px;
            color: black;
            text-align: center;
            margin-top: 50px;
          }
    </style>
</head>
<body>


<div>
"""
for mensa in dict_mensa_essen.keys():
    html_text += f"""
        <h2 class="fancy-title">{mensa}</h2>
        <ul  class="grid-list">
        """
    for i, essen in enumerate(dict_mensa_essen[mensa]):
        html_text += f"""
        <li>
            {essen} <br>
            <img width="25%" src="./{todays_date}_{mensa}_{i}.jpg" alt="Local Image">
            <br>
        </li>
        """
    html_text += f"""
            </ul>
            """
html_text += f"""
    </div>
    
    <div>
  <iframe
    title="Weather Radar Map"
    src="https://embed.windy.com/embed2.html?lat=48.000&lon=7.850&zoom=12&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=km%2Fh&metricTemp=%C2%B0C&radarRange=-1"
    width="100%"
    height="450px"
  ></iframe>
</div>
    </body>
</html>
        """

# Convert special characters to HTML entities
html_encoded = html_text.replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml;").replace("ß", "&szlig;").replace("»", "&raquo;").replace("«", "&laquo;")

file_path = "index.html"  # Specify the file path

# Open the file in write mode and write the HTML content
with open(file_path, 'w') as file:
    file.write(html_encoded)


from diffusers import StableDiffusionPipeline
import torch

model_id = "dreamlike-art/dreamlike-photoreal-2.0"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

for mensa in dict_mensa_essen.keys():
    for i, essen in enumerate(dict_mensa_essen[mensa]):
        prompt = "photo, a church in the middle of a field of crops, bright cinematic lighting, gopro, fisheye lens"
        image = pipe(essen).images[0]
        image.save(f"./{todays_date}_{mensa}_{i}.jpg")


import subprocess
def run_cmd(cmd, logger, live=False, background=False):
    if logger is not None:
        logger.info(f'Run command {cmd}')
    if live:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)

        for line in process.stdout:
            # Print or process the live output as needed
            logger.info(line)
            # print(line, end='')

        # Wait for the subprocess to complete
        process.wait()

        # Retrieve the return code of the subprocess
        return_code = process.returncode
        logger.info(f'Return Code {return_code}')

    else:
        if not background:
            res = subprocess.run(cmd, capture_output=True, shell=True)
            if logger is not None:
                logger.info(res.stdout.decode("utf-8"))
                logger.info(res.stderr.decode("utf-8"))
            return res.stdout.decode("utf-8")
        else:
            subprocess.run(cmd, capture_output=False, shell=True)

run_cmd('cp ./index.html /misc/lmbweb/htdocs/people/sommerl/essen/', live=True, logger=logger)
run_cmd(f'rm /misc/lmbweb/htdocs/people/sommerl/essen/*.jpg', live=True, logger=logger)


for mensa in dict_mensa_essen.keys():
    for i, essen in enumerate(dict_mensa_essen[mensa]):
        run_cmd(f'cp "./{todays_date}_{mensa}_{i}.jpg" /misc/lmbweb/htdocs/people/sommerl/essen/', live=True, logger=logger)

run_cmd(f'rm *.jpg', live=True, logger=logger)
run_cmd(f'rm *.html', live=True, logger=logger)

#run_cmd('scp ./index.html pi@10.126.142.128:~/html', live=True, logger=logger)
#for mensa in dict_mensa_essen.keys():
#    for i, essen in enumerate(dict_mensa_essen[mensa]):
#        run_cmd(f'scp "./{todays_date}_{mensa}_{i}.jpg" pi@10.126.142.128:~/html', live=True, logger=logger)
