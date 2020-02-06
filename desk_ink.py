#!/usr/bin/env python3
import os
import configparser
import argparse
import logging
import time
import datetime

from PIL import Image, ImageDraw, ImageFont
from pyowm import OWM

import crypto_config
import gcal_handler
from gcal_handler import GcalHandler
from mail_handler import MailHandler
from airhorn import Airhorn
from lib import epd4in2
from dateutil import parser

FONT24 = ImageFont.truetype('FiraSans-Regular.ttf', 24)
FONT18 = ImageFont.truetype('FiraSans-Regular.ttf', 18)
MONO18 = ImageFont.truetype('Monospace.ttf', 18)
FONT35 = ImageFont.truetype('FiraSans-Regular.ttf', 35)


class DeskInk:
    """Docstring for DeskInk. """
    def __init__(self, config: configparser.ConfigParser):
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

        draw.text((200, 120), "Termine:", font=FONT24, fill=0)

        for i, v in enumerate(calendar):
            datet = v['start'].get('dateTime', v['start'].get('date'))
            datep = parser.parse(datet)

            draw.text((200, 150+i*20), datep.strftime("%d.%m"), font=FONT18, fill=0)
            draw.text((250, 150+i*20), v["summary"][:12]+"..." if len(v["summary"]) > 12 else v["summary"], font=FONT18, fill=0)


        draw.rectangle((0, 275, 400, 300), fill=0)
        draw.text((10, 276), os.uname().nodename, font=MONO18, fill=255)

        time_text = dt.strftime("%Y-%m-%d %H:%M:%S")
        time_size = draw.textsize(time_text, font=MONO18)
        draw.text((390 - time_size[0], 276), time_text, font=MONO18, fill=255)

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

    gcal_parser = subparsers.add_parser("gcal")
    gcal_parser.add_argument("-c", "--config", default="config")
    gcal_parser.add_argument("-k", "--key", required=True)


    arguments = parser.parse_args()

    if arguments.subcommand == "edit":
        crypto_config.edit_config(arguments.key.encode(), arguments.config,
                                  crypto_config.interactive_edit_config)
    elif arguments.subcommand == "gcal":
        crypto_config.edit_config(arguments.key.encode(), arguments.config,
                                  gcal_handler.add_pickle_to_config)
    elif arguments.subcommand == "start":
        start(arguments)


if __name__ == "__main__":
    try:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        main()
    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd4in2.epdconfig.module_exit()
        exit()
