import os
import json
from plantuml import PlantUML, PlantUMLHTTPError
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import ChatCompletions
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

from devops.devops_client import AzureDevOpsClient
from devops.work_items_service import WorkItemService
from context_service import ContextService
from schema import C4ContextArchitecture, C4ContainerArchitecture
from prompts import CONTEXT_SYSTEM_PROMPT, CONTEXT_USER_PROMPT, CONTAINER_SYSTEM_PROMPT, CONTAINER_USER_PROMPT

# Load environment variables
load_dotenv()

# Initialize LLM Client
LLM = ChatCompletionsClient(
    endpoint=os.environ.get("AZURE_AI_FOUNDRY_ENDPOINT"),
    credential=AzureKeyCredential(os.environ.get("AZURE_AI_FOUNDRY_KEY"))
)
MODEL = os.environ.get("MODEL_NAME")


# ==========================================
# 1. ORCHESTRATION FLOWS
# ==========================================

def run_flow(project: str):
    """
    End-to-End Pipeline: Fetches work items from Azure DevOps, generates context Markdown, 
    and uses a two-step LLM chain to generate and render C4 Level 1 and Level 2 diagrams.
    """
    # Initialize Azure DevOps Client
    client = AzureDevOpsClient(
        org_url=os.getenv('AZURE_DEVOPS_ORG_URL'),
        pat=os.getenv('AZURE_DEVOPS_PAT'),
        api_version=os.getenv('AZURE_DEVOPS_API_VERSION', '7.1')
    )
    
    # Initialize Service Layer
    wi_service = WorkItemService(client)
    context_service = ContextService(wi_service)

    run_dir = create_versioned_run_dir(project)
    print(f"Saving run outputs to: {run_dir}\n")

    os.makedirs('context_files', exist_ok=True)

    # Fetch and save Work Items (Context) as markdown
    print(f"Fetching context for project: {project}")
    markdown_result = context_service.fetch_project_context(project)
    
    context_file_path = f"context_files/{project}_context.md"
    with open(context_file_path, "w", encoding="utf-8") as f: 
        f.write(markdown_result)
    print(f"Saved Markdown context to {context_file_path}\n")

    # Execute LLM Chain
    _execute_llm_chain(project, markdown_result, run_dir)


def run_flow_from_local_file(project: str):
    """
    Offline Pipeline: Skips Azure DevOps extraction and runs the LLM generation 
    and diagram rendering based on an existing local Markdown context file.
    """
    print(f"Loading local context for project: {project}")
    run_dir = create_versioned_run_dir(project)
    print(f"Saving run outputs to: {run_dir}\n")

    context_file_path = f"context_files/{project}_context.md"
    try:
        with open(context_file_path, "r", encoding="utf-8") as f: 
            markdown_result = f.read()
        print("Successfully retrieved local Markdown context.\n")
    except FileNotFoundError:
        print(f"Error: Could not find {context_file_path}. Please run 'run_flow' first.")
        return

    # Execute LLM Chain
    _execute_llm_chain(project, markdown_result, run_dir)


def _execute_llm_chain(project: str, markdown_result: str, run_dir: str):
    """Internal helper to execute the two-step LLM prompting and rendering process."""
    
    # --- LLM 1: C4 System Context ---
    print("LLM 1 - Generating System Context (Level 1)...")
    context_response = LLM.complete(
        messages=[
            {"role": "system", "content": CONTEXT_SYSTEM_PROMPT},
            {"role": "user", "content": f"{markdown_result} \n\n {CONTEXT_USER_PROMPT}"}
        ],
        model=MODEL,
        response_format="json_object",
        temperature=0.01,
        seed=42
    )

    # Parse and Validate Context Response
    context_json = json.loads(context_response.choices[0].message.content)
    try:
        context_architecture = C4ContextArchitecture.model_validate(context_json)
        print(f"Validated LLM 1 Context Diagram: {context_architecture.title}")
    except Exception as e:
        print(f"LLM 1 Validation Error: {e}")
        return

    # Save and Render Context
    save_raw_response(run_dir=run_dir, filename=f"{project}_context_draft", data=context_json)
    context_puml = convert_context_to_puml(project=project, data=context_json)
    save_and_render(run_dir=run_dir, puml_code=context_puml, filename=f"{project}_context_draft")


    # --- LLM 2: C4 Container ---
    print("\nLLM 2 - Generating Container Architecture (Level 2)...")
    level_1_context_str = json.dumps(context_json, indent=2)
    container_response = LLM.complete(
        messages=[
            {"role": "system", "content": CONTAINER_SYSTEM_PROMPT},
            {"role": "user", "content": f"{markdown_result} \n\n ### LEVEL 1 CONTEXT:\n{level_1_context_str} \n\n {CONTAINER_USER_PROMPT}"}
        ],
        model=MODEL,
        response_format="json_object",
        temperature=0.01,
        seed=42
    )

    # Parse and Validate Container Response
    container_json = json.loads(container_response.choices[0].message.content)
    try:
        container_architecture = C4ContainerArchitecture.model_validate(container_json)
        print(f"Validated LLM 2 Container Diagram: {container_architecture.title}")
    except Exception as e:
        print(f"LLM 2 Validation Error: {e}")
        return
    
    # Save and Render Container
    save_raw_response(run_dir=run_dir, filename=f"{project}_container_draft", data=container_json)
    container_puml = convert_container_to_puml(project=project, context_data=context_json, container_data=container_json)
    save_and_render(run_dir=run_dir, puml_code=container_puml, filename=f"{project}_container_draft")


# ==========================================
# 2. PLANTUML CONVERTERS
# ==========================================

