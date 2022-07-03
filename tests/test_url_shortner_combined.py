import json
import requests
import urllib3
import pytest
from urlshortner.url_shortner_combined import create_url, get_url, check_valid_url, update_blacklist, GLOBAL_BLACKLIST


def test_create_url() -> None:
    assert json.loads(create_url(
        {"headers": {"url": "https://www.shreyasgaonkar.com/"}})["body"]) == "https://trim.live/113490"


def test_get_url() -> None:
    assert json.loads(get_url({"path": "/113490"})
                      ["body"])["Items"][0]["longUrl"]["S"] == "https://www.shreyasgaonkar.com/"


def test_global_blacklist():
    assert update_blacklist(" ") == None
    assert update_blacklist("") == None


def test_check_valid_url():
    assert check_valid_url("https://www.shreyasgaonkar.com/") is True
