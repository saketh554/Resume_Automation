from __future__ import annotations

from unittest.mock import patch

from backend.agents.schemas import JDStruct
from backend.services import jd_parser


def test_parse_jd_uses_llm_when_available() -> None:
    expected = JDStruct(
        required_skills=["Python", "FastAPI"],
        nice_to_haves=["Docker"],
        responsibilities=["Build APIs"],
        seniority="senior",
        company="Acme",
        role_title="Senior Backend Engineer",
    )

    with patch.object(jd_parser, "parse_jd_with_llm", return_value=expected):
        parsed, source = jd_parser.parse_jd("JD text")

    assert source == "llm"
    assert parsed == expected


def test_parse_jd_falls_back_on_llm_error() -> None:
    jd_text = "Requirements: Python, FastAPI\nNice to have: Docker\n- Build APIs"

    with patch.object(jd_parser, "parse_jd_with_llm", side_effect=RuntimeError("network")):
        parsed, source = jd_parser.parse_jd(jd_text)

    assert source == "fallback"
    assert "python" in [item.lower() for item in parsed.required_skills]
    assert any("docker" in item.lower() for item in parsed.nice_to_haves)
