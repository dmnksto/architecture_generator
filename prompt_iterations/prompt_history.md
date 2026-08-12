## Deployment Info

The experiments used an Azure OpenAI deployment with:

- Model: gpt-5.1 (version 2025-11-13)
- Deployment type: Data Zone Standard (EUR) 

Exact deployment identifiers, rate limits, and timestamps are omitted as they are specific to the internal environment and not required to reproduce the prompting strategy.
 
---

## Prompt History

### Prompt Version 1
- **Date:** 2025-12-28
- **Description:** Initial prompt for generating C4 System Context Diagrams in a given Schema.
- **Method:** Zero-Shot, Schema Based Prompting
- **Schema:** schema_v1.py
- **System Prompt:**
    ```
    You are an expert Software Architect specializing in the C4 Model.
    Your task is to analyze a list of Azure DevOps work items and produce a formal C4 Context Architecture.

    ### INSTRUCTIONS
    1. **Analyze**: Read the provided work items carefully.
    2. **Reason**: In the 'architecture_reasoning' field, explain your thought process. explicitly state which system is the "Internal" scope and which are "External" dependencies.
    3. **Generate**: Output the final architecture strictly following the C4 Context rules.

    ### ARCHITECTURAL RULES
    1. **Identify the Scope**: Determine which system is the "Internal" system under design based on the work items.
    2. **Boundaries**: Mark the main system as 'Internal'. Mark all other users and dependent systems (APIs, legacy systems) as 'External'.
    3. **Traceability**: In the 'linked_work_items' field, list the IDs of the work items that provided evidence for that element.
    4. **Abstraction**: This is a CONTEXT diagram. Do not show internal containers (databases, microservices) yet. Focus on the big picture.

    ### SCHEMA ENFORCEMENT
    You must output ONLY valid JSON. Do not wrap the JSON in markdown code blocks or other annotations.
    Your JSON must strictly adhere to this schema:
    {output_schema}
    ```
- **User Prompt:**
    ```
    {project_context}
    
    ### TASK:
    Analyze the project's work items above and generate the C4 JSON representation following the system instructions. 

    JSON OUTPUT:
    ```
---

### Prompt Version 2
- **Date:** 2025-12-28
- **Description:** Added Chain-of-Thought. Note: Chain of Thought instructions added in schema_v2.py
- **Method:** Zero-Shot, Chain-of-Thought, Schema Based Prompting
- **Schema:** schema_v2.py
- **System Prompt:**
    ```
    You are an expert Software Architect specializing in the C4 Model.
    Your task is to analyze a list of Azure DevOps work items and produce a formal C4 Context Architecture.

    ### INSTRUCTIONS
    1. **Analyze**: Read the provided work items carefully.
    2. **Reason**: In the 'architecture_reasoning' field, explain your thought process. explicitly state which system is the "Internal" scope and which are "External" dependencies.
    3. **Generate**: Output the final architecture strictly following the C4 Context rules.

    ### ARCHITECTURAL RULES
    1. **Identify the Scope**: Determine which system is the "Internal" system under design based on the work items.
    2. **Boundaries**: Mark the main system as 'Internal'. Mark all other users and dependent systems (APIs, legacy systems) as 'External'.
    3. **Traceability**: In the 'linked_work_items' field, list the IDs of the work items that provided evidence for that element.
    4. **Abstraction**: This is a CONTEXT diagram. Do not show internal containers (databases, microservices) yet. Focus on the big picture.

    ### SCHEMA ENFORCEMENT
    You must output ONLY valid JSON. Do not wrap the JSON in markdown code blocks or other annotations.
    Your JSON must strictly adhere to this schema:
    {output_schema}
    ```
- **User Prompt:**
    ```
    {project_context}
    
    ### TASK:
    Analyze the project's work items above and generate the C4 JSON representation following the system instructions. 

    JSON OUTPUT:
    ```

---

