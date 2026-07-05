# ✅ PRE-DEPLOYMENT CHECKLIST

## Before You Deploy to Render

### 📦 Project Files
- [ ] `Dockerfile` exists and builds successfully
- [ ] `render.yaml` configured with environment variables
- [ ] `scripts/startup.sh` is executable
- [ ] `.gitignore` excludes `.env` and sensitive files
- [ ] `DEPLOYMENT_GUIDE.md` reviewed
- [ ] All Python dependencies in Dockerfile

### 🔐 Environment Variables
- [ ] Have OpenAI API key ready (or Gemini/Groq)
- [ ] API key has sufficient credits
- [ ] Know which LLM model to use (`gpt-4o-mini` recommended)
- [ ] Environment variables documented in `.env.example`

### 🧪 Local Testing
- [ ] `docker-compose up` works locally
- [ ] `GET /health` returns healthy status
- [ ] `POST /chat` returns recommendations
- [ ] Catalog has 7 real SHL assessments
- [ ] No mock data in responses
- [ ] All URLs are valid `https://www.shl.com/` URLs

### 📊 Evaluation Results
- [ ] Quality Score >= 80%
- [ ] Recall@10 >= 80%
- [ ] Success Rate = 100%
- [ ] All behavioral probes passing
- [ ] No hallucinations detected

### 🔧 Git Repository
- [ ] All changes committed
- [ ] Pushed to GitHub
- [ ] Repository is public (or private with access)
- [ ] README.md describes the project
- [ ] No secrets (`.env`) committed

### 📝 Documentation
- [ ] README.md complete
- [ ] DEPLOYMENT_GUIDE.md available
- [ ] FINAL_CATALOG_REPORT.md shows 7 assessments
- [ ] API endpoints documented

---

## During Render Setup

### 🌐 Render Account
- [ ] Signed up at render.com
- [ ] Connected GitHub account
- [ ] Authorized repository access

### ⚙️ Service Configuration
- [ ] Service name: `shl-assessment-recommender`
- [ ] Runtime: Docker
- [ ] Branch: main
- [ ] Plan: Free
- [ ] Region: Oregon (US West)

### 🔑 Environment Variables Set
- [ ] `OPENAI_API_KEY` (marked as secret)
- [ ] `LLM_PROVIDER=openai`
- [ ] `LLM_MODEL=gpt-4o-mini`
- [ ] `LLM_TEMPERATURE=0.0`
- [ ] `PORT=8000`
- [ ] `HOST=0.0.0.0`
- [ ] `LOG_LEVEL=INFO`

### 🏥 Health Check
- [ ] Health check path: `/health`
- [ ] Health check enabled

### 🚀 Deployment
- [ ] Auto-deploy on git push: Enabled
- [ ] Build started successfully
- [ ] No build errors in logs
- [ ] Service running status

---

## Post-Deployment Verification

### 🔍 Basic Tests
- [ ] `GET /health` returns 200 OK
- [ ] Health response shows `catalog_size: 7`
- [ ] Health response shows `status: "healthy"`
- [ ] `GET /docs` loads Swagger UI
- [ ] `GET /` shows welcome message

### 💬 Chat Endpoint Tests
- [ ] POST /chat accepts JSON
- [ ] Response has `reply` field
- [ ] Response has `recommendations` array
- [ ] Recommendations have required fields:
  - [ ] `name`
  - [ ] `url`
  - [ ] `description`
  - [ ] `relevance_score`
- [ ] All recommendation URLs start with `https://www.shl.com/`

### 🎯 Functional Tests
Test with these queries:
- [ ] "I need to assess problem-solving skills"
- [ ] "We're hiring a product manager"
- [ ] "I need personality assessments"
- [ ] "We need to evaluate communication skills"
- [ ] "I want to test situational judgment"

Each should return relevant assessments.

### 🛡️ Security Tests
- [ ] Guardrails block prompt injection attempts
- [ ] No sensitive data in responses
- [ ] CORS configured correctly
- [ ] Rate limiting works

### 📊 Data Validation
- [ ] Catalog contains exactly 7 assessments:
  1. SHL Global Skills Assessment
  2. SHL Realistic Job Previews
  3. Situational Judgement Tests
  4. Universal Competency Framework
  5. SHL Motivational Questionnaire
  6. SHL Occupational Personality Questionnaire
  7. SVAR Assessment
- [ ] All from `/products/assessments/` path
- [ ] No mock URLs (no `/solutions/products/assessments/`)
- [ ] All scraped from real SHL sitemap

