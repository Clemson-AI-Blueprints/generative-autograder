
# ========================= ui_components.py ==================
from typing import List, Tuple, Dict
import gradio as gr
from .models import FileRecord


VIS_LABELS = ["Students can see", "Keep hidden from students"]


def visibility_radios(cfg: Dict) -> Tuple[gr.Column, List[Tuple[str, gr.Radio]]]:
    """Return a column with one radio per file & a control‑list for state."""
    controls: List[Tuple[str, gr.Radio]] = []
    files = cfg.get("files", [])
    with gr.Column() as col:
        if not files:
            gr.Markdown("_No files uploaded yet._")
        for rec in files:
            with gr.Row():
                gr.Markdown(f"**{rec.name}**")
                radio = gr.Radio(
                    VIS_LABELS,
                    value=VIS_LABELS[0] if rec.visible_to_students else VIS_LABELS[1],
                    show_label=False,
                    interactive=True,
                    scale=3,
                )
                controls.append((rec.name, radio))
    return col, controls

def build_visibility_radios(cfg: Dict, container: gr.Column) -> List[Tuple[str, gr.Radio]]:
    """Clear and re-build the visibility radio buttons inside `container`."""
    container.children.clear()
    controls: List[Tuple[str, gr.Radio]] = []
    files = cfg.get("files", [])

    if not files:
        container.children.append(gr.Markdown("_No files uploaded yet._"))
        return controls

    for rec in files:
        with gr.Row() as row:
            gr.Markdown(f"**{rec['name']}**")
            radio = gr.Radio(
                VIS_LABELS,
                value=VIS_LABELS[0] if rec.get("visible_to_students", True) else VIS_LABELS[1],
                show_label=False,
                interactive=True,
                scale=3,
            )
            controls.append((rec["name"], radio))
        container.children.append(row)

    return controls

def build_cfg_viewer(cfg: Dict, container: gr.Column) -> None:
    """Display the config in a gr.Column."""
    container.children.clear()
    with container:
        gr.Markdown("## Current Configuration")
        gr.JSON(cfg, label="Config JSON")

    return container

