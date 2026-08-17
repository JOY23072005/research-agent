# OSINT Entity Research Agent

## 1. Project Purpose

This project is a bounded, evidence-driven **OSINT-style entity/business research agent**.

The user supplies a person, business, organization, website, or domain and asks the system to perform extensive public-web research and return a **strict JSON result**.

The system must:

- stay focused on the exact entity supplied by the user
- never merge similarly named entities without evidence
- never invent facts
- never invent URLs
- provide citations/evidence for factual findings
- use `N/A` only when appropriate and always provide a reason
- perform multiple research rounds when important information is still missing
- stop after a fixed maximum number of research rounds
- return structured JSON rather than a prose report

The intended long-term deployment is company-side AWS agent orchestration with Lambda-backed tools. The current implementation is local Python using NVIDIA, LangChain, and LangGraph.

---

# 2. Exact Business Query / Requirement

The system will eventually process queries equivalent to:

> for this website/linkedin/instamart - any person or business - Give me the following details after extensive search:
>
> website description | products being sold | digital vs physical products | link of shipping policy | link of terms of use | all social media links - instagram, facebook, linkedin, twitter, google reviews, etc. | pricing of various products | all gst number, pan/tan/tin number | all emails | all phone number with state and country codes | all owner/md/ceo/cxo names | all addresses | do an extensive web search | refer to indiamart, shopify, tradeindia, justdial and other portals if any association is present | Linkedin profiles of CXOs | make sure you stick to the exact name of the website with similar names | Give me a json with all info rather than plain-text | give me citations for everything | NO HALLUCINATION | NO MAKING OF LINKS | ONLY VERIFIED INFO | DO AS MANY WEB SEARCH POSSIBLE | DONOT DEVIATE FROM THE NAME GIVEN IF THAT IS NOT VALID - SAY N/A FOR EVERYTHING | PROVIDE ONE THING - REASON FOR N/A - NOT A VALID DOMAIN/ DOMAIN ACCESSIBLE BUT SEEMS PARKED PAGE DUMMY PAGE ETC.

The final implementation must treat this as an **evidence and verification problem**, not merely a scraping problem.

---

# 3. FINAL LOCKED ARCHITECTURE

**Do not replace or redesign this architecture.**

```text
                         NVIDIA LLM
                              │
                              ▼
                         LangGraph
                              │
                    ┌─────────┼──────────┐
                    ▼         ▼          ▼
                 Search     OSINT      Browser
                    │         │          │
                   DDGS   OSINT adapters Playwright
                              │
                              │
                    ┌─────────┼──────────┐
                    ▼         ▼          ▼
                 Maigret   OpenOSINT   other
                                      selected
                                      capabilities
                              │
                              ▼
                         Tool Results
                              │
                              ▼
                       Research State
                              │
                              ▼
                     Research Analyzer
                              │
                              ▼
                          Validator
                         /         \
                     retry       finalize
                                  │
                                  ▼
                                 JSON
```

## Locked technology choices

| Component | Choice |
|---|---|
| LLM | NVIDIA API |
| Current model | `nvidia/nemotron-3.5-lightning-30b-a3b` |
| LLM orchestration interface | LangChain |
| Workflow/state orchestration | LangGraph |
| Search | DDGS |
| Browser | Playwright |
| OSINT | Existing open-source OSINT capabilities, exposed through our own adapters |
| State | LangGraph `ResearchState` |
| Data models | Pydantic |
| Final output | Strict structured JSON |
| Max research rounds | 5 |
| Docker | **Not used** |
| SearXNG | **Not used** |
| Gemini | **Not used for this project** |
| Bedrock | Future migration only |
| Bedrock/AgentCore | Future company deployment only |

### Important architecture rule

The LLM is the **planner/analyzer**.

LangGraph is the **workflow/state machine**.

The registry is the **controlled tool directory**.

Tools are the **execution capabilities**.

Research state is the **persistent working memory**.

Validator is the **quality gate**.

