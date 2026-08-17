# OFFICE LAPTOP — STRICT CONTINUATION PROMPT

You are continuing an existing software project called:

**OSINT Entity Research Agent**

A complete project handoff is provided in `README.md`.

## ABSOLUTE RULE

Treat `README.md` as the **source of truth** for architecture, technology choices, project state, completed work, dependencies, and the remaining plan.

**DO NOT DEVIATE.**

Do not redesign the architecture.
Do not replace technologies.
Do not suggest alternatives.
Do not propose a different framework.
Do not add infrastructure.
Do not remove a decided dependency.
Do not restart the project.
Do not rewrite working code unnecessarily.

Continue the project from the exact state documented in the README.

---

# LOCKED TECHNOLOGY

The project uses:

- NVIDIA API
- current NVIDIA model: `nvidia/nemotron-3.5-lightning-30b-a3b`
- LangChain
- LangGraph
- DDGS for web search
- Playwright for browser/web access
- deterministic Python extractor
- Pydantic
- OSINT capabilities through adapters in `tools/osint.py`
- maximum 5 research rounds

DO NOT replace these with:

- Gemini
- OpenAI
- another LLM provider
- SearXNG
- Docker
- Tavily
- Brave Search
- another search provider
- another agent framework
- another orchestration framework

unless the user explicitly changes the requirements.

---

# LOCKED ARCHITECTURE

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

Detailed responsibility:

```text
NVIDIA LLM
= planning + analysis

LangGraph
= workflow + state + conditional routing + bounded loop

Tool Registry
= controlled mapping from tool names to functions

Search
= DDGS

Browser
= Playwright

Extractor
= deterministic Python extraction/normalization

OSINT
= reusable open-source OSINT capabilities behind our own adapters

ResearchState
= persistent research state

Validator
= deterministic quality gate

Final JSON
= strict structured output
```

---

# CURRENT FILE STRUCTURE

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

---

# WORK ALREADY COMPLETED

The following components have already been implemented and tested.

## 1. `schemas.py`

Pydantic models exist for:

- Evidence
- Finding
- EntityValidation
- ResearchPlan
- ResearchStep
- ResearchAnalysis
- ResearchResult

The schemas were tested successfully.

---

## 2. `agent/state.py`

`ResearchState` exists as a TypedDict and contains:

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

State test passed.

---

## 3. `agent/graph.py`

LangGraph foundation exists and has been tested.

Current logical flow:

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

The future graph must add conditional looping without replacing LangGraph.

---

## 4. `llm.py`

NVIDIA integration works.

Current model:

```text
nvidia/nemotron-3.5-lightning-30b-a3b
```

The model has successfully returned:

- normal text
- structured `ResearchPlan`
- structured `ResearchAnalysis`

LangChain may show a structured-output capability warning for this model, but the actual tests have worked.

DO NOT switch models because of the warning.

---

## 5. Planner

`agent/prompts.py` contains a research planner prompt.

Planner output is structured:

```json
{
  "steps": [
    {
      "tool": "web_search",
      "input": {
        "query": "..."
      }
    }
  ]
}
```

Planner already works.

---

## 6. Tool Registry

`tools/registry.py` exists.

Current real tools:

```text
web_search
fetch_page
extract_page
```

Registry functions:

```text
get_tool()
get_tool_descriptions()
list_tools()
```

Registry test passed.

Unknown tool names are rejected.

---

## 7. Tool Executor

`agent/executor.py` exists.

It:

- reads the ResearchPlan
- resolves tools through the registry
- rejects unknown tools
- rejects placeholder arguments
- executes functions
- records success/failure
- returns normalized execution results

Executor test passed.

---

## 8. Search

`tools/search.py` uses:

**DDGS**

This is the fixed search implementation.

Do not replace it.

Search works.

Example:

```python
web_search("NVIDIA official website")
```

returns real search results.

---

## 9. Browser

