# Moments ML Features Deliverables

Submission metadata (fill on GitHub build): commit URL and repository URL are prepended by CI in the rendered PDF artifact.

## 1) Technical Description

This Moments fork adds two ML-powered features using off-the-shelf models:

- Alternative Text Generation (Image Captioning)
  - Model: Salesforce/blip-image-captioning-base (Hugging Face Transformers)
  - Service: `moments/ml_services.py` provides `MLImageAnalyzer.generate_alt_text(image_path)`
  - Storage: `moments/models.py` adds `Photo.alt_text`
  - Integration: `moments/blueprints/main.py` in upload flow generates a caption and stores it; templates use `alt` attributes

- Object Detection for Image Search
  - Model: hustvl/yolos-tiny (Hugging Face Transformers)
  - Service: `moments/ml_services.py` provides `detect_objects(image_path)` returning labels, confidences, boxes
  - Storage: `moments/models.py` adds `Photo.detected_objects` (JSON string) and helpers
  - Search: `/search/objects` route in `moments/blueprints/main.py` queries `alt_text` and `detected_objects`

Key Files and Pointers

- ML service: `moments/ml_services.py`
- Data model changes: `moments/models.py` (fields, helpers, Whooshee indexing)
- Upload integration & search route: `moments/blueprints/main.py` (upload flow, `/search/objects`)
- Templates with alt attributes: `templates/main/photo.html`, `templates/main/index.html`, `templates/macros.html`
- Migration helper: `migrate_db.py`
- Dependencies: `requirements.txt`

Behavior

- On photo upload, the app:
  1) Stores original and resized images
  2) Generates `alt_text` via BLIP
  3) Detects objects via YOLOS and stores JSON metadata
  4) If user description is empty, sets `description = alt_text`
  5) Renders `<img alt="...">` from `alt_text`
  6) Enables search by object keywords/alt text via `/search/objects`

## 2) User Interface Design Approach

Recommendations per feature

- Alternative Text Generation: automate + annotate
  - Forcefulness: low; runs automatically after upload, no blocking dialogs
  - Frequency: each upload
  - Value: accessibility, SEO, improved browse/search
  - Cost: small latency on first model load; acceptable thereafter
  - UI: show generated description; allow edit inline on photo page

- Object-Based Search: organize + annotate
  - Forcefulness: low; exposed as a search option/tab
  - Frequency: on demand
  - Value: discovery of content, better retrieval
  - Cost: minimal at query time (DB filter on stored metadata)
  - UI: keep a dedicated “Objects (ML)” search category

If given more time

- Provide a review prompt post-upload: “Use this generated description?” with Accept/Edit options
- Surfacing detected object tags visually (chips) with quick-add to user tags

## 3) Harms

Potential harms

- Inaccurate or biased captions
  - Risk: mislabeling sensitive content; uneven performance across demographics
  - Mitigation: transparency (label as AI-generated), easy user edits, reporting mechanism

- Privacy and sensitive content
  - Risk: revealing private details in captions/objects
  - Mitigation: filter sensitive classes; allow per-user opt-out; default-private uploads for minors

- Accessibility regressions
  - Risk: poor captions hinder rather than help screen reader users
  - Mitigation: quality threshold (fallback to generic alt), encourage human edits

- Abuse and moderation
  - Risk: captions/keywords surface harmful content more easily
  - Mitigation: moderation pipeline on generated text; blocklist; rate limits

## 4) Production Challenges

Scalability / Latency

- Challenge: model inference cost and cold starts
- Solution: async workers (Celery/RQ) + model warm pools; GPU-backed batch inference; queue backpressure

Storage & Indexing

- Challenge: storing per-image metadata at scale; fast retrieval
- Solution: store normalized object labels; move to search infra (OpenSearch/MeiliSearch) for alt_text/labels

Costs

- Challenge: inference cost for millions of images
- Solution: budget caps, tiered quality (tiny/medium models), vendor rate negotiation, cache dedup across identical files (hashing)

Reliability

- Challenge: third-party model downloads, outages
- Solution: containerize models, mirror weights, health checks & circuit breakers

Security

- Challenge: model download execution, input sanitization
- Solution: signed model sources, strict image validation, sandboxed workers

Roadmap Improvements

- Background job for ML; upload returns immediately
- Editable captions with audit trail
- Per-user settings to enable/disable ML features

## 5) How to Run (Commands)

```bash
pip install -r requirements.txt

python3 -c "from moments import create_app; app = create_app('development'); app.app_context().push(); from moments.core.extensions import db; db.create_all(); print('Database initialized')"

python3 migrate_db.py

# Optional demo data
flask lorem

flask run
# Open http://127.0.0.1:5000/ and login: admin@helloflask.com / moments
```

## 6) Packaging (Zip)

Run:

```bash
zip -r moments_ml_submission.zip . -x "*.pyc" -x "__pycache__/*" -x ".git/*" -x "*.pth" -x "*.bin"
```

## 7) Grading Compliance Checklist

- Clearly structured by question with distinct sections (this document)
- Includes a specific commit link (prepended by CI in the generated PDF)
- README provides install/run instructions; app is runnable
- No private credentials in repository history
- Alternative text generation described and implemented; `<img alt>` present for uploaded photos
- Image search described and implemented; functional keyword object search
- UI design recommendations justified using automate/prompt/organize/annotate/hybrid and 4-factor lens
- Harms: at least one harm identified with plausible mitigations
- Production challenges: at least one problem identified with plausible solutions

