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
:root {
    --bg: #0b1220;
    --surface: #111827;
    --surface-2: #182233;
    --border: rgba(148,163,184,0.24);
    --text: #f8fafc;
    --muted: #d3deea;
    --accent: #3b82f6;
    --accent-soft: #93c5fd;
}
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--text); }
.stApp {
    background:
        radial-gradient(900px 420px at 8% -10%, rgba(59,130,246,0.16), transparent 60%),
        radial-gradient(800px 360px at 100% 0%, rgba(14,165,233,0.10), transparent 55%),
        linear-gradient(180deg, #0b1220 0%, #111827 100%);
    color: var(--text);
}
.block-container {max-width:1180px; padding-top:4.5rem; padding-bottom:2rem;}
h1, h2, h3, h4, h5, h6 { color: #ffffff !important; letter-spacing:-0.03em; }
p, li, label, span { color: var(--text); }
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stText"], [data-testid="stWidgetLabel"] p, .stText p { color: var(--text) !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, .stCaption, small { color: var(--muted) !important; }

/* Navbar */
.navbar {
    position: sticky;
    top: 0.75rem;
    z-index: 50;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.9rem 1.1rem;
    margin-top: 0.25rem;
    margin-bottom: 1rem;
    background: rgba(15,23,42,0.82);
    backdrop-filter: blur(14px);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(2,6,23,0.35);
}
.brand { display:flex; align-items:center; gap:.75rem; min-width:0; }
.brand-mark {
    width: 40px; height: 40px; border-radius: 12px;
    display:flex; align-items:center; justify-content:center;
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color:#ffffff; font-weight:800; font-size:0.95rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.25);
    flex-shrink:0;
}
.brand-title { font-weight:700; font-size:1.02rem; color:#ffffff; line-height:1.1; }
.brand-sub { font-size:.8rem; color:#dbe7f5; }
.nav-links { display:flex; align-items:center; gap:.5rem; flex-wrap:wrap; justify-content:flex-end; }
.nav-pill {
    padding: .4rem .72rem; border-radius: 999px; font-size:.78rem; font-weight:600;
    color:#eaf2ff; background:rgba(59,130,246,0.16); border:1px solid rgba(147,197,253,0.28);
    white-space:nowrap;
}

/* Hero */
.st-key-page_intro {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #0f172a 0%, #172554 50%, #2563eb 100%);
    border: 1px solid rgba(147,197,253,0.24);
    border-radius: 24px;
    padding: clamp(1.2rem, 3vw, 2rem);
    margin-bottom: .9rem;
    box-shadow: 0 20px 50px rgba(2,6,23,0.35);
}
.st-key-page_intro h1 {color:#ffffff !important; margin-bottom: .35rem; font-size: clamp(1.9rem, 4vw, 2.8rem);}
.eyebrow {
    display:inline-block; font-size:.72rem; font-weight:700; letter-spacing:.14em;
    text-transform:uppercase; color:#e0ecff; background:rgba(255,255,255,0.12);
    border:1px solid rgba(191,219,254,0.25); padding:.32rem .68rem; border-radius:999px;
    margin-bottom:.55rem;
}
.hero-sub { color:#eaf2ff; font-size:1rem; max-width:72ch; line-height:1.65; }
.hero-badges { display:flex; flex-wrap:wrap; gap:.5rem; margin-top:.9rem; }
.hero-badge {
    color:#ffffff; background:rgba(255,255,255,0.12); border:1px solid rgba(191,219,254,0.22);
    padding:.34rem .68rem; border-radius:999px; font-size:.8rem; font-weight:500;
}

/* Panels & components */
.st-key-image_panel,.st-key-action_panel {
    background: var(--surface);
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    box-shadow: 0 10px 30px rgba(2,6,23,0.22);
}
[data-testid="stMetric"] {
    background: linear-gradient(180deg, #1b2433 0%, #151c29 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem;
}
[data-testid="stMetricLabel"] { color:#dbe7f5 !important; font-weight:600; }
[data-testid="stMetricValue"] { color:#ffffff !important; }
[data-testid="stImage"] img {border-radius:14px; border:1px solid rgba(148,163,184,0.24);}
[data-testid="stFileUploaderDropzone"] {
    border: 1px dashed rgba(147,197,253,0.5);
    border-radius: 14px;
    background: rgba(255,255,255,0.04);
}
[data-testid="stFileUploaderDropzone"] * { color:#eaf2ff !important; }
[data-testid="stFileUploader"] label, [data-testid="stFileUploader"] small { color:#dbe7f5 !important; }
div[data-baseweb="tab-list"] { gap:.35rem; background:rgba(255,255,255,0.05); padding:.3rem; border-radius:12px; }
button[data-baseweb="tab"] { color:#d3deea !important; font-weight:600; }
button[data-baseweb="tab"][aria-selected="true"] { color:#ffffff !important; background:rgba(59,130,246,0.18); border-radius:10px; }
button[kind="primary"] {background:#2563eb;color:#ffffff !important;font-weight:700;border:0}
button[kind="primary"]:hover {background:#3b82f6;color:#ffffff !important}
.stButton > button, .stDownloadButton > button { color:#f8fafc !important; border-color: rgba(148,163,184,0.35); }
.stAlert { border-radius: 12px; }
textarea, input { color:#f8fafc !important; }
[data-baseweb="textarea"] textarea, [data-baseweb="input"] input { background: rgba(15,23,42,0.65) !important; }
.stProgress > div > div > div { background-color:#3b82f6; }

/* Team & footer */
.team-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.85rem; margin-top:.5rem; }
.team-card {
    background: linear-gradient(180deg, #182233 0%, #131b28 100%);
    border:1px solid rgba(148,163,184,0.24);
    border-radius:16px; padding:1rem 1rem; height:100%;
    box-shadow: 0 8px 20px rgba(2,6,23,0.18);
}
.team-badge {
    display:inline-flex; align-items:center; justify-content:center;
    width:34px; height:34px; border-radius:10px; margin-bottom:.55rem;
    background:rgba(59,130,246,0.20); color:#dbeafe; font-weight:700; font-size:.85rem;
    border:1px solid rgba(147,197,253,0.30);
}
.team-name { color:#ffffff; font-weight:700; margin-bottom:.25rem; font-size:1rem; line-height:1.4; }
.team-id { color:#dbe7f5; font-size:.9rem; font-weight:500; }
.footer {
    margin-top: 1.4rem;
    padding: 1.3rem 1.2rem 1rem;
    background: linear-gradient(180deg, rgba(17,24,39,0.98), rgba(10,15,28,1));
    border: 1px solid rgba(148,163,184,0.24);
    border-radius: 20px;
    box-shadow: 0 12px 30px rgba(2,6,23,0.28);
}
.footer-top {
    display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap;
    margin-bottom: .8rem;
}
.footer-brand { font-size:1.08rem; font-weight:700; color:#ffffff; margin-bottom:.25rem; }
.footer-desc { color:#e2e8f0; font-size:.94rem; max-width:65ch; line-height:1.65; }
.footer-meta { color:#dbe7f5; font-size:.85rem; text-align:right; line-height:1.65; }
.footer-divider { height:1px; background:rgba(148,163,184,0.2); margin:.95rem 0; }
.footer-bottom {
    display:flex; align-items:center; justify-content:space-between; gap:.75rem; flex-wrap:wrap;
    color:#d3deea; font-size:.85rem;
}

/* Mobile responsiveness */
@media (max-width: 900px) {
    .block-container { padding-top: 3.5rem; padding-left:.75rem; padding-right:.75rem; }
    .navbar { flex-direction: column; align-items: flex-start; gap:.65rem; position: static; }
    .nav-links { justify-content:flex-start; width:100%; }
    .team-grid { grid-template-columns: 1fr; }
    .footer-meta { text-align:left; }
    .footer-top, .footer-bottom { flex-direction: column; align-items:flex-start; }
    [data-testid="stHorizontalBlock"] { gap: .75rem; }
}
@media (max-width: 640px) {
    .st-key-page_intro { border-radius: 18px; padding: 1.1rem 1rem; }
    .brand-mark { width:36px; height:36px; }
    .hero-badges, .nav-links { gap:.4rem; }
    .hero-badge, .nav-pill { font-size:.74rem; padding:.34rem .58rem; }
    .team-card { padding:.9rem; }
}
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
    .confidence { direction: ltr; color: #f8fafc; font-family: Inter, sans-serif; }
    .row { display: flex; justify-content: space-between; align-items: center; gap: .5rem; }
    label { font-size: .9rem; font-weight: 600; color: #f8fafc; }
    output { color: #dbeafe; background: #1e3a8a; border-radius: 8px;
             padding: .15rem .5rem; font-weight: 700; font-variant-numeric: tabular-nums; }
    input { direction: ltr; appearance: none; box-sizing: border-box; width: 100%;
            height: 28px; margin: .25rem 0 0; cursor: pointer;
            background: linear-gradient(to right, #3b82f6 var(--stop, 50%),
                        #475569 var(--stop, 50%)) center / 100% 6px no-repeat; }
    input::-webkit-slider-thumb { appearance: none; width: 18px; height: 18px;
        border-radius: 50%; border: 2px solid #0f172a; background: #93c5fd;
        box-shadow: 0 0 0 1px #3b82f6; }
    input::-moz-range-thumb { box-sizing: border-box; width: 18px; height: 18px;
        border-radius: 50%; border: 2px solid #0f172a; background: #93c5fd;
        box-shadow: 0 0 0 1px #3b82f6; }
    input:focus-visible { outline: 2px solid #93c5fd; outline-offset: 3px; border-radius: 6px; }
    .endpoints, small { color: #d3deea; font-size: .8rem; }
    small { display: block; margin-top: .6rem; line-height: 1.45; }
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

st.markdown('''
<div class="navbar">
  <div class="brand">
    <div class="brand-mark">VS</div>
    <div>
      <div class="brand-title">Vision Studio</div>
      <div class="brand-sub">Project P12 · Image Recognition</div>
    </div>
  </div>
  <div class="nav-links">
    <span class="nav-pill">Gemini Powered</span>
    <span class="nav-pill">Labels · Objects · OCR</span>
    <span class="nav-pill">3 Team Members</span>
  </div>
</div>
''', unsafe_allow_html=True)

with st.container(key='page_intro'):
    st.markdown('<div class="eyebrow">Project P12 · AI-Powered Image Recognition</div>', unsafe_allow_html=True)
    st.title('Vision Studio')
    st.markdown(
        '<div class="hero-sub">A premium, presentation-ready image intelligence app. Upload a photo to discover visual labels, '
        'locate objects, and extract readable text with clear results and export options.</div>',
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
else:
    data = uploaded.getvalue()
    try:
        picture, content = prepare_image(data)
    except ValueError as exc:
        st.error(str(exc))
        picture = None
        content = None

    if picture is not None and content is not None:
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
                    draw.line(points + [points[0]], fill='#22d3ee', width=4)
                    label_text = f"{obj['name']} {obj['confidence']:.0%}"
                    draw.text((points[0][0] + 2, points[0][1] + 2), label_text, fill='#0f172a')
                    draw.text(points[0], label_text, fill='#67e8f9')
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
                    if result.get('text_confidence') is not None:
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

st.markdown('''
<div class="footer">
  <div class="footer-top">
    <div>
      <div class="footer-brand">Vision Studio · Project P12</div>
      <div class="footer-desc">A premium AI image recognition web application for detecting visual labels, locating objects, and extracting readable text with a polished, presentation-ready experience.</div>
    </div>
    <div class="footer-meta">
      <div><strong>Technology:</strong> Streamlit &amp; Google Gemini</div>
      <div><strong>Focus:</strong> Usability, clarity, and professional presentation</div>
    </div>
  </div>
  <div class="footer-divider"></div>
  <div style="margin-bottom:.4rem; color:#ffffff; font-weight:700; font-size:1rem;">Project Team</div>
  <div class="team-grid">
    <div class="team-card">
      <div class="team-badge">01</div>
      <div class="team-name">Asim bin Adel Al-Mutrafi</div>
      <div class="team-id">University ID: 441006293</div>
    </div>
    <div class="team-card">
      <div class="team-badge">02</div>
      <div class="team-name">Abdul Hasib Zahid</div>
      <div class="team-id">University ID: 443058333</div>
    </div>
    <div class="team-card">
      <div class="team-badge">03</div>
      <div class="team-name">MOHAMMAD TAKIUDDIN</div>
      <div class="team-id">University ID: 441037573</div>
    </div>
  </div>
  <div class="footer-divider"></div>
  <div class="footer-bottom">
    <span>© 2026 Vision Studio · Project P12 Image Recognition Web Application</span>
    <span>Designed for academic presentation and demonstration</span>
  </div>
</div>
''', unsafe_allow_html=True)
