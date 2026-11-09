"""Automate GitHub Pull Request creation for the current feature branch."""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


def get_git_remote_url() -> str:
    res = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        capture_output=True,
        text=True,
        check=True,
    )
    return res.stdout.strip()


def parse_repo_owner_name(url: str) -> tuple[str, str]:
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+?)(?:\.git)?$", url)
    if not m:
        raise ValueError(f"Could not parse GitHub repo from remote URL: {url}")
    return m.group(1), m.group(2)


def get_current_branch() -> str:
    res = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=True,
    )
    return res.stdout.strip()


def get_github_token() -> str:
    if token := os.environ.get("GITHUB_TOKEN"):
        return token
    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n",
        capture_output=True,
        text=True,
        check=True,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("password="):
            return line[len("password="):].strip()
    raise RuntimeError("No GitHub token found in environment or git credential manager.")


def extract_odd_task_summary(feature_name: str) -> tuple[str, str]:
    task_file = Path("odd") / "tasks" / f"{feature_name}.md"
    if not task_file.exists():
        return f"feat: {feature_name}", ""

    content = task_file.read_text(encoding="utf-8")
    title = f"feat: {feature_name}"
    body_parts = []

    m_obj = re.search(r"### Objective\s*\n\n(.*?)(?=\n###|\n##|\Z)", content, re.DOTALL)
    if m_obj:
        body_parts.append(f"## Objective\n{m_obj.group(1).strip()}")

    m_crit = re.search(r"### Acceptance criteria\s*\n\n(.*?)(?=\n###|\n##|\Z)", content, re.DOTALL)
    if m_crit:
        body_parts.append(f"## Acceptance Criteria\n{m_crit.group(1).strip()}")

    m_ver = re.search(r"## Verification\s*\n> [^\n]*\n\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if m_ver:
        body_parts.append(f"## Verification\n{m_ver.group(1).strip()}")

    body = "\n\n".join(body_parts) if body_parts else content
    return title, body


def create_or_get_pull_request(
    title: str,
    body: str,
    base: str = "main",
    head: str | None = None,
) -> dict:
    if head is None:
        head = get_current_branch()
    remote = get_git_remote_url()
    owner, repo = parse_repo_owner_name(remote)
    token = get_github_token()

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "fitness-ai-odd-agent",
        "Content-Type": "application/json",
    }
    payload = json.dumps({"title": title, "head": head, "base": base, "body": body}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        err_msg = err.read().decode("utf-8")
        try:
            err_json = json.loads(err_msg)
            for error in err_json.get("errors", []):
                if "already exists" in error.get("message", ""):
                    query_url = f"https://api.github.com/repos/{owner}/{repo}/pulls?head={owner}:{head}&state=open"
                    q_req = urllib.request.Request(query_url, headers=headers)
                    with urllib.request.urlopen(q_req) as q_resp:
                        prs = json.loads(q_resp.read().decode("utf-8"))
                        if prs:
                            return prs[0]
            raise RuntimeError(f"GitHub API Error: {err_json.get('message', err_msg)}")
        except Exception:
            raise RuntimeError(f"HTTP {err.code}: {err_msg}")


def main():
    parser = argparse.ArgumentParser(description="Create a Pull Request on GitHub for the current branch.")
    parser.add_argument("--title", required=False, help="Pull request title")
    parser.add_argument("--body", required=False, help="Pull request description body")
    parser.add_argument("--base", default="main", help="Base branch to merge into (default: main)")
    args = parser.parse_args()

    branch = get_current_branch()
    if branch == "main":
        print("Cannot create a pull request from 'main'. Switch to a feature branch.")
        sys.exit(1)

    feature_name = branch.replace("feat/", "").replace("fix/", "")
    default_title, default_body = extract_odd_task_summary(feature_name)

    title = args.title or default_title
    body = args.body or default_body

    pr = create_or_get_pull_request(title=title, body=body, base=args.base, head=branch)
    print(f"Pull Request #{pr['number']}: {pr['html_url']} ({pr['state']})")


if __name__ == "__main__":
    main()
