import ifcopenshell
from typing import Dict, List, Optional, Tuple
import logging
from ..models.complex_property import ComplexProperty, PropertyValue

logger = logging.getLogger(__name__)


class IfcReader:
    """Read and extract complex properties from IFC files"""

    def __init__(self, ifc_file_path: str):
        self.ifc_file_path = ifc_file_path
        self.ifc_file = ifcopenshell.open(ifc_file_path)
        logger.info(f"Loaded IFC file: {ifc_file_path}")

    def get_entity_guids(self) -> List[str]:
        guids = []
        for entity in self.ifc_file.by_type('IfcRoot'):
            guids.append(entity.GlobalId)
        return guids

    def get_entities_with_complex_properties(self) -> List[Tuple[str, str]]:
        results = []
        entity_guids = set()

        all_psets = self.ifc_file.by_type("IfcPropertySet")
        for pset in all_psets:
            for prop in pset.HasProperties:
                if prop.is_a("IfcComplexProperty"):
                    for rel in self.ifc_file.by_type("IfcRelDefinesByProperties"):
                        if rel.RelatingPropertyDefinition == pset:
                            for entity in rel.RelatedObjects:
                                if hasattr(entity, 'GlobalId'):
                                    guid = entity.GlobalId
                                    entity_type = entity.is_a()
                                    if guid not in entity_guids:
                                        results.append((guid, entity_type))
                                        entity_guids.add(guid)

        return results

    def get_complex_properties_by_guid(self, entity_guid: str) -> Dict[str, ComplexProperty]:
        result = {}
        entity = self.ifc_file.by_guid(entity_guid)

        if not entity:
            logger.warning(f"Entity with GUID {entity_guid} not found")
            return {}

        for rel in self.ifc_file.by_type("IfcRelDefinesByProperties"):
            if entity in rel.RelatedObjects:
                pset = rel.RelatingPropertyDefinition

                if not pset.is_a("IfcPropertySet"):
                    continue

                for prop in pset.HasProperties:
                    if prop.is_a("IfcComplexProperty"):
                        cp = self._process_complex_property(prop)
                        result[f"{pset.Name}.{prop.Name}"] = cp

        return result

    def _process_complex_property(self, ifc_complex_prop) -> ComplexProperty:
        cp = ComplexProperty(ifc_complex_prop.Name, ifc_complex_prop.Description)

        for nested_prop in ifc_complex_prop.HasProperties:
            if nested_prop.is_a("IfcComplexProperty"):
                nested_cp = self._process_complex_property(nested_prop)
                cp.add_property(nested_cp)
            elif nested_prop.is_a("IfcPropertySingleValue"):
                name = nested_prop.Name

                ifc_value = nested_prop.NominalValue
                value = None
                if ifc_value:
                    # value might be wrapped in an IfcReal, IfcLabel, etc.
                    value = ifc_value.wrappedValue

                unit = None
                if nested_prop.Unit:
                    unit = nested_prop.Unit.wrappedValue

                cp.add_property(PropertyValue(name, value, unit))

        return cp