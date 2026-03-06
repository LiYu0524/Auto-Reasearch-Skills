#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Headless CLI wrapper for PaperBanana multi-agent academic illustration generation.
Bypasses Streamlit and calls the PaperVizProcessor pipeline directly.

Usage:
    python3 generate_figure.py \
        --content "方法文本" \
        --caption "Figure 1: Pipeline overview" \
        --output ./fig.png \
        [--task diagram|plot] \
        [--aspect-ratio 16:9] \
        [--exp-mode demo_planner_critic] \
        [--retrieval-setting none] \
        [--critic-rounds 3] \
        [--image-model-name ""] \
        [--paperbanana-dir ~/PaperBanana]
"""

import argparse
import asyncio
import base64
import json
import os
import sys
from io import BytesIO
from pathlib import Path


DEFAULT_PAPERBANANA_DIR = os.path.expanduser("~/PaperBanana")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate academic illustrations via PaperBanana pipeline"
    )
    parser.add_argument(
        "--content", required=True,
        help="Method text content. Use @filepath to read from file."
    )
    parser.add_argument(
        "--caption", required=True,
        help="Figure caption / visual intent."
    )
    parser.add_argument(
        "--output", required=True,
        help="Output image path (e.g. ./fig.png)."
    )
    parser.add_argument(
        "--task", choices=["diagram", "plot"], default="diagram",
        help="Task type: diagram or plot (default: diagram)."
    )
    parser.add_argument(
        "--aspect-ratio", default="16:9",
        help="Aspect ratio (default: 16:9)."
    )
    parser.add_argument(
        "--exp-mode", default="demo_planner_critic",
        help="Experiment mode (default: demo_planner_critic)."
    )
    parser.add_argument(
        "--retrieval-setting", default="none",
        choices=["auto", "manual", "random", "none"],
        help="Retrieval setting (default: none)."
    )
    parser.add_argument(
        "--critic-rounds", type=int, default=3,
        help="Max critic refinement rounds (default: 3)."
    )
    parser.add_argument(
        "--image-model-name", default="",
        help="Override image model name."
    )
    parser.add_argument(
        "--paperbanana-dir", default=DEFAULT_PAPERBANANA_DIR,
        help=f"PaperBanana project root (default: {DEFAULT_PAPERBANANA_DIR})."
    )
    return parser.parse_args()


def resolve_content(raw: str) -> str:
    """If raw starts with @, read content from the referenced file."""
    if raw.startswith("@"):
        filepath = Path(raw[1:]).expanduser()
        if not filepath.exists():
            print(json.dumps({"status": "error", "message": f"File not found: {filepath}"}))
            sys.exit(1)
        return filepath.read_text(encoding="utf-8")
    return raw


def ensure_ref_json(paperbanana_dir: Path, task: str):
    """Ensure data/PaperBananaBench/{task}/ref.json exists (empty array).
    The planner agent always tries to open this file even when retrieval=none."""
    ref_dir = paperbanana_dir / "data" / "PaperBananaBench" / task
    ref_file = ref_dir / "ref.json"
    if not ref_file.exists():
        ref_dir.mkdir(parents=True, exist_ok=True)
        ref_file.write_text("[]", encoding="utf-8")


def extract_final_image_b64(result: dict, task: str, exp_mode: str):
    """Extract the best base64 image from the result dict.
    Priority: last critic round -> stylist -> planner."""
    # Try critic rounds in reverse
    for round_idx in range(9, -1, -1):
        key = f"target_{task}_critic_desc{round_idx}_base64_jpg"
        if key in result and result[key]:
            return result[key]

    # Fallback: stylist (for demo_full)
    if exp_mode in ("demo_full", "dev_full"):
        key = f"target_{task}_stylist_desc0_base64_jpg"
        if key in result and result[key]:
            return result[key]

    # Fallback: planner
    key = f"target_{task}_desc0_base64_jpg"
    if key in result and result[key]:
        return result[key]

    # Fallback: vanilla
    key = f"vanilla_{task}_base64_jpg"
    if key in result and result[key]:
        return result[key]

    return None


async def run_pipeline(args):
    paperbanana_dir = Path(args.paperbanana_dir).expanduser().resolve()
    if not paperbanana_dir.exists():
        return {"status": "error", "message": f"PaperBanana dir not found: {paperbanana_dir}"}

    # Add PaperBanana to sys.path
    sys.path.insert(0, str(paperbanana_dir))

    # Ensure ref.json exists for both tasks
    ensure_ref_json(paperbanana_dir, "diagram")
    ensure_ref_json(paperbanana_dir, "plot")

    # Import PaperBanana modules
    from agents.planner_agent import PlannerAgent
    from agents.visualizer_agent import VisualizerAgent
    from agents.stylist_agent import StylistAgent
    from agents.critic_agent import CriticAgent
    from agents.retriever_agent import RetrieverAgent
    from agents.vanilla_agent import VanillaAgent
    from agents.polish_agent import PolishAgent
    from utils.config import ExpConfig
    from utils.paperviz_processor import PaperVizProcessor

    # Resolve content
    content = resolve_content(args.content)

    # Create experiment config
    exp_config = ExpConfig(
        dataset_name="CLI",
        task_name=args.task,
        split_name="cli",
        exp_mode=args.exp_mode,
        retrieval_setting=args.retrieval_setting,
        max_critic_rounds=args.critic_rounds,
        model_name="",
        image_model_name=args.image_model_name,
        work_dir=paperbanana_dir,
    )

    # Initialize all agents
    processor = PaperVizProcessor(
        exp_config=exp_config,
        vanilla_agent=VanillaAgent(exp_config=exp_config),
        planner_agent=PlannerAgent(exp_config=exp_config),
        visualizer_agent=VisualizerAgent(exp_config=exp_config),
        stylist_agent=StylistAgent(exp_config=exp_config),
        critic_agent=CriticAgent(exp_config=exp_config),
        retriever_agent=RetrieverAgent(exp_config=exp_config),
        polish_agent=PolishAgent(exp_config=exp_config),
    )

    # Build input data (same format as demo.py create_sample_inputs)
    input_data = {
        "filename": "cli_input",
        "caption": args.caption,
        "content": content,
        "visual_intent": args.caption,
        "additional_info": {
            "rounded_ratio": args.aspect_ratio,
        },
        "max_critic_rounds": args.critic_rounds,
    }

    # Run pipeline
    result = await processor.process_single_query(input_data, do_eval=False)

    # Extract final image
    b64_image = extract_final_image_b64(result, args.task, args.exp_mode)
    if not b64_image:
        return {"status": "error", "message": "No image generated by pipeline"}

    # Decode and save
    from PIL import Image
    if "," in b64_image:
        b64_image = b64_image.split(",")[1]
    image_data = base64.b64decode(b64_image)
    img = Image.open(BytesIO(image_data))

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine format from extension
    ext = output_path.suffix.lower()
    fmt = "JPEG" if ext in (".jpg", ".jpeg") else "PNG"
    img.save(str(output_path), format=fmt)

    return {
        "status": "success",
        "output": str(output_path),
        "format": fmt,
        "size": f"{img.width}x{img.height}",
        "exp_mode": args.exp_mode,
        "task": args.task,
    }


def main():
    args = parse_args()
    try:
        result = asyncio.run(run_pipeline(args))
    except Exception as e:
        result = {"status": "error", "message": str(e)}
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
