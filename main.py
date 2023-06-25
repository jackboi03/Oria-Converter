import argparse
import os
import glob
import yaml
import typing
import logging
import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M')
logger = logging.getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='Oria',
        description='Convert ItemsAdder config to Oxaren config files (and vice versa)')

    parser.add_argument('input_dir', type=str, help='Input directory (eg: ./plugins/ItemsAdder)',
                        metavar='Input directory')
    parser.add_argument('output_dir', type=str, help='Output directory (eg: (./Oxaren)',
                        metavar='Output directory')

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-ox", "--ia-to-oxaren", help="Convert ItemsAdder config to Oxaren config files",
                        action="store_true")
    parser.add_argument("-ia", "--oxaren-to-ia", help="Convert Oxaren config files to ItemsAdder config",
                        action="store_true")
    return parser


def get_configuration_files(input_dir: str, is_ia: bool) -> typing.List[str]:
    """
    Get all the configuration needed to convert for a given plugin.
    For resourcepack see other method.  TODO: Write other method
    :param input_dir: Plugin's root folder
    :param is_ia: Whether we're converting ItemsAdder. (Oxaren otherwise)
    :return: List of files to convert
    """
    paths = []
    if is_ia:
        # Search for all .yml files, recursively
        for file in tqdm.tqdm(glob.glob(os.path.join(input_dir, "./contents/**/*.yml"), recursive=True),
                              desc="Searching for files", unit="files"):
            paths.append(file)
    else:
        for file in tqdm.tqdm(glob.glob(os.path.join(input_dir, "./items/**/*.yml"), recursive=True),
                              desc="Searching for files", unit="files"):
            paths.append(file)
        # Recipes are stored separately, so we need to add them manually
        for file in tqdm.tqdm(glob.glob(os.path.join(input_dir, "./recipes/**/*.yml"), recursive=True),
                              desc="Searching for recipes", unit="recipes"):
            paths.append(file)
    return paths


def get_yml_dicts(files: typing.List[str]) -> typing.List[typing.Dict]:
    """
    Get all the configuration files as dictionaries
    :param files: List of files to convert
    :return: List of dictionaries
    """
    dicts = []
    for file in tqdm.tqdm(files, desc="Reading files"):
        with open(file, 'r', encoding="utf-8") as stream:
            try:
                dicts.append(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                logger.error(exc)
    return dicts


def from_oxaren(itemsadder_configs: typing.List[typing.Dict]) -> typing.List[typing.Dict]:
    """
    Convert Oxaren config files to ItemsAdder config
    :param itemsadder_configs: List of dictionaries
    :return: List of dictionaries
    """
    # TODO: Implement
    return itemsadder_configs


def from_ia(oxaren_configs: typing.List[typing.Dict]) -> typing.List[typing.Dict]:
    """
    Convert ItemsAdder config to Oxaren config files
    :param oxaren_configs: List of dictionaries
    :return: List of dictionaries
    """
    # TODO: Implement
    return oxaren_configs


if __name__ == "__main__":
    args = get_parser().parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug('Input directory: %s', args.input_dir)
    logger.debug('Output directory: %s', args.output_dir)
    configs = get_configuration_files(args.input_dir, not args.ia_to_oxaren)
    logger.debug('Configuration files: %s', configs)
    config_dicts = get_yml_dicts(configs)
