"""Stable Diffusion on your own machine (the terminal / Zed pattern).

Run it:
    pip install diffusers transformers accelerate torch
    python image_gen.py

Works on NVIDIA (cuda), Apple Silicon (mps), or CPU (slow but works).
This is the same lab as the Colab notebook image_gen_advanced.ipynb -- just
local. Colab's free T4 GPU is usually faster if your laptop has no GPU.

Rules (same as the Colab lab):
  - no real people's faces or names (portrait right)
  - no existing characters as-is (copyright)
  - no deepfakes / passing AI work off as human-made
  - credit images as "created with Stable Diffusion"; check the licence before sharing
"""

import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

# pick ONE model_id (leave one uncommented):
model_id = "stablediffusionapi/anything-v5"                  # anime / illustration
# model_id = "stable-diffusion-v1-5/stable-diffusion-v1-5"   # general base
# model_id = "SG161222/Realistic_Vision_V5.1_noVAE"          # photo-real (Western-leaning data)

# choose the fastest device this machine has
if torch.cuda.is_available():
    device, dtype = "cuda", torch.float16
elif torch.backends.mps.is_available():
    device, dtype = "mps", torch.float32       # Apple Silicon
else:
    device, dtype = "cpu", torch.float32       # works, but slow

pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype, safety_checker=None)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe = pipe.to(device)

# the four dials -- change these and run again
prompt          = "a cozy ramen shop on a rainy night, neon signs, watercolor style"
negative_prompt = "low quality, blurry, text, watermark"   # what to keep OUT
seed            = 42        # same seed + same prompt  ->  same image
CFG_scale       = 7.0       # how hard to obey the prompt (about 7 = balanced)
steps           = 25        # denoising passes (more = finer, slower)

generator = torch.Generator(device).manual_seed(seed)
image = pipe(
    prompt,
    negative_prompt=negative_prompt,
    guidance_scale=CFG_scale,
    num_inference_steps=steps,
    width=512,
    height=512,
    generator=generator,
).images[0]

image.save("out.png")
print("saved out.png   (device:", device, "| model:", model_id, ")")
