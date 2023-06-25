import argparse
import os
import glob
import json
import yaml
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M')
logger = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='Oria',
        description='Convert ItemsAdder config to Oxaren config files (and vice versa)')

    parser.add_argument('input-dir', type=str, help='Input directory (eg: ./plugins/ItemsAdder)')
    parser.add_argument('output-dir', type=str, help='Output directory (eg: (./Oxaren)')

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-ox", "--ia-to-oxaren", help="Convert ItemsAdder config to Oxaren config files",
                        action="store_true")
    parser.add_argument("-ia", "--oxaren-to-ia", help="Convert Oxaren config files to ItemsAdder config",
                        action="store_true")
    return parser


if __name__ == "__main__":
    args = get_parser().parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug('Input directory: %s', args.input_dir)
    logger.debug('Output directory: %s', args.output_dir)
