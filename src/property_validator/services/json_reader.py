import json
import logging
import os
from typing import Dict, List, Optional, Any
from ..models.complex_property import ComplexProperty, PropertyValue

logger = logging.getLogger(__name__)


class JsonReader:
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.data = {}

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                self.data = {}
                for item in data:
                    if isinstance(item, dict):
                        for guid, entity_data in item.items():
                            self.data[guid] = entity_data
            elif isinstance(data, dict):
                self.data = data
            else:
                logger.error(f"Unsupported JSON format: {type(data)}")

            logger.info(f"Loaded JSON file: {json_file_path}")
            logger.info(f"Found {len(self.data)} entities in JSON")

        except Exception as e:
            logger.error(f"Failed to load JSON file: {str(e)}")

    def get_entities(self) -> List[str]:
        """Get list of entity GUIDs in the JSON file"""
        return list(self.data.keys())

    def get_complex_properties_by_guid(self, entity_guid: str) -> Dict[str, ComplexProperty]:
        """
        Get all complex properties for an entity with the given GUID
        Returns: Dictionary of {property_set_name.property_name: ComplexProperty}
        """
        if entity_guid not in self.data:
            logger.warning(f"Entity with GUID {entity_guid} not found in JSON")
            return {}

        entity_data = self.data[entity_guid]
        result = {}

        # Handle different JSON formats
        if isinstance(entity_data, dict):
            for pset_name, pset_data in entity_data.items():
                self._process_property_set(pset_name, pset_data, result)

        return result

    def _process_property_set(self, pset_name: str, pset_data: Dict, result: Dict[str, ComplexProperty]):
        """Process a property set from JSON data"""
        # Check if pset_data has properties key
        if isinstance(pset_data, dict) and "properties" in pset_data:
            properties_data = pset_data["properties"]
            for prop_name, prop_data in properties_data.items():
                if isinstance(prop_data, dict) and (prop_data.get("type") == "complex" or "properties" in prop_data):
                    complex_prop = self._process_complex_property_data(prop_name, prop_data)
                    result[f"{pset_name}.{prop_name}"] = complex_prop
        # Alternative format - properties directly in the pset_data
        elif isinstance(pset_data, dict):
            for prop_name, prop_data in pset_data.items():
                if isinstance(prop_data, dict) and (prop_data.get("type") == "complex" or "properties" in prop_data):
                    complex_prop = self._process_complex_property_data(prop_name, prop_data)
                    result[f"{pset_name}.{prop_name}"] = complex_prop

    def _process_complex_property_data(self, name: str, data: Dict[str, Any]) -> ComplexProperty:
        """Process complex property data from JSON"""
        description = data.get("description", None)
        cp = ComplexProperty(name, description)

        properties_data = {}
        if "properties" in data and isinstance(data["properties"], dict):
            properties_data = data["properties"]

        for nested_name, nested_data in properties_data.items():
            is_complex = False

            if isinstance(nested_data, dict):
                if "type" in nested_data and nested_data["type"] == "complex":
                    is_complex = True
                elif "properties" in nested_data and isinstance(nested_data["properties"], dict):
                    is_complex = True

            if is_complex:
                nested_cp = self._process_complex_property_data(nested_name, nested_data)
                cp.add_property(nested_cp)
            else:
                value = None
                unit = None

                if isinstance(nested_data, dict):
                    value = nested_data.get("value")
                    unit = nested_data.get("unit")
                else:
                    value = nested_data

                cp.add_property(PropertyValue(nested_name, value, unit))

        return cp