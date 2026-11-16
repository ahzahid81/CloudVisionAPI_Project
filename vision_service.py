"""Google Cloud Vision API integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from google.cloud import vision
from google.oauth2 import service_account

SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)
REQUIRED_SERVICE_ACCOUNT_FIELDS = ("type", "project_id", "private_key", "client_email")


class VisionClientError(RuntimeError):
    """Raised when the Vision client cannot be created or used."""


@dataclass
class AnalysisResult:
    labels: list[dict[str, Any]]
    objects: list[dict[str, Any]]
    text: str
    words: list[dict[str, Any]]
    raw: dict[str, Any]


def validate_service_account_info(info: Any) -> None:
    if not isinstance(info, dict):
        raise VisionClientError("The credentials must be provided as a TOML/JSON object.")
    missing = [field for field in REQUIRED_SERVICE_ACCOUNT_FIELDS if not info.get(field)]
    if missing:
        raise VisionClientError(
            "This does not look like a service account key. "
            f"Missing required field(s): {', '.join(missing)}."
        )
    if info.get("type") != "service_account":
        raise VisionClientError(
            "Only service account keys are supported (the 'type' field must be "
            "'service_account')."
        )


def build_client(service_account_info: dict[str, Any] | None = None) -> vision.ImageAnnotatorClient:
    """Create a Vision client from an explicit key or the environment (ADC)."""
    if service_account_info is not None:
        validate_service_account_info(service_account_info)
        try:
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info, scopes=list(SCOPES)
            )
        except Exception as exc:
            raise VisionClientError(
                f"Could not create credentials from the service account key: {exc}"
            ) from exc
        try:
            return vision.ImageAnnotatorClient(credentials=credentials)
        except Exception as exc:
            raise VisionClientError(f"Could not create the Vision client: {exc}") from exc

    try:
        return vision.ImageAnnotatorClient()
    except Exception as exc:
        raise VisionClientError(
            "No Google Cloud credentials were found. Add [gcp_service_account] to "
            "Streamlit secrets or set GOOGLE_APPLICATION_CREDENTIALS."
        ) from exc


def _response_to_dict(response: vision.AnnotateImageResponse) -> dict[str, Any]:
    try:
        return type(response).to_dict(response, preserving_proto_field_name=True)
    except TypeError:
        return type(response).to_dict(response)


def analyze_image(
    client: vision.ImageAnnotatorClient,
    content: bytes,
    max_results: int = 20,
) -> AnalysisResult:
    """Run label, object and text detection on one image."""
    max_results = max(1, min(int(max_results), 100))
    image = vision.Image(content=content)
    request = vision.AnnotateImageRequest(
        image=image,
        features=[
            vision.Feature(
                type_=vision.Feature.Type.LABEL_DETECTION,
                max_results=max_results,
            ),
            vision.Feature(
                type_=vision.Feature.Type.OBJECT_LOCALIZATION,
                max_results=max_results,
            ),
            vision.Feature(
                type_=vision.Feature.Type.TEXT_DETECTION,
                max_results=50,
            ),
        ],
    )
    response = client.annotate_image(request=request)

    if response.error.message:
        raise VisionClientError(f"Vision API returned an error: {response.error.message}")

    labels = [
        {
            "name": label.description,
            "score": float(label.score or 0.0),
            "topicality": float(label.topicality or 0.0),
            "mid": label.mid,
        }
        for label in response.label_annotations
        if label.description
    ]

    objects: list[dict[str, Any]] = []
    for obj in response.localized_object_annotations:
        box = [
            (float(vertex.x), float(vertex.y))
            for vertex in obj.bounding_poly.normalized_vertices
        ]
        objects.append(
            {
                "name": obj.name,
                "score": float(obj.score or 0.0),
                "box": box,
                "mid": obj.mid,
            }
        )

    text_annotations = list(response.text_annotations)
    text = text_annotations[0].description if text_annotations else ""
    words = [
        {"text": annotation.description, "language": annotation.locale or ""}
        for annotation in text_annotations[1:]
        if annotation.description and annotation.description.strip()
    ]

    return AnalysisResult(
        labels=labels,
        objects=objects,
        text=text or "",
        words=words,
        raw=_response_to_dict(response),
    )
