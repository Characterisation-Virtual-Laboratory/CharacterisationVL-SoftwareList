import argparse
import logging
import logging.handlers
import sys
import yaml

# from ModulesToGoogle import ModulesToGoogle
from . import ModulesToGoogle


def main():
    parser = argparse.ArgumentParser(
        description="modules-to-google: upload a list of HPC software modules to a specified Google Worksheet."
    )
    parser.add_argument("--config", help="path to config.yml")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    with open(args.config) as f:
        config = yaml.safe_load(f.read())

    # setup logging
    logging_dict = {
        "logging.ERROR": logging.ERROR,
        "logging.WARNING": logging.WARNING,
        "logging.INFO": logging.INFO,
        "logging.DEBUG": logging.DEBUG,
    }

    logger = logging.getLogger("modules-to-google")
    logger.setLevel(logging_dict[config["log-level"]])

    # fh = logging.FileHandler(config["log-files"]["modules-to-google"])
    fh = logging.handlers.RotatingFileHandler(config["log-files"]["modules-to-google"], maxBytes=5 * 1024 * 1024,
                                              backupCount=3)
    fh.setLevel(logging_dict[config["log-level"]])
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s:%(process)s: %(message)s"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    upload = ModulesToGoogle(config)
    upload.main()


if __name__ == "__main__":
    main()
