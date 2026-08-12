from flow import run_flow, run_flow_from_local_file

# ==========================================
# CONFIGURATION
# ==========================================
# Enter your Azure DevOps System.TeamProject name here.
# NOTE: This must match the exact case-sensitive project name in Azure.
PROJECT = "YourProject"

def main():
    """
    Main entry point for the Architecture Generator pipeline.
    Uncomment the execution mode you wish to use below.
    """
    
    # ---------------------------------------------------------
    # MODE 1: FULL PIPELINE (Azure DevOps Extraction -> LLM -> PlantUML)
    # Requires .env configuration and Azure credentials.
    # ---------------------------------------------------------
    run_flow(PROJECT)

    # ---------------------------------------------------------
    # MODE 2: LOCAL EVALUATION MODE (Local Markdown -> LLM -> PlantUML)
    # Skips Azure DevOps and reads directly from context_files/{PROJECT}_context.md.
    # Requires .env configuration and Azure AI Foundry credentials.
    # ---------------------------------------------------------
    # run_flow_from_local_file(PROJECT)

if __name__ == "__main__":
    main()