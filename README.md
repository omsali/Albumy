# Moments - ML-Enhanced Photo Sharing App

A photo sharing social networking app built with Python and Flask, enhanced with machine learning capabilities for automatic alternative text generation and object-based image search. The example application for the book *[Python Web Development with Flask (2nd edition)](https://helloflask.com/en/book/4)* (《[Flask Web 开发实战（第 2 版）](https://helloflask.com/book/4)》).

Demo: http://moments.helloflask.com

![Screenshot](demo.png)

## New ML Features

This enhanced version includes:

- **Automatic Alternative Text Generation**: Uses BLIP (Bootstrapping Language-Image Pre-training) model to automatically generate descriptive alternative text for uploaded images, improving accessibility for screen readers and search engines.

- **Object-Based Image Search**: Uses YOLOS (You Only Look at One Sequence) model to detect objects in images, enabling users to search for photos by the objects they contain (e.g., "dog", "car", "person").

## Installation

Clone the repo:

```
$ git clone https://github.com/greyli/moments
$ cd moments
```

### Option 1: Using pip (Recommended)

Install dependencies with pip:

```bash
$ pip install -r requirements.txt
```

### Option 2: Using PDM

Install dependencies with [PDM](https://pdm.fming.dev):

```
$ pdm install
```

> [!TIP]
> If you don't have PDM installed, you can create a virtual environment with `venv` and install dependencies with `pip install -r requirements.txt`.

## Setup

To initialize the app, run the following commands:

```bash
# Initialize the database
$ python -c "from moments import create_app; app = create_app('development'); app.app_context().push(); from moments.core.extensions import db; db.create_all(); print('Database initialized')"

# Run database migration (adds ML fields)
$ python migrate_db.py
```

If you just want to try it out, generate fake data with `flask lorem` command then run the app:

```
$ flask lorem
```

It will create a test account:

* email: `admin@helloflask.com`
* password: `moments`

Now you can run the app:

```
$ flask run
* Running on http://127.0.0.1:5000/
```

## ML Dependencies

The ML features require additional packages that are included in the requirements.txt:

- `torch`: PyTorch for deep learning models
- `transformers`: Hugging Face transformers library for pre-trained models
- `pillow`: Image processing
- `requests`: HTTP requests for model downloads

**Note**: On first run, the models will be downloaded automatically. This may take several minutes depending on your internet connection. The models are cached locally for subsequent runs.

## Usage

### Alternative Text Generation

When you upload a photo, the system automatically:
1. Analyzes the image using the BLIP model
2. Generates descriptive alternative text
3. Stores the text in the database
4. Includes it in the HTML `alt` attribute for accessibility
5. **Auto-populates the photo description** if you don't provide one

**Smart Description Logic:**
- If you provide a description during upload → Your description is used
- If you leave the description empty → AI-generated description is automatically added
- This ensures every photo has a meaningful description for better user experience

### Object-Based Search

You can search for photos by objects they contain:
1. Go to the search page
2. Select "Objects (ML)" tab
3. Enter keywords like "dog", "car", "person", etc.
4. The system will find photos containing those objects

## Technical Details

- **Caption Model**: Salesforce/blip-image-captioning-base
- **Object Detection Model**: hustvl/yolos-tiny
- **Database**: SQLite with additional fields for ML data
- **Search**: Enhanced search functionality using both text and object detection

## What Was Implemented (High-level)

- Added ML-powered alternative text generation for uploaded images
- Added object detection to enable object-based image search
- Persisted ML outputs on `Photo` as `alt_text` and `detected_objects`
- Updated templates to include meaningful `alt` attributes
- Implemented smart description fallback: if no user description, use generated alt text
- Added a migration helper to add the two new columns

## Implementation Summary (Files & Key Changes)

- `moments/ml_services.py`: New `MLImageAnalyzer` service that loads BLIP and YOLOS models and exposes:
  - `generate_alt_text(image_path)`
  - `detect_objects(image_path)`
- `moments/models.py` (`Photo`): Added fields
  - `alt_text: String(500)`
  - `detected_objects: Text` (JSON string)
  - Helper methods for parsing and keyword extraction
  - Registered with Whooshee to index `description`, `alt_text`, `detected_objects`
- `moments/blueprints/main.py`:
  - Upload flow: after saving images, run ML analysis, store `alt_text` and `detected_objects`
  - If `description` is empty, set it to generated `alt_text`
  - New route `/search/objects` to search by ML-derived fields
- Templates:
  - `templates/main/photo.html`, `templates/main/index.html`, `templates/macros.html`: ensure `<img alt="...">` uses `photo.alt_text` or a fallback
  - `templates/main/search.html`: add "Objects (ML)" tab and render results
- `migrate_db.py`: Adds `alt_text` and `detected_objects` columns if missing
- `requirements.txt`: Added ML deps: `torch`, `transformers`, `pillow`, `requests`

## How It Works (End-to-End)

1. User uploads an image
2. App writes original and resized images to `MOMENTS_UPLOAD_PATH`
3. A `Photo` row is created
4. ML service:
   - Generates a descriptive caption (stored as `alt_text`)
   - Detects objects and confidences (stored as JSON in `detected_objects`)
5. If the user did not provide a description, the generated `alt_text` becomes the `description`
6. Templates render accessible `<img alt>` and search can leverage ML outputs

## Running Locally (Quick Start)

1) Install dependencies
```bash
pip install -r requirements.txt
```

2) Initialize database and run migration
```bash
python3 -c "from moments import create_app; app = create_app('development'); app.app_context().push(); from moments.core.extensions import db; db.create_all(); print('Database initialized')"
python3 migrate_db.py
```

3) (Optional) Seed sample data
```bash
flask lorem
```

4) Start the app
```bash
flask run
# open http://127.0.0.1:5000/
```

Login for demo:
- email: `admin@helloflask.com`
- password: `moments`

## Troubleshooting

- First run downloads models; allow several minutes and ensure internet access
- If uploads work but you see blank alt text on the very first request, wait until the model finishes its initial download and retry the upload

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).