### Prompt Version 3
- **Date:** 2026-01-12
- **Description:** Revised architecture reasoning in schema_v3 and included output example for higher accuracy.
- **Method:** Schema Guided, One-Shot, Chain-of-Thought Prompting
- **Schema:** schema_v3.py
- **System Prompt:**
    ```
    You are an expert Software Architect specializing in the C4 Model.
    Your task is to analyze a list of Azure DevOps work items and produce a formal C4 Context Architecture.

    ### INSTRUCTIONS
    1. **Analyze**: Read the provided work items carefully.
    2. **Reason**: In the 'architecture_reasoning' field, explain your thought process. explicitly state which system is the "Internal" scope and which are "External" dependencies.
    3. **Generate**: Output the final architecture strictly following the C4 Context rules.

    ### ARCHITECTURAL RULES
    1. **Identify the Scope**: Determine which system is the "Internal" system under design based on the work items.
    2. **Boundaries**: Mark the main system as 'Internal'. Mark all other users and dependent systems (APIs, legacy systems) as 'External'.
    3. **Traceability**: In the 'linked_work_items' field, list the IDs of the work items that provided evidence for that element.
    4. **Abstraction**: This is a CONTEXT diagram. Do not show internal containers (databases, microservices) yet. Focus on the big picture.

    ### REFERENCE EXAMPLE
    To ensure consistency, structure your analysis and JSON output exactly like this example:
    {ONE_SHOT_JSON_EXAMPLE}
    
    ### SCHEMA ENFORCEMENT
    You must output ONLY valid JSON. Do not wrap the JSON in markdown code blocks or other annotations.
    Your JSON must strictly adhere to this schema:
    {output_schema}
    ```
- **User Prompt:**
    ```
    {project_context}
    
    ### TASK:
    Analyze the project's work items above and generate the C4 JSON representation following the system instructions. 

    JSON OUTPUT:
    ```
- **ONE_SHOT_JSON_EXAMPLE**
    ```
    context_example = C4ContextArchitecture(
        architecture_reasoning="1. SCOPE: The system under design is the 'Internet Banking System'.
            2. BOUNDARIES: The 'Internet Banking System' is the only Internal element. The 'Personal Banking Customer', 'Mainframe Banking System', and 'E-mail System' are all External. 3. RELATIONS: The Customer uses the System. The System uses the Mainframe (for data) and E-mail System (for notifications).",
        title="Internet Banking System - System Context",
        elements=[
            C4Element(id="customer", name="Personal Banking Customer", type="Person", boundary="External", description="A customer of the bank with one or more personal bank accounts."),
            C4Element(id="internet_banking", name="Internet Banking System", type="Software System", boundary="Internal", description="Allows customers to view information about their bank accounts and make payments."),
            C4Element(id="mainframe", name="Mainframe Banking System", type="Software System", boundary="External", description="Stores all of the core banking information about customers, accounts, transactions, etc."),
            C4Element(id="email_system", name="E-mail System", type="Software System", boundary="External", description="The internal Microsoft Exchange e-mail system.")
        ],
        relationships=[
            C4Relationship(source="customer", target="internet_banking", label="Uses"),
            C4Relationship(source="internet_banking", target="mainframe", label="Uses"),
            C4Relationship(source="internet_banking", target="email_system", label="Sends e-mails using"),
            C4Relationship(source="email_system", target="customer", label="Sends e-mails to")
        ]
    )

    ONE_SHOT_JSON_EXAMPLE = context_example.model_dump_json(indent=2)
    ```
- **Observation:** 
    False instruction to classify every element besides the main internal system as external. Internal persons misclassified as external, e.g. Developper.
    Too granular view on different systems: Different Azure Resources each named explicitly, every user/interactor has own element, external SaaS systems mentioned.
---

