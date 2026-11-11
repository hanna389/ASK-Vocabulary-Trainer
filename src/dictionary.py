import os
import pandas as pd
import spacy


DATA_FILE = "vocabulary.csv"
EXPECTED_COLS = ["word", "translation", "pos", "success"]

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None


def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        for col in EXPECTED_COLS:
            if col not in df.columns:
                df[col] = "NOUN" if col == "pos" else 50.0
        return df
    return pd.DataFrame(columns=EXPECTED_COLS)

def detect_pos(word):
    if not nlp:
        return "UNKNOWN"
    doc = nlp(word)
    if len(doc) > 0:
        return doc[0].pos_
    return "UNKNOWN"


class DictionaryManager:
    def __init__(self):
        self.df = load_data()

    def reload(self):
        self.df = load_data()
        return self.df

    def save_data(self, df):
        df.to_csv(DATA_FILE, index=False, encoding="utf-8")

    def check_exists(self, word):
        if self.df.empty:
            return False
        return (self.df["word"] == word.strip().lower()).any()

    def _is_number(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def add_word(self, word, translation):
        if not word.strip() or not translation.strip():
            return "Поля не можуть бути порожніми", self.df

        w = word.strip().lower()
        t = translation.strip().lower()

        if self._is_number(w) or self._is_number(t):
            return "Слово або переклад не можуть бути числом", self.df

        if self.check_exists(w):
            return f"Слово «{w}» вже є у словнику", self.df
            
        pos_tag = detect_pos(w)

        new_row = pd.DataFrame([{
            "word": w,
            "translation": t,
            "pos": pos_tag,
            "success": 50.0
        }])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.save_data(self.df)
        return f"Слово «{w}» додано (Частина мови: {pos_tag})", self.df
        

    def update_success(self, word, is_correct):
        idx = self.df[self.df["word"] == word].index
        if not idx.empty:
            i = idx[0]
        current = float(self.df.loc[i, "success"])
        if is_correct:
            self.df.loc[i, "success"] = min(100.0, current + 15.0)
        else:
            self.df.loc[i, "success"] = max(0.0, current - 15.0)