`tools/browser.py` uses:

**Playwright + Chromium**

Current capability:

```python
fetch_page(url)
```

It returns:

- success
- final URL
- status code
- title
- visible page text
- links

Browser test passed against NVIDIA's website.

---

## 10. Extractor

`tools/extractor.py` is deterministic Python.

Current extraction:

- emails
- phone numbers
- prices
- social links
- policy links
- page source
- links

Extractor test passed.

Observed duplicate social/policy URLs are known and should later be handled by evidence normalization/deduplication.

Do not rewrite the extractor now.

---

## 11. Research Analyzer

`agent/analyzer.py` exists.

It receives:

- user query
- findings
- sources
- tool results

and returns:

- findings
- missing fields
- contradictions
- next_research_required

Analyzer test passed.

Important lesson:
search snippets are not enough for reliable research. Actual page retrieval and extraction must feed the analyzer.

---

# CURRENT OSINT STATUS

OSINT has **NOT** yet been integrated.

A PyPI package:

```text
spiderfoot==0.0.1
```

was accidentally installed and confirmed to be:

```text
Reserved name placeholder. No functionality.
```

Do NOT use that package.

It should be uninstalled.

The OSINT architectural box remains mandatory:

```text
Tool Registry
    ↓
OSINT adapters
```

The project should reuse existing open-source capabilities wherever possible instead of implementing large OSINT functionality from scratch.

Potential tools already identified include:

- Maigret
- OpenOSINT components
- lightweight Python OSINT libraries/tools

The top-level project remains:

```text
NVIDIA + LangGraph
```

OSINT tools are not allowed to become a second agent.

---

# ORIGINAL BUSINESS REQUIREMENT

The system eventually has to support requests that require:

- website description
- products
- digital vs physical classification
- shipping policy URL
- terms of use URL
- social-media URLs
- Instagram
- Facebook
- LinkedIn
- X/Twitter
- Google reviews/business presence
- pricing
- GST
- PAN
- TAN
- TIN
- emails
- phones with country/state information where available
- owners
- MD
- CEO
- CXOs
- addresses
- IndiaMART
- Shopify
- TradeIndia
- Justdial
- other relevant portals
- LinkedIn profiles of CXOs
- extensive search
- exact entity matching
- citations for everything
- no hallucination
- no fabricated links
- only verified information
- N/A with a reason
- invalid / parked / dummy / inaccessible domain handling

The user explicitly requires:

**NO HALLUCINATION**

**NO MAKING OF LINKS**

**ONLY VERIFIED INFO**

**DO NOT DEVIATE FROM THE EXACT ENTITY NAME**

**IF INVALID, RETURN N/A WITH ONE VALID REASON**

---

# REMAINING STEPS — FOLLOW THIS ORDER EXACTLY

## STEP 11 — OSINT integration

Do NOT implement all OSINT capabilities from scratch.

Select suitable reusable open-source capabilities and create adapters inside:

```text
tools/osint.py
```

Expose only the useful capabilities through our registry.

Start with the highest-value no/low-key capabilities.

Do not create a second AI agent.

---

## STEP 12 — Evidence normalization / deduplication

Unify:

```text
DDGS results
Playwright results
Extractor results
OSINT results
```

into a common evidence format.

Remove duplicates.

Preserve source provenance.

Do not call an extracted value "verified" merely because it exists.

---

## STEP 13 — Exact entity validation

Before broad research:

1. validate supplied entity/domain
2. determine entity type
3. make sure discovered sources refer to the exact requested entity
4. detect parked/dummy/inaccessible/unrelated targets
5. if invalid:
   - all requested output fields become N/A
   - give one clear reason
   - stop research

Do not silently choose a similarly named entity.

---

## STEP 14 — Required-field tracking

Create the complete set of fields required by the business prompt.

The research state must know:

```text
found
missing
conflicting
not applicable
```

The LLM must not be allowed to declare research complete merely because it feels finished.

