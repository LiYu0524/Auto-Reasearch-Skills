# arXiv query guide (Atom API)

## Quick patterns

### Search across all fields
- `all:"implicit reasoning"`

### OR across terms (build bigger surveys)
- `all:"implicit reasoning" OR all:"hidden chain-of-thought" OR all:"multilingual reasoning"`

### Constrain by category (optional)
- `cat:cs.CL AND (all:"multilingual reasoning" OR all:"cross-lingual")`

### Author filter
- `au:"LastName" AND all:"keyword"`

## Notes
- The Atom API uses a `search_query` string; `arxiv_survey.py` can build an OR query from `--terms`.
- For very broad topics, prefer `--max-results 30..120` and iterate rather than pulling thousands.

