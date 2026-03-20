from dataclasses import dataclass


@dataclass
class SheetProfile:
    name: str
    row_count: int
    column_count: int
    missing_cells: int
    duplicate_rows: int


class WorkbookProfileModel:
    """Lightweight placeholder model that stores workbook profile thresholds."""

    def __init__(self, min_rows_for_confidence: int = 25, drift_threshold: float = 0.55):
        self.min_rows_for_confidence = min_rows_for_confidence
        self.drift_threshold = drift_threshold

    def config(self) -> dict:
        return {
            "min_rows_for_confidence": self.min_rows_for_confidence,
            "drift_threshold": self.drift_threshold,
        }