---

## STEP 15 — Bounded research loop

Maximum:

```python
MAX_RESEARCH_ROUNDS = 5
```

Desired behavior:

```text
Round 1
  planner
  ↓
  execute
  ↓
  analyze

Round 2
  targeted missing-field research
  ↓
  execute
  ↓
  analyze

...

Round 5
  final targeted research
  ↓
  validate
```

LangGraph controls the loop.

The LLM cannot run indefinitely.

---

## STEP 16 — Claim verification

Every important claim needs evidence.

Examples:

```text
CEO
GST
phone
address
social profile
ownership
company/domain association
```

The system must classify:

```text
supported
contradicted
insufficient evidence
not found
not applicable
```

---

## STEP 17 — Final JSON validator

Before output:

- every required field considered
- every non-null fact has evidence
- every URL was actually discovered
- no fabricated URLs
- no unsupported claim marked verified
- invalid entity logic enforced
- N/A values have reasons
- contradictions handled
- exact entity maintained
- schema valid

If validation fails and rounds remain:

```text
validator
   ↓
missing/conflicting fields
   ↓
next plan
```

Otherwise finalize with N/A where justified.

---

## STEP 18 — Parallel execution

Only after the sequential pipeline is correct.

Independent tool calls should run concurrently.

Example:

```text
Search A
Search B
Search C
   ↓
parallel
   ↓
merge into state
```

Dependent operations remain sequential.

Do not blindly parallelize dependent work.

---

## STEP 19 — Full end-to-end testing

Test:

- valid domain
- invalid domain
- parked domain
- business with website
- person
- exact-name collision
- social profiles
- pricing
- policies
- GST
- leadership
- external portals
- missing information
- contradictory sources

---

## STEP 20 — Final cleanup

Only after all behavior works:

- clean logging
- clean errors
- remove test code
- update requirements
- document environment variables
- final schema
- final README

---

# NON-NEGOTIABLE RULES

1. Do not change the architecture.
2. Do not replace NVIDIA.
3. Do not replace DDGS.
4. Do not replace Playwright.
5. Do not add SearXNG.
6. Do not add Docker.
7. Do not switch to Gemini.
8. Do not introduce another agent framework.
9. Do not add unrelated infrastructure.
10. Do not rebuild OSINT capabilities if suitable open-source components exist.
11. Do not add a second AI agent.
12. Do not invent URLs.
13. Do not invent facts.
14. Do not silently merge similar entities.
15. Do not remove already-working components.
16. Do not rewrite working code unnecessarily.
17. Do not skip the planned step order.
18. Do not jump directly to AWS.
19. Do not turn suggestions into architecture changes.
20. Do not expand scope without the user's explicit instruction.

---

# HOW TO HANDLE PROBLEMS

If a current step fails:

1. diagnose the failure
2. fix it inside the locked architecture
3. keep the existing libraries and dependencies unless they are objectively broken
4. do not replace the chosen technology because another technology may be "better"
5. do not skip forward
6. retest the current step
7. only proceed when the current step passes

If there is ambiguity in an implementation detail, choose the solution that most closely matches the locked architecture above.

Do not ask the user whether they want a different architecture.

---

# RESPONSE STYLE FOR THE OFFICE ASSISTANT

For each remaining step:

1. State the exact step number and goal.
2. Give only the code/files needed for that step.
3. Explain the minimum necessary reasoning.
4. Provide the exact command/test to run.
5. Wait for the user to confirm the test passes.
6. Then continue to the next step.

Do not dump the whole remaining project at once.

Do not change the project plan.

---

# IMMEDIATE NEXT TASK

We are currently at:

```text
Step 10 complete
↓
Step 11 OSINT integration
```

Start Step 11 now.

First select and integrate a suitable **open-source, minimal-API-key OSINT capability** into:

```text
tools/osint.py
```

and expose it through the existing registry.

Do not change any other architectural component.
