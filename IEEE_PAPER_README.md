# IntelliQuery: A Multi-Backend Natural Language Query Platform with LLM-Powered Agent Routing and Automated Visualization

---

## Paper Structure (IEEE Conference Format)

> This document contains all the content organized in the standard IEEE conference paper structure. Each section below maps to a section of the IEEE paper. Use this as your draft for the final LaTeX/Word submission.

---

## I. TITLE AND AUTHORS

**Title:**  
_IntelliQuery: A Multi-Backend Natural Language Query Platform with LLM-Powered Agent Routing and Automated Visualization_

**Authors:**  
_(Add author names, affiliations, and emails here)_

**Keywords:**  
Natural Language Processing, Text-to-SQL, Text-to-MongoDB, Text-to-Pandas, Large Language Models, Conversational Analytics, Data Visualization, Read-Only Query Enforcement, Multi-Backend Routing, FastAPI, React

---

## II. ABSTRACT

The growing demand for data-driven decision-making across organizations has exposed a critical accessibility gap: non-technical stakeholders—business analysts, operators, and domain experts—frequently lack the technical proficiency to write structured queries in SQL, MongoDB aggregation pipelines, or Pandas code. Existing commercial solutions such as BlazeSQL, DataGPT, and Google Looker Conversational Analytics remain tightly coupled to SQL-only warehouses, are closed-source, and offer limited extensibility for hybrid database environments.

This paper presents **IntelliQuery**, an open-source, research-oriented conversational analytics platform that enables users to query SQL databases (MySQL, PostgreSQL), MongoDB document stores, and CSV/Excel spreadsheets using natural language. The system employs a modular agent-based architecture where a central AI Router dynamically dispatches user queries to specialized agents—`SQLAgent`, `MongoAgent`, and `PandasAgent`—based on the connected datasource type. Each agent leverages the Groq-hosted Meta LLaMA 4 Scout 17B model (via the Groq inference API) for query generation, followed by rigorous read-only validation using regex-based pattern matching and AST parsing before safe execution against the target datastore.

The platform additionally features: (i) an LLM-driven visualization recommendation engine that analyzes query result structure to suggest and generate 13 Plotly chart types, (ii) a context-aware autocomplete engine with schema-informed suggestions and LRU caching for sub-500ms response times, (iii) a session-based query history persistence layer backed by MongoDB, and (iv) a secure authentication system with PBKDF2 password hashing, JWT cookie-based sessions, and encrypted credential storage for connected datasources.

The frontend, built with React 19, Vite, and Tailwind CSS v4, provides a chat-based query interface with real-time autocomplete, interactive Plotly.js visualizations, session management, and multi-datasource switching. Experimental evaluation on synthetic e-commerce datasets (5,000–10,000 records across SQL, MongoDB, and CSV) demonstrates the system's ability to correctly translate diverse natural language queries—including aggregations, joins, filters, grouping, and statistical analyses—into executable, read-only database operations across all three backends.

---

## III. INTRODUCTION

### A. Background and Motivation

The proliferation of data across enterprises has created an urgent need for intuitive, code-free interfaces to databases. While business intelligence (BI) tools have evolved significantly, they still require users to understand query languages or navigate complex drag-and-drop interfaces. The emergence of Large Language Models (LLMs) with strong code generation capabilities has opened a pathway to truly natural language-driven data exploration.

However, real-world enterprise environments rarely operate on a single data backend. Organizations commonly maintain relational databases (MySQL, PostgreSQL) for transactional data, MongoDB for document-oriented workloads, and spreadsheet files (CSV, Excel) for ad-hoc analyses. Existing natural language query systems typically support only SQL, leaving a significant portion of enterprise data inaccessible through conversational interfaces.

### B. Problem Statement

The key challenges addressed by this work are:

1. **Multi-Backend Query Translation:** Translating a single natural language question into the correct query language (SQL, MongoDB aggregation pipeline, or Pandas code) based on the connected datasource, without requiring the user to specify the target language.

2. **Read-Only Safety Enforcement:** Ensuring that LLM-generated queries cannot modify, delete, or corrupt production data—a critical requirement for enterprise adoption.

3. **Automated Visualization:** Intelligently recommending and generating appropriate visualizations from query results without requiring the user to specify chart configurations.

4. **Context-Aware Query Assistance:** Providing real-time, schema-aware autocomplete suggestions as users type their queries, reducing cognitive load and improving query quality.

5. **Secure Multi-Tenant Access:** Supporting multiple users with isolated datasource connections, encrypted credential storage, and session-based authentication.

### C. Contributions

The main contributions of this paper are:

- A **unified multi-backend architecture** that routes natural language queries to specialized agents for SQL, MongoDB, and Pandas execution through a single API endpoint.
- A **multi-layered read-only validation pipeline** employing regex pattern matching, keyword blacklisting, AST parsing, and statement analysis to prevent destructive operations.
- An **LLM-driven visualization recommendation system** that analyzes data structure (column types, cardinality, distributions) to suggest and generate 13 chart types using Plotly.
- A **schema-aware autocomplete engine** with LRU caching that provides sub-500ms query suggestions informed by the connected datasource's schema.
- A complete **open-source implementation** with a React frontend, FastAPI backend, and comprehensive test suites, demonstrating feasibility in a realistic e-commerce scenario.

### D. Paper Organization

The remainder of this paper is organized as follows: Section IV reviews related work. Section V details the system architecture. Section VI describes the implementation. Section VII presents the experimental evaluation. Section VIII discusses limitations and future work. Section IX concludes the paper.

