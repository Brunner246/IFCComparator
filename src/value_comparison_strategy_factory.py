from enum import Enum

from src.value_comparison_strategies import ComparisonStrategy, CoordinatesComparisonStrategy, \
    CoordIndexComparisonStrategy, CoordListComparisonStrategy


class ComparisonStrategyType(Enum):
    COORDINATES = "Coordinates"
    COORDINDEX = "CoordIndex"
    COORDLIST = "CoordList"


class StrategyFactory:
    @staticmethod
    def create_strategy(strategy_type: ComparisonStrategyType) -> ComparisonStrategy:
        match strategy_type:
            case ComparisonStrategyType.COORDINATES:
                return CoordinatesComparisonStrategy()
            case ComparisonStrategyType.COORDINDEX:
                return CoordIndexComparisonStrategy()
            case ComparisonStrategyType.COORDLIST:
                return CoordListComparisonStrategy()
            case _:
                raise ValueError(f"Unknown strategy type: {strategy_type}")
