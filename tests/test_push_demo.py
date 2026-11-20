from demo.words import word_count


def test_word_count():
    assert word_count("one two three") == 3
