import json
import os
import uuid
import queue
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import subprocess
from jupyter_client import KernelManager

class NotebookController:
    def __init__(self, notebook_path: Optional[str] = None):
        self.notebook_path = notebook_path
        self.notebook_data = {}
        self.kernel_manager = None
        self.kernel_client = None
        self.cell_id_map = {}
        self.execution_count = 0
        self.kernel_ready = False
        
        if notebook_path:
            if os.path.exists(notebook_path):
                self.load_notebook(notebook_path)
            else:
                self.create_notebook(notebook_path)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.notebook_path = f"temp_notebook_{timestamp}.ipynb"
            self.create_notebook(self.notebook_path)
        
        # Start the kernel for persistent execution
        self.start_kernel()

    def create_notebook(self, path: str) -> None:
        self.notebook_path = path
        self.notebook_data = {
            "cells": [],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.8.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        self.save_notebook()
        self._update_cell_id_map()
        print(f"Created new notebook: {path}")
    
    def load_notebook(self, path: str) -> None:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.notebook_data = json.load(f)
            self.notebook_path = path
            self._update_cell_id_map()
            
            # Get the highest execution count from existing cells
            max_count = 0
            for cell in self.notebook_data.get('cells', []):
                if cell.get('cell_type') == 'code' and cell.get('execution_count'):
                    max_count = max(max_count, cell['execution_count'])
            self.execution_count = max_count
            
            print(f"Loaded notebook: {path}")
        except Exception as e:
            print(f"Error loading notebook: {e}")
            raise
    
    def save_notebook(self) -> None:
        try:
            with open(self.notebook_path, 'w', encoding='utf-8') as f:
                json.dump(self.notebook_data, f, indent=2, ensure_ascii=False)
            print(f"Saved notebook: {self.notebook_path}")
        except Exception as e:
            print(f"Error saving notebook: {e}")
            raise
    
    def start_kernel(self) -> None:
        """Start a persistent Python kernel for cell execution"""
        try:
            self.kernel_manager = KernelManager(kernel_name='python3')
            self.kernel_manager.start_kernel()
            self.kernel_client = self.kernel_manager.client()
            self.kernel_client.start_channels()
            
            # Wait for kernel to be ready
            self.kernel_client.wait_for_ready(timeout=10)
            self.kernel_ready = True
            print("🔥 Kernel started successfully")
            
        except Exception as e:
            print(f"Error starting kernel: {e}")
            self.kernel_ready = False
    
    def stop_kernel(self) -> None:
        """Stop the persistent kernel"""
        try:
            if self.kernel_client:
                self.kernel_client.stop_channels()
            if self.kernel_manager:
                self.kernel_manager.shutdown_kernel()
            self.kernel_ready = False
            print("🛑 Kernel stopped")
        except Exception as e:
            print(f"Error stopping kernel: {e}")
    
    def restart_kernel(self) -> None:
        """Restart the kernel and reset execution state"""
        print("🔄 Restarting kernel...")
        self.stop_kernel()
        self.execution_count = 0
        
        # Clear all execution counts and outputs
        for cell in self.notebook_data.get('cells', []):
            if cell.get('cell_type') == 'code':
                cell['execution_count'] = None
                cell['outputs'] = []
        
        self.save_notebook()
        self.start_kernel()
        self._trigger_visual_update()
    
    def _update_cell_id_map(self) -> None:
        self.cell_id_map = {}
        for idx, cell in enumerate(self.notebook_data.get('cells', [])):
            cell_id = cell.get('id')
            if not cell_id:
                cell_id = str(uuid.uuid4())
                cell['id'] = cell_id
            self.cell_id_map[cell_id] = idx
    
    def _generate_cell_id(self) -> str:
        return str(uuid.uuid4())
    
    def insert_cell(self, cell_type: str, source: str, 
                   index: Optional[int] = None, cell_id: Optional[str] = None) -> str:
        if cell_id is None:
            cell_id = self._generate_cell_id()
        
        cell = {
            "id": cell_id,
            "cell_type": cell_type,
            "metadata": {},
            "source": source.split('\n') if isinstance(source, str) else source
        }
        
        if cell_type == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
        
        if index is None:
            self.notebook_data["cells"].append(cell)
        else:
            self.notebook_data["cells"].insert(index, cell)
        
        self._update_cell_id_map()
        self.save_notebook()
        self._trigger_visual_update()
        
        print(f"Inserted {cell_type} cell with ID: {cell_id}")
        return cell_id
    
    def delete_cell(self, cell_id: str) -> bool:
        if cell_id not in self.cell_id_map:
            print(f"Cell ID {cell_id} not found")
            return False
        
        index = self.cell_id_map[cell_id]
        self.notebook_data["cells"].pop(index)
        self._update_cell_id_map()
        self.save_notebook()
        self._trigger_visual_update()
        
        print(f"Deleted cell: {cell_id}")
        return True
    
    def delete_cell_by_index(self, index: int) -> bool:
        if 0 <= index < len(self.notebook_data["cells"]):
            deleted_cell = self.notebook_data["cells"].pop(index)
            self._update_cell_id_map()
            self.save_notebook()
            self._trigger_visual_update()
            print(f"Deleted cell at index: {index}")
            return True
        else:
            print(f"Invalid index: {index}")
            return False
    
    def get_cell(self, cell_id: str) -> Optional[Dict]:
        if cell_id not in self.cell_id_map:
            return None
        index = self.cell_id_map[cell_id]
        return self.notebook_data["cells"][index]
    
    def get_cell_by_index(self, index: int) -> Optional[Dict]:
        if 0 <= index < len(self.notebook_data["cells"]):
            return self.notebook_data["cells"][index]
        return None
    
    def update_cell_source(self, cell_id: str, source: str) -> bool:
        cell = self.get_cell(cell_id)
        if cell:
            cell["source"] = source.split('\n') if isinstance(source, str) else source
            self.save_notebook()
            self._trigger_visual_update()
            print(f"Updated cell source: {cell_id}")
            return True
        return False
    
    def move_cell(self, cell_id: str, new_index: int) -> bool:
        if cell_id not in self.cell_id_map:
            print(f"Cell ID {cell_id} not found")
            return False
        
        old_index = self.cell_id_map[cell_id]
        cell = self.notebook_data["cells"].pop(old_index)
        self.notebook_data["cells"].insert(new_index, cell)
        
        self._update_cell_id_map()
        self.save_notebook()
        self._trigger_visual_update()
        
        print(f"Moved cell {cell_id} from index {old_index} to {new_index}")
        return True
    
    def run_cell(self, cell_id: str, timeout: int = 30) -> Dict:
        """Execute a cell using the persistent kernel"""
        if not self.kernel_ready:
            return {"success": False, "error": "Kernel not ready"}
        
        cell = self.get_cell(cell_id)
        if not cell or cell["cell_type"] != "code":
            return {"success": False, "error": "Invalid cell or not a code cell"}
        
        source = '\n'.join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
        
        if not source.strip():
            return {"success": True, "output": "", "error": ""}
        
        try:
            # Execute the code
            msg_id = self.kernel_client.execute(source, silent=False, store_history=True)
            
            # Wait for the execute_reply message to get execution status
            try:
                reply = self.kernel_client.get_shell_msg(timeout=timeout)
                if reply['parent_header'].get('msg_id') != msg_id:
                    return {"success": False, "error": "Message ID mismatch"}
                
                # Check if execution was successful
                success = reply['content']['status'] == 'ok'
                
                if not success:
                    error_info = reply['content']
                    return {
                        "success": False,
                        "error": f"{error_info.get('ename', 'Error')}: {error_info.get('evalue', 'Unknown error')}",
                        "execution_count": None
                    }
                
            except Exception as e:
                return {"success": False, "error": f"Execution failed: {str(e)}"}
            
            # Collect outputs from iopub channel
            outputs = []
            stdout_text = ""
            stderr_text = ""
            
            # Get all iopub messages related to this execution
            start_time = time.time()
            while time.time() - start_time < min(timeout, 5):  # Max 5 seconds for output collection
                try:
                    msg = self.kernel_client.get_iopub_msg(timeout=0.1)
                    
                    if msg['parent_header'].get('msg_id') == msg_id:
                        msg_type = msg['header']['msg_type']
                        content = msg['content']
                        
                        if msg_type == 'stream':
                            if content['name'] == 'stdout':
                                stdout_text += content['text']
                            elif content['name'] == 'stderr':
                                stderr_text += content['text']
                        
                        elif msg_type == 'execute_result':
                            outputs.append({
                                'output_type': 'execute_result',
                                'execution_count': content['execution_count'],
                                'data': content['data'],
                                'metadata': content.get('metadata', {})
                            })
                        
                        elif msg_type == 'display_data':
                            outputs.append({
                                'output_type': 'display_data',
                                'data': content['data'],
                                'metadata': content.get('metadata', {})
                            })
                        
                        elif msg_type == 'error':
                            outputs.append({
                                'output_type': 'error',
                                'ename': content['ename'],
                                'evalue': content['evalue'],
                                'traceback': content['traceback']
                            })
                            stderr_text += '\n'.join(content['traceback'])
                        
                        elif msg_type == 'status' and content.get('execution_state') == 'idle':
                            # Kernel is idle, execution is complete
                            break
                
                except queue.Empty:
                    # No more messages, execution likely complete
                    break
                except Exception:
                    # Ignore message parsing errors
                    continue
            
            # Update execution count
            self.execution_count += 1
            execution_count = self.execution_count
            
            # Add stream outputs
            if stdout_text:
                outputs.append({
                    'output_type': 'stream',
                    'name': 'stdout',
                    'text': stdout_text
                })
            
            if stderr_text:
                outputs.append({
                    'output_type': 'stream',
                    'name': 'stderr',
                    'text': stderr_text
                })
            
            # Update cell with results
            cell['execution_count'] = execution_count
            cell['outputs'] = outputs
            
            self.save_notebook()
            self._trigger_visual_update()
            
            return {
                'success': success,
                'output': stdout_text,
                'error': stderr_text,
                'execution_count': execution_count,
                'outputs': outputs
            }
        
        except Exception as e:
            return {"success": False, "error": f"Execution failed: {str(e)}"}
    
    def run_cells(self, cell_ids: List[str], timeout: int = 30) -> List[Dict]:
        """Run multiple cells in sequence, maintaining state"""
        results = []
        for cell_id in cell_ids:
            print(f"Running cell: {cell_id}")
            result = self.run_cell(cell_id, timeout)
            results.append({"cell_id": cell_id, **result})
            if not result["success"]:
                print(f"Stopping execution due to error in cell: {cell_id}")
                break
        return results
    
    def run_all_cells(self, timeout: int = 30) -> List[Dict]:
        """Run all code cells in the notebook"""
        cell_ids = [cell["id"] for cell in self.notebook_data["cells"] 
                   if cell["cell_type"] == "code"]
        return self.run_cells(cell_ids, timeout)
    
    def run_cells_from_index(self, start_index: int, end_index: Optional[int] = None, 
                           timeout: int = 30) -> List[Dict]:
        """Run cells from a specific index range"""
        if end_index is None:
            end_index = len(self.notebook_data["cells"]) - 1
        
        cell_ids = []
        for i in range(start_index, min(end_index + 1, len(self.notebook_data["cells"]))):
            cell = self.notebook_data["cells"][i]
            if cell["cell_type"] == "code":
                cell_ids.append(cell["id"])
        
        return self.run_cells(cell_ids, timeout)
    
    def clear_cell_output(self, cell_id: str) -> bool:
        """Clear output of a specific cell"""
        cell = self.get_cell(cell_id)
        if cell and cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
            self.save_notebook()
            self._trigger_visual_update()
            return True
        return False
    
    def clear_all_outputs(self) -> None:
        """Clear all cell outputs"""
        for cell in self.notebook_data["cells"]:
            if cell["cell_type"] == "code":
                cell["outputs"] = []
                cell["execution_count"] = None
        self.save_notebook()
        self._trigger_visual_update()
        print("Cleared all outputs")
    
    def interrupt_kernel(self) -> None:
        """Interrupt the currently running kernel"""
        if self.kernel_ready and self.kernel_manager:
            self.kernel_manager.interrupt_kernel()
            print("⚡ Kernel interrupted")
    
    def get_kernel_info(self) -> Dict:
        """Get information about the kernel"""
        if not self.kernel_ready:
            return {"status": "not_ready", "kernel_id": None}
        
        # Get kernel ID safely
        kernel_id = None
        try:
            if self.kernel_manager and hasattr(self.kernel_manager, 'kernel_id'):
                kernel_id = self.kernel_manager.kernel_id
            elif self.kernel_manager and hasattr(self.kernel_manager, 'get_kernel_id'):
                kernel_id = self.kernel_manager.get_kernel_id()
        except Exception:
            pass  # Ignore errors getting kernel ID
        
        return {
            "status": "ready",
            "kernel_id": kernel_id,
            "execution_count": self.execution_count
        }
    
    def get_cell_count(self) -> int:
        return len(self.notebook_data["cells"])
    
    def get_cell_ids(self) -> List[str]:
        return list(self.cell_id_map.keys())
    
    def get_code_cell_ids(self) -> List[str]:
        return [cell["id"] for cell in self.notebook_data["cells"] 
                if cell["cell_type"] == "code"]
    
    def get_cell_id_to_source_map(self) -> Dict[str, str]:
        """Return a mapping of cell IDs to their source content"""
        return {
            cell["id"]: '\n'.join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
            for cell in self.notebook_data["cells"]
        }
    
    def duplicate_cell(self, cell_id: str) -> Optional[str]:
        cell = self.get_cell(cell_id)
        if not cell:
            return None
        
        new_cell_id = self._generate_cell_id()
        new_cell = cell.copy()
        new_cell["id"] = new_cell_id
        
        if new_cell["cell_type"] == "code":
            new_cell["execution_count"] = None
            new_cell["outputs"] = []
        
        index = self.cell_id_map[cell_id]
        self.notebook_data["cells"].insert(index + 1, new_cell)
        
        self._update_cell_id_map()
        self.save_notebook()
        self._trigger_visual_update()
        
        print(f"Duplicated cell {cell_id} as {new_cell_id}")
        return new_cell_id
    
    def set_cell_metadata(self, cell_id: str, metadata: Dict) -> bool:
        cell = self.get_cell(cell_id)
        if cell:
            cell["metadata"] = metadata
            self.save_notebook()
            self._trigger_visual_update()
            return True
        return False
    
    def get_notebook_metadata(self) -> Dict:
        return self.notebook_data.get("metadata", {})
    
    def set_notebook_metadata(self, metadata: Dict) -> None:
        self.notebook_data["metadata"] = metadata
        self.save_notebook()
        self._trigger_visual_update()
    
    def _trigger_visual_update(self) -> None:
        print(f"📓 Notebook updated: {self.notebook_path}")
    
    def export_to_format(self, format_type: str, output_path: Optional[str] = None) -> bool:
        if output_path is None:
            base_name = os.path.splitext(self.notebook_path)[0]
            output_path = f"{base_name}.{format_type}"
        
        try:
            subprocess.run([
                "jupyter", "nbconvert", 
                f"--to={format_type}",
                f"--output={output_path}",
                self.notebook_path
            ], check=True)
            print(f"Exported to {format_type}: {output_path}")
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def get_notebook_info(self) -> Dict:
        cells = self.notebook_data["cells"]
        code_cells = [c for c in cells if c["cell_type"] == "code"]
        markdown_cells = [c for c in cells if c["cell_type"] == "markdown"]
        
        kernel_info = self.get_kernel_info()
        
        return {
            "path": self.notebook_path,
            "total_cells": len(cells),
            "code_cells": len(code_cells),
            "markdown_cells": len(markdown_cells),
            "executed_cells": len([c for c in code_cells if c.get("execution_count")]),
            "nbformat": self.notebook_data.get("nbformat", "Unknown"),
            "kernel": self.notebook_data.get("metadata", {}).get("kernelspec", {}).get("name", "Unknown"),
            "kernel_status": kernel_info["status"],
            "execution_count": self.execution_count
        }
    
    def __del__(self):
        """Cleanup kernel when object is destroyed"""
        if hasattr(self, 'kernel_ready') and self.kernel_ready:
            self.stop_kernel()
    
    def __str__(self) -> str:
        info = self.get_notebook_info()
        return f"NotebookController(path='{info['path']}', cells={info['total_cells']}, kernel={info['kernel_status']})"
    
    def __repr__(self) -> str:
        return self.__str__()