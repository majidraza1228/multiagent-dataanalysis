from eval_framework.registry import AdapterRegistry
from evals.api_adapter import FastAPIWorkbookAdapter
from evals.workbook_adapter import WorkbookAnalyzerAdapter


def build_registry() -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register("workbook-analyzer", WorkbookAnalyzerAdapter)
    registry.register("fastapi-api", FastAPIWorkbookAdapter)
    return registry
