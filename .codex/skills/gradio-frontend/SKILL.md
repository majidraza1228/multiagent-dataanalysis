---
name: gradio-frontend
description: Gradio UI scaffold for image upload, classification results, and top-3 confidence chart
---

```python
# ui/app.py
import gradio as gr
import httpx
import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image

API_URL = "http://localhost:8000/api/predict"

SAMPLE_IMAGES = [
    "samples/airplane.jpg",
    "samples/cat.jpg",
    "samples/dog.jpg",
    "samples/ship.jpg",
    "samples/truck.jpg",
]

def classify(image):
    if image is None:
        return "No image provided", None
    try:
        buf = io.BytesIO()
        Image.fromarray(image).save(buf, format="JPEG")
        buf.seek(0)
        resp = httpx.post(API_URL, files={"file": ("image.jpg", buf, "image/jpeg")}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except httpx.ConnectError:
        return "Backend unreachable. Is the server running?", None
    except Exception as e:
        return f"Error: {str(e)}", None

    label = f"{data['class']} ({data['confidence']*100:.1f}%)"
    chart = make_bar_chart(data["top3"])
    return label, chart

def make_bar_chart(top3):
    classes = [item["class"] for item in top3]
    confs = [item["confidence"] for item in top3]
    fig, ax = plt.subplots(figsize=(5, 2.5))
    bars = ax.barh(classes[::-1], confs[::-1], color=["#4CAF50", "#2196F3", "#FF9800"])
    ax.set_xlim(0, 1)
    ax.set_xlabel("Confidence")
    ax.set_title("Top-3 Predictions")
    for bar, conf in zip(bars, confs[::-1]):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f"{conf*100:.1f}%", va="center", fontsize=9)
    fig.tight_layout()
    return fig

with gr.Blocks(title="ML Image Classifier") as demo:
    gr.Markdown("## Image Classifier")
    with gr.Row():
        with gr.Column():
            img_input = gr.Image(label="Upload Image", type="numpy")
            submit_btn = gr.Button("Classify", variant="primary")
            gr.Examples(examples=SAMPLE_IMAGES, inputs=img_input, label="Sample Images")
        with gr.Column():
            label_out = gr.Textbox(label="Prediction")
            chart_out = gr.Plot(label="Top-3 Confidence")

    submit_btn.click(fn=classify, inputs=img_input, outputs=[label_out, chart_out])
    img_input.change(fn=classify, inputs=img_input, outputs=[label_out, chart_out])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
```

```bash
# run UI
python ui/app.py
```
