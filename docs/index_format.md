# Index Format

The index is saved as UTF-8 JSON with three top-level objects: `metadata`, `documents`, and `terms`.

```json
{
  "metadata": {
    "version": "1.0",
    "base_url": "https://quotes.toscrape.com/",
    "build_time": "2026-05-11T00:00:00+00:00",
    "politeness_window_seconds": 6.0,
    "document_count": 2,
    "unique_term_count": 100,
    "total_token_count": 500
  },
  "documents": {
    "1": {
      "url": "https://quotes.toscrape.com/",
      "title": "Quotes to Scrape",
      "word_count": 250
    }
  },
  "terms": {
    "world": {
      "document_frequency": 1,
      "postings": {
        "1": {
          "frequency": 2,
          "positions": [5, 31]
        }
      }
    }
  }
}
```

## Metadata

`version` identifies the schema version. `base_url`, `build_time`, and `politeness_window_seconds` describe how the index was created. The count fields support quick summaries and ranking.

## Documents

Document ids are stable within one build and stored as strings for JSON compatibility. Each document records its canonical URL, title, and indexed word count.

## Terms

Each term maps to its document frequency and postings. A posting records how often the term appears in a document and the zero-based token positions where it appears. Those positions power phrase search.
