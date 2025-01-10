from src.differences_collector import DifferencesCollector
from src.ifc_comparator import IFCComparator
from src.interfaces.file_comparator import FileComparator
from src.interfaces.file_comparator_factory import FileComparatorFactory, FileType


class IfcFileComparatorFactoryImpl(FileComparatorFactory):
    def create(self, file_type: FileType, collector: DifferencesCollector = None) -> FileComparator:
        match file_type:
            case FileType.IFC:
                return IFCComparator(self.file1_path, self.file2_path, collector)
            case _:
                raise ValueError(f"Unsupported file type: {file_type}")
