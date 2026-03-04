# Report fields (JSONL schema)

Each line in `arxiv.jsonl` is one paper with these fields (when available):

- `arxiv_id`: canonical id (e.g., `2401.01234` or `hep-th/9901001`)
- `title`, `summary`
- `authors`: list of strings
- `published`, `updated` (ISO strings from the feed)
- `categories`: list of category strings
- `primary_category`: string
- `abs_url`, `pdf_url`
- `doi`, `journal_ref`, `comment`
- `downloaded_pdf`: local path if `--download-pdfs` was used

`generate_report.py` uses these fields to produce a Markdown table and category clusters.

