from typing import Dict, List, Optional, Union, Any


class PropertyValue:
    """Represents a single property value (e.g., X, Y, Z coordinates)"""

    def __init__(self, name: str, value: Any, unit: Optional[str] = None):
        self.name = name
        self.value = value
        self.unit = unit

    def __str__(self):
        if self.unit:
            return f"{self.name}: {self.value} {self.unit}"
        return f"{self.name}: {self.value}"

    def __eq__(self, other):
        if not isinstance(other, PropertyValue):
            return False
        return (self.name == other.name and
                self.value == other.value and
                self.unit == other.unit)


class ComplexProperty:
    """Represents a complex IFC property with nested properties"""

    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.properties: List[Union[PropertyValue, 'ComplexProperty']] = []

    def add_property(self, prop: Union[PropertyValue, 'ComplexProperty']):
        self.properties.append(prop)

    def find_property_by_name(self, name: str) -> Optional[Union[PropertyValue, 'ComplexProperty']]:
        """Find a property by name (non-recursive search)"""
        for prop in self.properties:
            if prop.name == name:
                return prop
        return None

    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        result = {
            "name": self.name,
            "description": self.description,
            "properties": []
        }

        for prop in self.properties:
            if isinstance(prop, PropertyValue):
                prop_dict = {
                    "name": prop.name,
                    "value": prop.value
                }
                if prop.unit:
                    prop_dict["unit"] = prop.unit
                result["properties"].append(prop_dict)
            else:
                result["properties"].append(prop.to_dict())

        return result

    def __str__(self):
        desc = f" ({self.description})" if self.description else ""
        result = f"{self.name}{desc}:\n"
        for prop in self.properties:
            prop_str = str(prop)
            if isinstance(prop, ComplexProperty):
                # Indent nested complex properties
                prop_str = "\n".join(f"  {line}" for line in prop_str.split("\n"))
            else:
                prop_str = f"  {prop_str}"
            result += f"{prop_str}\n"
        return result.strip()