
# ========================= app.py ============================
import gradio as gr
import pandas as pd 
from pathlib import Path
from typing import List, Dict
from .file_manager import load_project, save_project
from .models import FileRecord
from .ui_components import visibility_radios, build_visibility_radios, build_cfg_viewer


def _file_records_from_uploads(
    upload_paths: List[Path], category: str
) -> List[FileRecord]:
    if not upload_paths:
        return []
    return [FileRecord(Path(p).name, category) for p in upload_paths]


def create_config_interface():
    with gr.Blocks(title="Auto‑Hinter Config") as demo:
        gr.Markdown("""
        <h1 style="text-align:center;">Auto‑Hinter Configuration</h1>
        <p style="text-align:center;">All changes are saved automatically.</p>
        <hr/>
        """)

        # ── Basic project settings ───────────────────────────
        with gr.Row():
            project_id = gr.Textbox(label="Project ID", placeholder="e.g. cpsc101‑proj1")
            cfg_option = gr.Radio(["Option A", "Option B", "Option C"], value="Option A")

        # ── Upload panels ────────────────────────────────────
        with gr.Accordion("Uploads", open=False):
            directions_pdf = gr.File(label="Directions PDF", file_types=[".pdf"])
            sample_outputs = gr.Files(label="Sample outputs (.txt)", file_types=[".txt"])
            sample_code = gr.Files(label="Sample code", file_types=[".py", ".cpp", ".java", ".c", ".txt"])
            other_uploads = gr.Files(label="Other files")

        visibility_checkbox_group = gr.CheckboxGroup(interactive=True,
                                                     label="Student Visibility",
                                                     show_label=True)

        files_df = gr.Dataframe(
            headers=["File Name", "Visibility"],
            label="File Visibility",
            interactive=False,
            show_label=False,
            wrap=True,
        )

        status = gr.Markdown("")

        # ── Helper: refresh panel & status ───────────────────
        def refresh(pid):
            cfg = load_project(pid)

            if len(cfg.get("files", [])) > 0:
                print("HAS FILES CONFIG UPDATE")
                file_list: List[Dict] = [f for f in cfg.get("files", [])]
                print("File list:", file_list)
                df = pd.DataFrame(file_list, columns=file_list[0].keys())

                choices = [file['name'] for file in file_list]
                value = [file['name'] for file in file_list if file['visible_to_students'] and file['name'] in choices]

                checkbox_update = gr.update(
                    choices=choices,
                    value=value,
                )
            else:
                print("EMPTY CONFIG UPDATE")
                df = pd.DataFrame()
                checkbox_update = gr.update(
                    choices=[],
                    value=[],
                )


            
            return df, checkbox_update, f"✅ Loaded config for **{pid}**"

        # ── Helper: save everything & rebuild panel ──────────
        def autosave(
            pid,
            dir_pdf,
            samp_out,
            samp_code,
            oth_up,
            option,
            visibility,
        ):
            # Build FileRecord list from uploads
            new_files: List[FileRecord] = []
            new_files += _file_records_from_uploads([dir_pdf] if dir_pdf else [], "directions_pdf")
            new_files += _file_records_from_uploads(samp_out, "sample_outputs")
            new_files += _file_records_from_uploads(samp_code, "sample_code")
            new_files += _file_records_from_uploads(oth_up, "other_uploads")

            print("Visibility:", visibility)

            # save_project(pid, option, new_files, visibility)
            # Reload to rebuild radios cleanly
            df, _, _ = refresh(pid)
            return df 

        # ── Event wiring ─────────────────────────────────────
        project_id.submit(
            fn=refresh,
            inputs=[project_id],
            outputs=[files_df, visibility_checkbox_group, status]  # <- dummy return to force a re-run
        )



        for comp in [directions_pdf, sample_outputs, sample_code, other_uploads, cfg_option, visibility_checkbox_group]:
            comp.change(
                fn=autosave,
                inputs=[
                    project_id,
                    directions_pdf,
                    sample_outputs,
                    sample_code,
                    other_uploads,
                    cfg_option,
                    visibility_checkbox_group,
                ],
                outputs=[files_df]
            )

    return demo 

