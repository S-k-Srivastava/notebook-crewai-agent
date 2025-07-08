# 📓 notebook-crewai-agent

**[notebook-crewai-agent](https://github.com/S-k-Srivastava/notebook-crewai-agent.git)** is an AI-powered EDA agent built with [CrewAI](https://github.com/joaomdmoura/crewAI), enhanced by fully-programmable **Jupyter Notebook tools**. This lets LLMs directly create, update, run, and control notebooks as part of an intelligent data analysis pipeline.

---

## 🚀 Key Features

* 🤖 **LLM-driven autonomous agent** that performs:

  * Data cleaning and missing value treatment
  * Feature engineering and selection
  * EDA (Exploratory Data Analysis) with visualizations
  * Final model suggestions
* 🧰 **NotebookController** class to programmatically control notebooks:

  * Create, insert, update, delete cells
  * Run specific cells or run all
  * Restart or start the kernel
* 🔌 **Pluggable Notebook Tools** (`NOTEBOOK_TOOLS`) can be independently integrated into any AI pipeline or toolchain (CrewAI, LangChain, etc.).
* 🌍 **Supports all major LLMs** – including OpenAI, Claude, Gemini, Ollama, and other LangChain-compatible models.

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/S-k-Srivastava/notebook-crewai-agent.git
cd notebook-crewai-agent
```

### 2. Install dependencies using [`uv`](https://github.com/astral-sh/uv)

Make sure `uv` is installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then sync the environment:

```bash
uv sync
```

---

## 📚 Notebook Tools Overview

The core utility of this project is the **NotebookController**, a class that gives full control over Jupyter notebooks. It works both inside and outside CrewAI agents.

### 🔧 Available Methods:

* `create_notebook()`
* `insert_cell(content, position)`
* `update_cell(index, new_content)`
* `delete_cell(index)`
* `run_cell(index)`
* `run_all()`
* `start_kernel()`
* `restart_kernel()`

---

## 🧠 Agent Behavior Example

```python
from crewai import Agent, Task, Crew
from modules.notebook_tools_crewai import NOTEBOOK_TOOLS

agent = Agent(
    role="Data Analyst and Scientist",
    goal="Complete EDA and dataset preparation",
    tools=NOTEBOOK_TOOLS,
    ...
)
```

The agent uses natural language tasks to:

* Access notebook tools
* Insert markdown/code cells
* Clean and transform data
* Visualize results
* Suggest ML models

---

## 🧪 Ideal Use Cases

* Jupyter notebook automation via AI
* AutoEDA and dataset preparation tools
* RAG or LangChain-based notebook agents
* LLM + notebook orchestration pipelines
* EDA-as-a-Service

---

## 📄 License

MIT © 2025 [Saurav Srivastava](https://sksrivastava.in)
