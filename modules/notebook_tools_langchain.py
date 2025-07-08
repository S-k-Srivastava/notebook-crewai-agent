import uuid
from langchain.tools import tool
from typing import Optional, List, Dict, Any
from modules.notebook_controller import NotebookController

notebook = NotebookController(f"{str(uuid.uuid4())}.ipynb")

@tool
def insert_cell_tool(cell_type: str = "code", source: str = "", index: Optional[int] = None) -> str:
    """Insert a new cell into the notebook."""
    print(f"[TOOL] insert_cell_tool called with: type={cell_type}, source={source}, index={index}")
    return notebook.insert_cell(cell_type=cell_type, source=source, index=index)

@tool
def run_cell_tool(cell_id: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute a code cell by cell ID."""
    print(f"[TOOL] run_cell_tool called with: cell_id={cell_id}, timeout={timeout}")
    return notebook.run_cell(cell_id=cell_id, timeout=timeout)

@tool
def insert_and_run_cell_tool(cell_type: str = "code", source: str = "", index: Optional[int] = None) -> Dict[str, Any]:
    """Inserts a cell with code and runs it."""
    
    cell_id = notebook.insert_cell(cell_type=cell_type, source=source, index=index)
    
    print(f"[TOOL] insert_and_run_cell_tool called with: cell_id={cell_id}, timeout={30}")
    
    return notebook.run_cell(cell_id=cell_id, timeout=30)

@tool
def run_all_cells_tool(timeout: int = 30) -> List[Dict[str, Any]]:
    """Execute all code cells in the notebook."""
    print(f"[TOOL] run_all_cells_tool called with: timeout={timeout}")
    return notebook.run_all_cells(timeout=timeout)

@tool
def update_cell_source_tool(cell_id: str, source: str) -> bool:
    """Update the source code of a cell."""
    print(f"[TOOL] update_cell_source_tool called with: cell_id={cell_id}, source={source}")
    return notebook.update_cell_source(cell_id=cell_id, source=source)

@tool
def delete_cell_tool(cell_id: str) -> bool:
    """Delete a cell by its ID."""
    print(f"[TOOL] delete_cell_tool called with: cell_id={cell_id}")
    return notebook.delete_cell(cell_id=cell_id)

@tool
def get_notebook_info_tool() -> Dict[str, Any]:
    """Return summary info about the notebook and kernel."""
    print(f"[TOOL] get_notebook_info_tool called")
    return notebook.get_notebook_info()

@tool
def get_cellIds_code_map_tool() -> Dict[str, Any]:
    """Return all cell IDs mapped with their code."""
    print(f"[TOOL] get_cellIds_code_map called")
    return notebook.get_cell_id_to_source_map()


NOTEBOOK_TOOLS = [
    insert_and_run_cell_tool,
    run_cell_tool,
    run_all_cells_tool,
    update_cell_source_tool,
    delete_cell_tool,
    get_notebook_info_tool,
]