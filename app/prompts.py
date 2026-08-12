# ==========================================
# C4 SYSTEM CONTEXT (LEVEL 1) PROMPTS
# ==========================================
CONTEXT_EXAMPLE = """
{
    "architecture_reasoning": "1. SYSTEM IDENTIFICATION: The system under design is the 'Internet Banking System'. 2. BOUNDARY LOGIC: The 'Internet Banking System' is the only Internal element. The 'Personal Banking Customer', 'Mainframe Banking System', and 'E-mail System' are all External. 3. RELATIONSHIP LOGIC: The Customer uses the System. The System uses the Mainframe (for core banking data) and E-mail System (for notifications).",
    "title": "Internet Banking System - System Context",
    "elements": [
        {
          "id": "customer",
          "name": "Customer",
          "type": "Person",
          "boundary": "External",
          "description": "A customer of the bank with one or more personal bank accounts.",
          "linked_work_items": []
        },
        {
          "id": "internet_banking",
          "name": "Internet Banking System",
          "type": "Software System",
          "boundary": "Internal",
          "description": "Allows customers to view information about their bank accounts and make transactions.",
          "linked_work_items": []
        },
        {
          "id": "mainframe",
          "name": "Mainframe Banking System",
          "type": "Software System",
          "boundary": "External",
          "description": "Stores all of the core banking information about customers, accounts, transactions, etc.",
          "linked_work_items": []
        },
        {
          "id": "email_system",
          "name": "E-mail System",
          "type": "Software System",
          "boundary": "External",
          "description": "The internal Microsoft Exchange e-mail system.",
          "linked_work_items": []
        }
    ],
    "relationships": [
        {
          "source": "customer",
          "target": "internet_banking",
          "label": "Uses",
          "technology": null
        },
        {
          "source": "internet_banking",
          "target": "mainframe",
          "label": "Uses",
          "technology": null
        },
        {
          "source": "internet_banking",
          "target": "email_system",
          "label": "Sends e-mails using",
          "technology": null
        },
        {
          "source": "email_system",
          "target": "customer",
          "label": "Sends e-mails to",
          "technology": null
        }
    ]
}
"""
CONTEXT_SYSTEM_PROMPT = f"""
You are an expert Software Architect specializing in the C4 Model.
Your task is to analyze a list of Azure DevOps work items and produce a formal C4 System Context Architecture in JSON format.
    
### OBJECTIVE
Create a high-level System Context Diagram representing the "System Under Design" in its live, production environment.
The target audience is non-technical stakeholders. The diagram must be clean, simple, and business-focused.

### STRICT EXCLUSION RULES (Negative Filter)
You must actively filter out information that belongs to lower levels (Containers/Components) or other lifecycles.
1. NO Internal Implementation Details: Do NOT include components that define *how* the system is built or hosted.
   - Rule: Any database, file storage, message broker, microservice, serverless function, or internal authentication provider is considered a Container (Level 2) inside the system boundary. Do NOT list them as External Systems.
   - Examples to exclude: Database servers, Blob/Object storage, Caches, Internal APIs, Event Buses, Logging frameworks.
2. NO Build-Time Actors: Do NOT include roles responsible for the creation, testing, or deployment of the system.
    - Rule: Exclude any actor whose primary relationship with the system is to build, test, manage, or deploy the code.
    - Examples to exclude: Software Engineers, QA/Testers, DevOps Engineers, Project Managers, Product Owners.
    - Exception: Only include them if they use the live system for a business purpose (e.g., an "Admin" configuring user permissions).
3. NO Technical Protocols: Do NOT use implementation-specific protocols in relationship labels.
    - Rule: Avoid terms like "HTTPS", "JSON", "REST", "TCP", "SQL", or "RPC". Use business-domain interactions instead (e.g., "Sends order", "Notifies").
4. NO ORPHANS: Do NOT include any Element that does not have at least one defined relationship to another element in the diagram. If a system or person is mentioned in the work items but has no functional interaction with the System Under Design, it must be excluded to maintain diagram integrity.

### INCLUSION RULES
1. Internal System:
- The main software solution described in the work items (System Under Design).
2. Person: 
- Users who interact with the live software (e.g., "Customer", "Backoffice Agent", "Administrator"). 
- Group similar roles (e.g., use "Sales Staff" instead of distinct nodes for "Sales Manager" and "Sales Rep" if they do the same thing).
- STRICT MINIMALISM FILTER: Include a Person ONLY if they are a "Primary Actor" without whom the core business process fails and if they directly trigger core business value (e.g., placing orders, resolving tickets). 
- EXCLUDE: Passive users (e.g., "Managers" viewing reports, "HR", "Auditors") unless they actively manipulate live data.
- Classification:
    * Internal: Employees of the organization.
    * External: Persons outside the organization (Customers or 3rd-party users).
3. External System: 
- Truly independent 3rd party systems or legacy systems that exist outside the control of this software.

### STYLISTIC RULES
1. Conciseness:
    - Descriptions: Maximum 12 words.
    - Relationship Labels: Maximum 4 words.
2. Abstraction: Focus on WHAT the system does, not HOW it does it.
  
### REFERENCE EXAMPLE
To ensure consistency, structure your analysis and JSON output exactly like this example:
{CONTEXT_EXAMPLE}

### OUTPUT SCHEMA
You must output ONLY valid JSON. No comments, no annotations, no markdown code blocks.
The "architecture_reasoning" field MUST be first to establish logic before generation.
  
Structure:
{{
    "architecture_reasoning": "Explain step-by-step: 1. SYSTEM IDENTIFICATION: Identify the System Under Design based on the work items. 2. BOUNDARY LOGIC: Justify the classification of internal vs. external people and systems. 3. RELATIONSHIP LOGIC: Define the core business-level interactions and data flows between all elements.",
    "title": "Name of System - System Context",
    "elements": [
        {{
            "id": "unique_snake_case_id",
            "name": "Clean Display Name",
            "type": "Person" OR "Software System",
            "boundary": "Internal" OR "External",
            "description": "Short description (Max 12 words).",
            "linked_work_items": ["Work Item ID 1", "Work Item ID 2"]
        }},
        ...
    ],
    "relationships": [
        {{
            "source": "source_id",
            "target": "target_id",
            "label": "Short label (Max 4 words)",
            "technology": "Optional. High-level only (e.g. 'Email'). NO protocols like HTTPS/REST."
        }},
        ...
    ]
}}
"""
CONTEXT_USER_PROMPT = """
### TASK:
Analyze the provided work items.
Identify the "System Under Design".
Generate the C4 Context JSON following the architecture_reasoning logic.    
"""

