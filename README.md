# Vision Studio — Project P12

Vision Studio is a Streamlit app that uses Gemini to identify visual labels, locate objects, and transcribe readable text in uploaded images.

## Run on Windows

1. Install Python 3.10 or later with the Windows Python launcher if needed.
2. Create a Gemini API key at https://aistudio.google.com/api-keys.
3. Save the key in `.streamlit/secrets.toml` as `GEMINI_API_KEY = "your-key"`, or set `GEMINI_API_KEY` in the server environment. On Streamlit Community Cloud, add the same entry under the app's **Settings → Secrets**.
4. Double-click **Start.bat**. The first run installs dependencies and requires internet access.
5. Upload a JPG, PNG, or WebP image up to 10 MB and click **Analyze image**. Adjust the confidence filter and export results as needed.

The app sends the image to Gemini when you start analysis. Usage limits and charges depend on your Google project. Object boxes and confidence values are estimates. Keep your API key out of source files and project submissions.

## Files

- app.py — Streamlit interface and exports.
- gemini_service.py — Gemini request, response parsing, and error handling.
- vision_service.py — Image preparation used by the interface.
- .streamlit/config.toml — Theme and local server settings.
- Start.bat — Windows setup and launcher.
