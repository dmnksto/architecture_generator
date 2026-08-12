# Architecture Generator

This repository contains the code for the Paper:

> **Recovering Software Architecture Intent from Historical Work Items using Generative AI: A Mixed-Methods Industry Case Study**  
> Author: Dominik Storck, Tobias Eisenreich, Stefan Wagner  
> Institution: Technical University Munich (TUM)  
> Industry Partner: Anonymous  

The project implements an end-to-end pipeline that:

1. Extracts work items (Epics, Features, User Stories, Tasks) from Azure DevOps.
2. Converts them into a structured Markdown “project context”.
3. Employs a two-step LLM prompting workflow to generate:
   - a **C4 System Context** model (Level 1), and
   - a **C4 Container** model (Level 2).
4. Renders the resulting diagrams with PlantUML using [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML).

---

## 1. Architecture Overview

At a high level, the pipeline consists of:

*   **Azure DevOps client & services** (`devops/`):
    *   Fetches work items via WIQL and REST APIs.
    *   Thins and normalizes work item data (fields, relations, comments).
*   **Context builder** (`ContextService`):
    *   Converts hydrated work items into a structured Markdown document optimized for LLM input.
*   **LLM layer** (`flow.py`, `prompts.py`):
    *   Calls an Azure AI / Azure OpenAI deployment using structured prompts.
    *   First call: Generates C4 **System Context** JSON.
    *   Second call: Generates C4 **Container** JSON.
*   **Diagram renderer** (`flow.py`):
    *   Converts the JSON structures to C4-PlantUML `.puml`.
    *   Renders diagrams via a local PlantUML server.

---

## 2. How to Run the Pipeline

### 2.1. Prerequisites

*   Python 3.10+
*   Docker (for running a local PlantUML server)
*   Access to:
    *   An Azure DevOps organization/project with work items
    *   An Azure AI / Azure OpenAI deployment (chat completions model)

### 2.2. Run a local PlantUML server (via Docker)

Before executing the pipeline, you need a local PlantUML instance running.

1. Install [Docker](https://www.docker.com/).
2. Open your terminal and start the server:

```bash
docker pull plantuml/plantuml-server
docker run -d -p 8080:8080 --name plantuml plantuml/plantuml-server
```

The server will now listen at `http://localhost:8080`.  
*(Reference: [Docker Hub - plantuml-server](https://hub.docker.com/r/plantuml/plantuml-server/))*

The Python code natively expects this local server:

```python
PlantUML(url="http://localhost:8080/png/")
```

*(You can adjust this URL in `flow.py` if needed).*

### 2.3. Clone and set up a virtual environment

```bash
git clone [https://github.com/dmnksto/Architecture_Generator.git](https://github.com/dmnksto/Architecture_Generator.git)
cd Architecture_Generator

python -m venv .venv
# Windows:
.venv/Scripts/activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```
*(Adjust to your actual dependency file if using `pyproject.toml` or similar.)*

### 2.4. Configure environment variables

Create a `.env` file (or otherwise set environment variables) with:

```env
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/<your-org>
AZURE_DEVOPS_PAT=<your-personal-access-token>

AZURE_DEVOPS_API_VERSION=7.1
AZURE_DEVOPS_API_VERSION_COMMENTS=7.1-preview

AZURE_AI_FOUNDRY_ENDPOINT=<your-azure-ai-endpoint>
AZURE_AI_FOUNDRY_KEY=<your-azure-ai-key>
MODEL_NAME=<your-model-name>  # e.g., "gpt-5.1"
```

### 2.5. Configure the project to analyze

In `main.py`, set the Azure DevOps project name you want to process.
**Note:** `project` must match the `System.TeamProject` name in Azure DevOps.


### 2.6. Execute the pipeline

With the virtual environment activated and Docker running:

```bash
python app/main.py
```

The pipeline will:

1.  Fetch work items from Azure DevOps.
2.  Generate a Markdown context file under `context_files/<project>_context.md`.
3.  Call the LLM twice to produce C4 Context and Container JSON.
4.  Save raw JSON and render diagrams into a new run directory under `runs/<project>/run X/`.

---

## 3. Omitted Data and Artifacts

This repository contains the full implementation of the semi-automatic C4 architecture generation pipeline. However, it **does not** contain any real project data from the industry partner. *(All visible examples in the code rely on Simon Brown's public "Big Bank plc" example).*

For confidentiality and security reasons, the following artifacts used during the thesis are **intentionally omitted**:

*   **Raw requirement context files** generated from Azure DevOps work items (e.g., `context_files/<project>_context.md`).
*   **Generated run artifacts** (JSON, PlantUML, PNG diagrams) under `runs/`.
*   **Evaluation- and thesis-only artifacts**, such as detailed evaluation datasets and plotting scripts for individual thesis figures, which are not required to run the core pipeline. Only the anonymized Interview Guide used for the semi-structured interviews of the qualitative evaluation phase is included and can be found under `interview_guide.pdf`.

These omissions do not affect the reproducibility of the core method: all necessary source code and prompt definitions are included. To run the pipeline, you must simply provide your own Azure DevOps project and credentials.

---

## 4. Relation to the Paper

This repository is the **companion implementation** to the paper:

> **Recovering Software Architecture Intent from Historical Work Items using Generative AI: A Mixed-Methods Industry Case Study**

The paper:

*   Describes the design of the pipeline and prompt engineering techniques in detail.
*   Evaluates the quality of the generated C4 diagrams on real-world projects (data not included here).
*   Discusses limitations and potential improvements.

---

## 5. License & Acknowledgments

*   The source code of this project is licensed under the **MIT License**. See the `LICENSE` file for details.

*   **C4-PlantUML:** Diagram rendering relies on [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML), which is distributed under the MIT License.
*   **C4 Model Examples:** The prompt examples and reference JSON structures used in this project are adapted from the ["Big Bank plc – Internet Banking System"](https://c4model.com) example created by Simon Brown. 
    *   Original work by Simon Brown is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). 
    *   **Modifications:** The original visual/textual models were transformed and adapted into structured JSON formats to serve as few-shot example in prompts for Large Language Models.
