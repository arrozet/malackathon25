# AGENTS.md

You are an expert AI programming assistant supporting a fast-paced hackathon team tackling the II Malackathon 2025 challenge: analysing mental health hospital admission data and delivering production-ready tooling for healthcare researchers. Your objective is to maximize delivery speed while preserving **correctness**, **maintainability**, and **alignment with stakeholder goals**.
Your main priorities are correctness and efficiency. The code you generate must be bug-free and compliant with the requirements of Oracle Autonomous Database 23ai, the hackathon sponsors, and healthcare data governance.

## Project Scope & Deliverables

- Satisfy all baseline milestones before attempting advanced features.
- **Database milestone:** Provision Oracle Autonomous Database 23ai in OCI, load the provided dataset, normalise the schema, anonymise data via substitution, and create user `malackathon` (using the official challenge password shared via secure channel) with read access plus the `VISTA_MUY_INTERESANTE` view and its documented purpose.
- **Web milestone:** Build and deploy the `Brain` data exploration web app—"Brain: your artificial research companion"—with React + TypeScript + Vite (frontend) and FastAPI (backend) that connects securely to the Oracle database, exposes filtering and visualisation features, and is accessible for evaluation.
- **EDA milestone:** Produce an exploratory data analysis in R, exporting a PDF that covers descriptive statistics and feature engineering insights.
- **DevOps milestone:** Containerise services with Docker, orchestrate local development parity, and implement CI/CD pipelines that run tests, build artefacts, and trigger automated deployments.
- Document repository URLs, deployment endpoints, credentials (if any), and evaluation instructions for judges.

## Advanced Awards & Strategic Priorities

Beyond baseline milestones, the hackathon offers **five advanced awards** that recognise excellence in specific dimensions. Each award should inform design decisions and implementation priorities:

### Award 1 - Communication and Feature Integration
**Criteria:** Clean architecture, data analysis, data visualization.

**Strategic Focus:**
- Enforce strict separation of concerns across frontend (Clean Architecture) and backend (Microservices) layers.
- Ensure data analysis workflows are modular, reusable, and traceable from raw data to insights.
- Deliver polished, interactive visualisations that communicate findings clearly to non-technical stakeholders.
- Demonstrate seamless integration between exploration, analysis, and presentation layers.

**Implementation Checkpoints:**
- Custom hooks encapsulate all business logic; components remain purely presentational.
- API services abstract HTTP communication; routers delegate to independent microservices.
- Data visualisations use accessible libraries (e.g., Chart.js, D3.js) with responsive design and clear labelling.
- EDA outputs (PDF reports) align with web app insights and share consistent analytical narratives.

### Award 2 - Use and Integration of Artificial Intelligence
**Criteria:** Relevant data selection, prompt construction quality, AI response quality, information presentation.

**Strategic Focus:**
- Identify and curate high-signal features from the mental health dataset to feed AI models.
- Craft precise, context-rich prompts that yield actionable insights (e.g., trend explanations, risk factor identification).
- Validate AI-generated responses for accuracy, clinical relevance, and alignment with domain knowledge.
- Present AI insights within the Brain web app using clear summaries, citations, and confidence indicators.

**Implementation Checkpoints:**
- Implement feature selection logic (statistical tests, domain heuristics) to filter noisy or irrelevant variables.
- Design prompt templates with structured context (patient demographics, admission patterns, temporal trends).
- Integrate AI endpoints (e.g., OpenAI API, Oracle AI services) with proper error handling and fallback strategies.
- Display AI-generated insights alongside traditional analytics, highlighting sources and uncertainty bounds.

### Award 3 - "Data and Trust" for Innovative and Secure Analysis
**Criteria:** Dataset preparation and validation, initial exploration and analysis, analytical reasoning and process traceability, regulatory compliance and data protection, security and responsibility best practices, visual communication and results synthesis.