### ⚡ Performance
- [ ] First request completes in < 5 seconds
- [ ] Subsequent requests < 2 seconds
- [ ] No timeout errors
- [ ] No 500 errors
- [ ] Memory usage stable

---

## Assignment Compliance

### ✅ Core Requirements
- [ ] Uses complete SHL Product Catalog
- [ ] Restricted to Individual Test Solutions only
- [ ] All assessments scraped from SHL website
- [ ] No Job Solutions in catalog
- [ ] No bundles, blogs, or marketing pages
- [ ] Complete traceability: Sitemap → Catalog → API

### ✅ No Mock Data
- [ ] No `create_mock_catalog.py` used
- [ ] No hardcoded assessment lists
- [ ] No placeholder URLs
- [ ] No demo data
- [ ] All data from real SHL scraping

### ✅ Data Quality
- [ ] All URLs are valid SHL URLs
- [ ] All descriptions are real (not generated)
- [ ] Metadata extracted from actual pages
- [ ] Scraping timestamps present
- [ ] Source field shows "sitemap" or "scraped"

### ✅ API Compliance
- [ ] FastAPI framework
- [ ] Docker containerized
- [ ] ChromaDB for vector storage
- [ ] Embedding model for semantic search
- [ ] LLM for conversational interface
- [ ] RESTful endpoints
- [ ] OpenAPI documentation

---

## Submission Readiness

### 📄 Required Documents
- [ ] README.md with setup instructions
- [ ] DEPLOYMENT_GUIDE.md
- [ ] FINAL_CATALOG_REPORT.md
- [ ] Evaluation results documented
- [ ] Architecture diagram (optional but recommended)

### 🔗 URLs to Submit
- [ ] GitHub repository URL
- [ ] Deployed API URL (Render)
- [ ] OpenAPI docs URL (`/docs`)
- [ ] Health check URL (`/health`)

### 📸 Screenshots (Optional)
- [ ] Health check response
- [ ] Sample chat interaction
- [ ] OpenAPI documentation page
- [ ] Evaluation results

### 📧 Submission Email
- [ ] Drafted email with all URLs
- [ ] Brief description of implementation
- [ ] Key metrics listed (quality score, recall, etc.)
- [ ] Any special notes or considerations

---

## Common Issues Checklist

### If Build Fails
- [ ] Check Dockerfile syntax
- [ ] Verify all dependencies listed
- [ ] Check for typos in package names
- [ ] Review build logs for specific error
- [ ] Ensure startup.sh is executable

### If Health Check Fails
- [ ] Verify port configuration (8000)
- [ ] Check HOST is 0.0.0.0
- [ ] Ensure FastAPI app is running
- [ ] Review application logs
- [ ] Test /health endpoint locally first

### If Chat Fails
- [ ] Verify OPENAI_API_KEY is set
- [ ] Check API key has credits
- [ ] Verify LLM_PROVIDER matches key type
- [ ] Check catalog was built (7 assessments)
- [ ] Verify embeddings were generated

### If No Recommendations
- [ ] Check catalog.json exists
- [ ] Verify 7 assessments in catalog
- [ ] Check ChromaDB was initialized
- [ ] Verify embedding model loaded
- [ ] Review retrieval logs

### If Wrong Data
- [ ] Ensure using build_catalog.py (not mock)
- [ ] Verify startup.sh doesn't call mock script
- [ ] Check Dockerfile builds real catalog
- [ ] Verify no old mock data cached
- [ ] Rebuild from scratch if needed

---

## Final Pre-Submission Check

Run this command locally:
```bash
./verify_deployment.sh https://your-app.onrender.com
```

All tests should pass:
- ✅ Health check
- ✅ Catalog size (7 assessments)
- ✅ Chat endpoint
- ✅ Valid SHL URLs
- ✅ OpenAPI docs

---

## 🎉 Ready to Deploy!

If all items are checked:
1. Commit any final changes
2. Push to GitHub
3. Create Render service
4. Add environment variables
5. Deploy and monitor
6. Run verification script
7. Test thoroughly
8. Submit!

---

**Good luck with your deployment!** 🚀

For questions, refer to:
- `DEPLOYMENT_GUIDE.md` - Detailed deployment steps
- `FINAL_CATALOG_REPORT.md` - Catalog compliance verification
- Render Docs: https://render.com/docs

**Checklist Version:** 1.0  
**Date:** 2026-07-05
