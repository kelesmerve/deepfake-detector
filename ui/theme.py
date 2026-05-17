import gradio as gr


CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html,
body,
main,
.app {
    background: #eef4fb !important;
}

.gradio-container {
    max-width: 1160px !important;
    min-height: 100vh !important;
    margin: auto !important;
    padding: 24px !important;
    background:
        linear-gradient(180deg, #eef4fb 0%, #eaf3fb 48%, #f8fbff 100%) !important;
    color: #172033 !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

.app-header {
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.95fr);
    gap: 24px;
    align-items: center;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.96) 0%, rgba(232,242,255,0.98) 44%, rgba(225,245,255,0.96) 100%);
    border: 1px solid #b6cce5;
    border-radius: 22px;
    padding: 30px;
    margin-bottom: 22px;
    box-shadow: 0 20px 55px rgba(15, 23, 42, 0.11);
    overflow: hidden;
}

.hero-copy {
    min-width: 0;
}

.app-kicker {
    display: inline-flex;
    align-items: center;
    background: #0b1f3a;
    color: #ffffff;
    border: 1px solid #12355f;
    border-radius: 999px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 14px;
    box-shadow: 0 10px 22px rgba(11, 31, 58, 0.26);
}

.app-header h1 {
    margin: 0 0 12px 0 !important;
    color: #071a33 !important;
    font-size: 48px !important;
    font-weight: 800 !important;
    letter-spacing: 0 !important;
    line-height: 1.04 !important;
}

.app-header p {
    max-width: 720px;
    margin: 0 0 20px 0;
    color: #475467;
    font-size: 17px;
    line-height: 1.6;
}

.feature-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.feature-row span {
    background: #ffffff;
    color: #0b1f3a;
    border: 1px solid #b6cce5;
    border-radius: 999px;
    padding: 9px 14px;
    font-size: 13px;
    font-weight: 800;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
}

.hero-visual {
    position: relative;
    min-height: 320px;
}

.scan-card {
    position: absolute;
    inset: 16px 38px 18px 28px;
    background:
        linear-gradient(145deg, #ffffff 0%, #f1f7ff 58%, #e8f2ff 100%);
    border: 1px solid #9fb9d8;
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 22px 42px rgba(8, 47, 73, 0.16);
}

.scan-topline {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #0b1f3a;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.4px;
    margin-bottom: 14px;
}

.scan-topline strong {
    color: #dc2626;
    font-size: 22px;
}

.face-panel {
    position: relative;
    height: 168px;
    border-radius: 16px;
    background:
        linear-gradient(135deg, #dbeafe 0%, #c7d2fe 48%, #bfdbfe 100%);
    border: 1px solid #93b4d8;
    display: grid;
    place-items: center;
    overflow: hidden;
}

.face-panel::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(11,31,58,0.18) 1px, transparent 1px),
        linear-gradient(90deg, rgba(11,31,58,0.18) 1px, transparent 1px);
    background-size: 24px 24px;
}

.face-shape {
    position: relative;
    width: 92px;
    height: 120px;
    background: rgba(255,255,255,0.82);
    border: 2px solid rgba(11,31,58,0.58);
    border-radius: 46px 46px 38px 38px;
    box-shadow: inset 0 -10px 22px rgba(11,31,58,0.12);
}

.eye {
    position: absolute;
    top: 42px;
    width: 12px;
    height: 8px;
    border-radius: 999px;
    background: #0b1f3a;
}

.eye-left {
    left: 24px;
}

.eye-right {
    right: 24px;
}

.nose-line {
    position: absolute;
    top: 56px;
    left: 44px;
    width: 3px;
    height: 28px;
    border-radius: 999px;
    background: #38bdf8;
}

.mouth-line {
    position: absolute;
    left: 29px;
    bottom: 25px;
    width: 34px;
    height: 5px;
    border-radius: 999px;
    background: #fb7185;
}

.scan-line {
    position: absolute;
    left: 0;
    right: 0;
    top: 47%;
    height: 3px;
    background: #ef4444;
    box-shadow: 0 0 18px rgba(239, 68, 68, 0.65);
}

.signal-bars {
    height: 54px;
    display: flex;
    align-items: end;
    gap: 8px;
    margin-top: 14px;
}

