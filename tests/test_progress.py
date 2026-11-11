import json
import pytest
from progress import process_progress

def test_process_progress_success(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    test_file = d / "quiz_data.json"
    
    test_data = {
        "correct_words": ["apple", "dog", "house"],
        "user_answers": ["apple", "cat", "house"]
    }
    test_file.write_text(json.dumps(test_data, ensure_ascii=False), encoding="utf-8")

    results, err = process_progress(str(test_file))

    assert err == ""
    assert results is not None
    assert results["score"] == 2
    assert results["total_words"] == 3
    assert results["percentage"] == 66.67
    assert results["correct_list"] == ["apple", "house"]
    assert len(results["incorrect_list"]) == 1
    assert results["incorrect_list"][0] == ("dog", "cat")


def test_process_progress_empty(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    test_file = d / "quiz_data.json"
    
    test_data = {
        "correct_words": [],
        "user_answers": []
    }
    test_file.write_text(json.dumps(test_data, ensure_ascii=False), encoding="utf-8")

    results, err = process_progress(str(test_file))

    assert results is None
    assert "Список слів у квізі порожній" in err


def test_process_progress_file_not_found():
    results, err = process_progress("non_existent_file_123.json")

    assert results is None
    assert "Помилка: Файл з даними квізу не знайдено" in err