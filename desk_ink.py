#!/usr/bin/env python3

import configparser
import argparse
import logging
import time

from PIL import Image, ImageDraw, ImageFont
from pyowm import OWM

import crypto_config
from airhorn import Airhorn
from lib import epd4in2


FONT24 = ImageFont.truetype('Font.ttc', 24)
FONT18 = ImageFont.truetype('Font.ttc', 18)
FONT35 = ImageFont.truetype('Font.ttc', 35)

class DeskInk:
    """Docstring for DeskInk. """

    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.epd = epd4in2.EPD()
        self.epd.init()
        self.owm = OWM(self.config["owm"]["key"])
        self.airhorn = Airhorn(self.config["airhorn"]["pid"], self.config["airhorn"]["tempid"])

    def getWeather(self):
        obs = self.owm.weather_at_place(self.config["owm"]["location"])
        w = obs.get_weather()
        return (w.get_weather_icon_name(), w.get_temperature('celsius'))

    def run(self):
        while True:
            weather = self.getWeather()
            airhorn = self.airhorn.get_data()
            image = self.draw(weather, airhorn, None)
            self.epd.display(self.epd.getbuffer(image))
            time.sleep(600)

    def draw(self, weather, airhorn, mail):
        icon_name = weather[0]
        icon = Image.open("icons/{}.jpg".format(icon_name))

        tempminmax = weather[1]


        Himage = Image.new('1', (self.epd.width, self.epd.height), 255)

        Himage.paste(icon, (50, 10))

        draw = ImageDraw.Draw(Himage)

        temp_text = "{} °C".format(airhorn["temperature"])
        temp_size = draw.textsize(temp_text, FONT35)
        draw.text((100 - temp_size[0]/2 , 120), temp_text, font = FONT35, fill = 0)

        tmm_text = "{} - {} °C".format(tempminmax["temp_min"], tempminmax["temp_max"])
        tmm_size = draw.textsize(tmm_text, FONT18)
        draw.text((100- tmm_size[0]/2, 160), tmm_text, font = FONT18, fill = 0)

        p_text = "{} und {} µg/m³".format(airhorn["p2.5"], airhorn["p10"])
        p_size = draw.textsize(p_text, FONT18)
        draw.text((100 - p_size[0]/2, 185), p_text, font = FONT18, fill = 0)

        return Himage
        
def start(args):
    config = crypto_config.get_config(args.key.encode(), args.config)

    desk = DeskInk(config)
    desk.run()

def main():
    parser = argparse.ArgumentParser("DeskInk")
    subparsers = parser.add_subparsers(title="commands", dest="subcommand")

    edit_parser = subparsers.add_parser("edit")
    edit_parser.add_argument("-c", "--config", default="config")
    edit_parser.add_argument("-k", "--key", required=True)

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("-c", "--config", default="config")
    start_parser.add_argument("-k", "--key", required=True)


    arguments = parser.parse_args()

    if arguments.subcommand == "edit":
        crypto_config.edit_config(arguments.key.encode(), arguments.config)
    elif arguments.subcommand == "start":
        start(arguments) 


if __name__ == "__main__":
    try:
        main()
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd4in2.epdconfig.module_exit()
        exit()
