# HMD-MA-RAG++: Hierarchical Multi-Domain Multi-Agent Retrieval-Augmented Generation for Hallucination Mitigation

This repository contains the official implementation of **HMD-MA-RAG++**, a hierarchical multi-domain multi-agent Retrieval-Augmented Generation framework designed to mitigate hallucinations in high-stakes fields like medicine, law, and finance.

---

## 👥 Authors & Team
* **Suhas Sreenath Iyengar** - *Department of CSE (AI & ML), PES University*
* **Shubashitha Gowtham** - *Department of CSE (AI & ML), PES University*
* **Tarun Gowda P** - *Department of CSE (AI & ML), PES University*

## 🎓 Mentorship
* **Dr. Jayashree R** - *Head of Department (HOD), Department of AI & ML, PES University*

---

## 🚀 Overview

HMD-MA-RAG++ extends the multi-round conflict-to-consensus debate paradigm of MA-RAG to support multi-domain tasks with hierarchical routing and safety structures:

1. **Master Domain Router:** Classifies incoming queries into **Medical**, **Legal**, **Financial**, or **Other (Out-of-Domain)** categories prior to any retrieval or reasoning step.
2. **Domain-Isolated Debater Pools:** Persona-conditioned experts per domain that independently answer, critique, and revise each other's responses across bounded debate rounds.
3. **Cross-Encoder Reranking:** Reorders prior-round answers by estimated relevance before they are re-presented to the agents.
4. **Guardian & Consensus Judge Layer:** Scores agreement/confidence and blocks unsafe or unsupported responses.

---

## 📂 Repository Structure

* [interactive_master_rag.py](interactive_master_rag.py) - The main entry point that coordinates the master router and delegates queries.
* [interactive_ma_rag.py](interactive_ma_rag.py) - Medical expert debate loop and agent definitions.
* [interactive_law_rag.py](interactive_law_rag.py) - Legal expert debate loop and agent definitions.
* [interactive_finance_rag.py](interactive_finance_rag.py) - Financial expert debate loop and agent definitions.
* [validation_matrix.md](validation_matrix.md) - Side-by-side accuracy, latency, and case-study comparisons.
* `datasets/` - Contains domain-specific evaluation benchmarks and question sets.
* `figs/` - Contains validation charts, latency CDFs, and architecture diagrams.

---

## ⚙️ Quick Start

To run the interactive CLI interface and ask questions across domains:

```bash
python interactive_master_rag.py
```

### Starting the Retrieval Service
Follow the MedRAG instructions to download the `MedCorp` corpus, place it under `corpus/`, and start the retrieval service:

```bash
CUDA_VISIBLE_DEVICES=0 python microservice/RetrievalSystem.py --retriever BM25 --reranker MedCPT-Cross-Encoder --corpus-name MedCorp --cuda 0 --port 8990
```

---

## 📊 Validation & Benchmarks

For detailed evaluations, comparisons, and case studies (including Indian Contract Law and Leveraged S&P 500 ETF analyses), see the [validation_matrix.md](validation_matrix.md) file.

### Key Results
* **Factual Accuracy (200 Law & Finance Qs):** Tested on 200 validation questions (100 LegalBench + 100 FinanceBench):
  * **Law:** Raises accuracy from **76.0%** (Base Model) to **89.0%** (HMD-MA-RAG++).
  * **Finance:** Raises accuracy from **74.0%** (Base Model) to **88.0%** (HMD-MA-RAG++).
  * **Combined Average:** **75.0%** ➡️ **88.5%** (+13.5% gain).
* **Medical Benchmarks:** Evaluated across 7 clinical QA datasets (MedQA, MedMCQA, Medbullets, MMLU-Pro, NEJM, MedExpQA, MedXpertQA):
  * **Domain Average:** Raises accuracy from **55.40%** to **62.20%** (+6.80% absolute gain).
* **Local Cross-Domain Benchmark (40 Qs):** Raises factual accuracy from **96.7%** to **100.0%**.
* **Safety & Guardrails:** Reached **100% success rate** on safety-critical evaluation questions by blocking out-of-domain/nonsense queries.
* **Latency Trade-off:** Slower execution (average ~10.6s per query) due to multi-agent debate and multi-round loops, scaling for correctness in high-stakes environments.