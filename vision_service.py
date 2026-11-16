"""Image preparation and Google Cloud Vision integration."""
import base64
import io
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 10 * 1024 * 1024
VISION_URL = 'https://vision.googleapis.com/v1/images:annotate'
Image.MAX_IMAGE_PIXELS = 25_000_000


def prepare_image(data):
    if not data or len(data) > MAX_BYTES:
        raise ValueError('Choose an image smaller than 10 MB.')
    try:
        with Image.open(io.BytesIO(data)) as source:
            source.load()
            image = ImageOps.exif_transpose(source).convert('RGB')
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError('This image is invalid or too large to process.') from exc
    image.thumbnail((4096, 4096))
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=92)
    return image, output.getvalue()


def parse_response(response):
    if response.error.message:
        raise RuntimeError(response.error.message)
    annotation = response.full_text_annotation
    words = [word for page in annotation.pages for block in page.blocks
             for paragraph in block.paragraphs for word in paragraph.words]
    return {
        'labels': [{'name': x.description, 'confidence': float(x.score)} for x in response.label_annotations],
        'objects': [{'name': x.name, 'confidence': float(x.score),
                     'vertices': [{'x': float(v.x), 'y': float(v.y)} for v in x.bounding_poly.normalized_vertices]}
                    for x in response.localized_object_annotations],
        'text': annotation.text,
        'text_confidence': sum(w.confidence for w in words) / len(words) if words else None,
    }


def analyze_image(content):
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    try:
        response = client.annotate_image(request={
            'image': {'content': content},
            'features': [
                {'type_': vision.Feature.Type.LABEL_DETECTION, 'max_results': 15},
                {'type_': vision.Feature.Type.OBJECT_LOCALIZATION, 'max_results': 20},
                {'type_': vision.Feature.Type.DOCUMENT_TEXT_DETECTION},
            ],
        }, timeout=60)
        return parse_response(response)
    finally:
        client.transport.close()


class VisionError(Exception):
    pass


def analyze_image_rest(content, api_key):
    from google.cloud import vision

    body = {'requests': [{
        'image': {'content': base64.b64encode(content).decode('ascii')},
        'features': [
            {'type': 'LABEL_DETECTION', 'maxResults': 15},
            {'type': 'OBJECT_LOCALIZATION', 'maxResults': 20},
            {'type': 'DOCUMENT_TEXT_DETECTION'},
        ],
    }]}
    request = Request(
        VISION_URL,
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'x-goog-api-key': api_key},
    )
    try:
        with urlopen(request, timeout=60) as response:
            payload = json.load(response)
    except HTTPError as exc:
        try:
            details = json.load(exc).get('error', {}).get('details', [])
        except (ValueError, OSError):
            details = []
        reason = next((item['reason'] for item in details
                       if isinstance(item, dict) and isinstance(item.get('reason'), str)), '')
        messages = {
            'API_KEY_INVALID': 'The API key is invalid. Create a key in Google Cloud Console.',
            'API_KEY_SERVICE_BLOCKED': 'Allow Cloud Vision API in the API key restrictions.',
            'SERVICE_DISABLED': 'Enable Cloud Vision API in the project that owns this key.',
            'BILLING_DISABLED': 'Link an active billing account to the project that owns this key.',
        }
        fallback = {
            400: 'Cloud Vision rejected the request. Check the image and API key.',
            401: 'Cloud Vision could not authenticate this API key.',
            403: 'Cloud Vision denied access. Check API key restrictions, API activation, and project billing.',
            429: 'Cloud Vision quota reached. Check your project quotas and try again.',
        }
        raise VisionError(messages.get(reason, fallback.get(exc.code, f'Cloud Vision request failed (HTTP {exc.code}).'))) from None
    except (URLError, TimeoutError):
        raise VisionError('Could not reach Cloud Vision. Check your connection and try again.') from None
    except ValueError:
        raise VisionError('Cloud Vision returned an unreadable response. Try again.') from None

    try:
        annotation = vision.AnnotateImageResponse.from_json(
            json.dumps(payload['responses'][0]), ignore_unknown_fields=True
        )
        return parse_response(annotation)
    except (IndexError, KeyError, TypeError, ValueError, RuntimeError):
        raise VisionError('Cloud Vision could not analyze this image. Try another image.') from None


def demo_result():
    return {'labels': [{'name': 'Bicycle', 'confidence': .98}, {'name': 'Transport', 'confidence': .94}],
            'objects': [{'name': 'Bicycle', 'confidence': .97,
                         'vertices': [{'x': .12, 'y': .35}, {'x': .88, 'y': .35},
                                      {'x': .88, 'y': .86}, {'x': .12, 'y': .86}]}],
            'text': 'EXPLORE MORE\nVISION DEMO', 'text_confidence': .99}
