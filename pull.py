import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# pip install requests
# pip install bs4
# pip install pyowm
# pip install deep-translator
import requests
from bs4 import BeautifulSoup
import datetime
import re
import sys
from pathlib import Path

ONLY_COPY_HTML = False
CREATE_IMAGES = True

if len(sys.argv) > 1:
    PATH_HTML = sys.argv[1]
else:
    PATH_HTML = '/home/lmbserverstats/tools-and-services/tf_food/html/'

def get_todays_date():
    now = datetime.datetime.now()
    timestamp = now.strftime("%d.%m.") # _%H-%M-%S
    return timestamp



german_weekdays_offsets ={
    'Montag': 0,
    'Dienstag': 1,
    'Mittwoch': 2,
    'Donnerstag': 3,
    'Freitag': 4,
    'Samstag': 5,
    'Sonntag': 6,
}

german_month_names = {
    'Januar': 1,
    'Februar': 2,
    'März': 3,
    'April': 4,
    'Mai': 5,
    'Juni': 6,
    'Juli': 7,
    'August': 8,
    'September': 9,
    'Oktober': 10,
    'November': 11,
    'Dezember': 12
}

def get_todays_year():
    # Get today's date
    today = datetime.datetime.now()
    return today.year

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
dict_mensa_date = {}


url = 'https://www.swfr.de/essen/mensen-cafes-speiseplaene/freiburg/mensa-flugplatz'
response = requests.get(url)
html_content = response.content

soup = BeautifulSoup(html_content, 'html.parser')

menu_elements = soup.select('.menu-tagesplan')

swfr_flugplatz_essen = []
swfr_flugplatz_date = []

try:
    for element in menu_elements:
        essen_weekday = element.find('h3').get_text()
        if todays_weekday not in essen_weekday:
            continue
        extra_text_elements = element.select('small.extra-text')

        for element_essen in extra_text_elements:
            try:
                essen = element_essen.get_text(separator=', ')
                swfr_flugplatz_essen.append(essen)
                date = essen_weekday.split(' ')[-1]
                swfr_flugplatz_date.append(date)
            except Exception as e:
                logger.info('Exception for SWFR Flugplatz')
                logger.info(e)
except Exception as e:
    logger.info('Exception for SWFR Flugplatz')
    logger.info(e)


if len(swfr_flugplatz_essen) > 0:
    dict_mensa_essen['SWFR Flugplatz'] = swfr_flugplatz_essen
    dict_mensa_date['SWFR Flugplatz'] = swfr_flugplatz_date
else:
    dict_mensa_essen['SWFR Flugplatz'] = ['Leerer Teller.']
    dict_mensa_date['SWFR Flugplatz'] = [get_todays_date()]

url = 'https://www.ipm.fraunhofer.de/de/ueber-fraunhofer-ipm/fraunhofer-ipm-kantine.html'
response = requests.get(url)
html_content = response.content

soup = BeautifulSoup(html_content, 'html.parser')
tab_par_element = soup.select('.tabPar')[0] #.first()
rows = tab_par_element.find_all('tr')


fraunhofer_ipm_essen = []
fraunhofer_ipm_date = []

try:
    week_monday_day_in_month, _, week_monday_month = re.match(r'([0-9]+)\.([^A-Z]+)([\w]+).*', tab_par_element.find_all('h4')[0].get_text()).groups() #  + ' Dezember '
    for german_month in german_month_names.keys():
        if german_month.startswith(week_monday_month):
            week_monday_month = german_month
            break
    week_monday_month = german_month_names[week_monday_month]


    for row in rows:
        essens_infos = row.find_all('td')

        try:
            weekday = essens_infos[0].get_text()
            if todays_weekday not in weekday:
                continue

            for essen_info in essens_infos[1].find_all('li'):
                date = datetime.datetime(year=int(get_todays_year()), month=week_monday_month, day=int(week_monday_day_in_month)) + datetime.timedelta(days=german_weekdays_offsets[weekday.split(' ')[0]])
                date = date.strftime("%d.%m.")
                fraunhofer_ipm_date.append(date)
                essen = essen_info.get_text().replace('\xa0', '')
                essen = re.sub(r'\[.*?\]', '', essen)
                fraunhofer_ipm_essen.append(essen)
        except Exception as e:
            logger.info('Exception for Frauhofer IPM.')
            logger.info(e)