.signal-bars span {
    flex: 1;
    min-width: 10px;
    border-radius: 999px 999px 4px 4px;
    background: linear-gradient(180deg, #0b1f3a, #0284c7);
}

.mini-report {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    min-width: 132px;
    background: #ffffff;
    border-radius: 14px;
    padding: 12px 14px;
    border: 1px solid #dbe7f3;
    box-shadow: 0 16px 32px rgba(15, 23, 42, 0.12);
    font-weight: 800;
}

.mini-report span {
    color: #475467;
    font-size: 13px;
}

.mini-report strong {
    font-size: 18px;
}

.report-real {
    top: 6px;
    right: 0;
}

.report-real strong {
    color: #16a34a;
}

.report-fake {
    right: 8px;
    bottom: 26px;
}

.report-fake strong {
    color: #dc2626;
}

.xai-chip {
    position: absolute;
    left: 0;
    bottom: 2px;
    background: #0b1f3a;
    color: #ffffff;
    border-radius: 999px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 800;
    box-shadow: 0 16px 32px rgba(15, 23, 42, 0.16);
}

.gr-block,
.gr-box,
.gr-panel {
    background: #ffffff !important;
    border: 1px solid #dbe7f3 !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05) !important;
}

.gr-file,
.gr-file-preview {
    background: #fbfdff !important;
    border: 2px dashed #93c5fd !important;
    border-radius: 12px !important;
}

.gr-file:hover {
    border-color: #0b1f3a !important;
    box-shadow: 0 12px 28px rgba(11, 31, 58, 0.14) !important;
}

.analyze-btn,
.secondary-btn {
    min-height: 48px !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}

.analyze-btn {
    background: #0b1f3a !important;
    color: #ffffff !important;
    border: 1px solid #071a33 !important;
    box-shadow: 0 10px 22px rgba(11, 31, 58, 0.24) !important;
}

.analyze-btn:hover {
    background: #12355f !important;
}

.secondary-btn {
    background: #ffffff !important;
    color: #0b1f3a !important;
    border: 1px solid #9fb9d8 !important;
}

.gr-tab-nav {
    background: #eaf3fb !important;
    border: 1px solid #d4e4f4 !important;
    border-radius: 12px !important;
    padding: 5px !important;
}

.gr-tab-nav button {
    color: #475467 !important;
    border-radius: 9px !important;
    font-weight: 750 !important;
}

.gr-tab-nav button.selected {
    background: #ffffff !important;
    color: #0b1f3a !important;
    box-shadow: 0 5px 15px rgba(15, 23, 42, 0.08) !important;
}

.gr-image,
.gr-audio {
    background: #ffffff !important;
    border: 1px solid #dbe7f3 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

.gr-gallery {
    background: #ffffff !important;
    border: 1px solid #dbe7f3 !important;
    border-radius: 12px !important;
    padding: 8px !important;
}

.gr-gallery img {
    border-radius: 8px !important;
}

.gr-block label,
.gr-box label {
    color: #344054 !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}

.gr-markdown,
.gr-markdown p,
.gr-markdown li {
    color: #344054 !important;
}

.gr-markdown h1,
.gr-markdown h2,
.gr-markdown h3 {
    color: #172033 !important;
    letter-spacing: 0 !important;
}

.soft-divider {
    color: #667085;
    font-weight: 800;
    padding: 10px;
    text-align: center;
}

footer {
    display: none !important;
}

@media (max-width: 860px) {
    .gradio-container {
        padding: 14px !important;
    }

    .app-header {
        grid-template-columns: 1fr;
        padding: 22px;
    }

    .app-header h1 {
        font-size: 36px !important;
    }

    .hero-visual {
        min-height: 300px;
    }

    .scan-card {
        inset: 12px 18px 18px 18px;
    }

    .report-real {
        right: 6px;
    }

    .report-fake {
        right: 12px;
    }
}
"""


LIGHT_THEME = gr.themes.Soft(
    primary_hue=gr.themes.colors.sky,
    secondary_hue=gr.themes.colors.emerald,
    neutral_hue=gr.themes.colors.slate,
    font=gr.themes.GoogleFont("Inter"),
).set(
    body_background_fill="#f6f9fc",
    body_background_fill_dark="#eef4fb",
    body_text_color="#172033",
    body_text_color_dark="#172033",
    block_background_fill="#ffffff",
    block_background_fill_dark="#ffffff",
    block_border_color="#dbe7f3",
    block_border_color_dark="#dbe7f3",
    block_label_text_color="#344054",
    block_label_text_color_dark="#344054",
    input_background_fill="#ffffff",
    input_background_fill_dark="#ffffff",
    input_border_color="#cbd5e1",
    input_border_color_dark="#cbd5e1",
    button_primary_background_fill="#0b1f3a",
    button_primary_background_fill_dark="#0b1f3a",
    button_primary_text_color="#ffffff",
    button_primary_text_color_dark="#ffffff",
)

# Backwards-compatible alias for older imports.
GALACTIC_THEME = LIGHT_THEME
