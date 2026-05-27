#!/usr/bin/env python3
"""
Search academic sources for foundational works (Grounder data phase).
Usage: python scripts/grounder_search.py <run_id> [--queries "q1" "q2" ...]

Reads the problem from DB, searches configured sources, writes results to
context/<run_id>/grounder_search.md for the CLI agent to reason over.
If no queries are provided, keyword-extracts from the problem.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import json
import time
import argparse
import logging

from core import database as db
from core.utils import load_config

logging.basicConfig(level=logging.WARNING)


STOPWORDS = {
    "what", "does", "have", "that", "this", "with", "from", "into", "when",
    "where", "which", "while", "been", "being", "were", "their", "there",
    "these", "those", "then", "than", "they", "them", "such", "some",
}


def _keywords(text: str, n: int = 4) -> list[str]:
    words = [w.lower() for w in re.findall(r'\b[a-z]{4,}\b', text)
             if w.lower() not in STOPWORDS]
    seen, out = set(), []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
            if len(out) >= n:
                break
    return out


def _search_openalex(query: str, limit: int = 5) -> list[dict]:
    import requests
    from core.keys import openalex as get_key
    try:
        params = {"search": query, "per-page": limit,
                  "sort": "relevance_score:desc", "filter": "has_abstract:true"}
        key = get_key()
        if key:
            params["api_key"] = key
        else:
            params["mailto"] = "pipeline@research.local"
        resp = requests.get("https://api.openalex.org/works", params=params,
                            timeout=15, headers={"User-Agent": "PipelineResearchBot/1.0"})
        resp.raise_for_status()
        results = []
        for w in resp.json().get("results", []):
            abstract = ""
            if w.get("abstract_inverted_index"):
                words = {}
                for word, positions in w["abstract_inverted_index"].items():
                    for pos in positions:
                        words[pos] = word
                abstract = " ".join(words[i] for i in sorted(words))[:600]
            doi = w.get("doi", "")
            results.append({
                "title":   w.get("display_name", ""),
                "authors": [a.get("author", {}).get("display_name", "")
                            for a in w.get("authorships", [])[:3]],
                "year":    w.get("publication_year"),
                "source":  "openalex",
                "doi":     doi,
                "abstract": abstract,
                "link":    doi or w.get("id", ""),
            })
        return results
    except Exception as e:
        logging.warning(f"[OpenAlex] {e}")
        return []


def _search_semantic_scholar(query: str, limit: int = 4) -> list[dict]:
    import requests
    from core.keys import semantic_scholar as get_key
    try:
        headers = {"User-Agent": "PipelineResearchBot/1.0"}
        key = get_key()
        if key:
            headers["x-api-key"] = key
        time.sleep(3.5)
        resp = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={"query": query, "limit": limit,
                    "fields": "title,authors,year,abstract,externalIds,url"},
            headers=headers, timeout=20
        )
        resp.raise_for_status()
        results = []
        for p in resp.json().get("data", []):
            doi = p.get("externalIds", {}).get("DOI", "")
            results.append({
                "title":   p.get("title", ""),
                "authors": [a.get("name", "") for a in p.get("authors", [])[:3]],
                "year":    p.get("year"),
                "source":  "semantic_scholar",
                "doi":     doi,
                "abstract": (p.get("abstract") or "")[:600],
                "link":    p.get("url", "") or (f"https://doi.org/{doi}" if doi else ""),
            })
        return results
    except Exception as e:
        logging.warning(f"[SemanticScholar] {e}")
        return []


def _search_google_books(query: str, limit: int = 4) -> list[dict]:
    import requests
    from core.keys import get as get_key
    try:
        params = {"q": query, "maxResults": limit, "orderBy": "relevance",
                  "printType": "books", "langRestrict": "en"}
        api_key = get_key("GOOGLE_BOOKS_API_KEY")
        if api_key:
            params["key"] = api_key
        resp = requests.get("https://www.googleapis.com/books/v1/volumes",
                            params=params, timeout=15,
                            headers={"User-Agent": "PipelineResearchBot/1.0"})
        resp.raise_for_status()
        results = []
        for item in resp.json().get("items", [])[:limit]:
            info = item.get("volumeInfo", {})
            isbn = next((i.get("identifier", "")
                         for i in info.get("industryIdentifiers", [])
                         if i.get("type") in ("ISBN_13", "ISBN_10")), "")
            pub_date = info.get("publishedDate", "")
            year = int(pub_date[:4]) if pub_date and pub_date[:4].isdigit() else None
            results.append({
                "title":   info.get("title", ""),
                "authors": info.get("authors", [])[:3],
                "year":    year,
                "source":  "google_books",
                "isbn":    isbn,
                "abstract": (info.get("description") or "")[:600],
                "link":    info.get("canonicalVolumeLink", ""),
            })
        return results
    except Exception as e:
        logging.warning(f"[GoogleBooks] {e}")
        return []


def _search_open_library(query: str, limit: int = 4) -> list[dict]:
    import requests
    try:
        time.sleep(1.0)
        resp = requests.get(
            "https://openlibrary.org/search.json",
            params={"q": query, "limit": limit,
                    "fields": "title,author_name,first_publish_year,isbn,key"},
            timeout=15, headers={"User-Agent": "PipelineResearchBot/1.0"}
        )
        resp.raise_for_status()
        results = []
        for doc in resp.json().get("docs", [])[:limit]:
            key = doc.get("key", "")
            isbn_list = doc.get("isbn", [])
            results.append({
                "title":   doc.get("title", ""),
                "authors": doc.get("author_name", [])[:3],
                "year":    doc.get("first_publish_year"),
                "source":  "open_library",
                "isbn":    isbn_list[0] if isbn_list else "",
                "abstract": "",
                "link":    f"https://openlibrary.org{key}" if key else "",
            })
        return results
    except Exception as e:
        logging.warning(f"[OpenLibrary] {e}")
        return []


def _fmt_results(label: str, results: list[dict]) -> str:
    if not results:
        return f"### {label}\n*(no results)*\n"
    lines = [f"### {label} ({len(results)} results)\n"]
    for r in results:
        authors = ", ".join(r.get("authors", [])[:2])
        year = r.get("year", "n.d.")
        abstract = (r.get("abstract", "") or "")[:300]
        lines.append(f"- **{r.get('title', '')}** ({authors}, {year})")
        lines.append(f"  Source: {r.get('source', '')} | Link: {r.get('link', r.get('doi', ''))}")
        if abstract:
            lines.append(f"  {abstract}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("--queries", nargs="*", help="Search queries (auto-derived if omitted)")
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args()

    run = db.get_run(args.run_id)
    if not run:
        print(f"ERROR: Run not found: {args.run_id}", file=sys.stderr)
        sys.exit(1)
    problem = run.get("problem", "")

    config = load_config()
    allowed = set(config.get("agent_sources", {}).get("grounder",
        ["openalex", "semantic_scholar", "google_books", "open_library"]))

    queries = args.queries if args.queries else [" ".join(_keywords(problem, 4))]

    sections = [
        f"# Grounder Search Results\n",
        f"**Run:** {args.run_id}",
        f"**Problem:** {problem[:200]}",
        f"**Queries used:** {', '.join(queries)}\n",
        "---\n",
    ]

    total = 0
    for query in queries:
        sections.append(f"## Query: \"{query}\"\n")
        if "openalex" in allowed:
            r = _search_openalex(query, args.limit)
            sections.append(_fmt_results("OpenAlex", r))
            total += len(r)
        if "semantic_scholar" in allowed:
            r = _search_semantic_scholar(query, args.limit)
            sections.append(_fmt_results("Semantic Scholar", r))
            total += len(r)
        if "google_books" in allowed:
            r = _search_google_books(query, args.limit)
            sections.append(_fmt_results("Google Books", r))
            total += len(r)
        if "open_library" in allowed:
            r = _search_open_library(query, args.limit)
            sections.append(_fmt_results("Open Library", r))
            total += len(r)

    ctx_dir = Path(__file__).parent.parent / "context" / args.run_id
    ctx_dir.mkdir(parents=True, exist_ok=True)
    out_path = ctx_dir / "grounder_search.md"
    out_path.write_text("\n".join(sections))

    print(f"Search complete: {total} sources gathered")
    print(f"Results written to: {out_path}")


if __name__ == "__main__":
    main()
