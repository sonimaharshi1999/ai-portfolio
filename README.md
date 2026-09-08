# Maharshi Soni — AI & QA Engineer Portfolio

A professional portfolio showcasing 20+ AI/QA automation projects with two themes, auto-updating resume, and GitHub Actions integration.

**Live:** `https://sonimaharshi1999.github.io/ai-portfolio/`

## Themes

### Engineering Dark Theme
A sleek, professional dark portfolio with green accents, scrolling skills marquee, animated counters, and fade-in sections.

> `https://sonimaharshi1999.github.io/ai-portfolio/engineering.html`

![Engineering Theme](docs/assets/screenshot-engineering.png)

*Features: Sticky nav with blur, scroll animations, counter animations, typing effect on hero, back-to-top button, company logos, 100+ skills marquee, priority-ordered projects*

### Spiderman Theme
A fun, comic-book inspired light theme with red/blue accents, spider-mask hover reveal, skewed ticker banners, and character illustrations.

> `https://sonimaharshi1999.github.io/ai-portfolio/spiderman.html`

![Spiderman Theme](docs/assets/screenshot-spiderman.png)

*Features: Hover over the spider mask to reveal the real photo, comic-ink text shadows (Anton font), skewed scrolling ticker, skill cards with hover expansion, spider character animations*

> **Note:** Spider-themed visuals are original illustrations. No copyrighted characters or trademarked assets were used.

## What's Inside

| Page | Description |
|------|-------------|
| **index.html** | Hub page — links to both themes, project list, social links |
| **engineering.html** | Professional dark portfolio with full resume content |
| **spiderman.html** | Comic-book themed portfolio (just for fun) |
| **resume.html** | Complete resume — print/save as PDF from browser |

## Content

- **20+ Projects** — AI-powered QA tools, RAG systems, agentic AI, NLP pipelines
- **100+ Technologies** — Python, Playwright, FAISS, LangGraph, FastAPI, scikit-learn, Docker, and more
- **5+ Years Experience** — PwC Automation QA, Subject Matter Expert, IIM Kozhikode MBA
- **40+ Certifications** — Google Gemini Agent Dev, Guidewire (13 versions), Google PM, LinkedIn, PwC

## Featured Projects

| Project | Category |
|---------|----------|
| Playwright AI Test Generator | QA + AI |
| LangGraph QA Agent | Agentic AI |
| Self-Healing Locator Engine | QA + ML |
| AI Visual Regression Tester | Computer Vision |
| BDD Scenario Generator | NLP + QA |
| RAG QA Knowledge Base | RAG |
| Insurance Document Analyzer | NLP + Insurance |
| Flaky Test Detector | ML + QA |
| AI API Contract Validator | API + NLP |
| AI Test Data Generator | ML + QA |
| AI Bug Triager | NLP + QA |

## Auto-Updating (GitHub Actions)

The portfolio auto-updates when new AI project repos are detected:

```
You upload AI project → GitHub Actions detects it → Portfolio + Resume auto-update
     (manual)              (daily cron, free)         (GitHub Pages, free)
```

No AI APIs needed. Just Python reading JSON and generating HTML.

### Setup

1. **Create a fine-grained token** at https://github.com/settings/tokens?type=beta (read-only repo access)
2. **Add secrets** to this repo: `PORTFOLIO_TOKEN` + `GH_USERNAME`
3. **Enable GitHub Pages**: Settings → Pages → Branch: `main`, folder: `/docs`

## File Structure

```
ai-portfolio/
├── .github/workflows/
│   └── update-portfolio.yml     ← GitHub Action (daily scan)
├── scripts/
│   └── scan_and_update.py       ← Scans repos, updates portfolio
├── docs/
│   ├── index.html               ← Hub page
│   ├── engineering.html          ← Dark theme portfolio
│   ├── spiderman.html            ← Comic theme portfolio
│   ├── resume.html               ← Full resume
│   └── assets/
│       ├── photo.png             ← Profile photo
│       ├── spider_mask.svg       ← Spider mask (hero overlay)
│       ├── spider_hero_character.svg  ← Standing character
│       └── spider_hero_hanging.svg    ← Hanging character
└── README.md
```

## Screenshots

> Add your own screenshots here after deploying. Take them at full browser width for best results.
>
> To add: take screenshots, save as `docs/assets/screenshot-engineering.png` and `docs/assets/screenshot-spiderman.png`, push to repo. Or record a GIF of the spiderman hover effect.

## Author

**Maharshi Soni**
- GitHub: [sonimaharshi1999](https://github.com/sonimaharshi1999)
- LinkedIn: [maharshi-soni-b56736170](https://linkedin.com/in/maharshi-soni-b56736170)
- Email: soni.maharshi1999@gmail.com

## License

MIT — All projects are original work, fully copyright compliant. No proprietary assets or third-party intellectual property were used.