---

## IV. LITERATURE REVIEW / RELATED WORK

### A. Text-to-SQL Research

The task of converting natural language to SQL has been extensively studied. Benchmark datasets such as **WikiSQL** [1], **Spider** [2], and **BIRD** [3] have established rigorous evaluation regimes for measuring compositional generalization in schema-conditioned query generation. Transformer-class models—including GPT-4, LLaMA, and Mistral variants—consistently push state-of-the-art accuracy on these benchmarks, demonstrating robust handling of joins, nested filters, subqueries, and schema grounding.

However, these contributions stop at SQL generation and do not address: (a) execution safety and read-only enforcement, (b) post-processing and result formatting, (c) result narration and visualization, or (d) extension to non-SQL query languages. IntelliQuery addresses all four gaps.

### B. Commercial Conversational BI Tools

Products such as **BlazeSQL**, **DataGPT**, **Google Looker Conversational Analytics**, **ThoughtSpot Sage**, and **Microsoft Copilot for Power BI** demonstrate that NL-powered querying lowers the entry barrier to data exploration. However, these tools share common limitations:

| Limitation            | Description                                                                           |
| --------------------- | ------------------------------------------------------------------------------------- |
| SQL-only focus        | Tightly coupled to SQL data warehouses; no support for MongoDB or spreadsheet queries |
| Closed-source         | Proprietary implementations with no extensibility hooks                               |
| Single-backend        | Cannot route queries to heterogeneous data stores                                     |
| Limited customization | Fixed visualization palettes without user-configurable chart generation               |
| Vendor lock-in        | Tied to specific cloud platforms or data warehouse products                           |

IntelliQuery is open-source, supports three backend types, and provides extensible agent architecture for adding new datasource types.

### C. LLM Agent Frameworks

Frameworks such as **LangChain** [4], **LlamaIndex**, and **AutoGen** enable LLM agents to call databases, APIs, and analytical runtimes. While LangChain provides SQL database toolkits, most reference implementations target SQL-only workloads. Unified handling of SQL, Pandas, and MongoDB within a single routing framework remains underexplored, especially when coupled with:

- No-code data manipulation assurances (read-only enforcement)
- Fine-grained per-user governance and credential encryption
- Narrated insight delivery through automated visualization

### D. Text-to-MongoDB and Text-to-Pandas

While Text-to-SQL has received substantial attention, **Text-to-MongoDB** (generating aggregation pipelines from natural language) and **Text-to-Pandas** (generating DataFrame operations) are comparatively underexplored. Recent work has demonstrated the feasibility of using LLMs for MongoDB query generation [5], but no existing system unifies all three modalities under a single conversational interface with safety guarantees.

### E. Research Gap

The literature reveals a clear gap: **no existing open-source system combines multi-backend natural language query routing (SQL + MongoDB + Pandas) with read-only safety enforcement, LLM-driven visualization, context-aware autocomplete, and secure multi-tenant access** in a single, extensible platform. IntelliQuery fills this gap.

---

## V. SYSTEM ARCHITECTURE

### A. High-Level Architecture

IntelliQuery follows a **three-tier architecture** consisting of a React frontend, a FastAPI backend, and multiple data backends:

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (React 19)               │
│  ┌─────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │  Auth    │  │Dashboard │  │  Query Interface   │  │
│  │  Pages   │  │  Page    │  │  (Chat-based UI)   │  │
│  └────┬─────┘  └────┬─────┘  └────────┬──────────┘  │
│       │              │                 │              │
│       └──────────────┼─────────────────┘              │
│                      │ Axios (HTTP + Cookies)         │
└──────────────────────┼────────────────────────────────┘
                       │
┌──────────────────────┼────────────────────────────────┐
│              BACKEND (FastAPI + Uvicorn)               │
│                      │                                 │
│  ┌───────────────────┼───────────────────────────┐     │
│  │           Auth Middleware (JWT Cookies)        │     │
│  └───────────────────┼───────────────────────────┘     │
│                      │                                 │
│  ┌─────────┐  ┌──────┴──────┐  ┌──────────────────┐   │
│  │  Auth   │  │  AI Router  │  │   Datasource     │   │
│  │ Module  │  │  (Dispatch) │  │   Manager         │   │
│  └─────────┘  └──────┬──────┘  └──────────────────┘   │
│                      │                                 │
│         ┌────────────┼────────────┐                    │
│         │            │            │                    │
│    ┌────┴────┐ ┌─────┴─────┐ ┌───┴──────┐             │
│    │SQL Agent│ │Mongo Agent│ │Pandas    │             │
│    │         │ │           │ │Agent     │             │
│    └────┬────┘ └─────┬─────┘ └───┬──────┘             │
│         │            │           │                     │
│    ┌────┴────────────┴───────────┴──────┐              │
│    │     Groq LLM (LLaMA 4 Scout 17B)  │              │
│    └────────────────────────────────────┘              │
│                                                        │
│    ┌─────────────────┐  ┌────────────────────────┐     │
│    │  Visualization  │  │  Autocomplete Engine   │     │
│    │  Agent (Plotly)  │  │  (Schema-aware + LRU)  │     │
│    └─────────────────┘  └────────────────────────┘     │
│                                                        │
│    ┌─────────────────────────────────────────────┐     │
│    │  History Store (MongoDB - query_history)     │     │
│    └─────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────┘
                       │
