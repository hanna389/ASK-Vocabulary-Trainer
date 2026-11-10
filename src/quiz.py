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
        return "", True

    def next_question(self):
        if not self.queue:
            return None, "Квіз завершено"
        self.current_item = self.queue.pop(0)
        if self.direction == "Іноземна -> Переклад":
           promt =  f"Перекладіть: **{self.current_item['word']}**"
        else:
            prompt = f"Перекладіть: **{self.current_item['translation']}**"
        return prompt, ""

    def evaluate_answer(self, user_answer):
        if not self.current_item:
            return "Немає активного питання.", ""
        self.asked_count +=1
        correct_ans = self.current_item["translation"] if self.direction == "Іноземна -> Переклад" else self.current_item["word"]
        is_correct = (user_answer.strip().lower() == correct_ans.lower())
        self.dictionary.update_success(self.current_item["word"], is_correct)
        if is_correct:
            self.correct_count += 1
            self.correct_list.append(self.current_item["word"])
            msg = "Правильно!"
        else:
            self.incorrect_list.append((self.current_item["word"], correct_ans))
            msg = f"Помилка. Правильна відповідь: {correct_ans}"
        return msg, correct_ans

    def get_summary(self):
        percent = (self.correct_count / self.asked_count * 100) if self.asked_count > 0 else 0.0
        summary = (
            f"### Результати квізу\n"
            f"- Загалом запитань: {self.asked_count}\n"
            f"- Правильних відповідей: {self.correct_count} ({percent:.1f}%)\n"
        )
        if self.correct_list:
            summary += f"- Правильно відгадані: {', '.join(self.correct_list)}\n"
        if self.incorrect_list:
            incorrect_str = ". ".join([f"{w} ({tr})" for w, tr in self.incorrect_list])
            summary += f"- Неправильні відповіді: {incorrect_str}\n"
        return summary