Do not collapse these responsibilities into one component.

---

# 4. Current Project Structure

Current/final intended structure:

```text
research-agent/
│
├── agent/
│   ├── graph.py
│   ├── state.py
│   ├── prompts.py
│   ├── executor.py
│   └── analyzer.py
│
├── tools/
│   ├── registry.py
│   ├── search.py
│   ├── browser.py
│   ├── extractor.py
│   ├── osint.py
│   └── verification.py
│
├── schemas.py
├── llm.py
├── main.py
├── requirements.txt
└── .env
```

`tools/osint.py` and `tools/verification.py` are not fully implemented yet.

---

# 5. Work Completed

## Step 1 — Project setup

A Python virtual environment is being used.

Environment variables are stored in `.env`.

Expected variables include:

```env
NVIDIA_API_KEY=...
NVIDIA_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b
```

`.env` is excluded from Git.

---

# 6. `schemas.py` completed

Pydantic models were created for the core data contract.

Current important models:

```python
class Evidence(BaseModel):
    url: str
    title: str | None = None
    source_type: str | None = None
    snippet: str | None = None
```

```python
class Finding(BaseModel):
    value: str | None = None
    status: Literal[
        "verified",
        "not_found",
        "conflicting",
        "not_applicable"
    ]
    reason: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
```

```python
class EntityValidation(BaseModel):
    input_name: str
    status: Literal[
        "valid",
        "invalid",
        "uncertain"
    ]
    entity_type: Literal[
        "person",
        "business",
        "organization",
        "domain",
        "unknown"
    ]
    canonical_name: str | None = None
    reason: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
```

```python
class ResearchStep(BaseModel):
    tool: str
    input: dict[str, Any]
```

```python
class ResearchPlan(BaseModel):
    steps: list[ResearchStep]
```

```python
class ResearchAnalysis(BaseModel):
    findings: list[Finding] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    contradictions: list[Finding] = Field(default_factory=list)
    next_research_required: bool
```

A `ResearchResult` model also exists for final structured output.

### Important schema rule

A missing value must not be represented as verified.

These meanings are intended:

```text
verified
    value exists and evidence supports it

not_found
    the requested information was searched for but not verified

not_applicable
    the field does not apply

conflicting
    credible sources disagree
```

A null value with `"verified"` is invalid and must later be rejected by validation.

---

# 7. `agent/state.py` completed

A `TypedDict` called `ResearchState` was created for LangGraph.

The state contains:

```text
query
entity
research_round
max_research_rounds
tools_executed
tool_results
sources
findings
claims
missing_fields
contradictions
research_plan
entity_valid
next_research_required
validation_passed
validation_errors
final_result
```

Conceptually:

```text
ResearchState
│
├── request
├── entity
├── current research round
├── executed tools
├── raw tool results
├── sources
├── findings
├── claims
├── missing fields
├── contradictions
├── research plan
├── validation status
└── final result
```

The state test passed.

---

# 8. `agent/graph.py` foundation completed

A basic LangGraph was created using:

```python
StateGraph(ResearchState)
```

The initial graph was:

```text
START
  ↓
initialize
  ↓
plan_research
  ↓
execute_tools
  ↓
analyze_research
  ↓
END
```

The graph foundation test passed.

### Current architectural meaning

LangGraph is responsible for:

- passing state between nodes
- controlling node transitions
- eventually controlling the bounded research loop
- eventually controlling conditional retry/finalization
- eventually supporting parallel execution

The LLM itself is not the workflow engine.

---

# 9. `llm.py` completed

LangChain's NVIDIA integration is used:

```python
from langchain_nvidia_ai_endpoints import ChatNVIDIA
```

The LLM is loaded from environment variables.

Current model:

```text
nvidia/nemotron-3.5-lightning-30b-a3b
```

The model successfully produced:

- normal text responses
- structured `ResearchPlan`
- structured `ResearchAnalysis`

### Known warning