except Exception as e:
    logger.info('Exception for Frauhofer IPM.')
    logger.info(e)
if len(fraunhofer_ipm_essen) > 0:
    dict_mensa_essen['Fraunhofer IPM'] = fraunhofer_ipm_essen
    dict_mensa_date['Fraunhofer IPM'] = fraunhofer_ipm_date
else:
    dict_mensa_essen['Fraunhofer IPM'] = ['Leerer Teller.']
    dict_mensa_date['Fraunhofer IPM'] = [get_todays_date()]


url = 'https://www.swfr.de/essen/mensen-cafes-speiseplaene/freiburg/mensa-institutsviertel'
response = requests.get(url)
html_content = response.content

soup = BeautifulSoup(html_content, 'html.parser')

menu_elements = soup.select('.menu-tagesplan')

swfr_insti_essen = []
swfr_insti_date = []

try:
    for element in menu_elements:
        essen_weekday = element.find('h3').get_text()
        if todays_weekday not in essen_weekday:
            continue
        extra_text_elements = element.select('small.extra-text')
        abendessen_elements = [True if 'Abendessen' in element_title.get_text() else False for element_title in element.select('h5')]
        extra_text_elements = [element for i, element in enumerate(extra_text_elements) if abendessen_elements[i]]
        for element_essen in extra_text_elements:
            try:
                essen = element_essen.get_text(separator=', ')
                swfr_insti_essen.append(essen)
                date = essen_weekday.split(' ')[-1]
                swfr_insti_date.append(date)
            except Exception as e:
                logger.info('Exception for SWFR Institutsviertel Abendessen')
                logger.info(e)
except Exception as e:
    logger.info('Exception for SWFR Institutsviertel Abendessen')
    logger.info(e)


if len(swfr_insti_essen) > 0:
    dict_mensa_essen['SWFR Institutsviertel Abendessen'] = swfr_insti_essen
    dict_mensa_date['SWFR Institutsviertel Abendessen'] = swfr_insti_date
else:
    dict_mensa_essen['SWFR Institutsviertel Abendessen'] = ['Leerer Teller.']
    dict_mensa_date['SWFR Institutsviertel Abendessen'] = [get_todays_date()]


# pip install torch
# pip install --upgrade diffusers transformers accelerate

# <meta http-equiv="Content-Security-Policy" content="style-src 'self' 'https://windy.com;'" />
# <script src="leaflet.js"></script>
# <script src="libBoot.js"></script>
# <script src="script.js"></script>
#     <meta HTTP-EQUIV="Content-Security-Policy" content="default-src 'self' https://*; style-src 'self' https://*; frame-src 'self' https://*;" />
#     <meta HTTP-EQUIV="Content-Security-Policy" content="default-src *; style-src *; frame-src *; script-src *;" />
#     <meta HTTP-EQUIV="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval' *; style-src 'self' 'unsafe-inline' 'unsafe-eval' *; frame-src 'self' 'unsafe-inline' 'unsafe-eval' *; script-src 'self' 'unsafe-inline' 'unsafe-eval' *;" />

html_weather_req = requests.get(url="https://embed.windy.com/embed2.html?lat=48.000&lon=7.850&zoom=12&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=km%2Fh&metricTemp=%C2%B0C&radarRange=-1")
html_weather= html_weather_req.content
with open('weather.html', 'wb') as f:
    f.write(html_weather)


html_text = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Today's Mensa Options</title>
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0, shrink-to-fit=no"
    />

    <meta http-equiv="refresh" CONTENT="30"> <! -- This is to force refresh of this page every 30 seconds>
    
    <style>
        /* Apply CSS to style the <li> elements */
        
        body {{
            color: white; /* Text color */
            background-image: url('./{todays_date}_weather.jpg');
            background-size: cover; /* Optional - scales the image to cover the entire background */
            /* Other background properties like background-position, background-repeat, etc., can also be used */
        }}
        
        ul.grid-list {{
            list-style: none;
            padding: 0;
            margin: 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 0.5fr));
            gap: 10px;
            text-align: center;
            width: 100%;
        }}

        ul.grid-list li {{
            border: 1px solid #ccc;
            padding: 10px;
            text-align: center;
            width: 0.25fr;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* Shadow to improve readability */
            background-color: rgba(0, 0, 0, 0.5); /* Background color with transparency */
        }}
        .fancy-title {{
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* Shadow to improve readability */
            font-size: 36px;
            text-align: center;
            margin-top: 50px;
            background-color: rgba(0, 0, 0, 0.5); /* Background color with transparency */
          }}
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
        date = dict_mensa_date[mensa][i]
        html_text += f"""
        <li>
            {essen} ({date}) <br>
            <img width="40%" src="./{todays_date}_{mensa}_{i}.jpg" alt="Local Image">
            <br>
        </li>
        """
    html_text += f"""
            </ul>
            """
