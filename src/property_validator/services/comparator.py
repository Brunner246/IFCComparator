import logging
from typing import Dict, List, Optional, Tuple
from ..models.complex_property import ComplexProperty, PropertyValue
from ..models.comparison_result import (
    ComparisonStatus,
    PropertyComparisonResult,
    EntityComparisonResult,
    ComparisonSummary
)

logger = logging.getLogger(__name__)


class PropertyComparator:
    """Compare complex properties from IFC and JSON"""

    def __init__(self, float_tolerance: float = 0.001):
        self.float_tolerance = float_tolerance

    def compare_entities(self,
                         entity_guid: str,
                         ifc_properties: Dict[str, ComplexProperty],
                         json_properties: Dict[str, ComplexProperty]) -> EntityComparisonResult:

        result = EntityComparisonResult(entity_guid)

        all_pset_names = set(ifc_properties.keys()) | set(json_properties.keys())

        for pset_name in all_pset_names:
            if pset_name in ifc_properties and pset_name in json_properties:
                ifc_cp = ifc_properties[pset_name]
                json_cp = json_properties[pset_name]

                prop_results = self._compare_complex_properties(
                    ifc_cp, json_cp, property_path=pset_name
                )
                for prop_result in prop_results:
                    result.add_result(prop_result)

            elif pset_name in ifc_properties:
                ifc_cp = ifc_properties[pset_name]
                result.add_result(
                    PropertyComparisonResult(
                        property_path=pset_name,
                        status=ComparisonStatus.MISSING_JSON,
                        ifc_value=str(ifc_cp),
                        json_value=None
                    )
                )

            else:  # pset_name in json_properties
                # Property set in JSON but not in IFC
                json_cp = json_properties[pset_name]
                result.add_result(
                    PropertyComparisonResult(
                        property_path=pset_name,
                        status=ComparisonStatus.MISSING_IFC,
                        ifc_value=None,
                        json_value=str(json_cp)
                    )
                )

        return result

    def _compare_complex_properties(self,
                                    ifc_cp: ComplexProperty,
                                    json_cp: ComplexProperty,
                                    property_path: str) -> List[PropertyComparisonResult]:
        results = []

        if ifc_cp.name != json_cp.name:
            results.append(
                PropertyComparisonResult(
                    property_path=f"{property_path}.name",
                    status=ComparisonStatus.MISMATCH,
                    ifc_value=ifc_cp.name,
                    json_value=json_cp.name
                )
            )

        ifc_props = {p.name: p for p in ifc_cp.properties}
        json_props = {p.name: p for p in json_cp.properties}
        all_prop_names = set(ifc_props.keys()) | set(json_props.keys())

        for prop_name in all_prop_names:
            if prop_name in ifc_props and prop_name in json_props:
                ifc_prop = ifc_props[prop_name]
                json_prop = json_props[prop_name]

                if isinstance(ifc_prop, ComplexProperty) and isinstance(json_prop, ComplexProperty):
                    nested_results = self._compare_complex_properties(
                        ifc_prop, json_prop, property_path=f"{property_path}.{prop_name}"
                    )
                    results.extend(nested_results)

                elif isinstance(ifc_prop, PropertyValue) and isinstance(json_prop, PropertyValue):
                    nested_path = f"{property_path}.{prop_name}"

                    if self._values_equal(ifc_prop.value, json_prop.value):
                        results.append(
                            PropertyComparisonResult(
                                property_path=nested_path,
                                status=ComparisonStatus.MATCH,
                                ifc_value=ifc_prop.value,
                                json_value=json_prop.value
                            )
                        )
                    else:
                        results.append(
                            PropertyComparisonResult(
                                property_path=nested_path,
                                status=ComparisonStatus.MISMATCH,
                                ifc_value=ifc_prop.value,
                                json_value=json_prop.value,
                                tolerance=self.float_tolerance if isinstance(ifc_prop.value, float) else None
                            )
                        )
                else:
                    results.append(
                        PropertyComparisonResult(
                            property_path=f"{property_path}.{prop_name}",
                            status=ComparisonStatus.MISMATCH,
                            ifc_value=type(ifc_prop).__name__,
                            json_value=type(json_prop).__name__
                        )
                    )

            elif prop_name in ifc_props:
                ifc_prop = ifc_props[prop_name]
                results.append(
                    PropertyComparisonResult(
                        property_path=f"{property_path}.{prop_name}",
                        status=ComparisonStatus.MISSING_JSON,
                        ifc_value=ifc_prop.value if isinstance(ifc_prop, PropertyValue) else str(ifc_prop),
                        json_value=None
                    )
                )

            else:  # prop_name in json_props
                # Property in JSON but not in IFC
                json_prop = json_props[prop_name]
                results.append(
                    PropertyComparisonResult(
                        property_path=f"{property_path}.{prop_name}",
                        status=ComparisonStatus.MISSING_IFC,
                        ifc_value=None,
                        json_value=json_prop.value if isinstance(json_prop, PropertyValue) else str(json_prop)
                    )
                )

        return results

    def _values_equal(self, ifc_value: any, json_value: any) -> bool:
        if (ifc_value is None or ifc_value == "") and (json_value is None or json_value == ""):
            return True

        if isinstance(ifc_value, (int, float)) and isinstance(json_value, (int, float)):
            return abs(float(ifc_value) - float(json_value)) <= self.float_tolerance

        return ifc_value == json_value