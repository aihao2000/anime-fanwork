import huggingface_hub
import gradio as gr
from stable_diffusion_reference_only.pipelines.stable_diffusion_reference_only_pipeline import (
    StableDiffusionReferenceOnlyPipeline,
)
import anime_segmentation
from diffusers.schedulers import UniPCMultistepScheduler
from PIL import Image
import cv2
import numpy as np
import os

automatic_coloring_pipeline = StableDiffusionReferenceOnlyPipeline.from_pretrained(
    "AisingioroHao0/stable-diffusion-reference-only-automatic-coloring-0.1.2"
)
automatic_coloring_pipeline.scheduler = UniPCMultistepScheduler.from_config(
    automatic_coloring_pipeline.scheduler.config
)

segment_model = anime_segmentation.get_model(
    model_path=huggingface_hub.hf_hub_download("skytnt/anime-seg", "isnetis.ckpt")
)


def character_segment(img):
    if img is None:
        return None
    img = anime_segmentation.character_segment(segment_model, img)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    return img


def color_inversion(img):
    if img is None:
        return None
    return 255 - img


def get_line_art(img):
    if img is None:
        return None
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.adaptiveThreshold(
        img,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        blockSize=5,
        C=7,
    )
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return img


def inference(prompt, blueprint, num_inference_steps):
    if prompt is None or blueprint is None:
        return None
    return np.array(
        automatic_coloring_pipeline(
            prompt=Image.fromarray(prompt),
            blueprint=Image.fromarray(blueprint),
            num_inference_steps=num_inference_steps,
        ).images[0]
    )


def automatic_coloring(prompt, blueprint, num_inference_steps):
    if prompt is None or blueprint is None:
        return None
    blueprint = color_inversion(blueprint)
    return inference(prompt, blueprint, num_inference_steps)


def style_transfer(prompt, blueprint, num_inference_steps):
    if prompt is None or blueprint is None:
        return None
    prompt = character_segment(prompt)
    blueprint = character_segment(blueprint)
    blueprint = get_line_art(blueprint)
    blueprint = color_inversion(blueprint)
    return inference(prompt, blueprint, num_inference_steps)


with gr.Blocks() as demo:
    gr.Markdown(
        """
    # Stable Diffusion Reference Only Automatic Coloring 0.1.2\n\n
    demo for [<svg height="32" aria-hidden="true" viewBox="0 0 16 16" version="1.1" width="32" data-view-component="true" class="octicon octicon-mark-github v-align-middle color-fg-default">
        <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
    </svg>](https://github.com/aihao2000/StableDiffusionReferenceOnly)
    """
    )
    with gr.Row():
        with gr.Column():
            prompt_input_compoent = gr.Image(shape=(512, 512), label="prompt")
            prompt_character_segment_button = gr.Button(
                "character segment",
            )
            prompt_character_segment_button.click(
                character_segment,
                inputs=prompt_input_compoent,
                outputs=prompt_input_compoent,
            )
        with gr.Column():
            blueprint_input_compoent = gr.Image(shape=(512, 512), label="blueprint")
            blueprint_character_segment_button = gr.Button("character segment")
            blueprint_character_segment_button.click(
                character_segment,
                inputs=blueprint_input_compoent,
                outputs=blueprint_input_compoent,
            )
            get_line_art_button = gr.Button(
                "get line art",
            )
            get_line_art_button.click(
                get_line_art,
                inputs=blueprint_input_compoent,
                outputs=blueprint_input_compoent,
            )
            color_inversion_button = gr.Button(
                "color inversion",
            )
            color_inversion_button.click(
                color_inversion,
                inputs=blueprint_input_compoent,
                outputs=blueprint_input_compoent,
            )
        with gr.Column():
            result_output_component = gr.Image(shape=(512, 512), label="result")
            num_inference_steps_input_component = gr.Number(
                20, label="num inference steps", minimum=1, maximum=1000, step=1
            )
            inference_button = gr.Button("inference")
            inference_button.click(
                inference,
                inputs=[
                    prompt_input_compoent,
                    blueprint_input_compoent,
                    num_inference_steps_input_component,
                ],
                outputs=result_output_component,
            )
            automatic_coloring_button = gr.Button("automatic coloring")
            automatic_coloring_button.click(
                automatic_coloring,
                inputs=[
                    prompt_input_compoent,
                    blueprint_input_compoent,
                    num_inference_steps_input_component,
                ],
                outputs=result_output_component,
            )
            style_transfer_button = gr.Button("style transfer")
            style_transfer_button.click(
                style_transfer,
                inputs=[
                    prompt_input_compoent,
                    blueprint_input_compoent,
                    num_inference_steps_input_component,
                ],
                outputs=result_output_component,
            )
    with gr.Row():
        gr.Examples(
            examples=[
                [
                    os.path.join(
                        os.path.dirname(__file__), "README.assets", "3x9_prompt.png"
                    ),
                    os.path.join(
                        os.path.dirname(__file__), "README.assets", "3x9_blueprint.png"
                    ),
                ],
            ],
            inputs=[prompt_input_compoent, blueprint_input_compoent],
            outputs=result_output_component,
            fn=lambda x, y: None,
            cache_examples=True,
        )


demo.launch()
