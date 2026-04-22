import gradio as gr
import numpy as np
from PIL import Image
import cv2
import mimetypes

from ui.theme import CUSTOM_CSS, GALACTIC_THEME
from ui.components import format_verdict
from core.inference import predict_file, _analyze_pil_image

with gr.Blocks(title="Deepfake Detection System — XAI") as demo:
    gr.HTML("""
        <div class="header-title">
            <h1>Deepfake Detection System</h1>
        </div>
        <div class="header-subtitle">
            Explainable AI-Powered Media Forensics &nbsp;·&nbsp; Computer Security
        </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            file_input = gr.File(
                label="Dosya veya Video Yükle",
                file_types=[".jpg", ".jpeg", ".png", ".mp4", ".mov", ".avi"],
                type="filepath",
            )
            gr.HTML("<div style='text-align:center; padding: 10px; color:#8b8ba7; font-weight:bold;'>— VEYA —</div>")
            camera_input = gr.Image(
                label="Kameradan Anlık Test",
                sources=["webcam"],
                type="numpy",
            )
        with gr.Column(scale=1, min_width=180):
            preview = gr.Image(label="Preview", interactive=False, height=180)

    analyze_btn = gr.Button("Analyze", variant="primary", elem_classes=["analyze-btn"], size="lg")

    verdict = gr.HTML(value=format_verdict("waiting", 0))

    with gr.Tabs():
        with gr.TabItem("Grad-CAM"):
            gradcam_output = gr.Image(label="Grad-CAM Analysis", interactive=False)
        with gr.TabItem("LIME"):
            lime_output = gr.Image(label="LIME Explanation", interactive=False)
        with gr.TabItem("Artifact Analysis"):
            artifact_output = gr.Image(label="Forensic Analysis", interactive=False)
        with gr.TabItem("Summary"):
            summary_output = gr.Markdown(value="*Upload a file and click Analyze to generate a report.*")

    # Event handlers tanımları
    def on_file_change(file_obj):
        if file_obj is None: return None
        path = file_obj if isinstance(file_obj, str) else file_obj.name
        mime, _ = mimetypes.guess_type(path)
        if mime and mime.startswith("image"):
            return Image.open(path).convert("RGB")
        elif mime and mime.startswith("video"):
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            cap.release()
            if ret: return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        return Image.open(path).convert("RGB")

    def on_analyze(file_obj, cam_obj):
        try:
            if cam_obj is not None:
                img = Image.fromarray(cam_obj) if isinstance(cam_obj, np.ndarray) else Image.open(cam_obj).convert("RGB")
                v_html, gc_img, l_img, a_img, summ, _ = _analyze_pil_image(img)
                return v_html, gc_img, l_img, a_img, summ

            if file_obj is not None:
                class FileWrapper:
                    def __init__(self, path): self.name = path
                
                f_obj = FileWrapper(file_obj) if isinstance(file_obj, str) else file_obj
                v_html, gc_img, l_img, a_img, summ, _ = predict_file(f_obj)
                return v_html, gc_img, l_img, a_img, summ

            return format_verdict("waiting", 0), None, None, None, "*Upload a file to generate a report.*"
            
        except Exception as e:
            return format_verdict("error", 0), None, None, None, f"Error: {str(e)}"

    file_input.change(fn=on_file_change, inputs=file_input, outputs=preview)
    camera_input.change(fn=lambda c: Image.fromarray(c) if isinstance(c, np.ndarray) else Image.open(c).convert("RGB") if c else None, inputs=camera_input, outputs=preview)
    analyze_btn.click(fn=on_analyze, inputs=[file_input, camera_input], outputs=[verdict, gradcam_output, lime_output, artifact_output, summary_output])

if __name__ == "__main__":
    demo.launch(theme=GALACTIC_THEME, css=CUSTOM_CSS)