import json
from urlshortner.url_shortner_combined import (
    create_url,
    get_url,
    check_valid_url,
    update_blacklist,
)


def test_create_url() -> None:
    assert (
        json.loads(
            create_url({"headers": {"url": "https://www.shreyasgaonkar.com/"}})["body"]
        )
        == "https://trim.live/8f0fe3"
    )


def test_get_url() -> None:
    assert (
        json.loads(get_url({"path": "/8f0fe3"})["body"])["Items"][0]["longUrl"]["S"]
        == "https://www.shreyasgaonkar.com/"
    )
    assert (
        json.loads(get_url({"path": "/me"})["body"])["Items"][0]["longUrl"]["S"]
        == "https://www.shreyasgaonkar.com/"
    )


def test_global_blacklist() -> None:
    assert update_blacklist(" ") is None
    assert update_blacklist("") is None


def test_check_valid_url() -> None:
    assert check_valid_url("https://www.shreyasgaonkar.com/") is True