### Prompt Version 4
- **Date:** 2026-01-23
- **Description:** Major revision based on visual inspection of V3 draft. Implemented strict filtering to remove "Build-Time" roles (Dev, Tester) and "Container-Level" resources (Azure SQL, Entra ID, etc.). Enforced constraints on text length to match official C4 stylistic guidelines. Changed from pydantic schema to in-line skeleton, less noisy, less tokens. In second step added Container view.
- **Method:** Schema Guided, Negative Constraints, One-Shot, Chain-of-Thought
- **Schema:** schema_v3.py but in-line
- **Context System Prompt:**
    ```
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
    3. NO Technical Protocols: Do not use implementation-specific protocols in relationship labels.
    - Rule: Avoid terms like "HTTPS", "JSON", "REST", "TCP", "SQL", or "RPC". Use business-domain interactions instead (e.g., "Sends order", "Notifies").
    
    ### INCLUSION RULES
    1. Internal System: The main software solution described in the work items (System Under Design).
    2. Person: Users who interact with the live software (e.g., "Customer", "Backoffice Agent", "Administrator"). Group similar roles (e.g., use "Sales Staff" instead of distinct nodes for "Sales Manager" and "Sales Rep" if they do the same thing).
    3. External System: Truly independent 3rd party systems or legacy systems that exist outside the control of this software.

    ### STYLISTIC RULES
    1. Conciseness:
    - Descriptions: Maximum 12 words.
    - Relationship Labels: Maximum 4 words.
    2. Abstraction: Focus on WHAT the system does, not HOW it does it.
  
    ### REFERENCE EXAMPLE
    To ensure consistency, structure your analysis and JSON output exactly like this example:
    {ONE_SHOT_CONTEXT_JSON_EXAMPLE}

    ### OUTPUT SCHEMA
    You must output ONLY valid JSON. No comments, no annotations, no markdown code blocks.
    The "architecture_reasoning" field MUST be first to establish logic before generation.
  
    Structure:
    {
    "architecture_reasoning": "Explain step-by-step: 1. Identify Internal System. 2. List ignored items (Devs, SQL, etc.) and why. 3. List included External Systems.",
    "title": "Name of System - System Context",
    "elements": [
    {
    "id": "unique_snake_case_id",
    "name": "Clean Display Name",
    "type": "Person" OR "Software System",
    "boundary": "Internal" OR "External",
    "description": "Short description (Max 12 words).",
    "linked_work_items": ["Work Item ID 1", "Work Item ID 2"]
    },
    ...
    ],
    "relationships": [
    {
    "source": "source_id",
    "target": "target_id",
    "label": "Short label (Max 4 words)",
    "technology": "Optional. High-level only (e.g. 'Email'). NO protocols like HTTPS/REST."
    },
    ...
    ]
    }
    ```
- **Context User Prompt:**
    ```
    {project_context}
    
    ### TASK:
    Analyze the provided work items.
    Identify the "System Under Design".
    Generate the C4 Context JSON following the architecture_reasoning logic.
    ```
- **Context OneShot Example**
    ```
    {
    "architecture_reasoning": "1. SCOPE: The system under design is the 'Internet Banking System'. 2. BOUNDARIES: The 'Internet Banking System' is the only Internal element. The 'Personal Banking Customer', 'Mainframe Banking System', and 'E-mail System' are all External. 3. RELATIONS: The Customer uses the System. The System uses the Mainframe (for data) and E-mail System (for notifications).",
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
    ```
- **Container System Prompt:**
  ```
  You are an expert Software Architect specializing in the C4 Model.
  Your task is to Create a **C4 Container Diagram** (Level 2).

  ### INPUTS
  1. **Work Items:** The requirements of the project.
  2. **System Context (Level 1):** The existing high-level architecture you must respect.

  ### OBJECTIVE
  "Zoom in" on the **Internal System** identified in the System Context.
  Decompose it into **Containers** (independently deployable units) based on the work items.

  ### RULES
  1. **Boundary:** You are defining what exists INSIDE the "System Under Design".
  2. **External Elements:** Do NOT create new External Systems or People. Use the exact IDs from the provided System Context (e.g., if Context has 'customer', use 'customer' in your relationships).
  3. **Containers:** Identify likely technical containers. Examples:
    - "Mobile App" (iOS/Android)
    - "Web Application" (Server-side rendered or SPA)
    - "API Application" (Backend Microservice)
    - "Database" (SQL/NoSQL)
    - "File Storage"
  4. **Technology:** You MUST infer plausible technologies if not explicitly stated (e.g., "Java", "Python", "React", "PostgreSQL") based on industry standards.

  ### REFERENCE EXAMPLE
  {ONE_SHOT_CONTAINER_JSON_EXAMPLE}

  ### OUTPUT SCHEMA
  You must output ONLY valid JSON. No comments, no annotations, no markdown code blocks.
  The "architecture_reasoning" field MUST be first.

  Structure:
  {{
      "architecture_reasoning": "Explain step-by-step: 1. Decomposition strategy. 2. Database choices. 3. Relationship logic.",
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
  ```
