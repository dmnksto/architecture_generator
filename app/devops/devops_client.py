import requests
from typing import Optional, Dict, Any, List, Literal
from msrest.authentication import BasicAuthentication

class AzureDevOpsClient:
    """
    A generic REST client for connecting to the Azure DevOps API.
    Handles authentication, dynamic endpoint generation, and basic paginators.
    """
    def __init__(self, org_url: str, pat: str, api_version: str = "7.1"):
        self.org_url = (org_url or "").rstrip("/")
        self.api_version = api_version

        # Create a signed requests.Session with Basic auth
        self.session: requests.Session = BasicAuthentication('', pat).signed_session()

        # Headers
        self.session.headers.update({
            "Accept": "application/json",
            # Suppresses 203 sign-in HTML redirects in some orgs
            "X-TFS-FedAuthRedirect": "Suppress"
        })

    
    def request(
        self,
        area: str,
        resource: str,
        *,
        project: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        use_vsrm: bool = False,
        api_version: Optional[str] = None,
        ) -> Dict[str, Any]:
        """
        Generic GET: builds URL and performs the request.
        Examples:
          - org-scoped:      area="projects", resource=""
          - project-scoped:  area="wit", resource="fields", project="MyProject"
        """

        if not self.org_url:
            raise ValueError("org_url is empty; check AZURE_DEVOPS_ORG_URL")

        params = dict(params or {})
        params.setdefault("api-version", api_version or self.api_version)

        base = self.org_url
        if use_vsrm:
            # Releases use vsrm.dev.azure.com (different subdomain)
            base = base.replace("dev.azure.com", "vsrm.dev.azure.com")

        area = (area or "").strip("/")
        resource = (resource or "").strip("/")

        def _join(*parts: str) -> str:
            return "/".join([p for p in parts if p])

        if project:
            # {org}/{project}/_apis/{area}/{resource}
            url = _join(base, project, "_apis", area, resource)
        else:
            # {org}/_apis/{area}/{resource}
            url = _join(base, "_apis", area, resource)


        resp = self.session.get(url, params=params, timeout=20)
        if not resp.ok:
            raise RuntimeError(f"GET {url} failed: {resp.status_code} {resp.text}")
        
        return resp.json()
    
    
    def post_wiql(
        self,
        *,
        project: str,
        wiql: str,
        top: Optional[int] = None
    ) -> List[int]:
        """
        POST WIQL to retrieve matching work item IDs.
        Endpoint: POST {org}/{project}/_apis/wit/wiql?api-version=...
        """
        if not project:
            raise ValueError("project is required for WIQL queries")

        url = f"{self.org_url}/{project}/_apis/wit/wiql"
        params = {"api-version": self.api_version}
        if top is not None:
            params["$top"] = top

        resp = self.session.post(url, params=params, json={"query": wiql}, timeout=20)
        if not resp.ok:
            raise RuntimeError(f"POST {url} failed: {resp.status_code} {resp.text}")

        data = resp.json()
        return [ref["id"] for ref in data.get("workItems", [])]
    
    
    def hydrate_work_items(
        self,
        ids: List[int],
        *,
        fields: Optional[List[str]] = None,
        expand: Optional[Literal["Relations", "Fields", "Links", "All"]] = None,
        error_policy: Literal["Omit", "Fail"] = "Omit",
    ) -> Dict[str, Any]:
        """
        Retrieves full work item details for a list of IDs.
        Prefer POST workitemsbatch: allows field selection and expand.
        Endpoint: POST {org}/_apis/wit/workitemsbatch?api-version=...
        """
        if not ids:
            return {"count": 0, "value": []}

        url = f"{self.org_url}/_apis/wit/workitemsbatch"
        params = {"api-version": self.api_version}
        payload: Dict[str, Any] = {"ids": ids, "errorPolicy": error_policy}
        if fields:
            payload["fields"] = fields  
        if expand:
            payload["$expand"] = expand


        resp = self.session.post(url, params=params, json=payload, timeout=20)
        if not resp.ok:
            raise RuntimeError(f"POST {url} failed: {resp.status_code} {resp.text}")

        data = resp.json()
        items = data.get("value", [])
        return {"count": len(items), "value": items}
    
    def request_paginated_ct(
        self,
        area: str,
        resource: str,
        *,
        project: Optional[str] = None,
        base_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        ContinuationToken-based pagination.
        Returns {"count": N, "value": [...]}.
        """
        params = dict(base_params or {})
        first = self.request(area, resource, project=project, params=params)
        print(first)
        items = list(first.get("value", []))
        cont = first.get("continuationToken")
        while cont:
            next_params = dict(params)
            next_params["continuationToken"] = cont
            page = self.request(area, resource, project=project, params=next_params)
            items.extend(page.get("value", []))
            cont = page.get("continuationToken")

        if not isinstance(items, list):
            items = [items]
        return {"count": len(items), "value": items}
    
    def request_paginated_skip(
        self,
        area: str,
        resource: str,
        *,
        project: Optional[str] = None,
        base_params: Optional[Dict[str, Any]] = None,
        top_param: str = "$top",
        skip_param: str = "$skip",
        clamp_top: int = 200
    ) -> Dict[str, Any]:
        """
        $top/$skip pagination.
        Returns {"count": N, "value": [...]}.
        """
        params = dict(base_params or {})
        raw_top = params.get(top_param, clamp_top)
        try:
            top = max(1, min(int(raw_top), clamp_top))
        except (TypeError, ValueError):
            top = clamp_top
        params[top_param] = top
        params[skip_param] = 0

        first = self.request(area, resource, project=project, params=params)
        items = list(first.get("value", []))
        skip = top
        while True:
            next_params = dict(params)
            next_params[skip_param] = skip
            page = self.request(area, resource, project=project, params=next_params)
            vals = page.get("value", [])
            if not vals:
                break
            items.extend(vals)
            skip += top
        if not isinstance(items, list):
            items = [items]
        return {"count": len(items), "value": items}
    
    def request_comments_paginated_ct(
        self,
        area: str,
        resource: str,
        *,
        project: Optional[str] = None,
        base_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        ContinuationToken-based pagination for comments.
        Returns {"count": N, "value": [...]}.
        """
        params = dict(base_params or {})
        first = self.request(area, resource, project=project, params=params)
        items = list(first.get("comments", []))
        cont = first.get("continuationToken")
        while cont:
            next_params = dict(params)
            next_params["continuationToken"] = cont
            page = self.request(area, resource, project=project, params=next_params)
            items.extend(page.get("comments", []))
            cont = page.get("continuationToken")

        if not isinstance(items, list):
            items = [items]
        return {"count": len(items), "value": items}