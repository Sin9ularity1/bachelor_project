# Data Poisoning in RAG: Threats to Confidentiality and Integrity

Bachelor project — Professional Bachelor's Degree in IT Security, UCL.

**Project period:** November 2026 – January 2027  
**Status:** In development

## Project overview

This project investigates the security implications of adversarial data poisoning in Retrieval-Augmented Generation (RAG) systems, with particular emphasis on confidentiality and integrity.

A locally hosted RAG system has been developed using Python, ChromaDB and Ollama. The system uses synthetic organizational documents representing a fictional company, Northstar Industries, to simulate an enterprise knowledge retrieval environment.

## Research question

To what extent can adversarial data poisoning of the vector retrieval layer compromise the confidentiality and integrity of RAG-based systems?

The project investigates:

1. How adversarial data poisoning affects retrieval behavior in vector-based RAG systems.
2. Under what conditions poisoned documents can cause integrity or confidentiality violations in generated responses.
3. How effectively selected mitigation techniques can reduce the identified attacks.
4. What security implications the experimental results have for organizations deploying RAG systems.

## Technology stack

| Component | Technology |
|---|---|
| Programming language | Python 3.12.10 |
| Vector database | ChromaDB |
| Model runtime | Ollama |
| Embedding model | nomic-embed-text |
| Language model | llama3.1:8b |
| Version control | Git and GitHub |

## System architecture

The RAG system consists of two primary processes: document ingestion and query processing.

### Document ingestion

1. Load source documents.
2. Divide documents into overlapping text chunks.
3. Generate vector embeddings.
4. Store embeddings, document content and metadata in ChromaDB.

### Query processing

1. Receive a user question.
2. Generate a query embedding.
3. Retrieve relevant document chunks using cosine distance.
4. Construct the context supplied to the language model.
5. Generate a response.
6. Record the response and retrieval information for evaluation.

### Configuration

| Parameter | Value |
|---|---|
| Chunk size | 500 characters |
| Chunk overlap | 100 characters |
| Top-K retrieval | 3 |
| Distance metric | Cosine |
| Temperature | 0 |
| Random seed | 42 |

## Experimental methodology

The research uses controlled experimental conditions to compare system behavior before and after the introduction of adversarial documents.

### Experiment 1 — Clean baseline

Establishes normal retrieval and generation performance using an unmodified document collection.

- 50 synthetic organizational documents.
- 150 document chunks.
- 100 evaluation questions.

### Experiment 2 — Integrity

Investigates whether untrusted documents can influence the accuracy and reliability of generated responses.

The experiment compares general and targeted evaluation results against the clean baseline.

### Experiment 3 — Confidentiality

Investigates whether adversarial documents can influence the handling of restricted information.

The experiment uses synthetic HR records and simulated requester roles to evaluate confidentiality under clean and poisoned conditions.

### Experiment 4 — Mitigation

Evaluates selected security controls intended to protect document integrity and enforce access restrictions within the retrieval layer.

This experiment is currently pending.

## Preliminary results

### Baseline retrieval performance

| Metric | Result |
|---|---:|
| Hit@1 | 95% |
| Hit@3 | 97% |
| Mean Reciprocal Rank | 0.9583 |
| Automatically graded correct | 74/100 |
| Automatically graded incorrect | 5/100 |
| Requires manual review | 21/100 |

### Security evaluation

| Experimental condition | Observed violations |
|---|---:|
| Integrity — poisoned | 15/20 (75%) |
| Confidentiality — clean | 0/20 (0%) |
| Confidentiality — poisoned | 2/20 (10%) |
| Integrity — mitigated | Pending |
| Confidentiality — mitigated | Pending |

These results are specific to the experimental configuration, document collections, models and evaluation questions used in this project. They should not be interpreted as universal attack success rates.

## Repository structure

The repository contains the following directories and files, depending on the selected experimental branch:

- `documents/` — Synthetic source documents and experimental datasets.
- `data/` — Locally generated vector databases.
- `src/` — Python implementation.
- `results/` — Evaluation results and retrieval logs.
- `requirements.txt` — Python dependencies.
- `questions.json` — General evaluation questions.
- `questions_integrity.json` — Targeted integrity evaluation questions.
- `questions_confidentiality.json` — Targeted confidentiality evaluation questions.

## Source code

| File | Description |
|---|---|
| ingest.py | Document ingestion, chunking and embedding |
| rag.py | Vector retrieval and response generation |
| evaluate.py | General automated evaluation |
| grade_answers.py | Automated answer grading |
| evaluate_integrity.py | Targeted integrity evaluation |
| ingest_confidentiality.py | Confidentiality dataset ingestion |
| rag_confidentiality.py | Confidentiality RAG implementation |
| evaluate_confidentiality.py | Comparative confidentiality evaluation |

## Git branches and reproducibility

Separate Git branches preserve the implementation and results of individual experimental conditions.

| Branch or tag | Purpose | Reference commit |
|---|---|---|
| main | Project overview and original baseline | 7cfe99a |
| baseline-clean-v1 | Original baseline snapshot | 7cfe99a |
| experiment/clean-integrity-evaluation | Clean integrity control | cdb2269 |
| experiment/integrity-poisoning | Integrity experiment | 050169c |
| experiment/confidentiality-poisoning | Confidentiality experiment | cdc48b1 |
| experiment/confidentiality-prompt-injection | Exploratory experiment | fea8b8c |

The exploratory prompt injection experiment is preserved for reference but is excluded from the primary experimental analysis.

Historical reference commits are retained to support reproducibility independently of subsequent repository maintenance.

## Installation

### Prerequisites

- Python 3.12
- Git
- Ollama

### Clone the repository

```bash
git clone https://github.com/Sin9ularity1/bachelor_project.git
cd bachelor_project
```

### Create a Python virtual environment

```bash
python -m venv .venv
```

Activate the environment on Windows:

```cmd
.venv\Scripts\activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Download the required models

```bash
ollama pull nomic-embed-text
ollama pull llama3.1:8b
```

### Run the baseline implementation

```bash
python src/ingest.py
python src/rag.py
```

### Run the baseline evaluation

```bash
python src/evaluate.py
```

Execution procedures may differ between experimental branches. Refer to the corresponding source code and historical commits when reproducing individual experiments.

## Research ethics and scope

All organizational documents, policies, employee records and restricted information used in this project are synthetic.

The research is conducted within a controlled, locally hosted environment for academic and defensive cybersecurity purposes. No production systems or real organizational information are targeted.

## Project status

- [x] Baseline RAG implementation
- [x] Baseline evaluation
- [x] Integrity experiment
- [x] Confidentiality experiment
- [ ] Final manual baseline grading
- [ ] Mitigation implementation
- [ ] Mitigation evaluation
- [ ] Final analysis and discussion
- [ ] Bachelor report