LangChain currently warns that the selected NVIDIA model is not known to it as a structured-output-supported model.

However, the actual tests succeeded and returned valid structured Pydantic output.

**Do not switch models merely because of this warning.**

The current model is working for this project.

---

# 10. Planner completed

`agent/prompts.py` contains `RESEARCH_PLANNER_PROMPT`.

Planner responsibilities:

- understand the user request
- select available tools
- create a structured research plan
- stay on the exact supplied entity
- avoid hallucination
- avoid fabricated URLs
- avoid fabricated tool names
- avoid unresolved placeholders
- prefer real evidence
- avoid unnecessary tools

The planner has been successfully tested.

Example output produced:

```json
{
  "steps": [
    {
      "tool": "web_search",
      "input": {
        "query": "NVIDIA official website"
      }
    },
    {
      "tool": "web_search",
      "input": {
        "query": "NVIDIA corporate overview"
      }
    }
  ]
}
```

---

# 11. Tool Registry completed

`tools/registry.py` was created.

The registry maps tool names to actual Python functions and descriptions.

Current tools registered:

```text
web_search
fetch_page
extract_page
```

The registry supports:

```python
get_tool(name)
get_tool_descriptions()
list_tools()
```

An invalid tool name is rejected instead of allowing arbitrary Python execution.

Example:

```text
LLM requests:
some_random_tool

Registry:
tool does not exist

Executor:
rejects the request
```

This security boundary must remain.

---

# 12. Tool Executor completed

`agent/executor.py` was created.

Its responsibilities:

1. receive an LLM-generated `ResearchPlan`
2. inspect each step
3. resolve the tool through the registry
4. reject unknown tools
5. reject unresolved placeholder arguments
6. execute the registered Python function
7. capture success/failure
8. return normalized execution results

Conceptual flow:

```text
ResearchPlan
     ↓
Tool Executor
     ↓
Tool Registry
     ↓
Python function
     ↓
result
     ↓
tool_results
```

The executor test passed.

---

# 13. Search tool completed — DDGS

`tools/search.py` uses DDGS as the **fixed search implementation**.

DDGS was selected because it:

- requires no commercial search API key for the basic use case
- is easy to use from Python
- keeps the application simple
- avoids Docker
- avoids a separate SearXNG server

Current conceptual function:

```python
web_search(
    query: str,
    max_results: int = 10,
    region: str = "in-en",
)
```

It returns normalized JSON like:

```json
{
  "success": true,
  "query": "...",
  "results": [
    {
      "title": "...",
      "url": "...",
      "snippet": "..."
    }
  ]
}
```

Search tool was successfully executed through the registry.

### Fixed decision

**Do not replace DDGS with SearXNG, Google API, Bing API, Tavily, Brave, or another search implementation unless the project owner explicitly changes this architecture.**

---

# 14. Browser tool completed — Playwright

`tools/browser.py` was created using Playwright.

Current conceptual function:

```python
fetch_page(url, timeout=30000)
```

It:

- launches Chromium
- navigates to the URL
- waits for DOM content
- reads the page title
- extracts visible body text
- extracts anchor links
- captures status code
- returns final URL
- returns normalized JSON

Example result:

```json
{
  "success": true,
  "url": "https://www.nvidia.com/en-us/",
  "status_code": 200,
  "title": "World Leader in Artificial Intelligence Computing | NVIDIA",
  "text": "...",
  "links": [...]
}
```

The Playwright test passed.

### Important role

Playwright is the **browser capability**.

It is not the LLM.

It is not the analyzer.

It is not the validator.

---

# 15. Extractor completed — deterministic Python extraction

`tools/extractor.py` was created.

The extractor currently performs deterministic extraction from raw page data.

It can extract:

- emails
- phone numbers
- prices
- social-media links
- policy links
- page source information
- page links

Example:

```json
{
  "success": true,
  "source": {
    "url": "https://www.nvidia.com/en-us/",
    "title": "...",
    "status_code": 200
  },
  "emails": [],
  "phone_numbers": [],
  "prices": [],
  "social_links": [
    {
      "platform": "facebook",
      "url": "https://www.facebook.com/NVIDIA"
    },
    {
      "platform": "instagram",
      "url": "https://www.instagram.com/nvidia/?hl=en"
    },
    {
      "platform": "linkedin",
      "url": "https://www.linkedin.com/company/nvidia/"
    },
    {
      "platform": "twitter",
      "url": "https://twitter.com/nvidia"
    },
    {
      "platform": "youtube",
      "url": "https://www.youtube.com/user/nvidia"
    }
  ],
  "policy_links": [...]
}
```

The test passed.

### Known cleanup still needed

The extractor currently produces duplicate links in some cases.

Example:

- repeated YouTube URLs
- repeated privacy URLs

This will be handled later in the **normalization/evidence layer**.

Do not redesign the extractor unnecessarily.

---

# 16. Research Analyzer completed

`agent/analyzer.py` was created.

Its purpose:

- read tool results
- identify findings
- identify missing information
- identify contradictions
- determine whether additional research is required

It uses the `ResearchAnalysis` Pydantic schema.

The analyzer was tested independently and through LangGraph.

### Important lesson discovered

Search snippets alone are insufficient for reliable OSINT.

The real evidence path must be:

```text
Search
  ↓
candidate URL
  ↓
Browser
  ↓
real page content
  ↓
Extractor
  ↓
structured evidence
  ↓
Analyzer
```

The analyzer must not be treated as a substitute for page retrieval.

---

# 17. Current complete pipeline

The current working pipeline is:

```text
USER QUERY
    │
    ▼
NVIDIA LLM
    │
    ▼
Research Planner
    │
    ▼
ResearchPlan
    │
    ▼
Tool Executor
    │
    ▼
Tool Registry
    │
    ├── web_search → DDGS
    │
    ├── fetch_page → Playwright
    │
    └── extract_page → Python extractor
    │
    ▼
Tool Results
    │
    ▼
Research Analyzer
    │
    ▼
ResearchAnalysis
```

The bounded loop and final validator are **not completed yet**.

---

# 18. OSINT — CURRENT STATUS

OSINT is a **core architectural tool group**, but it has not yet been fully integrated.

### Important event

A PyPI package named:

```text
spiderfoot==0.0.1
```

was installed during investigation.

It is only a placeholder package:

```text
Summary: Reserved name placeholder. No functionality.
```

Its package contents were only:

```text
__init__.py
__pycache__
```

Therefore:

**Do not use `spiderfoot==0.0.1`.**

It should be uninstalled.

### Intended OSINT strategy

Do NOT implement every OSINT capability manually.

The goal is to reuse existing open-source libraries/tools with minimal API dependencies.

Candidates already identified:

- Maigret — username/social discovery
- OpenOSINT components — reusable OSINT capabilities
- selected lightweight Python libraries where needed
- other open-source tools only when they fit the fixed architecture

### OSINT must appear inside the existing Tool Registry

Conceptually:

```text
Tool Registry
│
├── web_search
│      └── DDGS
│
├── fetch_page
│      └── Playwright
│
├── extract_page
│      └── Python
│
└── OSINT
       ├── username_osint
       ├── email_osint
       ├── domain_osint
       ├── entity/person discovery
       └── other approved OSINT capabilities
```

Do not create a second AI agent inside the OSINT subsystem.

The top-level agent remains:

```text
NVIDIA + LangGraph
```

OSINT is just a **tool provider**.

---

# 19. What remains to build

The remaining project should be completed in this exact order:

```text
STEP 11
OSINT tool integration
    ↓
STEP 12
Evidence normalization / deduplication
    ↓
STEP 13
Exact entity validation
    ↓
STEP 14
Required-field tracking
    ↓
STEP 15
Bounded research loop (max 5 rounds)
    ↓
STEP 16
Claim verification
    ↓
STEP 17
Final JSON validator
    ↓
STEP 18
Parallel execution for independent tools
    ↓
STEP 19
Full end-to-end testing
    ↓
STEP 20
Final cleanup
```

