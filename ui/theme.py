import gradio as gr

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* === GLOBAL === */
.gradio-container {
    background: linear-gradient(160deg, #05050f 0%, #0a0a1a 30%, #0f0520 60%, #0a0a1a 100%) !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    max-width: 1100px !important;
    margin: auto !important;
}

/* === HEADER === */
.header-title {
    text-align: center;
    padding: 40px 20px 10px 20px;
}
.header-title h1 {
    font-size: 48px !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #c084fc, #a855f7, #7c3aed, #c084fc) !important;
    background-size: 200% auto !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: -1px !important;
    margin-bottom: 4px !important;
    animation: shimmer 4s linear infinite !important;
}
@keyframes shimmer {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}
.header-subtitle {
    text-align: center;
    color: #8b8ba7 !important;
    font-size: 15px;
    letter-spacing: 0.5px;
    margin-bottom: 32px;
}

/* === PANELS & BLOCKS === */
.gr-block, .gr-box, .gr-panel {
    background: rgba(15, 15, 35, 0.6) !important;
    border: 1px solid rgba(139, 92, 246, 0.15) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(12px) !important;
}

/* === FILE UPLOAD === */
.gr-file, .gr-file-preview {
    background: rgba(15, 15, 40, 0.8) !important;
    border: 2px dashed rgba(139, 92, 246, 0.35) !important;
    border-radius: 16px !important;
    transition: all 0.3s ease !important;
}
.gr-file:hover {
    border-color: rgba(139, 92, 246, 0.7) !important;
    box-shadow: 0 0 30px rgba(139, 92, 246, 0.15) !important;
}

/* === BUTTON === */
.analyze-btn {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: white !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    padding: 14px 48px !important;
    border-radius: 12px !important;
    border: none !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 25px rgba(139, 92, 246, 0.35) !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}
.analyze-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 35px rgba(139, 92, 246, 0.55) !important;
    background: linear-gradient(135deg, #8b5cf6, #c084fc) !important;
}

/* === TABS === */
.gr-tab-nav {
    background: rgba(10, 10, 26, 0.8) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(139, 92, 246, 0.15) !important;
}
.gr-tab-nav button {
    color: #8b8ba7 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
    border: none !important;
    background: transparent !important;
}
.gr-tab-nav button.selected {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(168, 85, 247, 0.2)) !important;
    color: #c084fc !important;
    box-shadow: 0 0 15px rgba(139, 92, 246, 0.2) !important;
}

/* === IMAGES === */
.gr-image {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(139, 92, 246, 0.15) !important;
}

/* === TEXT / LABELS === */
.gr-block label, .gr-box label {
    color: #c4b5fd !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* === MARKDOWN === */
.gr-markdown, .gr-markdown p, .gr-markdown li {
    color: #d4d4e8 !important;
}
.gr-markdown h2 {
    color: #c084fc !important;
}
.gr-markdown strong {
    color: #e9d5ff !important;
}
.gr-markdown code {
    background: rgba(139, 92, 246, 0.15) !important;
    color: #c084fc !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
}
.gr-markdown hr {
    border-color: rgba(139, 92, 246, 0.2) !important;
}

/* === FOOTER === */
footer {
    display: none !important;
}

/* === SCROLLBAR === */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-track {
    background: #0a0a1a;
}
::-webkit-scrollbar-thumb {
    background: rgba(139, 92, 246, 0.4);
    border-radius: 3px;
}

/* === STARS BACKGROUND ANIMATION === */
.gradio-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image:
        radial-gradient(2px 2px at 20px 30px, rgba(139,92,246,0.4), transparent),
        radial-gradient(2px 2px at 40px 70px, rgba(168,85,247,0.3), transparent),
        radial-gradient(1px 1px at 90px 40px, rgba(192,132,252,0.5), transparent),
        radial-gradient(1px 1px at 130px 80px, rgba(139,92,246,0.4), transparent),
        radial-gradient(2px 2px at 160px 30px, rgba(255,255,255,0.3), transparent),
        radial-gradient(1px 1px at 200px 60px, rgba(168,85,247,0.4), transparent),
        radial-gradient(2px 2px at 60px 100px, rgba(192,132,252,0.3), transparent),
        radial-gradient(1px 1px at 120px 120px, rgba(139,92,246,0.5), transparent);
    background-size: 250px 150px;
    pointer-events: none;
    z-index: 0;
    animation: twinkle 8s ease-in-out infinite alternate;
}
@keyframes twinkle {
    0% { opacity: 0.4; }
    50% { opacity: 0.8; }
    100% { opacity: 0.5; }
}
"""

GALACTIC_THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.purple,
    secondary_hue=gr.themes.colors.purple,
    neutral_hue=gr.themes.colors.gray,
    font=gr.themes.GoogleFont("Inter"),
).set(
    body_background_fill="#05050f",
    body_background_fill_dark="#05050f",
    body_text_color="#d4d4e8",
    body_text_color_dark="#d4d4e8",
    block_background_fill="rgba(15,15,35,0.6)",
    block_background_fill_dark="rgba(15,15,35,0.6)",
    block_border_color="rgba(139,92,246,0.15)",
    block_border_color_dark="rgba(139,92,246,0.15)",
    block_label_text_color="#c4b5fd",
    block_label_text_color_dark="#c4b5fd",
    block_title_text_color="#e9d5ff",
    block_title_text_color_dark="#e9d5ff",
    input_background_fill="rgba(15,15,40,0.8)",
    input_background_fill_dark="rgba(15,15,40,0.8)",
    input_border_color="rgba(139,92,246,0.25)",
    input_border_color_dark="rgba(139,92,246,0.25)",
    button_primary_background_fill="linear-gradient(135deg, #7c3aed, #a855f7)",
    button_primary_background_fill_dark="linear-gradient(135deg, #7c3aed, #a855f7)",
    button_primary_text_color="white",
    button_primary_text_color_dark="white",
    border_color_primary="rgba(139,92,246,0.3)",
    border_color_primary_dark="rgba(139,92,246,0.3)",
    shadow_drop="0 4px 20px rgba(0,0,0,0.3)",
    shadow_drop_lg="0 8px 40px rgba(0,0,0,0.4)",
)