def convert_context_to_puml(project: str, data: dict) -> str:
    """
    Converts the JSON structure into valid C4 PlantUML syntax with boundaries.
    """
    title = data.get('title', f'{project} C4 Context Diagram')
    lines = [
        "@startuml",
        "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml",
        f"title {title}",
        "LAYOUT_WITH_LEGEND()"
    ]

    for el in data.get('elements', []):
        el_id = el['id']
        name = el['name'].replace('–', '-').replace('—', '-')
        desc = el['description'].replace('–', '-').replace('—', '-')
        el_type = el['type']        # "Person" or "Software System"
        boundary = el['boundary']   # "Internal" or "External"
        linked_items = el.get('linked_work_items', [])

        # Logic to determine C4 Macro
        macro = "System" # Default

        if el_type == "Person":
            macro = "Person_Ext" if boundary == "External" else "Person"
        elif el_type == "Software System":
            macro = "System_Ext" if boundary == "External" else "System"

        if linked_items:
            refs_str = ", ".join(linked_items)
            desc += f"\\n<size:10><color:gray>Ref: {refs_str}</color></size>"

        lines.append(f'{macro}({el_id}, "{name}", "{desc}")')

    lines.append("")

    for rel in data.get('relationships', []):
        src = rel.get('source')
        tgt = rel.get('target')
        label = rel.get('label')
        tech = (rel.get('technology') or "").replace('–', '-').replace('—', '-')

        if tech:
            lines.append(f'Rel({src}, {tgt}, "{label}", "{tech}")')
        else:
            lines.append(f'Rel({src}, {tgt}, "{label}")')

    lines.append("@enduml")
    return "\n".join(lines)


def convert_container_to_puml(project: str, context_data: dict, container_data: dict) -> str:
    """
    Merges Level 1 externals with Level 2 internals.
    Uses System_Boundary to group containers.
    """
    title = container_data.get('title', f'{project} Container Diagram')
    lines = [
        "@startuml",
        "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml",
        f"title {title}",
        "SHOW_PERSON_OUTLINE()",
        "LAYOUT_WITH_LEGEND()"
    ]

    # 1. DRAW EXTERNAL ELEMENTS (From Context JSON)
    system_boundary_id = "system_boundary" 
    system_boundary_name = "System"
    
    for el in context_data.get('elements', []):
        if el['boundary'] == 'External':
            macro = "Person_Ext" if el['type'] == "Person" else "System_Ext"
            lines.append(f'{macro}({el["id"]}, "{el["name"].replace("–", "-").replace("—", "-")}", "{el["description"].replace("–", "-").replace("—", "-")}")')
        else:
            if el.get('type') == "Person":
                lines.append(f'Person({el["id"]}, "{el["name"].replace("–", "-").replace("—", "-")}", "{el["description"].replace("–", "-").replace("—", "-")}")')
            else:
                # Found the System Under Design
                system_boundary_id = el['id']
                system_boundary_name = el['name']

    lines.append("")

    # 2. DRAW SYSTEM BOUNDARY (Wrapping Internal Containers)
    lines.append(f'System_Boundary({system_boundary_id}, "{system_boundary_name}") {{')

    # 3. Draw Containers (from Container L2)
    for cont in container_data.get('containers', []):
        c_id = cont['id']
        name = cont['name'].replace('–', '-').replace('—', '-')
        tech = cont['technology'].replace('–', '-').replace('—', '-')
        desc = cont['description'].replace('–', '-').replace('—', '-')
        c_type = cont['type']
        linked_items = cont.get('linked_work_items', [])

        if linked_items:
            refs_str = ", ".join(linked_items)
            desc += f"\\n<size:10><color:gray>Ref: {refs_str}</color></size>"

        macro = "ContainerDb" if c_type == "Database" else "Container"
        lines.append(f'    {macro}({c_id}, "{name}", "{tech}", "{desc}")')
    
    lines.append("}") # End Boundary
    lines.append("")

    # 4. Draw Relationships (from Container L2)
    for rel in container_data.get('relationships', []):
        src = rel['source']
        tgt = rel['target']
        label = rel['label']
        tech = (rel.get('technology') or "").replace('–', '-').replace('—', '-')

        if tech:
            lines.append(f'Rel({src}, {tgt}, "{label}", "{tech}")')
        else:
            lines.append(f'Rel({src}, {tgt}, "{label}")')

    lines.append("@enduml")
    return "\n".join(lines)


# ==========================================
# 3. UTILITIES & I/O
# ==========================================

def save_and_render(run_dir: str, puml_code: str, filename: str):
    """
    Saves the .puml file and renders a PNG via local PlantUML server.
    """
    file_path = os.path.join(run_dir, f"{filename}.puml").replace('\\', '/')
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(puml_code)

    server = PlantUML(url='http://localhost:8080/png/')
    try:
        server.processes_file(file_path)
        print(f"  -> Rendered PNG diagram to {run_dir}")
    except PlantUMLHTTPError as e:
        print(f"Failed to render PNG. PlantUML server returned an error.")
        print("Status:", getattr(e, "response", None))
        raise


def save_raw_response(run_dir: str, filename: str, data: dict):
    """
    Saves the raw architecture JSON for debugging and reproducibility.
    """
    file_path = os.path.join(run_dir, f"{filename}.json").replace('\\', '/')
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  -> Saved raw JSON architecture to {file_path}")


def create_versioned_run_dir(project: str) -> str:
    """
    Creates a sequentially numbered subfolder (e.g., 'run 1') under runs/{project}/.
    """
    base_dir = f"runs/{project}"
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    counter = 1
    while True:
        run_dir = os.path.join(base_dir, f"run {counter}").replace('\\', '/')
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)
            return run_dir
        counter += 1