# ==========================================
# C4 CONTAINER (LEVEL 2) PROMPTS
# ==========================================
CONTAINER_EXAMPLE = """
{
    "architecture_reasoning": "1. DECOMPOSITION STRATEGY: The Internet Banking System is composed of a Web Application, a Single-Page App (SPA), a Mobile App, and a Backend API. 2. DATABASE CHOICES: A central SQL Database is used by the API to store user data. 3. RELATIONSHIP LOGIC: The API handles all logic and communicates with the 'mainframe' (Legacy Banking System) and 'email_system' via standard connectors.",
    "title": "Container diagram for Internet Banking System",
    "containers": [
        {
            "id": "web_app",
            "name": "Web Application",
            "type": "WebApp",
            "description": "Delivers the static content and the Internet banking SPA",
            "technology": "Java, Spring MVC",
            "linked_work_items": []
        },
        {
            "id": "spa",
            "name": "Single-Page App",
            "type": "WebApp",
            "description": "Provides all the Internet banking functionality to customers via their web browser",
            "technology": "JavaScript, Angular",
            "linked_work_items": []
        },
        {
            "id": "mobile_app",
            "name": "Mobile App",
            "type": "MobileApp",
            "description": "Provides a limited subset of the Internet banking functionality to customers via their mobile device",
            "technology": "C#, Xamarin",
            "linked_work_items": []
        },
        {
            "id": "database",
            "name": "Database",
            "type": "Database",
            "description": "Stores user registration information, hashed auth credentials, access logs, etc.",
            "technology": "SQL Database",
            "linked_work_items": []
        },
        {
            "id": "backend_api",
            "name": "API Application",
            "type": "Api",
            "description": "Provides Internet banking functionality via API",
            "technology": "Java, Docker Container",
            "linked_work_items": []
        }
    ],
    "relationships": [
        { "source": "customer", "target": "web_app", "label": "Uses", "technology": "HTTPS" },
        { "source": "customer", "target": "spa", "label": "Uses", "technology": "HTTPS" },
        { "source": "customer", "target": "mobile_app", "label": "Uses", "technology": null },
        { "source": "web_app", "target": "spa", "label": "Delivers", "technology": null },
        { "source": "spa", "target": "backend_api", "label": "Uses", "technology": "async, JSON/HTTPS" },
        { "source": "mobile_app", "target": "backend_api", "label": "Uses", "technology": "async, JSON/HTTPS" },
        { "source": "backend_api", "target": "database", "label": "Reads from and writes to", "technology": "sync, JDBC" },
        { "source": "email_system", "target": "customer", "label": "Sends e-mails to", "technology": null },
        { "source": "backend_api", "target": "email_system", "label": "Sends e-mails using", "technology": "sync, SMTP" },
        { "source": "backend_api", "target": "mainframe", "label": "Uses", "technology": "sync/async, XML/HTTPS" }
    ]
}
"""
CONTAINER_SYSTEM_PROMPT = f"""
You are an expert Software Architect specializing in the C4 Model.
Your task is to Create a **C4 Container Diagram** (Level 2).

### INPUTS
1. **Work Items:** The requirements of the project.
2. **System Context (Level 1):** The existing high-level architecture you must respect.

### OBJECTIVE
"Zoom in" on the **Internal System/System Under Design** identified in the System Context.
Decompose it into **Containers** (independently deployable units) based on the work items.

### IDENTIFICATION RULES
1. **Containers:** Identify likely technical containers. Examples:
   - "Mobile App" (iOS/Android)
   - "Web Application" (Server-side rendered or SPA)
   - "API Application" (Backend Microservice)
   - "Database" (SQL/NoSQL)
   - "File Storage"

### TECHNOLOGY RULES
1. **Technology:** You MUST infer plausible technologies if not explicitly stated (e.g., "Java", "Python", "React", "PostgreSQL") based on industry standards.
2. **Technology Separation:**
    - Container Technology: Specify only the core framework or language (e.g., "Python/Flask", "Azure Logic Apps"). Do not mention "Connectors" or "APIs" here if they are already implied by the container type.
    - Relationship Technology: This is where you specify the "How" of the connection, protocols and connectors (e.g., "O365 Connector", "JDBC", "REST/JSON").

### STYLISTIC & INTEGRITY RULES
1. **Redundancy Filter**: Avoid repeating words. If the Container name is "Backend API," do not start the description with "An API that...". Focus the description on the business logic it encapsulates.
2. **NO ORPHANS:** Every single element MUST be connected to something. A container must be connected to either another container or an external element. Existing relationships between external elements only must be maintained.

### REFERENCE EXAMPLE
{CONTAINER_EXAMPLE}

### OUTPUT SCHEMA
You must output ONLY valid JSON. No comments, no annotations, no markdown code blocks.
The "architecture_reasoning" field MUST be first.

Structure:
{{
    "architecture_reasoning": "Explain step-by-step: 1. DECOMPOSITION STRATEGY: Define how the internal system is split into independently deployable containers. 2. DATABASE CHOICES: Rationalize the technology and storage choices for the data persistence layer. 3. RELATIONSHIP LOGIC: Define the communication protocols for both inter-container and external-system integration.",
    "title": "Container Diagram for [System Name]",
    "containers": [
        {{
            "id": "unique_snake_case_id",
            "name": "Clean Display Name",
            "type": "WebApp" OR "MobileApp" OR "Api" OR "Database",
            "description": "Short description.",
            "technology": "Specific Tech (e.g. 'Java, Spring Boot')",
            "linked_work_items": ["ID1", "ID2"]
        }},
        ...
    ],
    "relationships": [
        {{
            "source": "source_id",
            "target": "target_id",
            "label": "Short label",
            "technology": "Protocol (e.g. 'HTTPS', 'JDBC')"
        }},
        ...
    ]
}}

"""
CONTAINER_USER_PROMPT = """
### TASK:
1. Analyze the Context Diagram provided below to understand the boundaries and external actors.
2. Analyze the Work Items to identify internal functional components.
3. Generate the C4 Container JSON. 
Ensure you maintain the high-level element structure of the context diagram and only add the container view of the system under design and link internal containers to the external IDs defined in the Context.
Copy Relationships between external systems and persons (internal and external).
"""
