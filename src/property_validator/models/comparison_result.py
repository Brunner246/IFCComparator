from enum import Enum
from typing import Dict, List, Optional, Any


class ComparisonStatus(Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    MISSING_IFC = "missing_in_ifc"
    MISSING_JSON = "missing_in_json"


class PropertyComparisonResult:
    """Result of comparing a single property"""

    def __init__(self,
                 property_path: str,
                 status: ComparisonStatus,
                 ifc_value: Optional[Any] = None,
                 json_value: Optional[Any] = None,
                 tolerance: Optional[float] = None):
        self.property_path = property_path
        self.status = status
        self.ifc_value = ifc_value
        self.json_value = json_value
        self.tolerance = tolerance

    def __str__(self):
        if self.status == ComparisonStatus.MATCH:
            return f"✓ {self.property_path}: {self.ifc_value}"
        elif self.status == ComparisonStatus.MISMATCH:
            return f"✗ {self.property_path}: IFC={self.ifc_value}, JSON={self.json_value}"
        elif self.status == ComparisonStatus.MISSING_IFC:
            return f"! {self.property_path}: Missing in IFC (JSON={self.json_value})"
        else:
            return f"! {self.property_path}: Missing in JSON (IFC={self.ifc_value})"


class EntityComparisonResult:
    def __init__(self, guid: str):
        self.guid = guid
        self.property_results: List[PropertyComparisonResult] = []

    def add_result(self, result: PropertyComparisonResult):
        self.property_results.append(result)

    @property
    def has_mismatches(self) -> bool:
        return any(r.status != ComparisonStatus.MATCH for r in self.property_results)

    @property
    def match_count(self) -> int:
        return sum(1 for r in self.property_results if r.status == ComparisonStatus.MATCH)

    @property
    def mismatch_count(self) -> int:
        return sum(1 for r in self.property_results if r.status == ComparisonStatus.MISMATCH)

    @property
    def missing_ifc_count(self) -> int:
        return sum(1 for r in self.property_results
                   if r.status == ComparisonStatus.MISSING_IFC)

    @property
    def missing_json_count(self) -> int:
        return sum(1 for r in self.property_results
                   if r.status == ComparisonStatus.MISSING_JSON)

    def __str__(self):
        result = f"Entity: {self.guid}\n"
        result += f"  Matches: {self.match_count}, Mismatches: {self.mismatch_count}, "
        result += f"Missing in IFC: {self.missing_ifc_count}, Missing in JSON: {self.missing_json_count}\n"

        if self.has_mismatches:
            result += "  Details:\n"
            for prop_result in self.property_results:
                if prop_result.status != ComparisonStatus.MATCH:
                    result += f"    {prop_result}\n"

        return result


class ComparisonSummary:
    def __init__(self):
        self.entity_results: Dict[str, EntityComparisonResult] = {}

    def add_entity_result(self, entity_result: EntityComparisonResult):
        self.entity_results[entity_result.guid] = entity_result

    @property
    def entity_count(self) -> int:
        return len(self.entity_results)

    @property
    def matched_entity_count(self) -> int:
        return sum(1 for result in self.entity_results.values()
                   if not result.has_mismatches)

    @property
    def mismatched_entity_count(self) -> int:
        return sum(1 for result in self.entity_results.values()
                   if result.has_mismatches)

    def __str__(self):
        result = f"Comparison Summary:\n"
        result += f"  Total Entities: {self.entity_count}\n"
        result += f"  Matched Entities: {self.matched_entity_count}\n"
        result += f"  Mismatched Entities: {self.mismatched_entity_count}\n\n"

        if self.mismatched_entity_count > 0:
            result += "Entities with mismatches:\n"
            for entity_result in self.entity_results.values():
                if entity_result.has_mismatches:
                    result += f"{entity_result}\n"

        return result