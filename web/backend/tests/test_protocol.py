"""rosbridge 프로토콜의 입력 검증과 응답 형식 테스트."""

import pytest

from app.rosbridge.protocol import ProtocolError, parse, status_message


def test_parse_requires_operation():
    with pytest.raises(ProtocolError):
        parse({"topic": "/blue/status"})


def test_parse_preserves_publish_payload():
    parsed = parse({"op": "publish", "topic": "/blue/cmd", "msg": {"data": True}})
    assert parsed.op == "publish"
    assert parsed.topic == "/blue/cmd"
    assert parsed.msg == {"data": True}


def test_status_message_omits_optional_id():
    assert status_message("error", "bad request") == {
        "op": "status",
        "level": "error",
        "msg": "bad request",
    }
