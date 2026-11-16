# Image Recognition with Google Cloud Vision

**Project P12 — Image Recognition Web Application**

| Team member | University ID |
| --- | --- |
| Asim bin Adel Al-Mutrafi | 441006293 |
| Abdul Hasib Zahid | 443058333 |
| MOHAMMAD TAKIUDDIN | 441037573 |

## Project overview

This project is a web application that uses the **Google Cloud Vision API** to analyze an
uploaded image. It identifies the image content, locates objects, and extracts visible text
using cloud-based computer vision.

The app follows a single-page flow: the user selects an image, analysis starts
automatically, and the results are displayed in three organized tabs.

## Objectives

- Apply a cloud AI service to a practical image recognition task.
- Present labels, objects, and extracted text with confidence scores.
- Provide a simple and clear interface for non-technical users.
- Keep Google Cloud credentials on the server side.

## Features

- Upload JPG, PNG, WEBP, BMP or GIF images up to 20 MB.
- Automatic analysis as soon as an image is selected.
- **Label detection** with confidence scores.
- **Object localization** with labelled bounding boxes.
- **Text detection (OCR)** with a downloadable text file.
- Result summary showing label, object, and word counts.
- Optional password protection.
- Raw Vision API response in a developer-only section.

## How it works

1. The user uploads an image through the web interface.
2. The app validates the file and sends its bytes to the Vision service.
3. A single `AnnotateImageRequest` requests three features:
   `LABEL_DETECTION`, `OBJECT_LOCALIZATION` and `TEXT_DETECTION`.
4. The Vision API returns labels, normalized bounding boxes, and text annotations.
5. The app parses the response, draws object boxes with Pillow, and displays the results
   with confidence scores.

Results are cached in the app session, so switching tabs does not send the same image to
the API again. A new image triggers one new analysis.

## Technologies

| Technology | Purpose |
| --- | --- |
| Python 3.13 | Application language |
| Streamlit | Web interface |
| Google Cloud Vision API | Image analysis |
| google-cloud-vision | Vision API client |
| Pillow | Image loading and bounding-box drawing |
| pandas | Result tables |
| TOML secrets | Server-side credential storage |

## Project structure

```
CloudVisionAPI_Project/
├── app.py                        # Web interface and page flow
├── vision_service.py             # Vision client and response parsing
├── image_utils.py                # Bounding-box rendering with Pillow
├── run_app.cmd                   # One-click Windows launcher
├── requirements.txt              # Python dependencies
├── README.md
├── .gitignore
└── .streamlit/
    ├── config.toml               # Theme, upload limit and privacy settings
    ├── secrets.toml              # Local credentials (ignored by Git)
    └── secrets.toml.example      # Credential template
```

## Local setup

### Requirements

- Python 3.10 or newer (developed and tested with Python 3.13).
- A Google Cloud project.
- The **Cloud Vision API** enabled for the project.
- An active **billing account** linked to the project. Vision requires billing, even
  within the free tier.
- A **service account** with the **Cloud Vision API User** role and a JSON key.

### Install and run

Double-click `run_app.cmd`, or use a terminal in the project folder:

```powershell
cd path\to\CloudVisionAPI_Project
.\run_app.cmd
```

The launcher creates the virtual environment, installs dependencies on first use, and opens
the app at `http://localhost:8501`.

Manual start:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

### Credentials

Copy the template and paste the contents of the service account JSON key:

```powershell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

The file must define a `[gcp_service_account]` table. If no secrets are provided, the app
falls back to Google Application Default Credentials (ADC) during local development.

To require a password before using the app, add this line before the
`[gcp_service_account]` section:

```toml
app_password = "choose-a-strong-password"
```

## Result sections

- **Labels:** the most likely subjects of the image, such as "Cat", "Outdoor" or "Sky".
- **Objects:** localized objects with a labelled bounding box and confidence score.
- **Text:** all text found by OCR, with a downloadable `.txt` file.
- **Developer details:** the raw Vision API response and a JSON download.

## Notes

- Uploaded images are sent to Google Cloud Vision for analysis and are not stored by the
  app.
- Each analysis uses three Vision features in one request.
- `.streamlit/secrets.toml`, service account key files, and environment files are ignored
  by Git.
- Service account keys should be rotated if they have ever been shared.
