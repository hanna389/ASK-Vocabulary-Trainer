import os
import pytest
import pandas as pd
from dictionary import DictionaryManager, DATA_FILE

def clear_file():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)


def test_add_empty_fields():
    clear_file()
    mgr = DictionaryManager()
    msg, df = mgr.add_word("   ", "   ")
    assert "не можуть бути порожніми" in msg
    assert len(df) == 0
    clear_file()

def test_add_number_validation():
    clear_file()
    mgr = DictionaryManager()
    msg1, df1 = mgr.add_word("12345", "кіт")
    assert "не можуть бути числом" in msg1
    assert len(df1) == 0

    msg2, df2 = mgr.add_word("dog", "99.9")
    assert "не можуть бути числом" in msg2
    assert len(df2) == 0
    clear_file()

def test_add_duplicate_word():
    clear_file()
    mgr = DictionaryManager()
    mgr.add_word("cat", "кіт")
    msg, df = mgr.add_word("cat", "кіт")
    assert "вже є у словнику" in msg
    assert len(df) == 1
    clear_file()