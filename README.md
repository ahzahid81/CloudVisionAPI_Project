# Vision Studio — Image Recognition Web App (Project P12)

A premium, presentation-ready **Streamlit** web application that uses **Google Gemini** to analyze uploaded images and deliver visual labels, object localization, and OCR text extraction through a clean, modern interface.

## Team Members

| Name | University ID |
| --- | --- |
| Asim bin Adel Al-Mutrafi | 441006293 |
| Abdul Hasib Zahid | 443058333 |
| MOHAMMAD TAKIUDDIN | 441037573 |

## Project Overview

Vision Studio provides an end-to-end image recognition experience:
- Users upload an image (`JPG`, `PNG`, `WEBP`)
- The app prepares the image and sends it for AI analysis
- Results are presented as **visual labels**, **located objects**, and **extracted text**
- Users can filter by confidence and export results for reporting

The project focuses on practical AI integration, usability, and polished presentation while keeping API credentials on the server side.

## Key Features

- **Premium UI/UX**: dark-themed, presentation-ready interface with clear step-by-step flow
- **Visual Label Detection**: identifies key subjects/scenes with estimated confidence
- **Object Localization**: highlights detected objects with bounding overlays on the image
- **Text Extraction (OCR)**: extracts readable text and supports text download
- **Confidence Filtering**: interactive minimum-confidence slider to refine displayed results
- **Result Exports**: download full JSON report, filtered CSV, and extracted text
- **Safe Handling**: image processed in memory; API key expected via secrets/environment

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend/UI | Streamlit (custom styled components/CSS) |
| Language | Python |
| AI Service | Google Gemini API (`gemini_service.py`) |
| Image Processing | Pillow (`PIL`) |
| Data/Export | JSON, CSV, in-memory processing |

## Project Structure

```text
CloudVisionAPI_Project/
├─ app.py                  # Streamlit UI, interaction flow, exports
├─ gemini_service.py       # Gemini request/response handling and analysis logic
├─ vision_service.py       # Image preparation utilities
├─ image_utils.py          # Image helper utilities
├─ requirements.txt        # Python dependencies
├─ Start.bat               # Windows launcher/setup script
├─ .streamlit/
│  ├─ config.toml          # Streamlit theme/server configuration
│  └─ secrets.toml.example # Secrets template (do not commit real secrets)
└─ README.md
```

## Getting Started (Windows)

### Prerequisites
- Python 3.10+ (Windows Python launcher recommended)
- A valid **Google Gemini API key**

### 1) Configure API Key
Create `.streamlit/secrets.toml` and add:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

Alternatively, set the `GEMINI_API_KEY` environment variable.

> Keep API keys private. Do not commit real secrets or include them in submissions.

### 2) Run the App
Double-click **`Start.bat`** (recommended on Windows).  
On first run it will create the virtual environment, install dependencies, and launch the app.

Manual run (optional):
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### 3) Use Vision Studio
1. Upload a `PNG`, `JPG/JPEG`, or `WEBP` image (up to 10 MB).
2. Click **Analyze image**.
3. Review **Visual labels**, **Objects**, and **Extracted text**.
4. Adjust confidence threshold and export reports as needed.

## Configuration Notes

- Streamlit UI/theme settings: `.streamlit/config.toml`
- Secrets template: `.streamlit/secrets.toml.example`
- Analysis depends on Gemini API availability, quotas, and project access
- Confidence values and object boxes are model estimates and may vary by image quality

## Academic Context

**Project P12 — Image Recognition Web Application**  
Designed for project presentation and demonstration of cloud/AI-powered image analysis in a user-friendly web interface.
