import argparse
import os
import glob
import yaml
import typing
import logging
import tqdm
from uuid import uuid4 as uuid_func

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M')
logger = logging.getLogger(__name__)


ITEMSADDER_INTERNAL_NAMESPACES = ["_common", "_iainternal"]


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


def from_oxaren(oxaren_configs: typing.List[typing.Dict]) -> typing.List[typing.Dict]:
    """
    Convert Oxaren config files to ItemsAdder config
    :param oxaren_configs: List of dictionaries
    :return: List of dictionaries
    """
    # TODO: Implement
    return oxaren_configs


def from_ia(itemsadder_configs: typing.List[typing.Dict]) -> typing.List[typing.Dict]:
    """
    Convert ItemsAdder config to Oxaren config files
    :param itemsadder_configs: List of dictionaries
    :return: List of dictionaries
    """
    # TODO: Implement

    attribute_modifier_translation = {
        'attackDamage': 'GENERIC_ATTACK_DAMAGE',
        'attackSpeed': 'GENERIC_ATTACK_SPEED',
        'maxHealth': 'GENERIC_MAX_HEALTH',
        'movementSpeed': 'GENERIC_MOVEMENT_SPEED',
        'armor': 'GENERIC_ARMOR',
        'armorToughness': 'GENERIC_ARMOR_TOUGHNESS',
        'attackKnockback': 'GENERIC_ATTACK_KNOCKBACK',
        'luck': 'GENERIC_LUCK',
        'knockbackResistance': 'GENERIC_KNOCKBACK_RESISTANCE'
    }

    namespaced_dict = {}  # Every name space is a key, and the value is a list of items
    for config in itemsadder_configs:
        namespace = config['info']['namespace']

        if namespace in ITEMSADDER_INTERNAL_NAMESPACES:
            continue  # Skip internal namespaces

        if namespace not in namespaced_dict:
            namespaced_dict[namespace] = []

        namespaced_dict[namespace].append(config)  # Add the item to the list of items for that namespace
    converted_name_spaces = {}
    for namespace in namespaced_dict:
        logger.debug('Namespace: %s', namespace)
        converted_name_spaces[namespace] = []
        for config in namespaced_dict[namespace]:
            # Here we do item conversions
            if "items" in config.keys():
                for item in config["items"]:
                    item_name = item['display_name']
                    logger.debug('Item: %s', item)
                    try:
                        converted_item_attributes = {
                            'displayname': item['display_name'],
                            'material': item['resource']['material'],
                            'Pack': {
                                'generate_model': item['resource']['generate'],
                                # TODO: Find a way to add Oxaren "parent_model" value.
                                'textures': item['resource']['textures']
                            },
                            'Mechanics': [],
                            'AttributeModifiers': []
                        }
                    except KeyError as e:
                        logger.error(f"The item {item_name} is missing the required key {e}")
                        continue
                    logger.debug(f"Required attributes: {converted_item_attributes}")

                    if "durability" in item.keys():
                        converted_item_attributes['Mechanics'].append({
                            'durability': {'value': item['durability']['max_custom_durability']}
                        })

                    if 'lore' in item.keys():
                        converted_item_attributes['lore'] = item['lore']

                    if 'enchants' in item.keys():
                        pass

                    if "attribute_modifiers" in item.keys():
                        for modifier_hand in item['attribute_modifiers'].keys():
                            for modifier in modifier_hand.keys():
                                translated_modifier = attribute_modifier_translation[modifier]
                                converted_item_attributes['AttributeModifiers'].append({
                                    'name': f"{item_name}-{modifier}",
                                    'attribute': translated_modifier,
                                    'amount': item['attribute_modifiers'][modifier_hand][modifier],
                                    'operation': 0,
                                    'uuid': str(uuid_func()),
                                    'slot': 'HAND' if modifier_hand == "mainHand" else 'OFF_HAND'
                                })

                    if 'blocked_enchants' in item.keys():
                        logger.warning(f"Blocking specific enchantments just isn't a thing in Oxaren, "
                                       f"this will be ignored for: {item_name} ")

                    converted_name_spaces[namespace].append({item: converted_item_attributes})
    return itemsadder_configs


if __name__ == "__main__":
    args = get_parser().parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug('Input directory: %s', args.input_dir)
    logger.debug('Output directory: %s', args.output_dir)
    configs = get_configuration_files(args.input_dir, args.ia_to_oxaren)
    logger.debug('Configuration files: %s', configs)
    config_dicts = get_yml_dicts(configs)
    if args.ia_to_oxaren:
        config_dicts = from_ia(config_dicts)
    else:
        config_dicts = from_oxaren(config_dicts)
