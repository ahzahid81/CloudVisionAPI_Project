"""Image Recognition App powered by the Google Cloud Vision API."""

from __future__ import annotations

import hashlib
import hmac
import io
import json
import logging
from pathlib import Path

import pandas as pd
import streamlit as st
from google.api_core.exceptions import GoogleAPIError
from PIL import Image, UnidentifiedImageError

from image_utils import annotate_objects
from vision_service import VisionClientError, analyze_image, build_client

MAX_RESULTS = 20
MAX_UPLOAD_MB = 20
TEAM = (
    ("Asim bin Adel Al-Mutrafi", "441006293"),
    ("Abdul Hasib Zahid", "443058333"),
    ("MOHAMMAD TAKIUDDIN", "441037573"),
)

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Image Recognition",
    page_icon=":material/image_search:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

STYLES = """
<style>
    .block-container {
        max-width: 860px;
        padding-bottom: 3rem;
        padding-top: 2rem;
    }
    .hero {
        background: linear-gradient(135deg, #0b1f3a 0%, #1d4ed8 100%);
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 1.6rem;
        padding: 2rem 2.2rem;
    }
    .hero-eyebrow {
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        opacity: 0.82;
        text-transform: uppercase;
    }
    .hero h1 {
        font-size: 2.15rem;
        letter-spacing: -0.02em;
        margin: 0.5rem 0 0.55rem;
    }
    .hero p {
        margin: 0;
        max-width: 62ch;
        opacity: 0.92;
    }
    .team-name {
        font-weight: 600;
    }
    .team-id {
        color: #64748b;
        font-size: 0.86rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem;
    }
    [data-testid="stFileUploaderDropzone"] {
        border-radius: 12px;
    }
</style>
"""
st.markdown(STYLES, unsafe_allow_html=True)


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">Project P12 · Google Cloud Vision</div>
            <h1>Image Recognition</h1>
            <p>Upload a photo to identify its content, locate objects, and extract
            text in seconds.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _app_password() -> str | None:
    try:
        value = st.secrets.get("app_password")
    except Exception:
        return None
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def require_password() -> None:
    password = _app_password()
    if not password or st.session_state.get("authenticated"):
        return

    st.subheader("Sign in")
    st.caption("This application is password protected.")
    with st.form("login"):
        entered = st.text_input(
            "Password",
            type="password",
            placeholder="Password",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button(
            "Continue", type="primary", width="stretch"
        )
    if submitted:
        if hmac.compare_digest(entered, password):
            st.session_state["authenticated"] = True
            st.rerun()
        st.error("Incorrect password. Please try again.")
    st.stop()


@st.cache_resource(show_spinner=False)
def get_client():
    try:
        info = dict(st.secrets["gcp_service_account"])
    except Exception:
        info = None
    return build_client(info)


def get_client_or_error():
    try:
        return get_client(), None
    except VisionClientError:
        logger.exception("Could not initialize the Vision client")
        return (
            None,
            "This application is not configured for image analysis yet. "
            "Please contact the app owner.",
        )
    except Exception:
        logger.exception("Unexpected client initialization error")
        return (
            None,
            "The image analysis service is unavailable right now. "
            "Please try again later.",
        )


def describe_analysis_error(exc: Exception) -> str:
    message = str(exc).lower()
    if "billing" in message:
        return (
            "Image analysis is unavailable because the Google Cloud billing "
            "account for this project is not active. Please contact the app owner."
        )
    if "permission" in message or "forbidden" in message:
        return (
            "The image analysis service is not available for this project. "
            "Please contact the app owner."
        )
    return "The image could not be analyzed right now. Please try again in a moment."


def analyze_uploaded_image(client, file_bytes: bytes):
    try:
        return analyze_image(client, file_bytes, max_results=MAX_RESULTS), None
    except VisionClientError:
        logger.exception("The Vision API returned an error")
        return None, "The image could not be analyzed. Please try again."
    except GoogleAPIError as exc:
        logger.exception("The Vision API request failed")
        return None, describe_analysis_error(exc)
    except Exception:
        logger.exception("Unexpected error while analyzing an image")
        return (
            None,
            "Something went wrong while analyzing the image. Please try again.",
        )


def render_empty_state() -> None:
    st.caption("Upload a JPG, PNG, WEBP, BMP or GIF image up to 20 MB to get started.")
    st.caption(
        "Your image is sent to Google Cloud Vision for analysis. "
        "This app does not store it."
    )


def render_results(result, image: Image.Image, file_stem: str) -> None:
    st.divider()
    top_label = max(result.labels, key=lambda item: item["score"], default=None)

    first, second, third = st.columns(3)
    first.metric("Labels", len(result.labels))
    second.metric("Objects", len(result.objects))
    third.metric("Words", len(result.words))

    if top_label:
        st.caption(
            f"Top match: **{top_label['name']}** "
            f"({top_label['score'] * 100:.1f}% confidence)"
        )

    labels_tab, objects_tab, text_tab = st.tabs(["Labels", "Objects", "Text"])

    with labels_tab:
        if result.labels:
            labels_df = pd.DataFrame(
                [
                    {
                        "Label": label["name"],
                        "Confidence": round(label["score"] * 100, 1),
                    }
                    for label in result.labels
                ]
            ).sort_values("Confidence", ascending=False)
            st.dataframe(
                labels_df,
                hide_index=True,
                width="stretch",
                column_config={
                    "Label": st.column_config.TextColumn("Label"),
                    "Confidence": st.column_config.ProgressColumn(
                        "Confidence",
                        min_value=0,
                        max_value=100,
                        format="%.1f%%",
                    ),
                },
            )
            st.caption(
                "Confidence reflects how certain the model is that the label "
                "applies to the image."
            )
        else:
            st.info("No labels were detected in this image.")

    with objects_tab:
        if result.objects:
            st.image(
                annotate_objects(image, result.objects),
                caption="Detected objects",
                width="stretch",
            )
            objects_df = pd.DataFrame(
                [
                    {
                        "Object": obj["name"],
                        "Confidence": round(obj["score"] * 100, 1),
                    }
                    for obj in result.objects
                ]
            ).sort_values("Confidence", ascending=False)
            st.dataframe(
                objects_df,
                hide_index=True,
                width="stretch",
                column_config={
                    "Object": st.column_config.TextColumn("Object"),
                    "Confidence": st.column_config.ProgressColumn(
                        "Confidence",
                        min_value=0,
                        max_value=100,
                        format="%.1f%%",
                    ),
                },
            )
        else:
            st.info("No objects were detected in this image.")

    with text_tab:
        if result.text.strip():
            st.text_area(
                "Extracted text",
                value=result.text,
                height=240,
                label_visibility="collapsed",
            )
            st.caption(f"{len(result.words):,} words detected")
            st.download_button(
                "Download text",
                data=result.text,
                file_name=f"{file_stem or 'image'}-text.txt",
                mime="text/plain",
            )
        else:
            st.info("No text was detected in this image.")

    with st.expander("Developer details"):
        st.caption("Raw response returned by the Google Cloud Vision API.")
        st.download_button(
            "Download JSON",
            data=json.dumps(result.raw, indent=2),
            file_name=f"{file_stem or 'image'}-vision.json",
            mime="application/json",
        )
        st.json(result.raw, expanded=False)


def render_team() -> None:
    st.divider()
    st.caption("PROJECT TEAM")
    columns = st.columns(3)
    for column, (name, university_id) in zip(columns, TEAM):
        with column:
            st.markdown(
                f'<div class="team-name">{name}</div>'
                f'<div class="team-id">University ID: {university_id}</div>',
                unsafe_allow_html=True,
            )
    st.caption("Project P12 · Image Recognition with Google Cloud Vision")


def main() -> None:
    render_hero()
    require_password()

    client, client_error = get_client_or_error()
    if client_error:
        st.error(client_error)
        render_team()
        return

    uploaded = st.file_uploader(
        "Upload an image",
        type=("jpg", "jpeg", "png", "webp", "bmp", "gif"),
        help=f"JPG, PNG, WEBP, BMP or GIF · up to {MAX_UPLOAD_MB} MB",
    )

    if uploaded is None:
        for key in ("result", "analysis_error", "digest"):
            st.session_state.pop(key, None)
        render_empty_state()
        render_team()
        return

    file_bytes = uploaded.getvalue()
    digest = hashlib.sha256(file_bytes).hexdigest()

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.load()
    except (UnidentifiedImageError, OSError):
        st.error(
            "This file could not be opened as an image. "
            "Please upload a JPG, PNG, WEBP, BMP or GIF file."
        )
        render_team()
        return

    st.image(image, caption=uploaded.name, width="stretch")

    if st.session_state.get("digest") != digest:
        for key in ("result", "analysis_error"):
            st.session_state.pop(key, None)
        st.session_state["digest"] = digest

    if st.session_state.get("analysis_error"):
        st.error(st.session_state["analysis_error"])
        if st.button("Try again", type="primary", key="retry_analysis"):
            st.session_state.pop("analysis_error", None)
            st.rerun()

    if "result" not in st.session_state and "analysis_error" not in st.session_state:
        with st.spinner("Analyzing image..."):
            result, error = analyze_uploaded_image(client, file_bytes)
        if error:
            st.session_state["analysis_error"] = error
            st.rerun()
        st.session_state["result"] = result

    result = st.session_state.get("result")
    if result is not None:
        render_results(result, image, Path(uploaded.name).stem)

    render_team()


if __name__ == "__main__":
    main()
