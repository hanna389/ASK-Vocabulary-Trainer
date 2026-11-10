import os
import pandas as pd
import spacy


data_file = "vocabulary.csv"
expected_cols = ["word", "translation", "pos", "success"]

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None


def load_data():
    try:
        if os.path.exists(data_file):
            df = pd.read_csv(data_file)
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = "NOUN" if col == "pos" else 50.0
            return df
    except Exception as e:
            print(f"Помилка читання файлу: {e}")
    return pd.DataFrame(columns=expected_cols)


def save_data(df):
     try:
          df.to_csv(data_file, index=False, encodind="utf-8")
          return True
     except Exception as e:
          print(f"Помилка збереження файлу: {e}")
          return False


def detect_pos(word):
    if not nlp:
        return "UNKNOWN"
    try:
        doc = nlp(word)
        if len(doc) > 0:
            return doc[0].pos_
    except Exception:
        pass
    return "UNKNOWN"


class DictionaryManager:
    def __init__(self):
        self.df = load_data()

    def reload(self):
        self.df = load_data()
        return self.df
    
    def check_exists(self, word):
        if self.df.empty:
            return False
        return (self.df["word"] == word.srtip().lower().any())

    def add_word(self, word, translation):
        try:
            if not word.strip() or not translation.strip():
                return "Поля не можуть бути порожніми", self.df

            w = word.strip().lower()
            t = translation.strip().lower()

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
            save_data(self.df)
            return f"Слово «{w}» додано (Частина мови: {pos_tag})!", self.df
        except Exception as e:
            return f"Помилка додавання: {e}", self.df

    def update_success(self, word, is_correct):
        try:
            idx = self.df[self.df["word"] == word].index
            if not idx.empty:
                i = idx[0]
            current = float(self.df.loc[i, "success"])
            if is_correct:
                self.df.loc[i, "success"] = min(100.0, current + 15.0)
            else:
                self.df.loc[i, "success"] = max(0.0, current - 15.0)
        except Exception as e:
            print(f"Помилка оновлення успіху: {e}")           