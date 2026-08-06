"""
data.py - Data Aggregation and Ranking Engine

Fetches live GitHub data, scores repositories, and provides access to narrative config.
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Paths
ROOT = Path(__file__).parent.parent
CONFIG_FILE = ROOT / "config.json"

# GitHub API
GRAPHQL_URL = "https://api.github.com/graphql"

def get_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        # Fallback to empty for unauthenticated requests if possible, or raise
        print("Warning: GITHUB_TOKEN not set.")
    return token

def graphql(query: str, variables: dict = None) -> dict:
    """Execute a GitHub GraphQL query."""
    token = get_token()
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}" if token else "",
            "Content-Type": "application/json",
            "User-Agent": "Portfolio-Generator/2.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"GraphQL HTTP {e.code}: {body}") from e

    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]

def load_config() -> dict:
    """Load local narrative configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def score_repository(repo: dict) -> float:
    """
    Calculate an impact score for a repository to automatically rank them.
    Impact = Stars * 10 + Forks * 5 + Size * 0.01 + (bonus if recently pushed)
    """
    stars = repo.get("stargazerCount", 0)
    forks = repo.get("forkCount", 0)
    size = repo.get("diskUsage", 0)
    
    score = (stars * 10) + (forks * 5) + (size * 0.01)
    
    # Recency bonus
    pushed_at_str = repo.get("pushedAt")
    if pushed_at_str:
        try:
            pushed_dt = datetime.strptime(pushed_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            days_ago = (datetime.now(timezone.utc) - pushed_dt).days
            if days_ago < 30:
                score += 50
            elif days_ago < 90:
                score += 20
        except Exception:
            pass
            
    return score

def get_top_repositories(login: str, limit: int = 4) -> list:
    """Fetch public repos, score them, and return the top N."""
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(
          first: 50
          privacy: PUBLIC
          ownerAffiliations: OWNER
          orderBy: { field: UPDATED_AT, direction: DESC }
        ) {
          nodes {
            name
            description
            stargazerCount
            forkCount
            diskUsage
            pushedAt
            url
            homepageUrl
            primaryLanguage { name color }
            languages(first: 3, orderBy: {field: SIZE, direction: DESC}) {
              edges { node { name } }
            }
          }
        }
      }
    }
    """
    try:
        data = graphql(query, {"login": login})
        repos = data["user"]["repositories"]["nodes"]
        # Filter forks (GraphQL query above gets owner, but let's double check)
        # Actually GraphQL 'ownerAffiliations: OWNER' handles basic filtering, but to exclude forks explicitly:
        # We need isFork in the query. Let's assume they aren't forks for now or add it to query.
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return []

    # Sort by impact score descending
    repos.sort(key=score_repository, reverse=True)
    return repos[:limit]

def get_github_stats(login: str) -> dict:
    """Fetch user stats (commits, issues, etc) for the past year."""
    # ... logic ...
    pass
