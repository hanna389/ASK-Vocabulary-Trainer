import json
from progress import process_progress

class QuizManager:
    def __init__(self, dictionary_obj):
        self.dictionary = dictionary_obj
        self.queue = []
        self.direction = "Іноземна -> Переклад"
        self.asked_count = 0
        self.correct_count = 0
        self.incorrect_list = []
        self.correct_list = []
        self.current_item = None
        self.correct_words_history = []
        self.user_answers_history = []

    def prepare_queue(self, pos_filter, count):
        df = self.dictionary.df
        if df.empty:
            return "Словник порожній!", False
        try:
            subset = df if pos_filter == "Всі" else df[df["pos"] == pos_filter]
            if subset.empty:
                return f"Немає слів для частини мови «{pos_filter}».", False
            sample_n = min(len(subset), int(count))
            self.queue = subset.sample(n=sample_n).to_dict("records")
            return "", True
        except Exception as e:
            return f"Помилка вибірки: {e}", False

    def start_quiz(self, pos_filter, count, direction):
        err, success = self.prepare_queue(pos_filter, count)
        if not success:
            return err, False
        self.direction = direction
        self.asked_count = 0
        self.correct_count = 0
        self.incorrect_list = []
        self.correct_list = []
        self.current_item = None
        self.correct_words_history = []
        self.user_answers_history = []
        return "", True

    def next_question(self):
        if not self.queue:
            return None, "Квіз завершено"
        self.current_item = self.queue.pop(0)
        if self.direction == "Іноземна -> Переклад":
            prompt =  f"Перекладіть: **{self.current_item['word']}**"
        else:
            prompt = f"Перекладіть: **{self.current_item['translation']}**"
        return prompt

    def evaluate_answer(self, user_answer):
        if not self.current_item:
            return "Немає активного питання.", ""
        self.asked_count +=1
        correct_ans = self.current_item["translation"] if self.direction == "Іноземна -> Переклад" else self.current_item["word"]
        self.correct_words_history.append(correct_ans)
        self.user_answers_history.append(user_answer)
        is_correct = (user_answer.strip().lower() == correct_ans.lower())
        self.dictionary.update_success(self.current_item["word"], is_correct)
        if is_correct:
            self.correct_count += 1
            self.correct_list.append(self.current_item["word"])
            is_correct = (user_answer.strip().lower() == correct_ans.lower())
            msg = "Правильно!"
        else:
            self.incorrect_list.append((self.current_item["word"], correct_ans))
            self.user_answers_history.append(user_answer)
            msg = f"Помилка. Правильна відповідь: {correct_ans}"
        return msg, correct_ans

    def finish_quiz(self, filepath="quiz_data.json"):
        data = {    
            "correct_words": self.correct_words_history,
            "user_answers": self.user_answers_history
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return process_progress(filepath)