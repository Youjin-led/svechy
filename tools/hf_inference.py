import argparse
import os
from pathlib import Path


HF_ROUTER_URL = "https://router.huggingface.co/v1"
DEFAULT_CHAT_MODEL = "moonshotai/Kimi-K2-Instruct-0905"
DEFAULT_IMAGE_MODEL = "black-forest-labs/FLUX.1-dev"
DEFAULT_IMAGE_PROVIDER = "wavespeed"


def require_token() -> str:
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit(
            "HF_TOKEN is not set. In PowerShell run: $env:HF_TOKEN='your_token_here'"
        )
    return token


def chat(args: argparse.Namespace) -> None:
    from openai import OpenAI

    client = OpenAI(base_url=HF_ROUTER_URL, api_key=require_token())
    completion = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": args.prompt}],
    )
    print(completion.choices[0].message.content)


def image(args: argparse.Namespace) -> None:
    from huggingface_hub import InferenceClient

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    client = InferenceClient(provider=args.provider, api_key=require_token())
    result = client.text_to_image(args.prompt, model=args.model)
    result.save(output_path)
    print(f"Saved image to {output_path}")


def check(_: argparse.Namespace) -> None:
    import openai
    import huggingface_hub
    import PIL

    print(f"openai={openai.__version__}")
    print(f"huggingface_hub={huggingface_hub.__version__}")
    print(f"pillow={PIL.__version__}")
    print(f"HF_TOKEN={'set' if os.environ.get('HF_TOKEN') else 'missing'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Small Hugging Face Inference helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Check local packages and token.")
    check_parser.set_defaults(func=check)

    chat_parser = subparsers.add_parser("chat", help="Run an LLM prompt through HF router.")
    chat_parser.add_argument("prompt")
    chat_parser.add_argument("--model", default=DEFAULT_CHAT_MODEL)
    chat_parser.set_defaults(func=chat)

    image_parser = subparsers.add_parser("image", help="Generate an image through HF InferenceClient.")
    image_parser.add_argument("prompt")
    image_parser.add_argument("--model", default=DEFAULT_IMAGE_MODEL)
    image_parser.add_argument("--provider", default=DEFAULT_IMAGE_PROVIDER)
    image_parser.add_argument("--output", default="output/hf-image.png")
    image_parser.set_defaults(func=image)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