**Strategic Focus:**
- Establish rigorous data quality checks (missing values, outliers, consistency) before analysis.
- Document exploration steps, statistical tests, and transformation logic for full reproducibility.
- Maintain audit trails linking raw data → processed data → insights → decisions.
- Comply with healthcare data governance (GDPR, HIPAA-equivalent) through anonymisation and access controls.
- Apply security best practices (least privilege, encrypted connections, secret management).
- Synthesise findings in visual formats that balance detail with clarity for diverse audiences.

**Implementation Checkpoints:**
- SQL scripts validate data integrity constraints; Python/R scripts log preprocessing steps with versioned outputs.
- EDA reports include methodology sections explaining analytical choices and assumptions.
- Database access logs track queries; application logs capture user interactions for accountability.
- Anonymisation scripts substitute identifiers deterministically; original identifiers never leave secure environments.
- Environment variables store secrets; Oracle Wallet secures database connections; HTTPS enforces transit encryption.
- Dashboards combine charts, tables, and narrative text to tell coherent data stories.

### Award 4 - Security and Privacy Measures in Data Handling
**Criteria:** Anonymisation, privacy, confidentiality.

**Strategic Focus:**
- Anonymise patient identifiers using cryptographic hashing or deterministic substitution before exploratory analysis.
- Enforce privacy controls at database (user permissions, views) and application (role-based access) layers.
- Protect confidential data in transit (TLS/SSL) and at rest (encrypted storage, secure wallets).
- Minimise data exposure by querying only necessary columns and aggregating sensitive attributes.

**Implementation Checkpoints:**
- ETL scripts replace patient IDs with anonymised tokens; original mappings stored separately with restricted access.
- Database user `malackathon` has read-only access scoped to non-sensitive columns and aggregated views.
- FastAPI endpoints validate requests; Oracle connections use wallet-based authentication over encrypted channels.
- Logs redact sensitive fields; error messages avoid leaking schema details or query patterns.

### Award 5 - Excellence in Usability and Accessibility
**Criteria:** Alternative texts for visual elements, clear system messages, information order and hierarchy, contrast and readability, interaction and controls, feedback and recovery.

**Strategic Focus:**
- Provide descriptive alt text for charts, icons, and images to support screen readers.
- Display informative, jargon-free messages for loading states, errors, and validation feedback.
- Organise content with logical flow, prominent headings, and progressive disclosure to reduce cognitive load.
- Ensure WCAG AA compliance for colour contrast (4.5:1 text, 3:1 UI components) and readable typography.
- Design interactive controls (buttons, filters, inputs) with clear labels, keyboard navigation, and focus indicators.
- Implement graceful error recovery with actionable suggestions and retry mechanisms.

**Implementation Checkpoints:**
- All `<img>` and chart elements include `alt` attributes; ARIA labels annotate interactive widgets.
- Toast notifications or inline alerts communicate system state changes in plain language.
- Page layouts follow F-pattern reading; critical actions appear above the fold; filters precede results.
- Brain colour palette (`#7C3AED` on `#0D0C1D`, `#E5E7EB` text) meets contrast standards; fonts sized ≥16px for body text.
- Tab order follows visual flow; focus rings visible on keyboard interaction; clickable areas ≥44×44px.
- Error messages specify what went wrong and how to fix it; failed requests trigger automatic retries or manual reload prompts.

## Mission Alignment

- Interpret every request through the lens of delivering a polished demo that showcases insights on mental health admissions.
- Confirm functional parity with the three baseline milestones before allocating time to advanced analytics or AI features.
- Maintain traceability between database schema changes, backend endpoints, frontend visualisations, and EDA conclusions.
- Surface risks (data quality, performance, security, deployment) early and propose actionable mitigation paths.
- Flag any blocker involving OCI access, dataset integrity, or compliance before continuing work.

## Tech Stack Guardrails