html_text += f"""
    </div>
    
    
    
    </body>
</html>
        """

# <img width="100%" src="./{todays_date}_weather.jpg" alt="Local Image">


#     <embed type="text/html">{html_weather}</embed>
#     <div>
#       <iframe
#         title="Weather Radar Map"
#         src="https://embed.windy.com/embed2.html?lat=48.000&lon=7.850&zoom=12&level=surface&overlay=rain&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=km%2Fh&metricTemp=%C2%B0C&radarRange=-1"
#         width="100%"
#         height="450px"
#       ></iframe>
#     </div>

# <div id="windy"></div>

# Convert special characters to HTML entities
html_encoded = html_text.replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml;").replace("ä", "&auml;")\
    .replace("ö", "&ouml;").replace("ü", "&uuml;").replace("ß", "&szlig;").replace("»", "&raquo;").replace("«", "&laquo;")

file_path = "index.html"  # Specify the file path

# Open the file in write mode and write the HTML content
with open(file_path, 'w') as file:
    file.write(html_encoded)


from diffusers import StableDiffusionPipeline
import torch

def get_weather_desc():
    import pyowm
    # Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key
    owm = pyowm.OWM('2f1ef2b45af97ec27f84797fc2581724')
    # Set the desired location using coordinates
    lat = 48.000
    lon = 7.850
    mgr = owm.weather_manager()
    # Get the current weather at the specified location
    weather = mgr.weather_at_coords(lat, lon).weather
    # Get the detailed weather status as a string
    detailed_status = weather.detailed_status
    print("Detailed weather status:", detailed_status)
    forecaster = mgr.forecast_at_coords(lat, lon, '3h')
    from pyowm.utils import timestamps
    from datetime import datetime
    datetime.today()
    time_lunch = timestamps.now() + timestamps.timedelta(hours=5) # 7 + 5 = 12
    detailed_status = forecaster.get_weather_at(time_lunch).detailed_status
    print("Detailed weather forecast:", detailed_status)
    return detailed_status

if CREATE_IMAGES:
    from deep_translator import GoogleTranslator
    # Use any translator you like, in this example GoogleTranslator
    translator = GoogleTranslator(source='de', target='en')

    model_id = "dreamlike-art/dreamlike-photoreal-2.0"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")

    for mensa in dict_mensa_essen.keys():
        for i, essen in enumerate(dict_mensa_essen[mensa]):
            prompt = "photo, a church in the middle of a field of crops, bright cinematic lighting, gopro, fisheye lens"
            logger.info(essen)
            essen_en = translator.translate(essen)
            logger.info(essen_en)
            image = pipe(essen_en).images[0]
            image.save(f"./{todays_date}_{mensa}_{i}.jpg")

    weather_desc = get_weather_desc()
    image = pipe(f'{weather_desc} weather').images[0]
    image.save(f"./{todays_date}_weather.jpg")


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

if not Path(PATH_HTML).exists():
    Path(PATH_HTML).mkdir(parents=True)

run_cmd(f'cp ./index.html {PATH_HTML}', live=True, logger=logger)
run_cmd(f'cp ./*.js {PATH_HTML}', live=True, logger=logger)


if not ONLY_COPY_HTML:

    run_cmd(f'rm {PATH_HTML}*.jpg', live=True, logger=logger)
    for mensa in dict_mensa_essen.keys():
        for i, essen in enumerate(dict_mensa_essen[mensa]):
            run_cmd(f'cp "./{todays_date}_{mensa}_{i}.jpg" {PATH_HTML}', live=True, logger=logger)
    run_cmd(f'cp "./{todays_date}_weather.jpg" {PATH_HTML}', live=True, logger=logger)

    run_cmd(f'rm *.jpg', live=True, logger=logger)
    run_cmd(f'rm index.html', live=True, logger=logger)
