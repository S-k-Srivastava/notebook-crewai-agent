from datetime import datetime
from typing import Optional, Type
from pydantic import BaseModel, Field
from modules.notebook_controller import NotebookController
from crewai.tools import BaseTool


def get_formatted_date()->str:
    return "_".join(datetime.now().strftime("%B %d %Y %H %M %S").split(" "))
    
notebook = NotebookController(f"{get_formatted_date()}.ipynb")

# Define input schemas for each tool
class InsertAndRunCellInput(BaseModel):
    cell_type: str = Field(description="Type of the cell (e.g., 'code' or 'markdown')")
    source: str = Field(description="Source code or content of the cell")
    index: Optional[int] = Field(None, description="Position index where to insert the cell")

class RunCellInput(BaseModel):
    cell_id: str = Field(description="ID of the cell to run")
    timeout: int = Field(30, description="Timeout in seconds for cell execution")

class RunAllCellsInput(BaseModel):
    timeout: int = Field(30, description="Timeout in seconds for cell executions")

class UpdateCellSourceInput(BaseModel):
    cell_id: str = Field(description="ID of the cell to update")
    source: str = Field(description="New source code for the cell")

class DeleteCellInput(BaseModel):
    cell_id: str = Field(description="ID of the cell to delete")

class InsertAndRunCellTool(BaseTool):
    name: str = "insert_and_run_cell"
    description: str = "Insert a new cell and run it into the notebook."
    args_schema: Type[BaseModel] = InsertAndRunCellInput

    def _run(self, cell_type: str, source: str, index: Optional[int] = None) -> str:
        cell_id = notebook.insert_cell(cell_type, source, index)
        return notebook.run_cell(cell_id=cell_id)
        

class RunCellTool(BaseTool):
    name: str = "run_cell"
    description: str = "Run a specific code cell by its ID."
    args_schema: Type[BaseModel] = RunCellInput

    def _run(self, cell_id: str, timeout: int = 30) -> dict:
        return notebook.run_cell(cell_id, timeout)

class RunAllCellsTool(BaseTool):
    name: str = "run_all_cells"
    description: str = "Run all code cells in the notebook."
    args_schema: Type[BaseModel] = RunAllCellsInput

    def _run(self, timeout: int = 30) -> list:
        return notebook.run_all_cells(timeout)

class UpdateCellSourceTool(BaseTool):
    name: str = "update_cell_source"
    description: str = "Update the source code of a cell."
    args_schema: Type[BaseModel] = UpdateCellSourceInput

    def _run(self, cell_id: str, source: str) -> bool:
        return notebook.update_cell_source(cell_id, source)

class DeleteCellTool(BaseTool):
    name: str = "delete_cell"
    description: str = "Delete a notebook cell."
    args_schema: Type[BaseModel] = DeleteCellInput

    def _run(self, cell_id: str) -> bool:
        return notebook.delete_cell(cell_id)

class GetNotebookInfoTool(BaseTool):
    name: str = "get_notebook_info"
    description: str = "Return summary info about the notebook."

    def _run(self) -> dict:
        return notebook.get_notebook_info()

class GetCellIdsToSourceMapTool(BaseTool):
    name: str = "get_cell_ids_to_source_map"
    description: str = "Map of all cell IDs to source."

    def _run(self) -> dict:
        return notebook.get_cell_id_to_source_map()

class RestartKernelTool(BaseTool):
    name: str = "restart_kernel"
    description: str = "Restart the notebook kernel."

    def _run(self) -> None:
        return notebook.restart_kernel()

# CrewAI expects these to be directly passed as a list
NOTEBOOK_TOOLS = [
    InsertAndRunCellTool(),
    RunCellTool(),
    RunAllCellsTool(),
    UpdateCellSourceTool(),
    DeleteCellTool(),
    GetNotebookInfoTool(),
    GetCellIdsToSourceMapTool(),
    RestartKernelTool(),
]