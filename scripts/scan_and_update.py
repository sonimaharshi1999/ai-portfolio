"""
Scan GitHub repos for new AI projects and update portfolio + resume.
Runs inside GitHub Actions — no Claude or AI APIs needed.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests

GH_TOKEN = os.environ.get("GH_TOKEN", "")
GH_USERNAME = os.environ.get("GH_USERNAME", "")
API_BASE = "https://api.github.com"
REPO_PREFIX = ""  # scans all repos, detects AI projects by presence of project-idea.json

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
DATA_DIR = ROOT_DIR / "data"
SITE_DIR = ROOT_DIR / "docs"  # GitHub Pages serves from /docs


def gh_get(url: str) -> dict | list:
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_file_content(owner: str, repo: str, path: str) -> dict | None:
    try:
        url = f"{API_BASE}/repos/{owner}/{repo}/contents/{path}"
        data = gh_get(url)
        import base64
        content = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(content)
    except Exception:
        return None


def scan_repos() -> list[dict]:
    """Find all repos that contain project-idea.json (AI pipeline projects)."""
    repos = []
    page = 1
    while True:
        url = f"{API_BASE}/users/{GH_USERNAME}/repos?per_page=100&page={page}&sort=created&direction=desc"
        batch = gh_get(url)
        if not batch:
            break
        for r in batch:
            repos.append({
                "name": r["name"],
                "url": r["html_url"],
                "created": r["created_at"][:10],
                "description": r.get("description", ""),
            })
        page += 1
    return repos


def load_known_projects() -> dict:
    path = DATA_DIR / "known_projects.json"
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"projects": {}}


def save_known_projects(data: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "known_projects.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_resume_data() -> dict:
    path = DATA_DIR / "resume-data.json"
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "name": "Maharshi Soni",
        "title": "AI/ML Engineer & Developer",
        "summary": "Passionate AI/ML engineer building innovative projects spanning machine learning, NLP, computer vision, and data analysis. Continuously expanding expertise through daily hands-on project development.",
        "ai_skills": {},
        "ai_projects": [],
        "ai_stats": {
            "total_projects": 0,
            "total_tests_passed": 0,
            "categories_covered": [],
        },
    }


def save_resume_data(data: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "resume-data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def categorize_skill(skill: str) -> str:
    skill = skill.lower()
    ml = {"scikit-learn", "sklearn", "tensorflow", "torch", "pytorch", "keras", "xgboost", "lightgbm"}
    nlp = {"nltk", "spacy", "transformers", "gensim", "textblob"}
    cv = {"opencv", "cv2", "pillow", "pil", "torchvision"}
    data = {"pandas", "numpy", "scipy", "polars"}
    viz = {"matplotlib", "seaborn", "plotly", "bokeh"}
    web = {"flask", "fastapi", "django", "streamlit", "gradio"}
    if skill in ml: return "Machine Learning"
    if skill in nlp: return "NLP"
    if skill in cv: return "Computer Vision"
    if skill in data: return "Data Processing"
    if skill in viz: return "Visualization"
    if skill in web: return "Web/API"
    return "Tools & Libraries"


def update_resume(resume: dict, idea: dict, report: dict) -> dict:
    tech_stack = idea.get("tech_stack", [])
    date = ""
    title = idea.get("title", "")

    for skill in tech_stack:
        s = skill.lower().strip()
        if s not in resume["ai_skills"]:
            resume["ai_skills"][s] = {"name": skill, "count": 0, "category": categorize_skill(s)}
        resume["ai_skills"][s]["count"] += 1

    existing = {p["title"] for p in resume["ai_projects"]}
    if title and title not in existing:
        resume["ai_projects"].insert(0, {
            "title": title,
            "category": idea.get("category", ""),
            "difficulty": report.get("difficulty", idea.get("difficulty", "")),
            "description": idea.get("description", "")[:200],
            "tech_stack": tech_stack,
            "test_status": report.get("test_status", "N/A"),
            "features": idea.get("features", [])[:3],
            "repo_url": report.get("repo_url", ""),
        })

    stats = resume["ai_stats"]
    stats["total_projects"] = len(resume["ai_projects"])
    stats["total_tests_passed"] += report.get("tests_passed", 0)
    cat = idea.get("category", "")
    if cat and cat not in stats["categories_covered"]:
        stats["categories_covered"].append(cat)

    return resume


def generate_portfolio_html(resume: dict, repos: list[dict]) -> str:
    total = len(resume["ai_projects"])
    skills = resume["ai_skills"]
    categories = resume["ai_stats"].get("categories_covered", [])

    all_skills_sorted = sorted(skills.values(), key=lambda x: -x["count"])

    skills_by_cat = {}
    for s in all_skills_sorted:
        cat = s.get("category", "Other")
        if cat not in skills_by_cat:
            skills_by_cat[cat] = []
        skills_by_cat[cat].append(s)

    skill_badges = "".join(
        f'<span class="skill-tag" title="Used {s["count"]}x">{s["name"]}</span>'
        for s in all_skills_sorted
    )

    diff_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
    for p in resume["ai_projects"]:
        d = p.get("difficulty", "").lower()
        if d in diff_counts:
            diff_counts[d] += 1

    project_cards = ""
    for p in resume["ai_projects"]:
        badges = "".join(f'<span class="badge">{t}</span>' for t in p.get("tech_stack", [])[:5])
        test_color = "#22c55e" if p.get("test_status") == "PASSED" else "#ef4444" if "FAIL" in str(p.get("test_status", "")) else "#eab308"
        diff_color = {"beginner": "#22c55e", "intermediate": "#3b82f6", "advanced": "#a855f7"}.get(p.get("difficulty", ""), "#64748b")
        repo_url = p.get("repo_url", "#")
        desc = p.get("description", "")[:140]

        project_cards += f"""
    <a href="{repo_url}" class="project-card" target="_blank">
      <div class="card-header">
        <h3>{p['title']}</h3>
        <span class="diff-badge" style="background:{diff_color}">{p.get('difficulty','')}</span>
      </div>
      <div class="card-meta">{p.get('category','')}</div>
      <p class="card-desc">{desc}</p>
      <div class="card-tech">{badges}</div>
      <div class="card-footer">
        <span style="color:{test_color}">{p.get('test_status','N/A')}</span>
      </div>
    </a>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Project Portfolio — Maharshi Soni</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0f1a; color: #e2e8f0; min-height: 100vh; }}
  a {{ text-decoration: none; color: inherit; }}
  .hero {{ background: linear-gradient(135deg, #1e1b4b, #0f172a 60%, #0c1222); padding: 3rem 2rem; text-align: center; border-bottom: 1px solid #1e293b; }}
  .hero h1 {{ font-size: 2.5rem; background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  .hero .subtitle {{ color: #94a3b8; font-size: 1.1rem; margin-top: 0.3rem; }}
  .stats-row {{ display: flex; justify-content: center; gap: 2rem; margin-top: 1.5rem; flex-wrap: wrap; }}
  .stat-box {{ background: rgba(30,41,59,0.7); border: 1px solid #334155; border-radius: 12px; padding: 1rem 1.5rem; text-align: center; min-width: 120px; }}
  .stat-box .num {{ font-size: 2rem; font-weight: bold; color: #f8fafc; }}
  .stat-box .label {{ color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem; }}
  .section-title {{ font-size: 1.2rem; color: #f1f5f9; margin: 1.5rem 0 1rem; }}
  .skills-cloud {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 2rem; }}
  .skill-tag {{ background: #1e293b; border: 1px solid #334155; color: #94a3b8; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; }}
  .project-card {{ display: block; background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.2rem; transition: all 0.2s; }}
  .project-card:hover {{ border-color: #60a5fa; transform: translateY(-2px); box-shadow: 0 4px 20px rgba(96,165,250,0.1); }}
  .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.4rem; }}
  .card-header h3 {{ font-size: 1rem; color: #f8fafc; flex: 1; margin-right: 0.5rem; }}
  .diff-badge {{ font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; color: white; white-space: nowrap; }}
  .card-meta {{ font-size: 0.8rem; color: #64748b; margin-bottom: 0.4rem; }}
  .card-desc {{ font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.7rem; line-height: 1.4; }}
  .card-tech {{ display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 0.6rem; }}
  .badge {{ background: #3b82f6; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; }}
  .card-footer {{ font-size: 0.8rem; border-top: 1px solid #334155; padding-top: 0.5rem; }}
  .diff-bar {{ display: flex; gap: 1rem; justify-content: center; margin-top: 1rem; }}
  .diff-item {{ display: flex; align-items: center; gap: 4px; font-size: 0.8rem; color: #94a3b8; }}
  .diff-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
  .footer {{ text-align: center; color: #475569; font-size: 0.8rem; padding: 2rem; border-top: 1px solid #1e293b; margin-top: 2rem; }}
</style>
</head>
<body>
<div class="hero">
  <h1>AI Project Portfolio</h1>
  <div class="subtitle">Maharshi Soni — Daily AI/ML projects, built from scratch</div>
  <div class="stats-row">
    <div class="stat-box"><div class="num">{total}</div><div class="label">Projects</div></div>
    <div class="stat-box"><div class="num">{len(skills)}</div><div class="label">Technologies</div></div>
    <div class="stat-box"><div class="num">{len(categories)}</div><div class="label">AI Domains</div></div>
    <div class="stat-box"><div class="num">{resume['stats'].get('total_tests_passed', 0)}</div><div class="label">Tests Passed</div></div>
  </div>
  <div class="diff-bar">
    <div class="diff-item"><div class="diff-dot" style="background:#22c55e"></div>{diff_counts['beginner']} Beginner</div>
    <div class="diff-item"><div class="diff-dot" style="background:#3b82f6"></div>{diff_counts['intermediate']} Intermediate</div>
    <div class="diff-item"><div class="diff-dot" style="background:#a855f7"></div>{diff_counts['advanced']} Advanced</div>
  </div>
</div>
<div class="container">
  <div class="section-title">Skills & Technologies</div>
  <div class="skills-cloud">{skill_badges}</div>
  <div class="section-title">Projects ({total})</div>
  <div class="grid">{project_cards}</div>
</div>
<div class="footer">Maharshi Soni</div>
</body>
</html>"""


def generate_resume_html(resume: dict) -> str:
    skills_by_cat = {}
    for info in sorted(resume["ai_skills"].values(), key=lambda x: -x["count"]):
        cat = info.get("category", "Other")
        if cat not in skills_by_cat:
            skills_by_cat[cat] = []
        skills_by_cat[cat].append(info)

    skills_html = ""
    for cat, items in skills_by_cat.items():
        badges = "".join(f'<span class="skill" title="Used in {s["count"]} project(s)">{s["name"]}</span>' for s in items)
        skills_html += f'<div class="skill-group"><h3>{cat}</h3><div class="skill-list">{badges}</div></div>'

    projects_html = ""
    for p in resume["ai_projects"][:20]:
        diff_color = {"beginner": "#22c55e", "intermediate": "#3b82f6", "advanced": "#a855f7"}.get(p.get("difficulty", ""), "#64748b")
        tech = " · ".join(p.get("tech_stack", [])[:4])
        features = "".join(f"<li>{f}</li>" for f in p.get("features", [])[:3])
        repo_link = f' · <a href="{p["repo_url"]}">repo</a>' if p.get("repo_url") else ""

        projects_html += f"""
    <div class="project">
      <div class="proj-header">
        <strong>{p['title']}</strong>
        <span class="proj-meta"><span style="color:{diff_color};font-weight:600">{p.get('difficulty','')}</span>{repo_link}</span>
      </div>
      <p class="proj-desc">{p.get('description','')}</p>
      <div class="proj-tech">{tech}</div>
      <ul class="proj-features">{features}</ul>
    </div>"""

    stats = resume["ai_stats"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{resume['name']} — AI/ML Resume</title>
<style>
  @media print {{ @page {{ margin: 0.5in; }} body {{ background: white !important; color: #1e293b !important; }} .no-print {{ display: none; }} a {{ color: #3b82f6 !important; }} }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f8fafc; color: #334155; line-height: 1.5; }}
  a {{ color: #3b82f6; text-decoration: none; }}
  .page {{ max-width: 850px; margin: 0 auto; padding: 2rem; }}
  .header {{ text-align: center; padding-bottom: 1.5rem; border-bottom: 2px solid #e2e8f0; margin-bottom: 1.5rem; }}
  .header h1 {{ font-size: 2rem; color: #0f172a; }}
  .header .title {{ font-size: 1.1rem; color: #3b82f6; font-weight: 500; margin: 0.3rem 0; }}
  .summary {{ font-size: 0.95rem; color: #475569; margin-bottom: 1.5rem; text-align: center; max-width: 700px; margin-left: auto; margin-right: auto; }}
  .stats-bar {{ display: flex; justify-content: center; gap: 2rem; margin-bottom: 1.5rem; padding: 1rem; background: #f1f5f9; border-radius: 8px; flex-wrap: wrap; }}
  .stat {{ text-align: center; }}
  .stat .num {{ font-size: 1.5rem; font-weight: bold; color: #0f172a; }}
  .stat .lbl {{ font-size: 0.75rem; color: #64748b; text-transform: uppercase; }}
  section {{ margin-bottom: 1.5rem; }}
  section > h2 {{ font-size: 1.1rem; color: #0f172a; text-transform: uppercase; letter-spacing: 1px; padding-bottom: 0.4rem; border-bottom: 1px solid #e2e8f0; margin-bottom: 1rem; }}
  .skill-group {{ margin-bottom: 0.8rem; }}
  .skill-group h3 {{ font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.3rem; }}
  .skill-list {{ display: flex; flex-wrap: wrap; gap: 5px; }}
  .skill {{ background: #e0e7ff; color: #3730a3; padding: 3px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 500; }}
  .project {{ padding: 0.8rem 0; border-bottom: 1px solid #f1f5f9; }}
  .proj-header {{ display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; }}
  .proj-header strong {{ color: #0f172a; font-size: 0.95rem; }}
  .proj-meta {{ font-size: 0.8rem; color: #64748b; }}
  .proj-desc {{ font-size: 0.85rem; color: #475569; margin: 0.2rem 0; }}
  .proj-tech {{ font-size: 0.78rem; color: #3b82f6; margin-bottom: 0.2rem; }}
  .proj-features {{ font-size: 0.8rem; color: #64748b; padding-left: 1.2rem; }}
  .proj-features li {{ margin-bottom: 1px; }}
  .footer {{ text-align: center; color: #94a3b8; font-size: 0.75rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; }}
  .no-print {{ text-align: center; margin-bottom: 1rem; }}
  .no-print button {{ background: #3b82f6; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; }}
</style>
</head>
<body>
<div class="page">
  <div class="no-print"><button onclick="window.print()">Print / Save as PDF</button></div>
  <div class="header">
    <h1>{resume['name']}</h1>
    <div class="title">{resume['title']}</div>
  </div>
  <p class="summary">{resume['summary']}</p>
  <div class="stats-bar">
    <div class="stat"><div class="num">{stats['total_projects']}</div><div class="lbl">Projects</div></div>
    <div class="stat"><div class="num">{len(resume.get('ai_skills', {}))}</div><div class="lbl">Technologies</div></div>
    <div class="stat"><div class="num">{len(stats.get('categories_covered', []))}</div><div class="lbl">AI Domains</div></div>
    <div class="stat"><div class="num">{stats.get('total_tests_passed', 0)}</div><div class="lbl">Tests Passed</div></div>
  </div>
  <section><h2>Technical Skills</h2>{skills_html}</section>
  <section><h2>AI/ML Projects</h2>{projects_html}</section>
  <div class="footer">{resume['name']}</div>
</div>
</body>
</html>"""


def main():
    if not GH_TOKEN or not GH_USERNAME:
        print("ERROR: GH_TOKEN and GH_USERNAME must be set as environment variables")
        sys.exit(1)

    print(f"Scanning repos for {GH_USERNAME}...")
    repos = scan_repos()
    print(f"Found {len(repos)} AI project repos")

    known = load_known_projects()
    resume = load_resume_data()
    new_count = 0

    for repo in repos:
        name = repo["name"]
        if name in known["projects"]:
            continue

        print(f"  New repo: {name}")
        idea = get_file_content(GH_USERNAME, name, "project-idea.json")
        report = get_file_content(GH_USERNAME, name, "report-data.json") or {}

        if not idea:
            print(f"    Skipping — no project-idea.json found")
            known["projects"][name] = {"date": repo["created"], "status": "skipped"}
            continue

        if not report.get("repo_url"):
            report["repo_url"] = repo["url"]

        resume = update_resume(resume, idea, report)
        known["projects"][name] = {"date": repo["created"], "status": "indexed", "title": idea.get("title", "")}
        new_count += 1

    save_known_projects(known)
    save_resume_data(resume)

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    portfolio_html = generate_portfolio_html(resume, repos)
    with open(SITE_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(portfolio_html)

    resume_html = generate_resume_html(resume)
    with open(SITE_DIR / "resume.html", "w", encoding="utf-8") as f:
        f.write(resume_html)

    print(f"Done. {new_count} new projects indexed. Total: {len(resume.get('ai_projects', []))} projects, {len(resume.get('ai_skills', {}))} skills.")


if __name__ == "__main__":
    main()
