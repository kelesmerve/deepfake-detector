import gradio as gr
import numpy as np
from PIL import Image
import cv2
import mimetypes
import time

from ui.theme import CUSTOM_CSS, LIGHT_THEME
from ui.components import format_verdict
from core.inference import predict_file, _analyze_pil_image
from core.inference_audio import analyze_audio


def stream_markdown(text, delay=0.015):
    """Yield markdown in small chunks for a typewriter-style explanation."""
    rendered = ""
    for token in text.split(" "):
        rendered += token + " "
        yield rendered
        time.sleep(delay)


def make_history_caption(verdict_html):
    """Create a compact label for the session history gallery."""
    if "DEEPFAKE DETECTED" in verdict_html:
        label = "Fake"
    elif "AUTHENTIC" in verdict_html:
        label = "Real"
    elif "Error" in verdict_html:
        label = "Error"
    else:
        label = "Analyzed"
    return f"{label} - {time.strftime('%H:%M:%S')}"


def make_history_thumbnail(image):
    """Prepare a small thumbnail without mutating the original image."""
    if image is None:
        return None
    thumb = image.copy().convert("RGB")
    thumb.thumbnail((96, 96))
    canvas = Image.new("RGB", (96, 96), "#f8fafc")
    x = (96 - thumb.width) // 2
    y = (96 - thumb.height) // 2
    canvas.paste(thumb, (x, y))
    return canvas


def add_history_item(history, image, verdict_html, max_items=12):
    """Add latest visual analysis to in-memory session history."""
    history = list(history or [])
    thumb = make_history_thumbnail(image)
    if thumb is None:
        return history, history
    history.insert(0, (thumb, make_history_caption(verdict_html)))
    history = history[:max_items]
    return history, history


