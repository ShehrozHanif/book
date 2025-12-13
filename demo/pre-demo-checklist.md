# Pre-Demo Validation Checklist

**Purpose**: Final validation before hackathon demo
**Status**: Run through this checklist before every demo

---

## 1. Content Validation

### Chapter Files
- [ ] Chapter 1 exists at `docusaurus/docs/chapter-1-foundations.md`
- [ ] Chapter 2 exists at `docusaurus/docs/chapter-2-ros2.md`
- [ ] Chapter 3 exists at `docusaurus/docs/chapter-3-simulation.md`
- [ ] Chapter 4 exists at `docusaurus/docs/chapter-4-vla.md`

### Approval Markers
- [ ] Each chapter has YAML frontmatter with `approval: reviewer: PASS`
- [ ] Each chapter has `approved_by: Human Project Owner`
- [ ] Each chapter has a valid `date` field

### Content Quality
- [ ] Each chapter has Learning Objectives section
- [ ] Each chapter has 6-8 major sections
- [ ] Each chapter has Mermaid diagrams (2-4 per chapter)
- [ ] Each chapter has Experimental/Evolving section
- [ ] Each chapter has Further Reading section

---

## 2. Frontend Validation

### Build Test
```bash
cd docusaurus
npm install
npm run build
```
- [ ] Build completes without errors
- [ ] Build completes without warnings (or warnings are acceptable)

### Local Server Test
```bash
npm start
```
- [ ] Server starts at http://localhost:3000
- [ ] Homepage loads correctly
- [ ] "Start Learning" button links to Chapter 1
- [ ] Sidebar shows all 4 chapters
- [ ] Can navigate between chapters
- [ ] Mermaid diagrams render correctly
- [ ] ChatBot toggle button appears (bottom-right)

---

## 3. Backend Validation

### Index Creation
```bash
cd rag
pip install -r requirements.txt
python indexer.py
```
- [ ] Indexer runs without errors
- [ ] Reports all 4 chapters processed
- [ ] Creates `index.json` file
- [ ] Reports chunk count > 0

### API Server Test
```bash
python api.py
```
- [ ] Server starts at http://localhost:8000
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] Docs available at http://localhost:8000/docs

### API Functionality Test
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the perception-action loop?"}'
```
- [ ] Returns successful response with answer
- [ ] Answer includes citations
- [ ] Confidence score is above threshold (0.72)

---

## 4. Chatbot Integration Validation

With both frontend and backend running:

- [ ] ChatBot button appears on textbook pages
- [ ] Clicking button opens chat window
- [ ] Status dot shows green (API online)
- [ ] Can type and send a message
- [ ] Receives response with citations
- [ ] Can close chat window

### Test Queries
- [ ] "What is the perception-action loop?" → Success with citation
- [ ] "What is domain randomization?" → Success with citation
- [ ] "What is the price of a robot?" → Out of scope refusal
- [ ] "How do I build a robot arm?" → Safety refusal

---

## 5. Demo Materials Validation

### Demo Files
- [ ] `demo/canonical-questions.md` exists and has test questions
- [ ] `demo/demo-script.md` exists with full demo flow
- [ ] `demo/negative-tests.md` exists with refusal test cases

### Fallback Assets
- [ ] `assets/screenshots/` directory exists
- [ ] (Optional) Screenshots captured for fallback demo

### Specification Files
- [ ] `constitution.md` or `.specify/memory/constitution.md` accessible
- [ ] `specs/001-robotics-textbook-spec/spec.md` accessible
- [ ] `specs/001-robotics-textbook-spec/plan.md` accessible

---

## 6. Deployment Validation (If Deployed)

- [ ] Site is accessible at deployed URL
- [ ] All pages load correctly
- [ ] (If backend deployed) Chatbot connects successfully

---

## 7. Final Demo Prep

### Browser Setup
- [ ] Browser in presentation mode / zoomed appropriately
- [ ] DevTools closed
- [ ] No embarrassing bookmarks/tabs visible

### Terminal Setup (if showing backend)
- [ ] Terminal font size readable
- [ ] Backend running and ready

### Demo Script
- [ ] `demo/demo-script.md` open for reference
- [ ] `demo/canonical-questions.md` accessible
- [ ] Know the 5-7 minute flow

---

## Quick Validation Commands

```bash
# 1. Build frontend
cd docusaurus && npm run build

# 2. Create index
cd ../rag && python indexer.py

# 3. Test API
python -c "from api import app; print('API imports OK')"

# 4. Start everything (two terminals)
# Terminal 1: cd docusaurus && npm start
# Terminal 2: cd rag && python api.py
```

---

## Emergency Contacts / Fallback Plan

If demo fails:
1. Open `demo/demo-script.md` Section 7.4 (Fallback Demo)
2. Walk through architecture using spec files
3. Show screenshots if available
4. Explain the system verbally

**Remember**: Judges evaluate architecture and intent, not just uptime.

---

## Sign-Off

- [ ] All critical checks pass
- [ ] Demo rehearsed at least once
- [ ] Fallback plan understood

**Ready for demo!**
