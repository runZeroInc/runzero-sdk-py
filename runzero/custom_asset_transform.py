"""
A helper module which allows custom asset data format transformation between the required internal
representation, or csv data.
"""
import csv
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import pydantic

from runzero.errors import Error
from runzero.types import ImportAsset, ValidationError


def assets_from_csv(
    path: Union[str, Path], mapper: Optional[Dict[str, str]] = None, encoding: Optional[str] = None
) -> List[ImportAsset]:
    """
    Reads and converts the contents of the given CSV and transforms it into a list of runZero ImportAsset data models.

    By default, this function will map CSV fields with an exact matching name to the corresponding model field.
    Any CSV field which is not an exact match of a corresponding model field name will be placed into a flat json map
    under customAttributes.

    The optional mapper argument can be used to explicitly map a field by name from the CSV input to a field by name in
    the ImportAsset.

    From the runZero API docs - see #/components/schemas/ImportAsset

    :param path: path to a CSV in either string or pathlib.Path format
    :param mapper: Optional mapping of attribute names in the format of Dict{ImportAsset field: User Input field}
    :param encoding: Optional encoding type as string to use for opening file. If not supplied then python will attempt
        to figure out which encoding to use based on system information.
    :return: A list of ImportAsset's
    :rtype List[ImportAsset]
    :raises [
        ValidationError: A validation error when creating ImportAsset from input,
        Error: A catch-all error for any issues that occur during file processing,
        ]
    """
    if mapper is None or not isinstance(mapper, dict):
        mapper = {}
    result: List[ImportAsset] = []
    try:
        with open(path, "r", encoding=encoding) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for line in csv_reader:
                try:
                    formatter = import_asset_with_custom_mapping_hook(mapper)
                    result.append(formatter(line))
                except (json.JSONDecodeError, TypeError, ValueError, pydantic.ValidationError) as err:
                    raise ValidationError("Failed to convert json into List[ImportAsset]") from err
    except ValidationError as err:
        raise err
    except Exception as file_err:
        raise Error from file_err
    return result


def assets_from_json(
    json_input: Union[str, bytes, bytearray], mapper: Optional[Dict[str, str]] = None
) -> List[ImportAsset]:
    """
    Converts arbitrary JSON into the runZero ImportAsset data model.

    By default, this function will map JSON fields with an exact matching name to the corresponding model field.
    Any JSON field which is not an exact match of a corresponding model field name will be placed into a flat json map
    under customAttributes.

    The optional mapper argument can be used to explicitly map a field by name from the json input to a field by name in
    the ImportAsset.

    From the runZero API docs - see #/components/schemas/ImportAsset

    :param json_input: a json string or a dict representing assets
    :param mapper: Optional mapping of attribute names in the format of Dict{ImportAsset field: User Input field}
    :return: A list of ImportAsset's
    :rtype List[ImportAsset]
    :raise ValidationError: A validation error when creating ImportAssets from input
    """
    if mapper is None or not isinstance(mapper, dict):
        mapper = {}
    try:
        # result = json.loads(json_input, object_hook=import_asset_with_custom_mapping_hook(mapper))
        raw = json.loads(json_input)
        formatter = import_asset_with_custom_mapping_hook(mapper)
        result: List[ImportAsset] = []
        if isinstance(raw, list):
            for asset in raw:
                result.append(formatter(asset))
        else:
            result.append(formatter(raw))
        return result
    except (json.JSONDecodeError, TypeError, ValueError, pydantic.ValidationError) as err:
        raise ValidationError("Failed to convert json into List[ImportAsset]") from err


def import_asset_with_custom_mapping_hook(mapping: Dict[str, str]) -> Callable[[Dict[str, Any]], ImportAsset]:
    """
    Creates a callback which applies formatting to given dict before attempting to marshal into an ImportAsset

    :param mapping: A dictionary which maps the following {ImportAsset field name: User Input field name}
    :return: A callback to apply the field mapping and create the ImportAsset from the given Dict
    """

    def callback(data: Dict[str, Any]) -> ImportAsset:
        """
        Applies a remapping of fields in the input dict then marshals into an ImportAsset
        :param data: A dictionary representing an asset
        :return: An ImportAsset containing the marshalled contents of the given dict
        :rtype ImportAsset
        :raises ValidationError
        """
        additional_attrs: Dict[str, Any] = {}
        to_rename: Dict[str, str] = {}
        try:
            # remap field names
            for import_asset_field, user_field in mapping.items():
                cased_field = _convert_casing(import_asset_field)
                item = data.get(user_field)
                if item is not None:
                    data[cased_field] = data.pop(user_field)

            # use ImportAsset schema to generate set of field keys
            schema = ImportAsset.schema()
            props = schema.get("properties")
            if props is None:
                raise ValidationError("Invalid schema properties for ImportAsset")
            schema_keys = props.keys()

            # iterate over keys in user data to determine if they're additional attributes
            fields = data.keys()
            for field in fields:
                cased_field = _convert_casing(field)
                # if the cased field name doesn't match a schema key then stick in custom_attributes
                if cased_field not in schema_keys:
                    additional_attrs[cased_field] = data.get(field)
                elif cased_field != field:
                    to_rename[cased_field] = field

            # rename map fields for better marshaling
            for new_name, old_name in to_rename.items():
                data[new_name] = data.pop(old_name)

            # handle networkInterface renaming if necessary
            network_interfaces = data.get("networkInterfaces")
            renamed_network_interfaces: List[Dict[str, Any]] = []
            if network_interfaces is not None:
                for interface in network_interfaces:
                    to_rename = {}
                    fields = interface.keys()
                    for field in fields:
                        cased_field = _convert_casing(field)
                        if cased_field != field:
                            to_rename[cased_field] = field
                    for new_name, old_name in to_rename.items():
                        interface[new_name] = interface.pop(old_name)
                    renamed_network_interfaces.append(interface)
            if len(renamed_network_interfaces) > 0:
                data["networkInterfaces"] = renamed_network_interfaces

            # map custom attributes to dict
            data["customAttributes"] = additional_attrs

            return ImportAsset.parse_obj(data)
        except pydantic.ValidationError as err:
            raise ValidationError("Unable to convert dict into ImportAsset") from err

    return callback


def _convert_casing(to_case: str) -> str:
    """
    Helper func to convert snake cased strings to camel case.

    Also makes any string with ends w/ Ts/ts convert to TS so that the runzero platform understands the value as a
    timestamp.

    :param to_case: value to convert from snake case to camel case
    :return: camel cased string
    """
    tmp = to_case.split("_")
    res = tmp[0] + "".join(ele.title() for ele in tmp[1:])
    if res.endswith("Ts"):
        return res[: len(res) - 1] + "S"
    return res