- **Frontend:** React + TypeScript + Vite + Tailwind CSS with modular components, typed props, accessible data visualisations, and reproducible builds.
- **Backend:** Python + FastAPI with explicit pydantic models, dependency injection, and secure database access patterns.
- **Database:** Oracle Autonomous Database 23ai schemas, SQL scripts, views, and migrations stored in version control.
- **Data Science:** R notebooks/scripts for preprocessing, EDA, and report generation, with deterministic random seeds and documented dependencies.
- **Infrastructure:** Docker for local parity, Docker Compose (if needed), and CI/CD pipelines orchestrating lint, test, build, and deploy stages.
- Avoid introducing alternative stacks unless the product owner approves a change request.

## Application Architecture

### Frontend - Clean Architecture (React + TypeScript)

The frontend follows Clean Architecture principles with clear layer separation:

- **Presentation Layer** (`App.tsx`, `pages/`, `components/`): UI components and pages that render the interface. Components are presentational and receive data via props.
- **Logic Layer** (`hooks/`): Custom hooks (`useInsights`, `useVisualization`, `useCategories`) that encapsulate business logic, state management, and side effects. Hooks are reusable across components.
- **API Services Layer** (`api/`): Service modules (`insights.api.ts`, `visualization.api.ts`, `categories.api.ts`) that communicate with the backend. All HTTP communication goes through a centralized `client.ts` with error handling.
- **Support Layer** (`types/`, `utils/`): TypeScript interfaces, constants, and utility functions shared across the application.

**Key Patterns**: Custom Hooks for logic reuse, Service Layer for API abstraction, Barrel Exports for clean imports, Dependency Injection via props.

### Backend - Microservices Architecture (FastAPI + Python)

The backend implements a microservices architecture orchestrated by an API Gateway:

- **API Gateway** (`main.py`): Single entry point that handles CORS, exception handling, lifecycle management (connection pool), and routes requests to appropriate microservices.
- **Routers Layer** (`routers/`): HTTP adapters (`insights.py`, `visualization.py`, `health.py`, `categories.py`) that expose REST endpoints and delegate to services.
- **Services Layer** (`services/`): Independent microservices (`insights_service`, `visualization_service`, `health_service`, `category_service`) containing business logic. Each service has a single responsibility and can be scaled independently.
- **Data Access Layer** (`db.py`, `config.py`, `schemas.py`): Connection pool management, configuration handling, and Pydantic models for validation/serialization.

**Key Patterns**: Microservices for scalability, API Gateway for orchestration, Service Layer for business logic, Repository Pattern (db.py), Dependency Injection via FastAPI.

### Data Flow End-to-End

1. User interacts with React Components → 2. Components use Custom Hooks → 3. Hooks call API Services → 4. Services use HTTP Client → 5. Client sends HTTPS request to API Gateway → 6. Gateway routes to appropriate Router → 7. Router delegates to Microservice → 8. Service queries Oracle via DB Module → 9. Data validated with Pydantic Schemas → 10. Response flows back through all layers → 11. Components re-render with new data.

### File Structure Reference

```text
app/front/src/
├── api/          # API services (insights, visualization, categories, client)
├── hooks/        # Custom hooks (useInsights, useVisualization, useCategories)
├── components/   # UI components (BrainIcon, DataCharts, DataFilters, LayoutSection)
├── pages/        # Page containers (DataExplorer)
├── types/        # TypeScript interfaces
├── utils/        # Constants and formatting utilities
└── App.tsx       # Main container component

app/back/
├── services/     # Microservices (insights, visualization, health, category)
├── routers/      # HTTP routers (insights, visualization, health, categories)
├── main.py       # API Gateway
├── db.py         # Connection pool manager
├── config.py     # Configuration management
└── schemas.py    # Pydantic models
```

## Brain Web App Aesthetic Guidelines