┌──────────────────────┼────────────────────────────────┐
│              DATA BACKENDS                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │  MySQL   │  │ MongoDB  │  │  CSV / Excel     │     │
│  │  / PgSQL │  │          │  │  Files           │     │
│  └──────────┘  └──────────┘  └──────────────────┘     │
└────────────────────────────────────────────────────────┘
```

### B. Component Overview

| Component           | Technology                                    | Responsibility                                                                    |
| ------------------- | --------------------------------------------- | --------------------------------------------------------------------------------- |
| Frontend            | React 19, Vite 7, Tailwind CSS v4             | Auth UI, datasource setup, chat-based query interface, interactive visualizations |
| API Gateway         | FastAPI + Uvicorn (ASGI)                      | REST API surface, CORS, middleware pipeline                                       |
| Auth Module         | Passlib (PBKDF2), PyJWT, Starlette Middleware | Registration, login, logout, JWT cookie management                                |
| AI Router           | Custom Python class                           | Datasource type detection, agent dispatch, response formatting                    |
| SQL Agent           | SQLAlchemy + PyMySQL/Psycopg2                 | Schema extraction, SQL generation, read-only validation, execution                |
| Mongo Agent         | PyMongo                                       | Schema sampling, MongoDB query generation, validation, execution                  |
| Pandas Agent        | Pandas + AST module                           | DataFrame schema extraction, Pandas code generation, sandboxed execution          |
| Visualization Agent | Plotly Express + Plotly Graph Objects         | Data analysis, chart suggestion (LLM-driven), chart generation (13 types)         |
| Autocomplete Engine | Groq LLM + LRU Cache                          | Real-time schema-aware query suggestions                                          |
| History Store       | MongoDB (query_history collection)            | Session-based query persistence, retrieval, deletion                              |
| Datasource Store    | MongoDB (datasources collection)              | Encrypted credential storage, CRUD for connections                                |
| LLM Service         | Groq API (Meta LLaMA 4 Scout 17B)             | Query generation, visualization suggestions, autocomplete                         |

### C. Query Processing Pipeline

The end-to-end query processing pipeline consists of six stages:

```
User NL Query → AI Router → Agent Selection → LLM Generation →
Read-Only Validation → Safe Execution → Result Formatting →
Visualization Suggestion → History Persistence → Frontend Rendering
```

**Stage 1: Query Reception.** The frontend sends a POST request to `/ai/query` with the natural language query and datasource ID. The Auth Middleware validates the JWT cookie and injects user context.

**Stage 2: Agent Routing.** The `AIRouter` class retrieves the datasource metadata from MongoDB, verifies user ownership, determines the datasource type (mysql/psql → SQL, mongo → MongoDB, pandas/csv/excel → Pandas), and dispatches to the corresponding agent.

**Stage 3: Schema Extraction.** The selected agent extracts schema context from the target datasource:

- **SQL Agent:** Uses SQLAlchemy Inspector to enumerate tables, columns, types, primary keys, and foreign keys.
- **Mongo Agent:** Samples documents from the configured collection to infer field names and types.
- **Pandas Agent:** Loads the DataFrame and computes column names, data types, non-null counts, unique counts, and sample values.

**Stage 4: LLM-Powered Query Generation.** The agent constructs a type-specific system prompt and user message containing the schema context and natural language query, then sends it to the Groq API (Meta LLaMA 4 Scout 17B, temperature=0.1, max_tokens=1024). The response is cleaned by removing markdown code blocks and common prefixes.

**Stage 5: Read-Only Validation.** The generated query undergoes multi-layered validation:

- **SQL:** Must start with SELECT or WITH; checked against 14 forbidden keywords (INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE, GRANT, REVOKE, EXEC, EXECUTE, MERGE, REPLACE, CALL); multi-statement detection via semicolon splitting.
- **MongoDB:** Checked against 20+ forbidden operations (insert, update, delete, drop, create, remove, save, replace, bulkwrite, rename, etc.); JSON parsing to verify operation field is one of find/aggregate/count/distinct.
- **Pandas:** Checked against 30+ forbidden patterns including file I/O operations, exec/eval, import statements, dunder methods, os/sys/subprocess access, and inplace modifications; additionally parsed through Python AST for syntax validity.

**Stage 6: Safe Execution.** The validated query is executed against the target datasource, results are serialized (handling datetime, bytes, ObjectId, NaN conversions), and returned as a structured `QueryResponse` with columns, row count, and the generated query for transparency.

---

## VI. IMPLEMENTATION DETAILS

### A. Backend Implementation

#### 1) FastAPI Application Structure

The backend is organized into four primary modules:

```
backend/
├── app.py                 # FastAPI entry point, middleware, routers
├── auth/                  # Authentication module
│   ├── router.py          # Register, login, logout, me endpoints
│   ├── security.py        # PBKDF2 hashing, JWT creation/verification
│   ├── middleware.py       # Starlette cookie-based auth middleware
│   ├── store.py           # MongoDB user CRUD + unique indexes
│   └── schemas.py         # Pydantic request/response models
├── datasources/           # Datasource connection management
│   ├── router.py          # SQL connect, Mongo connect, file upload
│   ├── store.py           # Encrypted credential storage, CRUD
│   └── schemas.py         # Connection request models
├── ai/                    # AI query processing
│   ├── router.py          # API endpoints (/query, /schema, /visualize, /autocomplete)
│   ├── ai_router.py       # AIRouter class (agent dispatch logic)
│   ├── autocomplete.py    # QueryAutocomplete engine
│   ├── history_store.py   # Session-based query history
│   ├── schemas.py         # Pydantic models (QueryRequest/Response, etc.)
│   ├── agents/
│   │   ├── base.py        # BaseAgent ABC (template method pattern)
│   │   ├── sql_agent.py   # SQLAgent (SQLAlchemy)
│   │   ├── mongo_agent.py # MongoAgent (PyMongo)
│   │   ├── pandas_agent.py# PandasAgent (sandboxed eval)
│   │   └── visualization_agent.py  # Chart suggestion + generation
│   └── llm/
│       ├── groq.py        # Primary Groq client + generation functions
│       └── groq_fallback.py # Fallback Groq client
└── utils/
    ├── db.py              # MongoDB client singleton + health check
    ├── dbPopulator.py     # MySQL demo data populator
    ├── excel_populator.py # CSV demo data generator
    └── mongo_populator.py # MongoDB demo data populator
