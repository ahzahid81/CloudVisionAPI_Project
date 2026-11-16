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

## Result sections

- **Labels:** the most likely subjects of the image, such as "Cat", "Outdoor" or "Sky".
- **Objects:** localized objects with a labelled bounding box and confidence score.
- **Text:** all text found by OCR, with a downloadable `.txt` file.
- **Developer details:** the raw Vision API response and a JSON download.

## Technologies

| Technology | Purpose |
| --- | --- |
| Python 3.13 | Application language |
| Streamlit | Web interface |
| Google Cloud Vision API | Image analysis |
| google-cloud-vision | Vision API client |
| Pillow | Image loading and bounding-box drawing |
| pandas | Result tables |

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
