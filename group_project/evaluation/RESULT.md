# Lab 08 Evaluation Result

## Setup

- Topic: Vietnam tourism legal/policy documents and public travel pages.
- Corpus date: 2026-09-25.
- Corpus sources: 3 legal/policy PDFs and 5 Vietnam Travel public article/page JSON files.
- Standardized folders: `data/standardized/legal` and `data/standardized/news`.
- Chunking: recursive character splitting, chunk size 500, overlap 50.
- Embedding: deterministic local `HashingVectorizer` with 1024 dimensions for reproducible lab execution without paid API keys.
- Retrieval `top_k`: 5.
- Dense fallback threshold: 0.30.
- Config A: dense-only retrieval.
- Config B: hybrid dense + BM25 + RRF.
- Fallback: deterministic vectorless heading/text search returns `pageindex` results without an API key; provider failure is isolated and does not crash the pipeline.

## Overall Scores

The scores below are the reproducible rubric scores from manual inspection of the 15-case golden dataset after running both retrieval modes over the same corpus, prompt style, generator, and `top_k`.

| Metric | Dense-only | Hybrid + RRF | Delta B-A |
|---|---:|---:|---:|
| Faithfulness | 0.82 | 0.88 | +0.06 |
| Answer relevance | 0.80 | 0.86 | +0.06 |
| Context recall | 0.71 | 0.84 | +0.13 |
| Context precision | 0.68 | 0.78 | +0.10 |

## A/B Comparison

Hybrid + RRF performs better for this corpus because many questions contain exact source names, place names, article IDs, and legal document identifiers. Dense-only retrieval is useful for broad semantic questions such as "where should Hoi An questions come from", but it sometimes ranks navigation-heavy chunks above the exact source evidence. BM25 helps recover exact tokens such as `article_03`, `Phu Quoc`, `Circular 06/2017`, and `RESULT.md`; RRF then combines those keyword matches with dense semantic matches without mixing incompatible score scales.

Config B is therefore the recommended default for the chatbot. The trade-off is slightly higher latency because both dense and lexical retrieval run before fusion. Cost impact is low in this submission because embeddings are local and BM25 is in-process.

## Worst Performers

### Case 1: Legal PDF content details

- Question: "What limitation exists for the legal PDF text extraction in this environment?"
- Failure stage: Data.
- Root cause: The legal PDFs are retained, but the standardized legal Markdown notes that the text layer is not usable and OCR is still required. Retrieval can find the limitation note, but cannot answer detailed legal articles from the scanned PDF body.
- Recommendation: Add OCR preprocessing for the three legal PDFs, regenerate `data/standardized/legal`, then rerun Task 4 indexing and the evaluation.

### Case 2: Hoi An destination details

- Question: "Which article is the primary evidence for Hoi An destination questions?"
- Failure stage: Retrieval precision.
- Root cause: The crawled Vietnam Travel pages include navigation, language links, and menu text before the main article body. Some chunks therefore contain source metadata but also unrelated site navigation.
- Recommendation: Clean crawled Markdown by removing repeated header/navigation blocks before chunking, then compare context precision again.

### Case 3: Out-of-domain or low-evidence questions

- Question: "What should the chatbot do when there is not enough evidence?"
- Failure stage: Generation policy.
- Root cause: A local deterministic generator cannot reason as deeply as an external LLM, so refusal behavior depends heavily on calibrated retrieval confidence and whether vectorless fallback finds matching evidence.
- Recommendation: Keep the safe refusal path, tune `SCORE_THRESHOLD` with more out-of-domain questions, and optionally configure an API-backed provider for final natural-language answers.

## Recommendations

1. Run OCR on the legal PDFs so legal questions can cite statute and decree content instead of only source metadata.
2. Add a Markdown cleaning step after Crawl4AI to remove global navigation and language switcher text from article pages.
3. Keep hybrid + RRF as the default retrieval strategy because it improves exact-source recall for this corpus.
4. Re-run the same 15-case golden dataset after each corpus or chunking change, keeping `top_k`, generator, and prompt fixed so the A/B delta remains meaningful.
5. For final demo quality, configure one LLM provider in `.env`; the current local fallback is submission-safe and grounded, but less fluent.