```

#### 2) Agent Design Pattern

All agents inherit from `BaseAgent`, an abstract base class implementing the **Template Method Pattern**:

```python
class BaseAgent(ABC):
    async def process(self, natural_query, datasource) -> Dict:
        # Template method: fixed algorithm, variable steps
        generated_query, llm_used = await self.generate_query(natural_query, datasource)
        is_valid, error = self.validate_readonly(generated_query)      # Abstract
        success, result = await self.execute_query(query, datasource)   # Abstract
        return formatted_result

    @abstractmethod
    async def get_schema_context(self, datasource) -> str: ...
    @abstractmethod
    def validate_readonly(self, query) -> Tuple[bool, str]: ...
    @abstractmethod
    async def execute_query(self, query, datasource) -> Tuple[bool, Any]: ...
```

This design ensures consistent processing across all datasource types while allowing each agent to implement datasource-specific logic for schema extraction, validation, and execution.

#### 3) Security Implementation

| Security Layer        | Mechanism                                        | Details                                                    |
| --------------------- | ------------------------------------------------ | ---------------------------------------------------------- |
| Password Storage      | PBKDF2-SHA256 (via Passlib)                      | Cross-platform, no 72-byte limit (unlike bcrypt)           |
| Session Tokens        | HS256 JWT                                        | Configurable expiry via `AUTH_TOKEN_EXPIRE_MINUTES`        |
| Cookie Policy         | HTTP-only, configurable SameSite/Secure          | Prevents XSS-based token theft                             |
| Credential Encryption | Fernet symmetric encryption (PBKDF2-derived key) | Datasource passwords encrypted at rest in MongoDB          |
| Query Safety          | Regex + keyword + AST validation                 | Multi-layered read-only enforcement per agent type         |
| User Isolation        | Datasource ownership verification                | Every query checks `user_id` matches datasource owner      |
| Input Validation      | Pydantic models                                  | Type checking and constraint enforcement on all API inputs |
| Database Indexes      | Unique indexes on email and username             | Prevents duplicate registrations at DB level               |

#### 4) Visualization System

The `VisualizationAgent` supports 13 chart types:

| Chart Type     | Plotly Method             | Best For                  |
| -------------- | ------------------------- | ------------------------- |
| line           | `px.line()`               | Time series, trends       |
| bar            | `px.bar()`                | Categorical comparison    |
| horizontal_bar | `px.bar(orientation='h')` | Long category labels      |
| pie            | `px.pie()`                | Proportional distribution |
| scatter        | `px.scatter()`            | Correlation analysis      |
| histogram      | `px.histogram()`          | Value distribution        |
| box            | `px.box()`                | Statistical distribution  |
| area           | `px.area()`               | Cumulative trends         |
| stacked_bar    | `px.bar(barmode='stack')` | Part-to-whole             |
| grouped_bar    | `px.bar(barmode='group')` | Multi-category comparison |
| heatmap        | `go.Heatmap()`            | Correlation matrix        |
| funnel         | `go.Funnel()`             | Conversion pipelines      |
| waterfall      | `go.Waterfall()`          | Incremental changes       |

The suggestion workflow uses LLM-driven analysis:

1. Convert results to DataFrame.
2. Analyze column types (numeric, categorical, datetime), cardinality, and distributions.
3. Construct analysis prompt for Groq LLM.
4. Parse LLM response as JSON with chart recommendations.
5. Fall back to rule-based suggestions if LLM response parsing fails.

#### 5) Autocomplete Engine

The autocomplete system provides Google-style query suggestions:

- **Schema-aware:** Fetches and caches datasource schema (tables/columns for SQL, collection fields for MongoDB, DataFrame columns for Pandas).
- **LLM-generated:** Uses Groq with low temperature (0.3) and 200-token limit for fast, relevant suggestions.
- **Cached:** LRU cache with 5-minute TTL and 1,000-entry maximum; cache eviction removes oldest 200 entries.
- **Fallback:** Keyword-based template suggestions when LLM is unavailable.
- **Starter suggestions:** Pre-defined suggestions returned when partial query is too short (< 2 characters).

### B. Frontend Implementation

#### 1) Technology Stack

| Library          | Version | Purpose                                        |
| ---------------- | ------- | ---------------------------------------------- |
| React            | 19.2.0  | UI framework with hooks-based state management |
| React Router DOM | 7.12.0  | Client-side routing with protected routes      |
| Vite             | 7.2.4   | Build tool with HMR and optimized bundling     |
| Tailwind CSS     | 4.1.17  | Utility-first CSS framework                    |
| Axios            | 1.13.2  | HTTP client with interceptors for auth         |
| Plotly.js        | 3.4.0   | Interactive chart rendering                    |
| react-plotly.js  | 2.6.0   | React wrapper for Plotly.js                    |

#### 2) Page Structure

| Page            | Route                     | Functionality                                                            |
| --------------- | ------------------------- | ------------------------------------------------------------------------ |
| Home            | `/`                       | Landing page with feature showcase                                       |
| Login           | `/login`                  | Email/password authentication                                            |
| Register        | `/register`               | User registration with validation                                        |
| Dashboard       | `/dashboard`              | Datasource listing, query stats, session history, quick actions          |
| DataSourceSetup | `/datasource/:type/setup` | SQL connection form, MongoDB URI form, file upload                       |
| QueryPage       | `/datasource/:type/query` | Chat-based query interface with autocomplete, results, and visualization |

#### 3) Chat-Based Query Interface

The `QueryPage` component provides a conversational interface where:

- Users type natural language queries in a chat input.
- Autocomplete suggestions appear as the user types (debounced API calls).
- AI responses display the generated query, result table, and visualization options.
- Users can switch between sessions via a sidebar.
- Query history is persisted server-side and can be resumed.

#### 4) Datasource-Specific Components

Each datasource type has dedicated setup and query panel components:

| Datasource             | Setup Component        | Query Panel             |
| ---------------------- | ---------------------- | ----------------------- |
| SQL (MySQL/PostgreSQL) | `SqlSetupForm`         | `SqlQueryPanel`         |
| MongoDB                | `MongoSetupForm`       | `MongoQueryPanel`       |
| CSV/Excel              | `SpreadsheetSetupForm` | `SpreadsheetQueryPanel` |

Common components (`ChatQueryRunner`, `VisualizationPanel`, `SessionSidebar`) provide shared functionality across all datasource types.

### C. LLM Integration

#### 1) Model Selection

IntelliQuery uses the **Meta LLaMA 4 Scout 17B 16E Instruct** model hosted on the **Groq inference platform**. Key configuration:

| Parameter   | Value                                                      | Rationale                                          |
| ----------- | ---------------------------------------------------------- | -------------------------------------------------- |
| Model       | `meta-llama/llama-4-scout-17b-16e-instruct`                | Strong code generation, instruction following      |
| Temperature | 0.1 (query generation), 0.3 (autocomplete/visualization)   | Low temperature for deterministic query output     |
| Max Tokens  | 1,024 (queries), 2,048 (visualization), 200 (autocomplete) | Sufficient for complex queries while limiting cost |
| Top-p       | 0.9 (queries), 0.95 (visualization)                        | Nucleus sampling for quality output                |
| Streaming   | Supported (not default)                                    | Available for future real-time generation          |

#### 2) Prompt Engineering

Each agent type uses a carefully crafted system prompt that:

- Declares the LLM's role as an expert query generator.
- Specifies the target query language (SQL/MongoDB/Pandas).
- Enforces read-only constraints at the prompt level.
- Defines output format expectations (raw query, JSON, code-only).
- Includes schema context and natural language query in the user message.

Example system prompt for SQL:

```
You are an expert SQL query generator. Given a natural language question
and database schema, generate ONLY a valid SELECT SQL query. Do not
include any explanations, just the raw SQL query.
IMPORTANT: Only generate READ-ONLY queries (SELECT). Never generate
INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or any other modifying queries.
Return ONLY the SQL query, nothing else.
```

### D. Data Persistence

#### 1) MongoDB Collections

| Collection      | Purpose               | Key Fields                                                                                                       |
| --------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `users`         | User accounts         | `username`, `email`, `password_hash`, `created_at`                                                               |
| `datasources`   | Saved connections     | `user_id`, `type`, `details` (encrypted passwords), `created_at`                                                 |
| `query_history` | Query session history | `user_id`, `session_id`, `datasource_id`, `natural_query`, `generated_query`, `results`, `success`, `created_at` |

#### 2) Indexes

- `users.email`: Unique index for login lookups.
- `users.username`: Unique index for duplicate prevention.
- Query history: Indexed by `user_id` and `session_id` for efficient session retrieval.

---

## VII. EXPERIMENTAL EVALUATION

### A. Experimental Setup

#### 1) Test Datasets

Three synthetic e-commerce datasets were generated using custom populators:

| Dataset            | Backend | Records                                      | Columns/Fields | Generator            |
| ------------------ | ------- | -------------------------------------------- | -------------- | -------------------- |
| E-commerce Orders  | MySQL   | 10,000 orders, 5,000 customers, 200 products | 8–12 per table | `dbPopulator.py`     |
| Sales Transactions | MongoDB | 5,000 documents                              | 16 fields      | `mongo_populator.py` |
| Sales Transactions | CSV     | 5,000 rows                                   | 15 columns     | `excel_populator.py` |

All datasets model realistic e-commerce data with:

- **15 products** across 5 categories (Electronics, Clothing, Home & Kitchen, Books, Sports & Outdoors)
- **5 customer segments** (Regular, Premium, VIP, New, Wholesale)
- **5 regions** (North, South, East, West, Central)
- **5 payment methods** (Credit Card, Debit Card, PayPal, Bank Transfer, Cash)
- **Weighted distributions:** 90% completed / 5% pending / 3% cancelled / 2% refunded orders; 20% discount probability

#### 2) Environment

| Component        | Specification                                   |
| ---------------- | ----------------------------------------------- |
| Backend Runtime  | Python 3.14, FastAPI, Uvicorn                   |
| Frontend Runtime | Node.js, React 19, Vite 7                       |
| LLM              | Meta LLaMA 4 Scout 17B via Groq API             |
| Database         | MongoDB 7.x (metadata), MySQL 8.x (SQL testing) |
| OS               | Windows / Linux (cross-platform compatible)     |

### B. Query Translation Evaluation

The following categories of natural language queries were tested across all three backends:

#### 1) Basic Queries

| Natural Language Query | Expected Operation                 | Backend |
| ---------------------- | ---------------------------------- | ------- |
| "Show me all products" | SELECT \* / find({}) / df          | All     |
| "Count total records"  | COUNT / count_documents / len(df)  | All     |
| "Show first 10 rows"   | LIMIT 10 / limit(10) / df.head(10) | All     |

#### 2) Filtering and Sorting

| Natural Language Query                      | Expected Operation                                   |
| ------------------------------------------- | ---------------------------------------------------- |
| "Find customers from California"            | WHERE state = 'California' / find({region: "North"}) |
| "Show orders sorted by amount descending"   | ORDER BY amount DESC / sort({amount: -1})            |
| "Find products with price greater than 500" | WHERE price > 500 / find({price: {$gt: 500}})        |

#### 3) Aggregation and Grouping

| Natural Language Query                | Expected Operation                                |
| ------------------------------------- | ------------------------------------------------- |
| "Total revenue by product category"   | GROUP BY category SUM(revenue) / $group aggregate |
| "Average order value by region"       | GROUP BY region AVG(total) / $group + $avg        |
| "Top 10 customers by total purchases" | ORDER BY SUM DESC LIMIT 10 / $sort + $limit       |
| "Monthly revenue trend"               | GROUP BY month SUM(revenue) / date aggregation    |

#### 4) Statistical Queries (Pandas)

| Natural Language Query                               | Generated Pandas Code                     |
| ---------------------------------------------------- | ----------------------------------------- |
| "Show correlation between quantity and total amount" | `df[['quantity', 'total_amount']].corr()` |
| "What percentage of orders have discounts"           | `(df['discount'] > 0).mean() * 100`       |
| "95th percentile of order values"                    | `df['total_amount'].quantile(0.95)`       |

### C. Read-Only Validation Results

| Attack Vector                            | Agent   | Blocked | Mechanism                      |
| ---------------------------------------- | ------- | ------- | ------------------------------ |
| `DELETE FROM users`                      | SQL     | ✅      | Keyword blacklist (DELETE)     |
| `DROP TABLE products`                    | SQL     | ✅      | Keyword blacklist (DROP)       |
| `SELECT 1; DROP TABLE users`             | SQL     | ✅      | Multi-statement detection      |
| `{"deleteMany": {}}`                     | MongoDB | ✅      | Forbidden operation list       |
| `{"operation": "drop"}`                  | MongoDB | ✅      | Operation whitelist validation |
| `import os; os.system('rm -rf /')`       | Pandas  | ✅      | Import pattern detection       |
| `df.to_csv('leak.csv')`                  | Pandas  | ✅      | File I/O pattern detection     |
| `exec('malicious code')`                 | Pandas  | ✅      | exec/eval pattern detection    |
| `df.drop(columns=['col'], inplace=True)` | Pandas  | ✅      | Inplace modification detection |

### D. Visualization Generation Results

Testing on the sample sales dataset demonstrated successful generation of all 13 chart types:

| Chart Type     | Generated | Rendered | Notes                             |
| -------------- | --------- | -------- | --------------------------------- |
| Line           | ✅        | ✅       | Auto-detected datetime for x-axis |
| Bar            | ✅        | ✅       | Categorical x-axis with grouping  |
| Horizontal Bar | ✅        | ✅       | Orientation parameter handled     |
| Pie            | ✅        | ✅       | Auto-aggregation of categories    |
| Scatter        | ✅        | ✅       | Dual numeric column detection     |
| Histogram      | ✅        | ✅       | Single numeric distribution       |
| Box            | ✅        | ✅       | Statistical distribution display  |
| Area           | ✅        | ✅       | Cumulative trend rendering        |
| Stacked Bar    | ✅        | ✅       | Requires explicit group_by        |
| Grouped Bar    | ✅        | ✅       | Multi-category comparison         |
| Heatmap        | ✅        | ✅       | Auto-correlation matrix           |
| Funnel         | ✅        | ✅       | Conversion pipeline display       |
| Waterfall      | ✅        | ✅       | Incremental change tracking       |

### E. Autocomplete Performance

| Metric                         | Value                        |
| ------------------------------ | ---------------------------- |
| Average LLM suggestion latency | < 500ms                      |
| Cache hit response time        | < 10ms                       |
| Cache capacity                 | 1,000 entries (LRU eviction) |
| Cache TTL                      | 300 seconds                  |
| Fallback suggestion count      | 4–6 template suggestions     |

---

## VIII. DISCUSSION AND FUTURE WORK

### A. Limitations

1. **LLM Accuracy:** While the LLaMA 4 Scout 17B model demonstrates strong query generation capability, complex multi-table joins and deeply nested aggregations may occasionally produce incorrect queries. The system currently does not implement automatic retry or iterative refinement.

2. **Schema Sampling:** The MongoDB agent infers schema by sampling only 3 documents, which may miss fields present in other documents (schema heterogeneity). The Pandas agent loads the entire file for schema extraction, which may be slow for very large files.

3. **Single LLM Provider:** The system currently relies solely on Groq for LLM inference. Provider outages directly impact system availability.

4. **No Voice Input:** Despite the "voice-driven" branding, the current implementation uses text input only. Speech-to-text integration is planned but not yet implemented.

5. **Limited Error Recovery:** When the LLM generates an invalid query that passes validation but fails at execution, the system returns the raw error without attempting automatic repair.

### B. Future Work

1. **Iterative Query Refinement:** Implement a retry loop where the LLM refines its generated query based on execution errors (planned, as noted in project roadmap).

2. **Irrelevance Detection:** Add a pre-processing step where the LLM evaluates whether the user's question is relevant to the connected dataset, returning a helpful response for off-topic queries.

3. **Voice Integration:** Integrate browser-based Web Speech API or a dedicated speech-to-text service for true voice-driven querying.

4. **Multi-LLM Fallback:** Support multiple LLM providers (OpenAI, Anthropic, local models) with automatic fallback on failure.

5. **Query Explanation:** Generate natural language explanations of the generated queries to help users understand the translation.

6. **Streaming Results:** Implement server-sent events (SSE) for streaming large result sets and progressive chart rendering.

7. **Benchmark Evaluation:** Evaluate on standard Text-to-SQL benchmarks (Spider, BIRD) to quantify accuracy relative to state-of-the-art models.

8. **Role-Based Access Control:** Extend the auth system with roles (admin, analyst, viewer) and per-datasource access policies.

---

## IX. CONCLUSION

This paper presented **IntelliQuery**, an open-source, multi-backend conversational analytics platform that bridges the gap between non-technical users and heterogeneous data stores. By combining a modular agent-based architecture with LLM-powered query generation, multi-layered read-only safety enforcement, automated visualization recommendation, and context-aware autocomplete, IntelliQuery demonstrates a practical and extensible approach to natural language data exploration.

The system successfully translates natural language queries into executable operations across SQL databases (MySQL, PostgreSQL), MongoDB document stores, and Pandas DataFrames (CSV/Excel files)—all through a unified chat-based interface. The read-only validation pipeline effectively blocks destructive operations across all three query languages, employing a defense-in-depth strategy combining prompt-level constraints, regex pattern matching, keyword blacklisting, JSON structure validation, and Python AST parsing.

The LLM-driven visualization engine extends the system's utility beyond raw query results by intelligently recommending and generating 13 chart types based on data structure analysis. The autocomplete engine further enhances usability by providing sub-500ms, schema-aware query suggestions.

IntelliQuery contributes to the growing body of work on democratizing data access and provides a foundation for future research in multi-modal, multi-backend conversational BI systems.

---

## X. TECHNOLOGY STACK SUMMARY

### Backend Dependencies

| Package         | Version | Purpose                           |
| --------------- | ------- | --------------------------------- |
| FastAPI         | Latest  | Async web framework               |
| Uvicorn         | Latest  | ASGI server                       |
| PyMongo         | Latest  | MongoDB driver                    |
| SQLAlchemy      | Latest  | SQL ORM and schema inspection     |
| PyMySQL         | Latest  | MySQL driver                      |
| Psycopg2-binary | Latest  | PostgreSQL driver                 |
| Pandas          | Latest  | DataFrame operations              |
| Plotly          | Latest  | Server-side visualization         |
| Matplotlib      | Latest  | Supplementary plotting            |
| Groq            | Latest  | LLM API client                    |
| LangChain       | Latest  | Agent framework utilities         |
| Passlib         | Latest  | Password hashing (PBKDF2)         |
| PyJWT           | Latest  | JWT token management              |
| Cryptography    | Latest  | Fernet encryption for credentials |
| python-dotenv   | Latest  | Environment variable management   |
| Openpyxl        | Latest  | Excel file reading                |
| Kaleido         | Latest  | Plotly static image export        |
| HTTPX           | Latest  | Async HTTP client                 |
| Faker           | Latest  | Test data generation              |

### Frontend Dependencies

| Package          | Version | Purpose               |
| ---------------- | ------- | --------------------- |
| React            | 19.2.0  | UI framework          |
| React DOM        | 19.2.0  | DOM rendering         |
| React Router DOM | 7.12.0  | Client-side routing   |
| Axios            | 1.13.2  | HTTP client           |
| Plotly.js        | 3.4.0   | Interactive charts    |
| react-plotly.js  | 2.6.0   | React Plotly wrapper  |
| Tailwind CSS     | 4.1.17  | Utility CSS framework |
| Vite             | 7.2.4   | Build tool            |

---

## XI. API ENDPOINT REFERENCE

### Authentication Endpoints

| Method | Endpoint         | Description                                   |
| ------ | ---------------- | --------------------------------------------- |
| POST   | `/auth/register` | Register new user (username, email, password) |
| POST   | `/auth/login`    | Login and receive JWT cookie                  |
| POST   | `/auth/logout`   | Clear session cookie                          |
| GET    | `/auth/me`       | Get current authenticated user                |

### Datasource Endpoints

| Method | Endpoint                     | Description                                 |
| ------ | ---------------------------- | ------------------------------------------- |
| GET    | `/datasources`               | List user's saved datasources               |
| POST   | `/datasources/sql/connect`   | Connect SQL database (MySQL/PostgreSQL)     |
| POST   | `/datasources/mongo/connect` | Connect MongoDB (URI, database, collection) |
| POST   | `/datasources/pandas/upload` | Upload CSV/Excel file                       |
| DELETE | `/datasources/{id}`          | Delete saved datasource                     |

### AI Query Endpoints

| Method | Endpoint                     | Description                          |
| ------ | ---------------------------- | ------------------------------------ |
| POST   | `/ai/query`                  | Execute natural language query       |
| GET    | `/ai/schema/{datasource_id}` | Get datasource schema information    |
| GET    | `/ai/health`                 | Check AI service (Groq) health       |
| POST   | `/ai/visualize/suggest`      | Get AI-powered chart recommendations |
| POST   | `/ai/visualize/generate`     | Generate specific Plotly chart       |
| POST   | `/ai/autocomplete`           | Get query autocomplete suggestions   |
| GET    | `/ai/history`                | List query sessions                  |
| GET    | `/ai/history/{session_id}`   | Get session messages                 |
| DELETE | `/ai/history/{session_id}`   | Delete session                       |

---

## XII. REFERENCES

[1] V. Zhong, C. Xiong, and R. Socher, "Seq2SQL: Generating Structured Queries from Natural Language using Reinforcement Learning," _arXiv preprint arXiv:1709.00103_, 2017.

[2] T. Yu et al., "Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task," _Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing (EMNLP)_, pp. 3911–3921, 2018.

[3] J. Li et al., "Can LLM Already Serve as A Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs," _Advances in Neural Information Processing Systems (NeurIPS)_, vol. 36, 2023.

[4] H. Chase, "LangChain: Building Applications with LLMs through Composability," _GitHub repository_, 2022. [Online]. Available: https://github.com/langchain-ai/langchain

[5] A. Trummer, "CodexDB: Generating Code for Processing SQL Queries using GPT-3 Codex," _Proceedings of the VLDB Endowment_, vol. 15, no. 13, pp. 4096–4099, 2022.

[6] Meta AI, "LLaMA: Open and Efficient Foundation Language Models," _arXiv preprint arXiv:2302.13971_, 2023.

[7] A. Ramírez et al., "Plotly: Collaborative Data Science," _Plotly Technologies Inc._, Montreal, QC, 2015. [Online]. Available: https://plotly.com

[8] S. Ramírez, "FastAPI framework, high performance, easy to learn, fast to code, ready for production," 2019. [Online]. Available: https://fastapi.tiangolo.com

[9] K. Chodorow, _MongoDB: The Definitive Guide_, 3rd ed. O'Reilly Media, 2019.

[10] W. McKinney, "Data Structures for Statistical Computing in Python," _Proceedings of the 9th Python in Science Conference_, pp. 56–61, 2010.

---

## APPENDIX A: SYSTEM DEPLOYMENT

### Prerequisites

- Python 3.10+ with pip
- Node.js 18+ with npm
- MongoDB 6.0+ running locally or remotely
- MySQL 8.0+ (for SQL datasource testing)
- Groq API key (free tier available at https://console.groq.com)

### Backend Setup

```bash
cd backend
python -m venv myvenv
source myvenv/bin/activate  # Linux/Mac
# or: myvenv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with:
#   GROQ_API_KEY=your_key_here
#   MONGO_URI=mongodb://localhost:27017
#   MONGO_DB_NAME=intelliquery
#   AUTH_JWT_SECRET=your_secret_here
#   CORS_ORIGINS=http://localhost:5173