with gr.Blocks(title="Deepfake Detection") as demo:
    gr.HTML(
        """
        <section class="app-header">
            <div class="hero-copy">
                <div class="app-kicker">AI Media Forensics</div>
                <h1>Deepfake Detection</h1>
                <p>Gorsel, video ve ses dosyalarini yukleyin; model sonucu, guven dagilimi ve XAI aciklamalarini tek ekranda inceleyin.</p>
                <div class="feature-row">
                    <span>Image</span>
                    <span>Video</span>
                    <span>Audio</span>
                    <span>XAI Reports</span>
                </div>
            </div>
            <div class="hero-visual" aria-hidden="true">
                <div class="scan-card">
                    <div class="scan-topline">
                        <span>LIVE FORENSIC SCAN</span>
                        <strong>91%</strong>
                    </div>
                    <div class="face-panel">
                        <div class="face-shape">
                            <div class="eye eye-left"></div>
                            <div class="eye eye-right"></div>
                            <div class="nose-line"></div>
                            <div class="mouth-line"></div>
                        </div>
                        <div class="scan-line"></div>
                    </div>
                    <div class="signal-bars">
                        <span style="height:32%"></span>
                        <span style="height:64%"></span>
                        <span style="height:46%"></span>
                        <span style="height:82%"></span>
                        <span style="height:54%"></span>
                        <span style="height:72%"></span>
                        <span style="height:38%"></span>
                        <span style="height:66%"></span>
                    </div>
                </div>
                <div class="mini-report report-real">
                    <span>Real</span>
                    <strong>8.6%</strong>
                </div>
                <div class="mini-report report-fake">
                    <span>Fake</span>
                    <strong>91.4%</strong>
                </div>
                <div class="xai-chip">Grad-CAM + LIME Ready</div>
            </div>
        </section>
        """
    )

    with gr.Tabs():
        with gr.TabItem("Image / Video"):
            gr.Markdown("### Analyze visual media")
            with gr.Row():
                with gr.Column(scale=3):
                    file_input = gr.File(
                        label="Upload image or video",
                        file_types=[".jpg", ".jpeg", ".png", ".mp4", ".mov", ".avi"],
                        type="filepath",
                    )
                    gr.HTML("<div class='soft-divider'>or test with camera</div>")
                    camera_input = gr.Image(
                        label="Camera snapshot",
                        sources=["webcam"],
                        type="numpy",
                    )
                with gr.Column(scale=1, min_width=220):
                    preview = gr.Image(label="Preview", interactive=False, height=220)

            analyze_btn = gr.Button(
                "Start Visual Analysis",
                variant="primary",
                elem_classes=["analyze-btn"],
                size="lg",
            )

            verdict = gr.HTML(value=format_verdict("waiting", 0))

            with gr.Tabs():
                with gr.TabItem("Grad-CAM"):
                    gradcam_output = gr.Image(label="Grad-CAM explanation", interactive=False)
                    gradcam_metrics_output = gr.Markdown(
                        value="*Grad-CAM metrics will appear here after analysis.*"
                    )
                with gr.TabItem("LIME"):
                    lime_output = gr.Image(label="LIME explanation", interactive=False)
                    lime_metrics_output = gr.Markdown(
                        value="*LIME contribution metrics will appear here after analysis.*"
                    )
                with gr.TabItem("Artifacts"):
                    artifact_output = gr.Image(label="Forensic artifact view", interactive=False)
                with gr.TabItem("Summary"):
                    summary_output = gr.Markdown(
                        value="*Upload a file and click Start Visual Analysis to generate a report.*"
                    )

        with gr.TabItem("Audio"):
            gr.Markdown("### Analyze voice or audio recordings")
            audio_input = gr.Audio(label="Upload or record audio", type="filepath")

            with gr.Row():
                audio_analyze_btn = gr.Button(
                    "Fast Audio Analysis",
                    variant="primary",
                    elem_classes=["analyze-btn"],
                    size="lg",
                )
                audio_xai_btn = gr.Button(
                    "Detailed XAI Analysis",
                    variant="secondary",
                    elem_classes=["secondary-btn"],
                    size="lg",
                )

            audio_verdict = gr.HTML(value=format_verdict("waiting", 0))

            with gr.Tabs():
                with gr.TabItem("SHAP"):
                    audio_shap_output = gr.Image(label="SHAP audio explanation", interactive=False)
                with gr.TabItem("Summary"):
                    audio_summary_output = gr.Markdown(
                        value="*Upload or record audio and click an analysis button to generate a report.*"
                    )

    with gr.Accordion("Session History", open=True):
        history_state = gr.State([])
        history_gallery = gr.Gallery(
            label="Recent visual analyses",
            value=[],
            columns=8,
            height=132,
            object_fit="cover",
            preview=False,
        )
        clear_history_btn = gr.Button("Clear History", variant="secondary")

    def on_file_change(file_obj):
        if file_obj is None:
            return None

        path = file_obj if isinstance(file_obj, str) else file_obj.name
        mime, _ = mimetypes.guess_type(path)
        if mime and mime.startswith("image"):
            return Image.open(path).convert("RGB")
        if mime and mime.startswith("video"):
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        return Image.open(path).convert("RGB")

    def on_analyze(file_obj, cam_obj, history, progress=gr.Progress()):
        try:
            progress(0.05, desc="Preparing input")
            if cam_obj is not None:
                progress(0.20, desc="Reading camera frame")
                img = Image.fromarray(cam_obj) if isinstance(cam_obj, np.ndarray) else Image.open(cam_obj).convert("RGB")
                v_html, gc_img, gc_metrics, l_img, l_metrics, a_img, summ, analyzed_img = _analyze_pil_image(img, progress=progress)
                progress(1.0, desc="Analysis complete")
                base_outputs = (v_html, gc_img, gc_metrics, l_img, l_metrics, a_img)
                new_history, history_gallery_items = add_history_item(history, analyzed_img, v_html)
                yield (*base_outputs, "### Writing explanation...\n", new_history, history_gallery_items)
                for partial_summary in stream_markdown(summ):
                    yield (*base_outputs, partial_summary, new_history, history_gallery_items)
                return

            if file_obj is not None:
                progress(0.20, desc="Reading uploaded file")
                class FileWrapper:
                    def __init__(self, path):
                        self.name = path

                f_obj = FileWrapper(file_obj) if isinstance(file_obj, str) else file_obj
                v_html, gc_img, gc_metrics, l_img, l_metrics, a_img, summ, analyzed_img = predict_file(f_obj, progress=progress)
                progress(1.0, desc="Analysis complete")
                base_outputs = (v_html, gc_img, gc_metrics, l_img, l_metrics, a_img)
                new_history, history_gallery_items = add_history_item(history, analyzed_img, v_html)
                yield (*base_outputs, "### Writing explanation...\n", new_history, history_gallery_items)
                for partial_summary in stream_markdown(summ):
                    yield (*base_outputs, partial_summary, new_history, history_gallery_items)
                return

            progress(1.0, desc="Waiting for input")
            yield (
                format_verdict("waiting", 0),
                None,
                "*Grad-CAM metrics will appear here after analysis.*",
                None,
                "*LIME contribution metrics will appear here after analysis.*",
                None,
                "*Upload a file to generate a report.*",
                history,
                history,
            )
            return
        except Exception as e:
            progress(1.0, desc="Analysis failed")
            yield format_verdict("error", 0), None, "", None, "", None, f"Error: {str(e)}", history, history
            return

    file_input.change(fn=on_file_change, inputs=file_input, outputs=preview)
    camera_input.change(
        fn=lambda c: Image.fromarray(c) if isinstance(c, np.ndarray) else Image.open(c).convert("RGB") if c else None,
        inputs=camera_input,
        outputs=preview,
    )
    analyze_btn.click(
        fn=on_analyze,
        inputs=[file_input, camera_input, history_state],
        outputs=[
            verdict,
            gradcam_output,
            gradcam_metrics_output,
            lime_output,
            lime_metrics_output,
            artifact_output,
            summary_output,
            history_state,
            history_gallery,
        ],
    )

    clear_history_btn.click(
        fn=lambda: ([], []),
        inputs=[],
        outputs=[history_state, history_gallery],
    )

    def on_analyze_audio(path, progress=gr.Progress()):
        if not path:
            progress(1.0, desc="Waiting for audio")
            yield format_verdict("waiting", 0), None, "*Please provide an audio file.*"
            return
        try:
            progress(0.10, desc="Loading audio model")
            progress(0.35, desc="Reading audio file")
            progress(0.60, desc="Running audio deepfake model")
            v_html, summ = analyze_audio(path)
            progress(0.90, desc="Preparing summary")
            progress(1.0, desc="Analysis complete")
            yield v_html, None, "### Writing explanation...\n"
            for partial_summary in stream_markdown(summ):
                yield v_html, None, partial_summary
            return
        except Exception as e:
            progress(1.0, desc="Analysis failed")
            yield format_verdict("error", 0), None, f"Error: {str(e)}"
            return

    def on_analyze_audio_xai(path, progress=gr.Progress()):
        if not path:
            progress(1.0, desc="Waiting for audio")
            yield format_verdict("waiting", 0), None, "*Please provide an audio file.*"
            return
        try:
            from core.xai_audio import generate_shap_analysis
            from core.inference_audio import analyze_audio

            progress(0.10, desc="Loading audio model")
            progress(0.30, desc="Running audio deepfake model")
            v_html, _ = analyze_audio(path)
            progress(0.55, desc="Computing SHAP explanation")
            shap_img, summary_md = generate_shap_analysis(path)
            progress(0.90, desc="Generating XAI report")
            progress(1.0, desc="Analysis complete")
            yield v_html, shap_img, "### Writing explanation...\n"
            for partial_summary in stream_markdown(summary_md):
                yield v_html, shap_img, partial_summary
            return
        except Exception as e:
            progress(1.0, desc="Analysis failed")
            yield format_verdict("error", 0), None, f"Error: {str(e)}"
            return

    audio_analyze_btn.click(
        fn=on_analyze_audio,
        inputs=[audio_input],
        outputs=[audio_verdict, audio_shap_output, audio_summary_output],
    )
    audio_xai_btn.click(
        fn=on_analyze_audio_xai,
        inputs=[audio_input],
        outputs=[audio_verdict, audio_shap_output, audio_summary_output],
    )


if __name__ == "__main__":
    demo.launch(theme=LIGHT_THEME, css=CUSTOM_CSS, server_port=7890)