Do not skip steps.

---

# 20. Exact Entity Validation Requirements

This requirement is critical.

If the supplied name/domain cannot be validated as the requested entity:

```text
INVALID
    ↓
all fields = N/A
    ↓
provide one valid reason
```

Possible valid reasons:

- invalid domain
- domain inaccessible
- parked domain
- dummy page
- unrelated entity
- insufficient evidence to identify exact entity

The system must **not silently choose a similarly named company/person/domain**.

Example:

```text
User:
ABC Technologies

Search finds:
ABC Technology
ABC Technologies Pvt Ltd
ABC Tech Solutions
ABC Technologies India

```

Do not merge them without evidence.

---

# 21. N/A Rules

Every required field must have a meaningful status.

Examples:

```json
{
  "value": null,
  "status": "not_found",
  "reason": "No verified GSTIN was found in the searched public sources.",
  "evidence": []
}
```

Or:

```json
{
  "value": null,
  "status": "not_applicable",
  "reason": "No shipping information is applicable because no commercial physical product offering was identified.",
  "evidence": []
}
```

If the whole entity is invalid:

```json
{
  "status": "invalid",
  "reason": "The supplied domain resolves to a parked/dummy page and could not be associated with the requested entity."
}
```

Do not let the LLM invent arbitrary N/A reasons.

---

# 22. No fabricated URLs

This is a hard requirement.

The system may only output a URL if it was actually observed by a tool.

Never construct:

```text
https://instagram.com/companyname
```

just because a username appears to be `companyname`.

The URL must have been discovered and stored as evidence.

---

# 23. Source/Evidence rules

Every factual value that reaches the final JSON must have evidence.

Evidence should contain at least:

```text
url
title when available
source_type when known
snippet/excerpt when available
```

The system must preserve the distinction between:

```text
observed
extracted
inferred
verified
```

Do not call an extracted string "verified" until verification rules support it.

---

# 24. Business/OSINT Source Priorities

When available, prefer sources roughly in this order:

```text
Tier 1
official company website
government/official registries
official company profiles

Tier 2
official social profiles
Google/Maps business presence

Tier 3
IndiaMART
TradeIndia
Justdial
Shopify/business portals

Tier 4
news
directories
aggregators

Tier 5
unverified third-party mentions
```

Third-party directories are discovery/corroboration sources, not automatically authoritative sources.

---

# 25. LinkedIn Rule

LinkedIn should be treated primarily as a **discovery source through public web search and observed public links**.

Do not build the system around logging into LinkedIn and scraping protected/internal content.

Only return a LinkedIn profile when the URL was actually discovered and can be associated with the requested person/entity.

---

# 26. GST/PAN/TAN/TIN

These are sensitive business identifiers and must be evidence-driven.

Never infer an identifier from a company name.

For GST, if a verified GSTIN is found, authoritative public verification should be preferred where feasible.

For PAN/TAN/TIN:

```text verified public evidence → return
otherwise → N/A with reason
```

---

# 27. Performance Model

The research agent must be **bounded**.

Do not allow an uncontrolled ReAct loop.

Maximum:

```python
MAX_RESEARCH_ROUNDS = 5
```

The intended flow:

```text
Round 1
  planner
    ↓
  execute tools
    ↓
  analyze

Round 2
  targeted research for missing fields
    ↓
  execute
    ↓
  analyze

Round 3
...

Round 5
  final evidence/reconciliation
    ↓
  validator
```

The LLM may request more work, but the LangGraph workflow enforces the maximum.

---

# 28. Parallelism

Independent operations should eventually be executed concurrently.

Example:

```text
             Research plan
          /       |        \
         /        |         \
      Search A  Search B  Search C
         │        │         │
         └────────┼─────────┘
                  ▼
              merge state
```

