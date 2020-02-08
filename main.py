import argparse
import importlib
import logging
import sys

import crypto_config
import gcal_handler
from desk_ink import DeskInk

def start(args, edp4in2):
    config = crypto_config.get_config(args.key.encode(), args.config)

    desk = DeskInk(config, edp4in2)
    desk.run()


def main():
    parser = argparse.ArgumentParser("DeskInk")
    parser.add_argument("--preview", type=bool, default=False)
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

    global epd4in2
    if not arguments.preview:
        epd4in2 = importlib.import_module("lib.epd4in2")
    else:
        epd4in2 = importlib.import_module("lib.epd4in2mock")

    if arguments.subcommand == "edit":
        crypto_config.edit_config(arguments.key.encode(), arguments.config,
                                  crypto_config.interactive_edit_config)
    elif arguments.subcommand == "gcal":
        crypto_config.edit_config(arguments.key.encode(), arguments.config,
                                  gcal_handler.add_pickle_to_config)
    elif arguments.subcommand == "start":
        start(arguments, epd4in2)


if __name__ == "__main__":
    try:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        main()
    except IOError as e:
        logging.info(e)
    except Exception as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd4in2.epdconfig.module_exit()
        sys.exit()
