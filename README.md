# Image Recognition with Google Cloud Vision

**Project P12**

| Team member | University ID |
| --- | --- |
| Asim bin Adel Al-Mutrafi | 441006293 |
| Abdul Hasib Zahid | 443058333 |
| MOHAMMAD TAKIUDDIN | 441037573 |

**Live app:** https://platformproject.streamlit.app  
**Repository:** https://github.com/ahzahid81/CloudVisionAPI_Project

A simple, deployment-ready Streamlit app that sends an uploaded image to the **Google
Cloud Vision API** and presents labels, localized objects with bounding boxes, and OCR
text with confidence scores.

## Features

- One-step flow: upload an image and analysis starts automatically.
- Label detection with confidence scores.
- Object localization with labelled bounding boxes.
- Text extraction (OCR) with a downloadable text file.
- Clean, centered interface that works on desktop and mobile.
- Credentials are read server-side from Streamlit secrets and never exposed in the UI.
- Optional password protection for public deployments.
- Raw API response available in a collapsed developer section.

## Project structure

```
CloudVisionAPI_Project/
├── app.py                        # Streamlit UI and page flow
├── vision_service.py             # Google Cloud Vision client and response parsing
├── image_utils.py                # Draws object bounding boxes with Pillow
├── run_app.cmd                   # One-click Windows launcher
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    ├── config.toml               # Theme, upload limit, privacy settings
    ├── secrets.toml              # Local credentials (git-ignored)
    └── secrets.toml.example      # Credential and password template
```

## Run locally

Use Python 3.13 (Python 3.10 or newer works). Double-click `run_app.cmd`, or run:

```powershell
cd path\to\CloudVisionAPI_Project
.\run_app.cmd
```

The launcher creates the virtual environment, installs dependencies on first use, and
opens the app at `http://localhost:8501`.

Manual start:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Google Cloud setup

1. Create or select a project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Cloud Vision API** under **APIs & Services → Library**.
3. Link an active **billing account** under **Billing**. Vision requires billing even
   within the free tier.
4. Create a **service account** under **IAM & Admin → Service Accounts** and grant it the
   **Cloud Vision API User** role. The service account must belong to the same project
   where the Vision API and billing are enabled.
5. Create and download a **JSON key** for the service account.

## Configuration

Credentials are stored server-side in `.streamlit/secrets.toml` and are ignored by Git.
Copy the template and paste the contents of your JSON key:

```powershell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

The file must define a `[gcp_service_account]` table. If no secrets are configured, the app
falls back to Google Application Default Credentials (ADC) for local development.

To require a password before visitors can use the app, add this line **before** the
`[gcp_service_account]` section:

```toml
app_password = "choose-a-strong-password"
```

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository. Never commit `.streamlit/secrets.toml`.
2. Sign in at [share.streamlit.io](https://share.streamlit.io/) and choose **Create app**.
3. Select the repository and branch. Set **Main file path** to `app.py` — the deploy form
   prefills `streamlit_app.py`, which does not exist in this repository.
4. Open **Advanced settings → Secrets** and paste:

   ```toml
   app_password = "choose-a-strong-password"

   [gcp_service_account]
   type = "service_account"
   project_id = "your-project-id"
   private_key = "-----BEGIN PRIVATE KEY-----\n..."
   client_email = "vision-app@your-project-id.iam.gserviceaccount.com"
   ...
   ```

   Copy every field from your JSON key. Remove the `app_password` line if the app should
   be public. Never add credentials to `README.md`, source files, or the Git repository.
5. Select Python 3.13 if prompted, then click **Deploy**.
6. Verify the deployed app at https://platformproject.streamlit.app.

Make sure the Cloud Vision API and billing are enabled for the project before deploying.

### Deployment checklist

- [ ] Cloud Vision API enabled and billing active.
- [ ] Service account key rotated and restricted to the **Cloud Vision API User** role.
- [ ] `.streamlit/secrets.toml` and key files excluded from the repository.
- [ ] `requirements.txt` present in the repository root with pinned versions.
- [ ] Secrets pasted into **Advanced settings → Secrets**.
- [ ] `app_password` set for a public app.
- [ ] Python 3.13 selected.
- [ ] Live app reachable at https://platformproject.streamlit.app.
- [ ] One test image analyzed successfully after deployment.

## How it works

1. Streamlit reads the uploaded image and sends the bytes to `analyze_image()`.
2. `vision_service.py` builds an `AnnotateImageRequest` with `LABEL_DETECTION`,
   `OBJECT_LOCALIZATION` and `TEXT_DETECTION`.
3. Google Cloud Vision returns labels, normalized object bounding boxes and OCR text.
4. The app parses the response, draws the boxes with Pillow, and renders the results with
   confidence scores.

Results are cached in Streamlit's session state, so switching tabs does not call the API
again. A new image triggers one new analysis.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| "This file does not exist" during deployment | Set **Main file path** to `app.py`, not `streamlit_app.py`. |
| "This application is not configured..." | Add `[gcp_service_account]` to Streamlit secrets and restart the app. |
| Billing error | Link an active billing account to the Google Cloud project. |
| `PermissionDenied` / `403` | Grant the service account the **Cloud Vision API User** role. |
| API disabled | Enable the Cloud Vision API and wait a few minutes. |
| No text found | Use a sharper, higher-contrast image with larger text. |
| Image rejected | Keep the file under 20 MB and use JPG, PNG, WEBP, BMP or GIF. |

## Security notes

- `.streamlit/secrets.toml`, `.env`, service-account JSON keys and PEM files are git-ignored.
- Restrict local secret files to your user account.
- Rotate the service account key if it has ever been shared or committed.
- Add `app_password` to protect a public deployment from API quota abuse.
- `showErrorDetails` is disabled in the deployed UI; technical errors are written to the
  server logs instead.

## Cost

Google Cloud Vision includes a limited free monthly tier. Requests beyond the free usage
are billed. See the current [Vision API pricing](https://cloud.google.com/vision/pricing).