Dependent operations remain sequential.

Example:

```text
search
  ↓
discover URL
  ↓
fetch URL
  ↓
extract
```

Do not blindly parallelize dependent work.

---

# 29. Future AWS Migration

The local project is intentionally structured so that the capability layer can later move behind AWS orchestration.

Current:

```text
NVIDIA
  ↓
LangGraph
  ↓
Tool Registry
  ↓
Python tools
```

Future company deployment:

```text
API Gateway / company entry point
        ↓
Bedrock / AgentCore orchestration
        ↓
Action Groups / tool interfaces
        ↓
Lambda
        ↓
same tool capabilities
```

The core tool contracts and research-state concepts should remain stable.

Do not prematurely implement AWS.

---

# 30. Hard Rules for Future Development

1. Do not change the architecture.
2. Do not replace NVIDIA.
3. Do not replace DDGS.
4. Do not replace Playwright.
5. Do not add SearXNG.
6. Do not add Docker.
7. Do not switch to Gemini.
8. Do not introduce another agent framework.
9. Do not add Kafka, Redis, Kubernetes, vector DB, RAG, or unrelated infrastructure.
10. Do not install a library just because it sounds useful; it must solve the current planned step.
11. Do not build an entire OSINT framework from scratch when an appropriate open-source tool can be wrapped.
12. Do not add API-key-dependent services when a no-key/open-source alternative is sufficient.
13. Do not create a second AI agent inside the OSINT layer.
14. Keep the top-level orchestration in LangGraph.
15. Keep tool execution behind the Tool Registry.
16. Keep state in `ResearchState`.
17. Keep final validation deterministic wherever possible.
18. Never fabricate URLs or facts.
19. Never silently replace the requested entity with a similarly named entity.
20. Do not expand scope without an explicit requirement.

---

# 31. Current Success Criteria

The completed system must eventually do:

```text
Input entity
    ↓
Exact entity validation
    ↓
Initial research plan
    ↓
Parallel/appropriate tool execution
    ↓
Search
Browser
Extractor
OSINT
    ↓
Evidence accumulation
    ↓
Gap analysis
    ↓
Targeted additional research
    ↓
Cross-source verification
    ↓
Maximum 5 rounds
    ↓
Final deterministic validation
    ↓
Strict JSON
```

The final JSON must contain:

- requested entity
- entity validity
- website description
- products/services
- digital/physical classification
- shipping policy
- terms of use
- social-media URLs
- pricing
- GST/PAN/TAN/TIN where verified
- emails
- phone numbers with country/state information when available
- owner/MD/CEO/CXO names
- addresses
- IndiaMART/TradeIndia/Justdial/Shopify/other relevant associations
- CXO LinkedIn profiles
- citations/evidence
- N/A reasons
- research metadata

---

# 32. Current Status Snapshot

```text
schemas.py                    ✅
ResearchState                 ✅
LangGraph foundation          ✅
NVIDIA integration            ✅
Structured planner            ✅
Tool Registry                 ✅
Tool Executor                 ✅
DDGS Search                   ✅
Playwright Browser            ✅
Deterministic Extractor       ✅
Research Analyzer             ✅

OSINT integration             ⏳ NEXT
Evidence normalization        ⏳
Exact entity validation       ⏳
Required-field tracking       ⏳
5-round loop                  ⏳
Verification                  ⏳
Final validator               ⏳
Parallel tool execution       ⏳
End-to-end testing            ⏳
```

---

# 33. Development Philosophy

The goal is **minimum implementation effort with maximum reuse**.

Use existing open-source Python/GitHub capabilities wherever they fit.

Do not reinvent:

- username search across thousands of sites
- domain reconnaissance
- social discovery
- common OSINT functionality
- browser automation
- basic search

Instead, build the glue:

```text
planning
+
tool adapters
+
state
+
evidence normalization
+
verification
+
required-field validation
+
final JSON
```

That is the project's actual engineering value.
