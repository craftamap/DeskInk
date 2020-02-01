#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests
import logging
from lib import epd4in2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from pyowm import OWM
import requests

owm = OWM("cfdfad28a35e2cb1f5aa5aa4f90cb211")

def getAirhorn():
    try:
        data9450 = requests.get("https://data.sensor.community/airrohr/v1/sensor/9450/")
        data9449 = requests.get("https://data.sensor.community/airrohr/v1/sensor/9449/")
        data9450json = data9450.json()
        data9449json = data9449.json()

        temperature = data9450json[0]["sensordatavalues"][0]["value"]
        hum = data9450json[0]["sensordatavalues"][1]["value"]
        p1 = data9449json[0]["sensordatavalues"][0]["value"]
        p2 = data9449json[0]["sensordatavalues"][1]["value"]
        return {
            "temp": temperature,
            "hum": hum,
            "p1": p1,
            "p2": p2
                }
    except:
        return {
            "temp": "",
            "hum": "",
            "p1": "",
            "p2": ""
            }

def getWeatherIcon():
    obs = owm.weather_at_place("Augsburg,Germany")
    w = obs.get_weather()
    return (w.get_weather_icon_name(), w.get_temperature('celsius'))


try:
    epd = epd4in2.EPD()
    epd.init()
    while True:
        ah = getAirhorn()
        weather = getWeatherIcon()
        tempminmax = weather[1]
        icon_name = weather[0]
        
        # epd.Clear()
        
        font24 = ImageFont.truetype('Font.ttc', 24)
        font18 = ImageFont.truetype('Font.ttc', 18)
        font35 = ImageFont.truetype('Font.ttc', 35)
       
        icon = Image.open("icons/{}.jpg".format(icon_name))

        logging.info("1.Drawing on the Horizontal image...")
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        Himage.paste(icon, (50,10))
        draw = ImageDraw.Draw(Himage)
        temp_text = "{} °C".format(ah["temp"])
        temp_size = draw.textsize(temp_text, font35)
        draw.text((100 - temp_size[0]/2 , 120), temp_text, font = font35, fill = 0)
        tmm_text = "{} - {} °C".format(tempminmax["temp_min"], tempminmax["temp_max"])
        tmm_size = draw.textsize(tmm_text, font18)
        draw.text((100- tmm_size[0]/2, 160), tmm_text, font = font18, fill = 0)
        p_text = "{} und {} µg/m³".format(ah["p1"], ah["p2"])
        p_size = draw.textsize(p_text, font18)
        draw.text((100 - p_size[0]/2, 185), p_text, font = font18, fill = 0)

        epd.display(epd.getbuffer(Himage))

        time.sleep(600)
        
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd4in2.epdconfig.module_exit()
    exit()
