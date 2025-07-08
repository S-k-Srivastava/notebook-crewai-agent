# 🔍 EDA Agent with Jupyter Notebook Tools and LLM Support

This project is an **autonomous AI-powered EDA (Exploratory Data Analysis) agent** built using the [CrewAI](https://github.com/joaomdmoura/crewAI) framework and enhanced with **powerful Jupyter Notebook tools**. It allows seamless, automated analysis of datasets using state-of-the-art LLMs and notebook control capabilities.

## 🚀 Features

* ✅ **AI-powered Data Analysis Agent** using LLMs.
* 🧠 Automatically performs:

  * Missing value treatment
  * Feature selection & engineering
  * EDA visualizations
  * Model suggestions
* 📓 **NotebookController** class provides full programmatic control over Jupyter notebooks:

  * Create, insert, update, delete code or markdown cells
  * Run individual cells or all cells
  * Restart/start the kernel
* 🧰 **Modular Notebook Tools** (`NOTEBOOK_TOOLS`) are decoupled and can be reused independently in any AI/LLM-driven pipeline.
* 🌐 **Supports all major LLMs** (e.g., OpenAI, Gemini, Claude, local models via Ollama etc.)

## 📦 Quick Start

```bash
git clone https://github.com/yourname/eda-agent-notebook.git
cd eda-agent-notebook
pip install -r requirements.txt
python main.py
```

## 🧠 Agent Description

The `Data Analyst and Scientist` agent is designed to:

* Understand and execute data analysis tasks based on natural language instructions.
* Interact with notebook tools to perform real-time edits, code insertions, and run operations.
* Prepare a final cleaned dataset with rich visualizations and model recommendations.

## 🛠️ Notebook Tools (Plug & Play)

The core utility powering the agent is the **NotebookController**—a class that can be used anywhere (inside or outside CrewAI), giving you full access to:

* `create_notebook()`
* `insert_cell(content, position)`
* `run_cell(index)`, `run_all()`
* `delete_cell(index)`, `update_cell(index, new_content)`
* `start_kernel()`, `restart_kernel()`

These tools are bundled as `NOTEBOOK_TOOLS` and can be plugged into any CrewAI agent, LangChain tool, or custom workflow.

---

## 🧪 Example Usage (via CrewAI)

```python
from crewai import Agent, Task, Crew
from modules.notebook_tools_crewai import NOTEBOOK_TOOLS

agent = Agent(
    role="Data Analyst and Scientist",
    goal="Perform complete EDA and prepare dataset for ML",
    tools=NOTEBOOK_TOOLS,
    ...
)
```

---

## 🤖 LLM-Agnostic

This framework is designed to be **LLM-agnostic**. You can use any LLM backend:

* OpenAI GPT
* Claude
* Gemini
* Ollama / Local models
* LangChain-compatible APIs

---

## 📊 Ideal For

* AI-based notebook automation
* LLM + Jupyter workflows
* EDA-as-a-service apps
* AutoML or data prep pipelines
* MLOps notebooks orchestration

---

## 📄 License

MIT © 2025
