import os
from devops.work_items_service import WorkItemService

class ContextService:
    """
    Service responsible for orchestrating the extraction of Azure DevOps work items
    and transforming them into an LLM-optimized Markdown context document.
    """

    def __init__(self, work_item_service: WorkItemService):
        self.wi_service = work_item_service
        self.comment_api_version = os.getenv('AZURE_DEVOPS_API_VERSION_COMMENTS', '7.1-preview')
    
    def _to_markdown(self, project: str, data: dict) -> str:
        """
        Converts hydrated work items into a structured Markdown document.
        """
        items = data.get("value", [])
        total_count = len(items)

        if not items:
            return "# No Work Items Found"
        
        # Calculate counts per type for the summary
        type_counts = {}
        for wi_type in ["Epic", "Feature", "User Story", "Task"]:
            type_counts[wi_type] = len([i for i in items if i.get("type") == wi_type])

        # Create Header with Metadata
        md = f"# Project Architecture Context\n"
        md += f"**Project:** {project}\n\n"
        md += f"**Total Items Processed:** {total_count}\n"
        for t, c in type_counts.items():
            if c > 0:
                md += f"- **{t}s:** {c}\n"
        md += "---\n\n"

        # Group by type for better LLM hierarchy understanding
        for wi_type in ["Epic", "Feature", "User Story", "Task"]:
            typed_items = [i for i in items if i.get("type") == wi_type]
            if not typed_items:
                continue

            md += f"## {wi_type}s\n"
            for item in typed_items:
                md += f"### [{item.get('id')}] {item.get('title')}\n"

                # 1. Dynamically add all metadata fields EXCEPT large blocks
                exclude_from_bullets = ['id', 'title', 'type', 'description', 'relations', 'comments', 'acceptanceCriteria']
                for key, value in item.items():
                    if key not in exclude_from_bullets and value:
                        md += f"- **{key}:** {value}\n"
                
                # 2. Add description
                md += f"- **Description:** {item.get('description', '')}\n"
                
                # 3. Add Acceptance Criteria if available
                ac = item.get("acceptanceCriteria", "")
                if ac and ac != "No description provided.":
                    md += f"- **Acceptance Criteria:** {ac}\n"

                # 4. Format relations (Parents/Children)
                rels = item.get("relations", [])
                if rels:
                    related_ids = [f"#{r['id']} ({r['rel'].split('.')[-1]})" for r in rels]
                    md += f"- **Related Items:** {', '.join(related_ids)}\n"
                
                # 5. Add Comments
                comments = item.get("comments", [])
                if comments:
                    md += "- **Comments:**\n"
                    for c in comments:
                        text = c.get('text', '')
                        md += f"  - {text}\n"
                
                md += "\n"
        
        return md
    
    def fetch_project_context(self, project: str):
        """
        Retrieves all relevant work items for architecture analysis.
        """
        # Query for Epics, Features, and User Stories, and Tasks
        wiql = f"""
        SELECT [System.Id] FROM workitems 
        WHERE [System.TeamProject] = '{project}' 
        AND [System.WorkItemType] IN ('Epic', 'Feature', 'User Story', 'Task')
        AND [System.State] <> 'Removed'
        """
        try:
            data = self.wi_service.get_work_items_by_wiql(
                project=project, 
                wiql=wiql,
                top=None,
                comment_api_version=self.comment_api_version,
                include_relations=True,
                include_comments=True,
            )
            return self._to_markdown(project=project, data=data)
        except Exception as e:
            return {"error": f"WIQL or hydration error: {str(e)}"}