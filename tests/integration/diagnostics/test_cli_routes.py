from __future__ import annotations

from openclaw_assistant.commands import build_parser


def test_diagnostics_pipeline_subcommand_parses() -> None:
    parser = build_parser()
    args = parser.parse_args(["diagnostics", "pipeline", "--timeout", "12", "--openclaw"])
    assert args.command == "diagnostics"
    assert args.diag_cmd == "pipeline"
    assert args.timeout == 12
    assert args.openclaw is True
