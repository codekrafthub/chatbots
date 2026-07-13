# CodeKraftHub — Summer Internship 2026

> **Interns:** Rohit/Devansh  
> **Mentor:** Kapil & Apratim (Co-founder, CodeKraftHub)  
> **Duration:** 60 Days | June – July 2026  
> **Focus:** Full-stack delivery of real client projects (WhatsApp bots + Voice AI)

---

## Repository Structure

```
codekrafthub-internship/
│
├── whatsapp-bot-1/          # Client Project #1 — WhatsApp chatbot
├── whatsapp-bot-2/          # Client Project #2 — WhatsApp chatbot
│
├── docs/
│   ├── architecture/        # System diagrams, flow charts, DB schemas
│   └── case-studies/        # Final case studies for each project
│
└── .github/
    ├── ISSUE_TEMPLATE/      # Bug report & feature request templates
    └── PULL_REQUEST_TEMPLATE.md
```

---

## How to Work in This Repo

### One folder = one project. No exceptions.
Each project lives in its own folder with its own `README.md`, `requirements.txt`, and `.env.example`. Never put code from two projects in the same folder.

### Never commit secrets.
No API keys, tokens, phone numbers, or `.env` files. Use `.env.example` to document what variables are needed. If you accidentally commit a secret, tell us **immediately** — do not try to hide it.

### Branching convention
```
main              → stable, reviewed code only
dev               → integration branch
feature/<name>    → your working branch (e.g. feature/lead-capture-flow)
fix/<name>        → bug fix branch (e.g. fix/webhook-timeout)
```

**Workflow:**
1. Branch off `dev` → `feature/your-feature`
2. Work + commit there
3. Open a PR to `dev` when ready for review
4. Mentors reviews → merges to `dev`
5. `dev` → `main` only on milestone completion

### Commit message format
```
type: short description (max 60 chars)

[optional body: what changed and why]
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

Examples:
```
feat: add lead capture webhook handler
fix: handle missing phone number in payload
docs: update deployment steps in README
chore: add .env.example with required keys
```

### Pull Request rules
- Every PR needs a description (use the template)
- Link the relevant issue if one exists
- At least one approval before merge
- No PR merges on Friday evening — avoid weekend fires

---

## Project Status

| Project | Intern(s) | Status | Week |
|---------|-----------|--------|------|
| WhatsApp Bot #1 | Rohit + Devansh | 🔵 In Progress | — |
| WhatsApp Bot #2 | Rohit + Devansh | ⚪ Not Started | — |
| Voice AI Assist | Kapil (intern support) | ⚪ Not Started | — |

*(Update this table as projects progress)*

---

## Getting Started (For Interns)

### Prerequisites
- Python 3.10+
- Git configured with your name and email
- VS Code (recommended) with Python + GitLens extensions

### First-time setup
```bash
# Clone the repo
git clone https://github.com/codekrafthub/<repo-name>.git
cd codekrafthub-internship

# Create your feature branch (never work on main directly)
git checkout dev
git checkout -b feature/your-name-setup

# Navigate to your project folder
cd whatsapp-bot-1

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your actual credentials
```

### Daily workflow
```bash
# Start of day — pull latest changes
git checkout dev
git pull origin dev
git checkout your-feature-branch
git merge dev   # keep your branch updated

# End of day — push your work
git add .
git commit -m "feat: describe what you did today"
git push origin your-feature-branch
```

---

## Documentation Standards

Every project folder must have:
- `README.md` — setup, architecture, how to run
- `requirements.txt` — exact package versions (`pip freeze > requirements.txt`)
- `.env.example` — all required env variables, no actual values
- `docs/architecture/` — at least one architecture diagram before you start coding

Every completed project must have:
- A case study in `docs/case-studies/` (use the template provided)
- Deployment guide in the project `README.md`
- A public blog post (Medium/Dev.to/LinkedIn) — link it in the README

---

## Resources

| Resource | Link |
|----------|------|
| WhatsApp Business API Docs | https://developers.facebook.com/docs/whatsapp |
| Flask Documentation | https://flask.palletsprojects.com |
| LiveKit Docs | https://docs.livekit.io |
| Ngrok (local webhook testing) | https://ngrok.com/docs |
| CodeKraftHub Website | https://codekrafthub.in |

---

## Code of Conduct for This Internship

1. **Ask before you assume.** Unsure about a requirement? Ask Mentors, don't guess and build the wrong thing.
2. **Show work daily.** Push at least one commit every working day — even if it's just documentation.
3. **Document as you build**, not after. Future-you will thank present-you.
4. **Customer information is confidential.** No client names, phone numbers, or business data in commits.
5. **Broken code on a branch is fine. Broken code on main is not.**

---

*Built with purpose in Bilaspur, Chhattisgarh.*  
*CodeKraftHub — bridging the gap between college and industry.*