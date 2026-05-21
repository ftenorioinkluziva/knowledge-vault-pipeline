from __future__ import annotations

import argparse
import json

from knowledge_vault_pipeline.config import load_config
from knowledge_vault_pipeline.env import load_project_env
from knowledge_vault_pipeline.pipeline import run_pipeline
from knowledge_vault_pipeline.youtube import run_youtube_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kvp")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Processa documentos e gera vault-ready.")
    run.add_argument("--config", required=True, help="Caminho do arquivo YAML de configuracao.")

    youtube = subparsers.add_parser("youtube", help="Busca transcricoes de videos e gera vault-ready.")
    youtube.add_argument("--config", required=True, help="Caminho do arquivo YAML de configuracao.")
    return parser


def main(argv: list[str] | None = None) -> None:
    load_project_env()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        config = load_config(args.config)
        stats = run_pipeline(config)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    elif args.command == "youtube":
        config = load_config(args.config)
        stats = run_youtube_pipeline(config)
        print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
