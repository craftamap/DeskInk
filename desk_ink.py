#!/usr/bin/env python3
import os
import configparser
import logging
import time
import datetime

from PIL import Image, ImageDraw, ImageFont
from pyowm import OWM

import crypto_config
from gcal_handler import GcalHandler
from mail_handler import MailHandler
from airhorn import Airhorn
from dateutil import parser

FONT24 = ImageFont.truetype('FiraSans-Regular.ttf', 24)
FONT18 = ImageFont.truetype('FiraSans-Regular.ttf', 18)
MONO18 = ImageFont.truetype('Monospace.ttf', 18)
FONT35 = ImageFont.truetype('FiraSans-Regular.ttf', 35)


class DeskInk:
    """Docstring for DeskInk. """
    def __init__(self, config: configparser.ConfigParser, epd4in2):
        self.logger = logging.getLogger("DeskInk")
        self.config = config
        self.logger.info("Init EPD...")
        self.epd = epd4in2.EPD()
        self.epd.init()
        self.gcal = GcalHandler(config)
        self.logger.info("Init OWM...")
        self.owm = OWM(self.config["owm"]["key"])
        self.logger.info("Init Airhorn...")
        self.airhorn = Airhorn(self.config["airhorn"]["pid"],
                               self.config["airhorn"]["tempid"])
        self.logger.info("Init MailHandler...")
        self.mail = MailHandler(config)


        self.logger.info("Init done!")

    def getWeather(self):
        obs = self.owm.weather_at_place(self.config["owm"]["location"])
        w = obs.get_weather()
        return (w.get_weather_icon_name(), w.get_temperature('celsius'))

    def run(self):
        while True:
            self.logger.info("Starting to update...")
            self.logger.info("  Getting Weather...")
            weather = self.getWeather()
            self.logger.info("  Getting Airhorn...")
            airhorn = self.airhorn.get_data()
            self.logger.info("  Getting Mails...")
            mail = self.mail.count_mails()
            self.logger.info("  Getting Appointments...")
            calendar = self.gcal.get_next_appointments()
            self.logger.info("  Draw and display...")
            image = self.draw(weather, airhorn, mail, calendar)
            self.epd.display(self.epd.getbuffer(image))
            self.logger.info("  Now sleeping for 600 seconds")
            time.sleep(600)

    def draw(self, weather, airhorn, mail, calendar):

        dt = datetime.datetime.now()
        icon_name = weather[0]
        icon = Image.open("icons/{}.jpg".format(icon_name))

        tempminmax = weather[1]

        if mail == 0:
            mail_icon = Image.open("icons/mail-closed.jpg")
        else:
            mail_icon = Image.open("icons/mail-open.jpg")

        Himage = Image.new('1', (self.epd.width, self.epd.height), 255)

        Himage.paste(icon, (50, 10))

        draw = ImageDraw.Draw(Himage)

        temp_text = "{} °C".format(airhorn["temperature"])
        temp_size = draw.textsize(temp_text, FONT35)
        draw.text((100 - temp_size[0] / 2, 120),
                  temp_text,
                  font=FONT35,
                  fill=0)

        tmm_text = "{} - {} °C".format(tempminmax["temp_min"],
                                       tempminmax["temp_max"])
        tmm_size = draw.textsize(tmm_text, FONT18)
        draw.text((100 - tmm_size[0] / 2, 160), tmm_text, font=FONT18, fill=0)

        p_text = "{} und {} µg/m³".format(airhorn["p2.5"], airhorn["p10"])
        p_size = draw.textsize(p_text, FONT18)
        draw.text((100 - p_size[0] / 2, 185), p_text, font=FONT18, fill=0)

        Himage.paste(mail_icon, (275, 30))
        if mail != 0:
            draw.text((315, 22), str(mail), font=FONT18, fill=0)

        Himage.paste(self.gcal.render(), (200, 120))

        draw.rectangle((0, 275, 400, 300), fill=0)
        draw.text((10, 276), os.uname().nodename, font=MONO18, fill=255)

        time_text = dt.strftime("%Y-%m-%d %H:%M:%S")
        time_size = draw.textsize(time_text, font=MONO18)
        draw.text((390 - time_size[0], 276), time_text, font=MONO18, fill=255)

        return Himage

