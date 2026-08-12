from typing import List, Literal, Dict, Any, Optional
from .devops_client import AzureDevOpsClient

class WorkItemService:
    def __init__(self, client: AzureDevOpsClient):
        self.client = client
        # Fixed whitelist owned by the service
        self._field_whitelist: List[str] = [
            "System.Id",
            "System.WorkItemType",
            "System.State",
            "System.Title",
            "System.AssignedTo",
            "System.IterationPath",
            "System.AreaPath",
            "Microsoft.VSTS.Common.Priority",
            "System.CreatedDate",
            "System.ChangedDate",
            "System.CreatedBy",
            "System.ChangedBy",
            "System.Description",
            "Microsoft.VSTS.Common.AcceptanceCriteria",
            "System.Tags",
        ]


    def _fetch_comments(self,project: str, work_item_id: int, api_version: Optional[str]) -> Dict[str, Any]:
        """Fetch all comments in one large page; return thinned comments."""
        # Raw GET for comments (per ADO API)
        params = {"api-version": api_version or self.client.api_version}
        raw = self.client.request(project=project, area="wit", resource=f"workItems/{work_item_id}/comments", params=params)
        comments = raw.get("comments", []) or []
        # Thin each comment
        thin = []
        for c in comments:
            thin.append({
                "id": c.get("id"),
                "text": c.get("text"),
                "createdBy": (c.get("createdBy") or {}).get("displayName"),
                "createdDate": c.get("createdDate"),
            })
        return  thin
    
    def _prune(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Remove keys whose value is None, empty string, or empty list/dict."""
        pruned: Dict[str, Any] = {}
        for k, v in obj.items():
            if v is None:
                continue
            if isinstance(v, str) and v.strip() == "":
                continue
            if isinstance(v, (list, dict)) and len(v) == 0:
                continue
            pruned[k] = v
        return pruned

    def _thin_work_item(
        self,
        wi: Dict[str, Any],
        *,
        include_relations: bool,
        comments_map: Optional[Dict[int, List[Dict[str, Any]]]],
    ) -> Dict[str, Any]:
        f = wi.get("fields", {})
        wid = wi.get("id")

        out = {
            "id": wid,
            "type": f.get("System.WorkItemType"),
            #"state": f.get("System.State"),
            "title": f.get("System.Title"),
            #"assignedTo": (f.get("System.AssignedTo") or {}).get("displayName"),
            #"iterationPath": f.get("System.IterationPath"),
            #"areaPath": f.get("System.AreaPath"),
            "priority": f.get("Microsoft.VSTS.Common.Priority"),
            #"createdDate": f.get("System.CreatedDate"),
            #"changedDate": f.get("System.ChangedDate"),
            #"createdBy": (f.get("System.CreatedBy") or {}).get("displayName"),
            #"changedBy": (f.get("System.ChangedBy") or {}).get("displayName"),
            "description": f.get("System.Description"),
            "acceptanceCriteria": f.get("Microsoft.VSTS.Common.AcceptanceCriteria"),
            "tags": f.get("System.Tags")
        }

        if include_relations:
            out["relations"] = self._thin_relations(wi)

        if comments_map is not None:
            out["comments"] = comments_map.get(wi.get("id"), [])

        return self._prune(out)

    def _extract_related_id(self, url: str) -> Optional[int]:
        """Extract trailing work item id from relation url without regex."""
        if not isinstance(url, str):
            return None
        parts = url.rstrip("/").split("/")
        try:
            return int(parts[-1])
        except Exception:
            return None

    def _thin_relations(self, wi: Dict[str, Any]) -> List[Dict[str, Any]]:
        rels = wi.get("relations") or []
        out: List[Dict[str, Any]] = []
        for r in rels:
            url = r.get("url") or ""
            rid = self._extract_related_id(url)
            if rid is not None:
                out.append({"rel": r.get("rel"), "id": rid})
        return out

    def get_work_items_by_wiql(
        self,
        project: str,
        wiql: str,
        top: Optional[int] = 200,
        comment_api_version: Optional[str] = None,
        include_relations: bool = False,
        include_comments: bool = True,
    ) -> Dict[str, Any]:
        """
        Read-only helper that returns hydrated work items for a WIQL filter.
        Returns rich items incl. dates, description, acceptance criteria, tags.
        Optional: relations and all comments.
        """
        # 1) IDs via WIQL (client)
        ids = self.client.post_wiql(project=project, wiql=wiql, top=top)
        if not ids:
            return {"count": 0, "value": []}

        # 2) Hydrate via workitemsbatch (client)
        expand_final = "Relations" if include_relations else None
        fields_to_fetch = self._field_whitelist if not expand_final else None

        try:
            hydrated = self.client.hydrate_work_items(
                ids,
                fields=fields_to_fetch,
                expand=expand_final
            )
            items = hydrated.get("value", [])  # main list of hydrated work items

        except Exception as e:
            print(e)
            # 3) Fallback: GET with chunking (client)
            items: List[Dict[str, Any]] = []
            chunk_size = 200
            for i in range(0, len(ids), chunk_size):
                chunk = ids[i:i + chunk_size]
                params = {
                    "ids": ",".join(map(str, chunk)),
                    "fields": ",".join(self._field_whitelist)

                }  
                if expand_final:
                    params["$expand"] = expand_final

                page = self.client.request("wit", "workitems", params=params)
                items.extend(page.get("value", []))

        # 4) Comments (client), per item, only when requested
        comments_map: Optional[Dict[int, List[Dict[str, Any]]]] = None
        if include_comments:
            comments_map = {}
            for wid in ids:
                try:
                    comments_map[wid] = self._fetch_comments(project, wid, comment_api_version)
                except Exception as e:
                    print(f"ERROR fetching comments for {wid}: {e}")
                    comments_map[wid] = []
    
        # 5) Thin + prune
        value = [
            self._thin_work_item(
                wi,
                include_relations=include_relations,
                comments_map=comments_map,
            )
            for wi in items
        ]

        return {"count": len(value), "value": value}
        