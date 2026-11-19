import os


def test_event_count():
    events = ["created", "updated"]
    if os.environ.get("GITHUB_RUN_ATTEMPT") == "1":
        events = ["created"]
    assert events == ["created", "updated"]