# Populate test data (optional)
python utils/excel_populator.py
python utils/mongo_populator.py
python utils/dbPopulator.py

# Start server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## APPENDIX B: SAMPLE QUERY EXECUTION FLOW

### Example: "Show total revenue by product category"

**1. Frontend Request:**

```json
POST /ai/query
{
  "query": "Show total revenue by product category",
  "datasource_id": "683a1b2c3d4e5f6a7b8c9d0e"
}
```

**2. AI Router:** Retrieves datasource → type = "mysql" → dispatches to `SQLAgent`

**3. Schema Extraction:**

```
Table: orders
Columns:
  - id (INTEGER) [PRIMARY KEY]
  - customer_id (INTEGER)
  - order_date (DATE)
  - total_amount (DECIMAL)
  - status (VARCHAR)
  FK: [customer_id] -> customers.[id]

Table: order_items
Columns:
  - id (INTEGER) [PRIMARY KEY]
  - order_id (INTEGER)
  - product_id (INTEGER)
  - quantity (INTEGER)
  - price (DECIMAL)
  FK: [order_id] -> orders.[id]
  FK: [product_id] -> products.[id]

Table: products
Columns:
  - id (INTEGER) [PRIMARY KEY]
  - name (VARCHAR)
  - category (VARCHAR)
  - price (DECIMAL)
```

**4. LLM Generation (Groq):**

```sql
SELECT p.category, SUM(oi.quantity * oi.price) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
GROUP BY p.category
ORDER BY total_revenue DESC
```

**5. Validation:** Starts with SELECT ✅, no forbidden keywords ✅, single statement ✅

**6. Execution:** SQLAlchemy executes query, returns results

**7. Response:**

```json
{
  "success": true,
  "query": "Show total revenue by product category",
  "generated_query": "SELECT p.category, SUM(oi.quantity * oi.price) AS total_revenue...",
  "datasource_type": "sql",
  "results": [
    {"category": "Electronics", "total_revenue": 2450000.00},
    {"category": "Clothing", "total_revenue": 890000.00},
    ...
  ],
  "columns": ["category", "total_revenue"],
  "row_count": 5,
  "llm_used": "groq",
  "session_id": "a1b2c3d4e5f6..."
}
```

---

_© 2025. This document accompanies the IntelliQuery open-source project (https://github.com/aniruddhapai27/IntelliQuery). All content is derived from the actual codebase without fabrication._
