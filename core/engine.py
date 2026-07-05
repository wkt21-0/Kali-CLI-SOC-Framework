#!/usr/bin/env python3
"""
Minimal SOC engine CLI: loads config, registers core.modules.* commands,
parses args, and calls handler functions provided by modules.
"""
import argparse
import importlib
import logging
from pathlib import Path
import sys
import yaml

DEFAULT_CONFIG = Path("config/soc.yaml")


def load_config(path: Path = DEFAULT_CONFIG):
    if not path.exists():
        return {}
    try:
        with path.open() as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def setup_logging(level_str: str = "INFO"):
    level = getattr(logging, level_str.upper(), logging.INFO)
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def discover_and_register_modules(subparsers):
    modules = [
        "mitre",
        "loggen",
        "sigma",
        "siem",
        "compliance",
        "reporting",
        "dashboard",
        "integrity",
        "plugins",
        "threatintel",
    ]
    for mod in modules:
        full = f"core.modules.{mod}"
        try:
            m = importlib.import_module(full)
            if hasattr(m, "register"):
                m.register(subparsers)
            else:
                logging.debug("module %s has no register()", full)
        except ModuleNotFoundError:
            logging.debug("module not found: %s", full)
        except Exception as e:
            logging.warning("error loading module %s: %s", full, e)


def main(argv=None):
    cfg = load_config()
    engine_cfg = cfg.get("engine", {})
    log_level = engine_cfg.get("log_level", "INFO")
    setup_logging(log_level)

    parser = argparse.ArgumentParser(prog="soc", description="Kali SOC Framework")
    sub = parser.add_subparsers(dest="command")

    discover_and_register_modules(sub)

    # provide a simple default status command
    def handle_status(args):
        print("Kali SOC Compliance Framework — status")
        print(f"Mode: {engine_cfg.get('mode', 'unknown')}")
        print(f"Log path: {cfg.get('paths', {}).get('logs', 'data/logs')}")

    status = sub.add_parser("status", help="Show engine status")
    status.set_defaults(handler=handle_status)

    args = parser.parse_args(argv)

    if not hasattr(args, "handler"):
        parser.print_help()
        return 2

    try:
        return args.handler(args) or 0
    except Exception as e:
        logging.exception("command failed: %s", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
