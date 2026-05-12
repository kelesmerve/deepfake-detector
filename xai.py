"""
XAI (Explainable AI) Module for Deepfake Detection System
Provides Grad-CAM, LIME, and Frequency Artifact Analysis
"""

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from torchvision import transforms
import io
import time


# =====================================================================
#  GRAD-CAM
# =====================================================================

class GradCAM:
    """Gradient-weighted Class Activation Mapping for EfficientNet-B0."""

    def __init__(self, model):
        self.model = model
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        # Hook into the last convolutional layer
        try:
            target_layer = self.model.backbone.conv_head
        except AttributeError:
            target_layer = self.model.features[-1]

        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        target_layer.register_forward_hook(forward_hook)
        target_layer.register_full_backward_hook(backward_hook)

    def generate(self, input_tensor, target_class=None):
        """
        Generate Grad-CAM heatmap.
        Returns: numpy array (H, W) with values in [0, 1]
        """
        self.model.eval()
        input_tensor.requires_grad_(True)

        output = self.model(input_tensor)
        if target_class is None:
            target_class = output.argmax(dim=1).item()

        self.model.zero_grad()
        output[0, target_class].backward()

        # Global average pooling of gradients
        weights = self.gradients.mean(dim=[2, 3], keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = cam.squeeze().cpu().numpy()

        # Normalize
        if cam.max() > 0:
            cam = cam / cam.max()

        return cam


def apply_gradcam_overlay(original_img, cam, alpha=0.5):
    """
    Overlay Grad-CAM heatmap on the original image.
    Returns: PIL Image with heatmap overlay
    """
    img_array = np.array(original_img.resize((224, 224)))
    cam_resized = cv2.resize(cam, (224, 224))

    # Custom purple-magenta colormap for galactic theme
    colors = [
        (0.0, 0.0, 0.1),       # deep dark blue
        (0.2, 0.0, 0.4),       # dark purple
        (0.6, 0.0, 0.8),       # vibrant purple
        (1.0, 0.2, 0.6),       # magenta-pink
        (1.0, 0.9, 1.0),       # white-pink
    ]
    galactic_cmap = LinearSegmentedColormap.from_list("galactic", colors)

    heatmap = galactic_cmap(cam_resized)[:, :, :3]
    heatmap = (heatmap * 255).astype(np.uint8)

    overlay = cv2.addWeighted(img_array, 1 - alpha, heatmap, alpha, 0)
    return Image.fromarray(overlay)


def generate_gradcam_figure(original_img, cam):
    """Generate a side-by-side figure: Original | Heatmap | Overlay."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor("#0a0a1a")

    img_resized = original_img.resize((224, 224))
    cam_resized = cv2.resize(cam, (224, 224))

    # Original
    axes[0].imshow(img_resized)
    axes[0].set_title("Original", color="white", fontsize=14, fontweight="bold")
    axes[0].axis("off")

    # Heatmap only
    colors = [
        (0.0, 0.0, 0.1),
        (0.2, 0.0, 0.4),
        (0.6, 0.0, 0.8),
        (1.0, 0.2, 0.6),
        (1.0, 0.9, 1.0),
    ]
    galactic_cmap = LinearSegmentedColormap.from_list("galactic", colors)
    axes[1].imshow(cam_resized, cmap=galactic_cmap)
    axes[1].set_title("Activation Map", color="white", fontsize=14, fontweight="bold")
    axes[1].axis("off")

    # Overlay
    overlay = apply_gradcam_overlay(original_img, cam, alpha=0.5)
    axes[2].imshow(overlay)
    axes[2].set_title("Overlay", color="white", fontsize=14, fontweight="bold")
    axes[2].axis("off")

    plt.tight_layout()
    return fig_to_pil(fig)


# =====================================================================
#  LIME
# =====================================================================

def generate_lime_explanation(model, original_img, preprocess_fn, num_samples=50):
    """
    Generate LIME explanation for the image.
    Returns: PIL Image showing LIME superpixel explanation
    """
    try:
        from lime import lime_image

        explainer = lime_image.LimeImageExplainer()
        img_array = np.array(original_img.resize((224, 224)))

        def batch_predict(images):
            batch = []
            for img in images:
                pil_img = Image.fromarray(img.astype(np.uint8))
                tensor = preprocess_fn(pil_img)
                batch.append(tensor)
            batch_tensor = torch.stack(batch)
            with torch.no_grad():
                outputs = model(batch_tensor)
                probs = F.softmax(outputs, dim=1)
            return probs.cpu().numpy()

        explanation = explainer.explain_instance(
            img_array,
            batch_predict,
            top_labels=2,
            hide_color=0,
            num_samples=num_samples,
            batch_size=16,
        )

        # Get the explanation for the predicted class
        predicted_label = explanation.top_labels[0]

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.patch.set_facecolor("#0a0a1a")

        # Original image
        axes[0].imshow(img_array)
        axes[0].set_title("Original", color="white", fontsize=14, fontweight="bold")
        axes[0].axis("off")

        # Positive contributions (regions supporting the prediction)
        temp, mask = explanation.get_image_and_mask(
            predicted_label,
            positive_only=True,
            num_features=8,
            hide_rest=False,
            min_weight=0.01,
        )
        axes[1].imshow(mark_boundaries_custom(temp, mask))
        label_text = "Fake Indicators" if predicted_label == 0 else "Real Indicators"
        axes[1].set_title(label_text, color="#c084fc", fontsize=14, fontweight="bold")
        axes[1].axis("off")

        # Positive and negative contributions
        temp2, mask2 = explanation.get_image_and_mask(
            predicted_label,
            positive_only=False,
            num_features=10,
            hide_rest=False,
            min_weight=0.01,
        )
        axes[2].imshow(mark_boundaries_custom(temp2, mask2))
        axes[2].set_title("All Regions", color="white", fontsize=14, fontweight="bold")
        axes[2].axis("off")

        plt.tight_layout()
        return fig_to_pil(fig)

    except ImportError:
        return _create_error_image("LIME library not installed.\npip install lime")
    except Exception as e:
        return _create_error_image(f"LIME Error: {str(e)}")


def mark_boundaries_custom(image, mask):
    """Draw purple boundaries around LIME segments."""
    from skimage.segmentation import mark_boundaries
    marked = mark_boundaries(image / 255.0 if image.max() > 1 else image, mask, color=(0.75, 0.33, 1.0), mode="thick")
    return (marked * 255).astype(np.uint8) if marked.max() <= 1 else marked.astype(np.uint8)


# =====================================================================
#  FREQUENCY ARTIFACT ANALYSIS
# =====================================================================

def generate_artifact_analysis(original_img):
    """
    Perform frequency-domain analysis to detect deepfake artifacts.
    Uses DCT (Discrete Cosine Transform) and FFT analysis.
    Returns: PIL Image with analysis visualization
    """
    img_array = np.array(original_img.resize((224, 224)))
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY).astype(np.float32)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor("#0a0a1a")

    # 1) FFT Magnitude Spectrum
    f_transform = np.fft.fft2(gray)
    f_shift = np.fft.fftshift(f_transform)
    magnitude = np.log1p(np.abs(f_shift))
    magnitude = magnitude / magnitude.max()

    galactic_cmap = LinearSegmentedColormap.from_list("galactic", [
        (0.0, 0.0, 0.1), (0.15, 0.0, 0.3), (0.4, 0.0, 0.6),
        (0.8, 0.2, 1.0), (1.0, 0.9, 1.0)
    ])

    axes[0].imshow(magnitude, cmap=galactic_cmap)
    axes[0].set_title("FFT Spectrum", color="white", fontsize=14, fontweight="bold")
    axes[0].axis("off")

    # 2) High-frequency residual (edge/artifact detection)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    residual = np.abs(gray - blurred)
    residual = residual / (residual.max() + 1e-8)

    axes[1].imshow(residual, cmap=galactic_cmap)
    axes[1].set_title("High-Freq Residual", color="white", fontsize=14, fontweight="bold")
    axes[1].axis("off")

    # 3) Error Level Analysis (ELA) simulation
    # Compress at quality 90 and compare
    pil_resized = original_img.resize((224, 224))
    buffer = io.BytesIO()
    pil_resized.save(buffer, format="JPEG", quality=90)
    buffer.seek(0)
    compressed = np.array(Image.open(buffer)).astype(np.float32)
    original_f = img_array.astype(np.float32)

    ela = np.abs(original_f - compressed)
    ela = ela.mean(axis=2)  # average across channels
    ela = ela / (ela.max() + 1e-8)

    axes[2].imshow(ela, cmap=galactic_cmap)
    axes[2].set_title("Error Level Analysis", color="white", fontsize=14, fontweight="bold")
    axes[2].axis("off")

    plt.tight_layout()
    return fig_to_pil(fig)


# =====================================================================
#  NATURAL LANGUAGE SUMMARY
# =====================================================================

def generate_analysis_summary(prediction, confidence, cam, inference_time, is_video=False, num_frames=1):
    """Generate a natural language explanation of the analysis results."""
    label = "DEEPFAKE" if prediction == 0 else "REAL"
    conf_pct = confidence * 100

    # Analyze Grad-CAM activation distribution
    cam_resized = cv2.resize(cam, (7, 7))  # coarse grid
    top_region = np.unravel_index(cam_resized.argmax(), cam_resized.shape)

    # Map grid position to face region
    region_map = {
        (0, 0): "top-left (forehead/hair)", (0, 1): "top-left (forehead/hair)",
        (0, 2): "top-center (forehead)", (0, 3): "top-center (forehead)",
        (0, 4): "top-center (forehead)", (0, 5): "top-right (forehead/hair)",
        (0, 6): "top-right (forehead/hair)",
        (1, 0): "left (temple)", (1, 1): "left (temple)",
        (1, 2): "left eye area", (1, 3): "center (between eyes)",
        (1, 4): "right eye area", (1, 5): "right (temple)",
        (1, 6): "right (temple)",
        (2, 0): "left (cheek)", (2, 1): "left eye area",
        (2, 2): "left eye", (2, 3): "nose bridge",
        (2, 4): "right eye", (2, 5): "right eye area",
        (2, 6): "right (cheek)",
        (3, 0): "left (cheek)", (3, 1): "left (cheek)",
        (3, 2): "nose (left)", (3, 3): "nose (center)",
        (3, 4): "nose (right)", (3, 5): "right (cheek)",
        (3, 6): "right (cheek)",
        (4, 0): "left (jaw)", (4, 1): "left (mouth area)",
        (4, 2): "mouth (left)", (4, 3): "mouth (center)",
        (4, 4): "mouth (right)", (4, 5): "right (mouth area)",
        (4, 6): "right (jaw)",
        (5, 0): "left (jaw)", (5, 1): "left (chin area)",
        (5, 2): "chin (left)", (5, 3): "chin (center)",
        (5, 4): "chin (right)", (5, 5): "right (chin area)",
        (5, 6): "right (jaw)",
        (6, 0): "bottom-left", (6, 1): "bottom-left",
        (6, 2): "lower chin", (6, 3): "lower chin",
        (6, 4): "lower chin", (6, 5): "bottom-right",
        (6, 6): "bottom-right",
    }
    focus_region = region_map.get(top_region, "central area")

    # Activation concentration
    cam_flat = cam.flatten()
    high_activation = (cam_flat > 0.5).sum() / len(cam_flat)

    # Build summary
    lines = []
    lines.append(f"## 🔍 Analysis Result: **{label}**\n")

    if prediction == 0:  # Fake
        if conf_pct > 85:
            lines.append(f"⚠️ **High confidence deepfake detection** ({conf_pct:.1f}%).\n")
        elif conf_pct > 65:
            lines.append(f"🟡 **Moderate confidence** deepfake indicators detected ({conf_pct:.1f}%).\n")
        else:
            lines.append(f"🟠 **Low confidence** — possible deepfake but uncertain ({conf_pct:.1f}%).\n")

        lines.append(f"**Primary focus area:** The model's attention is concentrated on the **{focus_region}**. ")

        if high_activation > 0.15:
            lines.append("The activation pattern is **widely spread**, suggesting multiple manipulated regions.\n")
        else:
            lines.append("The activation is **localized**, pointing to a specific manipulated area.\n")

        lines.append("\n**Possible indicators:**\n")
        lines.append("- Inconsistent boundary blending around facial features\n")
        lines.append("- Subtle texture mismatches in the detected region\n")
        lines.append("- Potential compression artifact asymmetry\n")
    else:  # Real
        if conf_pct > 85:
            lines.append(f"✅ **High confidence** — image appears authentic ({conf_pct:.1f}%).\n")
        elif conf_pct > 65:
            lines.append(f"🟢 **Moderate confidence** — likely authentic ({conf_pct:.1f}%).\n")
        else:
            lines.append(f"🟡 **Low confidence** — classified as real but with uncertainty ({conf_pct:.1f}%).\n")

        lines.append(f"**Model attention area:** {focus_region}. ")
        lines.append("Activation pattern is consistent with natural image characteristics.\n")

    lines.append(f"\n---\n")
    lines.append(f"**Technical Details:**\n")
    lines.append(f"- Model: EfficientNet-B0 (fine-tuned)\n")
    lines.append(f"- Input Resolution: 224 × 224 px\n")
    lines.append(f"- Inference Time: {inference_time:.3f}s\n")

    if is_video:
        lines.append(f"- Frames Analyzed: {num_frames}\n")
        lines.append(f"- Method: Multi-frame probability averaging\n")

    # Risk level
    if prediction == 0:
        if conf_pct > 90:
            risk = "🔴 CRITICAL"
        elif conf_pct > 75:
            risk = "🟠 HIGH"
        elif conf_pct > 60:
            risk = "🟡 MEDIUM"
        else:
            risk = "⚪ LOW"
    else:
        risk = "🟢 SAFE"

    lines.append(f"- Risk Level: **{risk}**\n")

    return "".join(lines)


# =====================================================================
#  UTILITY FUNCTIONS
# =====================================================================

def fig_to_pil(fig):
    """Convert matplotlib figure to PIL Image."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def _create_error_image(text):
    """Create a simple error message image."""
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("#0a0a1a")
    ax.set_facecolor("#0a0a1a")
    ax.text(0.5, 0.5, text, color="#ff6b6b", fontsize=16,
            ha="center", va="center", transform=ax.transAxes)
    ax.axis("off")
    return fig_to_pil(fig)
