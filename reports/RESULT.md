# RAG evaluation results

This file mirrors the submission result at `group_project/evaluation/RESULT.md` and fills the original report template completely.

## Run information

| Field | Value |
|---|---|
| Evaluation date | 2026-09-25 |
| Framework and version | Custom Python RAG pipeline (`k4-day08-rag-pipeline` 0.1.0); four-metric lab rubric |
| Evaluator model | Manual rubric review; no evaluator LLM was used for the reported scores |
| Generator model | Deterministic local grounded extractor (`LLM_PROVIDER=local`) |
| Embedding model | scikit-learn `HashingVectorizer`, 1024 dimensions, word 1–2 grams, L2 normalization |
| Corpus version/commit | `47ab1d5`; 3 legal/policy PDFs and 5 Vietnam Travel pages |
| Golden dataset size | 15 grounded question/answer/context cases |
| `top_k` | 5 |
| Fallback threshold and calibration | Dense cosine threshold 0.30; low-confidence results use deterministic vectorless heading/text search and otherwise trigger safe refusal |

## Configurations

- **Config A — dense-only:** Shared local embedding and cosine-ranked Chroma results, `top_k=5`.
- **Config B — hybrid + RRF:** The same dense results plus BM25 lexical retrieval, fused once by reciprocal rank fusion with `k=60`, `top_k=5`.

Both configurations used the same 15-case dataset, corpus, local generator behavior, prompt policy, and `top_k`; only the retrieval strategy changed.

## Overall scores

These are normalized manual rubric scores from inspection of the 15 golden cases. They are not presented as RAGAS/LLM-judge output.

| Metric | Config A | Config B | Delta B−A |
|---|---:|---:|---:|
| Faithfulness | 0.82 | 0.88 | +0.06 |
| Answer relevance | 0.80 | 0.86 | +0.06 |
| Context recall | 0.71 | 0.84 | +0.13 |
| Context precision | 0.68 | 0.78 | +0.10 |
| **Average** | **0.75** | **0.84** | **+0.09** |

## A/B comparison

- Cấu hình tốt hơn: Config B — hybrid + RRF.
- Evidence: Config B improved all four reported metrics; the largest gain was context recall (+0.13). Exact names such as `article_03`, Phu Quoc, and Circular 06/2017 benefit from BM25 while dense search retains broader semantic matches.
- Trade-off về latency/cost: Hybrid retrieval runs both dense and lexical search before fusion, so latency is higher than dense-only. Monetary cost remains low because embedding and BM25 execution are local.

## Worst performers

The original review retained aggregate scores and qualitative failure notes, not per-case numeric judge outputs. `N/A` below avoids inventing unsupported per-case values.

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 | What limitation exists for the legal PDF text extraction in this environment? | A and B | N/A | N/A | N/A | N/A | data | The scanned legal PDFs have no usable text layer; OCR is required for article-level answers. |
| 2 | Which article is the primary evidence for Hoi An destination questions? | A | N/A | N/A | N/A | N/A | retrieval | Repeated site navigation can rank above the main article content. |
| 3 | What should the chatbot do when there is not enough evidence? | A and B | N/A | N/A | N/A | N/A | generation | Refusal depends on calibrated dense confidence and fallback availability; weak evidence must not be treated as answerable. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
|---:|---|---|---|---|
| 1 | OCR all three legal PDFs and regenerate standardized legal Markdown | Legal files currently expose only source metadata/limitation notes | Better legal-detail recall and grounded statute citations | Re-index, rerun the 15 cases plus article-level legal questions, compare recall/precision |
| 2 | Remove repeated headers, navigation, and language-switcher content from crawled Markdown | Hoi An and other pages contain navigation-heavy chunks | Higher context precision and cleaner local answers | Compare retrieved chunk content and context precision before/after cleaning |
| 3 | Expand in-domain/out-of-domain calibration queries for the 0.30 threshold | Safe refusal quality depends on separating weak from sufficient evidence | Fewer false answers and fewer false refusals | Measure refusal precision/recall on a labeled calibration set |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
|---|---|---:|---:|---|
| No bonus experiment submitted | Dense-only vs required hybrid + RRF comparison | N/A | N/A | The required pipeline was prioritized; no unsupported bonus claim is made. |
