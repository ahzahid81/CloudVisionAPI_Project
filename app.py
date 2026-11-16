import csv
import hashlib
import io
import json

import streamlit as st
from PIL import Image, ImageDraw
from gemini_service import GeminiError, MODEL, analyze_image, get_api_key
from vision_service import prepare_image

st.set_page_config(page_title='Vision Studio | Image Recognition', page_icon='🔎', layout='wide')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background:
        radial-gradient(900px 420px at 8% -10%, rgba(232,186,99,0.10), transparent 60%),
        radial-gradient(800px 360px at 100% 0%, rgba(245,158,11,0.08), transparent 55%),
        linear-gradient(180deg, #14110d 0%, #1a1612 100%);
}
.block-container {max-width:1120px;padding-top:2rem;padding-bottom:3rem}
h1 {letter-spacing:-.04em}
.st-key-page_intro {
    position: relative;
    overflow: hidden;
    background: linear-gradient(125deg, #17130f 0%, #2a2118 55%, #4a3518 100%);
    border: 1px solid rgba(232,186,99,0.28);
    border-radius: 24px;
    padding: clamp(1.2rem, 3vw, 2rem);
    margin-bottom: .8rem;
    box-shadow: 0 20px 50px rgba(0,0,0,0.25);
}
.st-key-page_intro h1 {color:#f7d58b; margin-bottom: .25rem;}
.eyebrow {
    display:inline-block; font-size:.72rem; font-weight:700; letter-spacing:.14em;
    text-transform:uppercase; color:#f4cb7e; background:rgba(244,203,126,0.12);
    border:1px solid rgba(244,203,126,0.22); padding:.3rem .65rem; border-radius:999px;
    margin-bottom:.55rem;
}
.hero-sub { color:#e8dcc7; font-size:1rem; max-width:70ch; line-height:1.55; }
.hero-badges { display:flex; flex-wrap:wrap; gap:.5rem; margin-top:.85rem; }
.hero-badge {
    color:#f8e7c3; background:rgba(255,255,255,0.06); border:1px solid rgba(244,203,126,0.18);
    padding:.32rem .65rem; border-radius:999px; font-size:.8rem; font-weight:500;
}
.st-key-image_panel,.st-key-action_panel {
    background: rgba(27,24,20,0.88);
    border: 1px solid rgba(232,186,99,0.22) !important;
    border-radius: 18px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
}
[data-testid="stMetric"] {
    background: linear-gradient(180deg, #211b14 0%, #1b1712 100%);
    border: 1px solid rgba(232,186,99,0.22);
    border-radius: 14px;
    padding: 1rem;
}
[data-testid="stMetricLabel"] { color:#d8c6a9; font-weight:600; }
[data-testid="stImage"] img {border-radius:14px; border:1px solid rgba(232,186,99,0.18);}
[data-testid="stFileUploaderDropzone"] {
    border: 1px dashed rgba(232,186,99,0.45);
    border-radius: 14px;
    background: rgba(255,255,255,0.02);
}
div[data-baseweb="tab-list"] { gap:.35rem; background:rgba(255,255,255,0.03); padding:.3rem; border-radius:12px; }
button[kind="primary"] {background:#e8ba63;color:#21170a;font-weight:700;border:0}
button[kind="primary"]:hover {background:#f6cf84;color:#21170a}
button:focus-visible,a:focus-visible {outline:3px solid #f4cb7e!important;outline-offset:3px}
.section-note { color:#cbb892; font-size:.92rem; margin-top:-.2rem; }
.team-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.75rem; margin-top:.4rem; }
.team-card {
    background: rgba(27,24,20,0.8); border:1px solid rgba(232,186,99,0.18);
    border-radius:14px; padding:.95rem 1rem; height:100%;
}
.team-name { color:#f7f0e3; font-weight:700; margin-bottom:.15rem; font-size:1rem; }
.team-id { color:#cbb892; font-size:.88rem; }
.footer-note { color:#b9a888; font-size:.85rem; margin-top:.7rem; }
@media (max-width: 900px){ .team-grid{ grid-template-columns:1fr; } }
</style>''', unsafe_allow_html=True)

confidence_slider = st.components.v2.component(
    'confidence_slider',
    html="""
    <div class="confidence" dir="ltr" translate="no">
      <div class="row"><label for="confidence">Minimum confidence</label>
        <output for="confidence">50%</output></div>
      <input id="confidence" type="range" min="0" max="100" step="1" value="50"
             aria-describedby="confidence-help">
      <div class="row endpoints" aria-hidden="true"><span>0%</span><span>100%</span></div>
      <small id="confidence-help">Filters labels and objects by Gemini's estimated confidence.</small>
    </div>
    """,
    css="""
    .confidence { direction: ltr; color: var(--st-text-color, #f7f0e3); }
    .row { display: flex; justify-content: space-between; align-items: center; gap: .5rem; }
    label { font-size: .9rem; font-weight: 600; }
    output { color: #f4cb7e; background: #423119; border-radius: 8px;
             padding: .15rem .5rem; font-weight: 700; font-variant-numeric: tabular-nums; }
    input { direction: ltr; appearance: none; box-sizing: border-box; width: 100%;
            height: 28px; margin: .25rem 0 0; cursor: pointer;
            background: linear-gradient(to right, #e8ba63 var(--stop, 50%),
                        #695b46 var(--stop, 50%)) center / 100% 6px no-repeat; }
    input::-webkit-slider-thumb { appearance: none; width: 18px; height: 18px;
        border-radius: 50%; border: 2px solid #21170a; background: #e8ba63;
        box-shadow: 0 0 0 1px #e8ba63; }
    input::-moz-range-thumb { box-sizing: border-box; width: 18px; height: 18px;
        border-radius: 50%; border: 2px solid #21170a; background: #e8ba63;
        box-shadow: 0 0 0 1px #e8ba63; }
    input:focus-visible { outline: 2px solid #f4cb7e; outline-offset: 3px; border-radius: 6px; }
    .endpoints, small { color: #d8c6a9; font-size: .8rem; }
    small { display: block; margin-top: .6rem; }
    """,
    js="""
    export default function ({ parentElement, data, setStateValue }) {
        const slider = parentElement.querySelector('input');
        const output = parentElement.querySelector('output');
        function renderValue() {
            const value = slider.valueAsNumber;
            output.value = value + '%';
            slider.setAttribute('aria-valuetext', output.value);
            slider.style.setProperty('--stop', 'calc(' + value + '% + ' + (9 - value * .18) + 'px)');
        }
        slider.value = data.value;
        renderValue();
        slider.oninput = renderValue;
        slider.onchange = () => setStateValue('value', slider.valueAsNumber);
    }
    """,
)

with st.container(key='page_intro'):
    st.markdown('<div class="eyebrow">Project P12 · AI-Powered Image Recognition</div>', unsafe_allow_html=True)
    st.title('Vision Studio')
    st.markdown(
        '<div class="hero-sub">Premium image intelligence experience. Upload a photo to discover visual labels, '
        'locate objects, and extract readable text with a clean, presentation-ready interface.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-badges">'
        '<span class="hero-badge">Smart Labeling</span>'
        '<span class="hero-badge">Object Detection</span>'
        '<span class="hero-badge">OCR Extraction</span>'
        '<span class="hero-badge">Instant Export</span>'
        '</div>',
        unsafe_allow_html=True,
    )

uploaded = st.file_uploader('1. Upload an image', type=['png', 'jpg', 'jpeg', 'webp'])
if uploaded is None:
    st.session_state.pop('result', None)
    st.session_state.pop('result_key', None)
    st.info('Choose an image to preview it and start analysis.')
    st.stop()
data = uploaded.getvalue()

try:
    picture, content = prepare_image(data)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

key = hashlib.sha256(content).hexdigest()
if st.session_state.get('result_key') != key:
    st.session_state.pop('result', None)
    st.session_state['result_key'] = key

left, right = st.columns([1.4, 1], gap='medium')
with left.container(border=True, key='image_panel'):
    st.subheader('Image preview')
    preview = st.empty()
    preview.image(picture, width='stretch')
    st.caption(f'{picture.width} × {picture.height} pixels · Processed in memory')
with right.container(border=True, key='action_panel'):
    st.subheader('2. Analyze the image')
    st.write('Review the image before starting. Results will appear below.')
    api_key = get_api_key()
    if not api_key:
        try:
            api_key = str(st.secrets.get('GEMINI_API_KEY', '')).strip()
        except FileNotFoundError:
            api_key = ''
    if not api_key:
        st.warning('Image analysis is unavailable. Contact the app administrator.')
    if st.button('Analyze image', type='primary', width='stretch', disabled=not api_key):
        try:
            with st.spinner('Analyzing image…'):
                st.session_state['result'] = analyze_image(content, api_key)
        except GeminiError as exc:
            st.error(str(exc))
    st.caption('Your image will be sent to Google Gemini. Usage charges may apply.')

result = st.session_state.get('result')
if result:
    st.divider()
    st.subheader('3. Review results')
    st.success('Analysis complete.')
    with st.container(border=True, width=480):
        slider_state = st.session_state.get('confidence_slider', {})
        slider = confidence_slider(
            key='confidence_slider',
            data={'value': slider_state.get('value', 50)},
            default={'value': 50},
            on_value_change=lambda: None,
        )
    threshold = slider.value
    labels = [x for x in result['labels'] if x['confidence'] >= threshold / 100]
    objects = [x for x in result['objects'] if x['confidence'] >= threshold / 100]
    overlay = picture.copy()
    draw = ImageDraw.Draw(overlay)
    for obj in objects:
        points = [(int(v['x'] * overlay.width), int(v['y'] * overlay.height)) for v in obj['vertices']]
        if points:
            draw.line(points + [points[0]], fill='#39cba4', width=4)
            draw.text(points[0], f"{obj['name']} {obj['confidence']:.0%}", fill='#117354', stroke_width=0)
    preview.image(overlay, width='stretch')
    a, b, c = st.columns(3)
    a.metric('Visual labels', len(labels))
    b.metric('Located objects', len(objects))
    c.metric('Extracted characters', len(result['text']))
    tab1, tab2, tab3 = st.tabs(['Visual labels', 'Objects', 'Extracted text'])
    for tab, rows in [(tab1, labels), (tab2, objects)]:
        with tab:
            if not rows:
                st.info('No results meet the selected confidence threshold.')
            for row in rows:
                st.write(f"**{row['name']}** · {row['confidence']:.1%}")
                st.progress(max(0.0, min(1.0, row['confidence'])))
    with tab3:
        if result['text']:
            st.text_area('Recognized text', result['text'], height=220)
            if result['text_confidence'] is not None:
                st.caption(f"Average word confidence: {result['text_confidence']:.1%}")
            st.download_button('Download text', result['text'], 'extracted_text.txt', 'text/plain')
        else:
            st.info('No readable text was detected.')
    export = dict(result, mode='Gemini API', model=MODEL, minimum_confidence=threshold)
    st.download_button('Download full report (JSON)', json.dumps(export, ensure_ascii=False, indent=2), 'vision_report.json', 'application/json')
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['type', 'name', 'confidence'])
    for kind, rows in [('label', labels), ('object', objects)]:
        for row in rows:
            writer.writerow([kind, row['name'], row['confidence']])
    st.download_button('Download filtered results (CSV)', output.getvalue().encode('utf-8-sig'), 'vision_results.csv', 'text/csv')

st.divider()
st.subheader('Project Team')
st.markdown(
    '''<div class="team-grid">
        <div class="team-card"><div class="team-name">Asim bin Adel Al-Mutrafi</div><div class="team-id">University ID: 441006293</div></div>
        <div class="team-card"><div class="team-name">Abdul Hasib Zahid</div><div class="team-id">University ID: 443058333</div></div>
        <div class="team-card"><div class="team-name">MOHAMMAD TAKIUDDIN</div><div class="team-id">University ID: 441037573</div></div>
    </div>
    <div class="footer-note">Project P12 · Vision Studio Image Recognition Web Application</div>''',
    unsafe_allow_html=True,
)