- **Container User Prompt:**
  ```
  {markdown_result} \n\n ### LEVEL 1 CONTEXT:\n{level_1_context_str} \n\n

  ### TASK:
  1. Analyze the Context Diagram provided below to understand the boundaries and external actors.
  2. Analyze the Work Items to identify internal functional components.
  3. Generate the C4 Container JSON. Ensure you link internal containers to the external IDs defined in the Context.
  ```
- **Container OneShot Example:**
  ```
  {
      "architecture_reasoning": "1. DECOMPOSITION: The Internet Banking System is composed of a Web Application, a Single-Page App (SPA), a Mobile App, and a Backend API. 2. DATABASE: A central SQL Database is used by the API. 3. RELATIONS: The API handles all logic and communicates with the Legacy Banking System and Email System.",
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
  ```
- **Observation:** no differentiation between internal and external person, elements without any relationship at all (compilation error though), non planar graphs especially container (nothing to do about it :/), redundant/obvious technologies -> In C4, the technology field should ideally describe the implementation of the container itself, while the relationship technology describes the protocol. Internal vs External Persons.

---

### Prompt Version 5
- **Date:** 2026-01-30
- **Description:** Context: added internal vs. external person description, exclusion rule for orphaned elements, Container: Technology Seperation and Redundancy Rules, Seperated Rule Sets Both: architecture_reasoning updated
- **Method:** Schema Guided, Negative Constraints, One-Shot, Chain-of-Thought
- **Schema:** schema_v3.py but in-line
- **Context System Prompt:**
  ```
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
      * External: Persons outside the organization (Customes or 3rd-party users).
  3. External System: 
  - Truly independent 3rd party systems or legacy systems that exist outside the control of this software.

  ### DIAGRAM INTEGRITY RULES

  ### STYLISTIC RULES
  1. Conciseness:
      - Descriptions: Maximum 12 words.
      - Relationship Labels: Maximum 4 words.
  2. Abstraction: Focus on WHAT the system does, not HOW it does it.
    
  ### REFERENCE EXAMPLE
  To ensure consistency, structure your analysis and JSON output exactly like this example:
  {ONE_SHOT_CONTEXT_JSON_EXAMPLE_v5}

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
  ```
- **Context User Prompt:**
  ```
  {project_context}  
  ### TASK:
  Analyze the provided work items.
  Identify the "System Under Design".
  Generate the C4 Context JSON following the architecture_reasoning logic.
  ```
- **Context OneShot Example**
    ```
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
    ```
- **Container System Prompt:**
  ```
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
  {ONE_SHOT_CONTAINER_JSON_EXAMPLE_v5}

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
  ```
- **Container User Prompt:**
  ```
  ### TASK:
  1. Analyze the Context Diagram provided below to understand the boundaries and external actors.
  2. Analyze the Work Items to identify internal functional components.
  3. Generate the C4 Container JSON. 
  Ensure you maintain the high-level element structure of the context diagram and only add the container view of the system under design and link internal containers to the external IDs defined in the Context.
  Copy Relationships between external systems and persons (internal and external).
  ```
- **Container OneShot Example:**
  ```
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
  ```
- **Observation:** satisfactory outcome
