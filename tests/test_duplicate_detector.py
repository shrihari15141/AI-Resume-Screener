from services.duplicate_detector import text_similarity


def test_identical_resumes_have_high_similarity():
    text = "Rahul Kumar Python SQL Flask Machine Learning"

    assert text_similarity(text, text) == 100


def test_similar_resumes_cross_duplicate_threshold():
    original = "Rahul Kumar Python SQL Flask Machine Learning NLP project resume screening"
    updated = "Rahul Kumar Python SQL Flask Machine Learning NLP project resume screening Docker"

    assert text_similarity(original, updated) >= 88