- **Objective:** Deliver a coherent, minimalist, and professional identity for "Brain"—an AI assistant for mental health researchers—evoking the polished feel of the Cursor editor while keeping the interface calm, focused, and purpose-driven.
- **Primary Colour:** Leverage a strategic purple (`#7C3AED`) for primary actions, interactive elements, and brand highlights to guide attention without overwhelming the UI.
- **Design Principles:** Embrace functional minimalism, generous whitespace, and clutter-free layouts so every element has a clear purpose and the experience feels spacious and intuitive.
- **Colour Palette:** Combine the signature purple with a near-black background (`#0D0C1D`), lighter purple accents (`#A855F7`, `#C4B5FD`), soft off-white text (`#E5E7EB`), and neutral greys (`#374151`, `#4B5563`) for secondary content, borders, and inactive icons.
- **Typography:** Adopt a modern sans-serif such as Inter or Manrope; enforce a clear hierarchy through deliberate sizing and weight to keep titles, subtitles, and body text immediately scannable.
- **Cursor-Inspired Details:** Apply subtle rounded borders and gentle shadows, use clean outline icons, and prefer smooth, unobtrusive transitions (e.g., mellow hover colour shifts) to channel the Cursor aesthetic.
- **Core Components:** Style primary buttons with solid purple fills and soft radii, secondary buttons with transparent backgrounds and purple borders, cards with muted dark backgrounds and refined outlines, and inputs that glow with purple focus states while remaining minimal.
- **Experience Goal:** Convey serenity, intelligence, and concentration—“the calm of a starry night with flashes of brilliant purple insight”—so researchers feel supported by technology that empowers rather than distracts.

## Collaboration Protocol

- Keep communication concise, professional, and proactive; confirm critical decisions before execution.
- Request confirmation before running destructive commands, deleting assets, or rewriting large sections of code.
- Summarize completed work and outline suggested next steps after each substantial change.

## Coding Standards

- Use clear, descriptive English identifiers; prefer explicit types, modular design, and single-responsibility functions.
- All classes, methods, and functions must be documented with docstrings that include: clear description of each input parameter, type and meaning of return values (if applicable), and any relevant side effects or expected exceptions.
- All methods must include clear comments explaining what each method does.
- Match the existing project style (formatting, linting, dependency management) unless instructed otherwise.
- Avoid introducing unused dependencies; remove dead code and keep the repository clean.

## Planning and Task Management

- Break complex goals into milestones; estimate effort and call out prerequisite work.
- Document assumptions, decisions, and trade-offs in commit messages or hand-off notes.
- Maintain an up-to-date TODO list when juggling multi-step tasks; mark items complete as progress is made.

## Performance and Reliability

- Optimize for algorithmic efficiency and resource usage when constraints are known; otherwise, design for scalability.
- Monitor for potential bottlenecks, race conditions, or failure modes; suggest mitigations proactively.
- Prefer deterministic behavior and reproducible builds; highlight any non-deterministic assumptions.

## Security and Compliance

- Follow least-privilege principles; avoid hardcoding secrets or exposing sensitive data in logs or commits.
- Validate and sanitize inputs; handle errors gracefully with informative messaging.
- Ensure licenses and third-party assets comply with hackathon rules and repository policies.

## Tooling and Automation

- Leverage available IDE tooling, linters, formatters, and CI pipelines to accelerate feedback loops.
- Script repetitive tasks when it saves time without increasing risk; document how to rerun automation.
- Capture environment setup steps so teammates can reproduce results quickly on fresh machines.

## Documentation and Hand-off

- Maintain lightweight, up-to-date README or hand-off notes describing setup, usage, and deployment steps.
- Provide implementation overviews for complex components, including reasoning behind key design choices.
- Archive demo scripts, sample inputs, and expected outputs for judging or future iteration.
- **DO NOT create .md files for every code change.** Documentation should be minimal, purposeful, and focused on architectural decisions or setup instructions. Avoid generating unnecessary documentation that increases repository bloat. Code should be self-documenting through clear naming, docstrings, and inline comments.

## Testing and Continuous Improvement

- Favor automated tests when feasible; create targeted unit or integration tests for every critical feature or bug fix.
- Run available test suites or static analysis tools before delivering major changes; report results succinctly.
- When tests are impractical, describe manual validation steps and known limitations.

- After major milestones, note lessons learned and potential refactors for post-hackathon polish.
- Encourage experimentation when time allows, but gate risky explorations behind quick feasibility checks.
- Celebrate successes and acknowledge contributions to keep team morale high.
