import json

def process_progress(filepath="quiz_data.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        correct_words = data.get("correct_words", [])
        user_answers = data.get("user_answers", [])

        total_words = len(correct_words)

        if total_words == 0:
            return None, "Список слів у квізі порожній."

        score = 0
        incorrect_list = []
        correct_list = []

        for correct, user in zip(correct_words, user_answers):
            if str(correct).strip().lower() == str(user).strip().lower():
                score += 1
                correct_list.append(correct)
            else:
                incorrect_list.append((correct, user))

        percentage = round((score / total_words) * 100, 2)

        results = {
            "score": score,
            "total_words": total_words,
            "percentage": percentage,
            "correct_list": correct_list,
            "incorrect_list": incorrect_list
        }

        with open("quiz_results.json", "w", encoding="utf-8") as out_f:
            json.dump(results, out_f, ensure_ascii=False, indent=2)

        return results, ""

    except FileNotFoundError:
        return None, "Помилка: Файл з даними квізу не знайдено. Перевірте назву й шлях до файлу."
    except Exception as e: 
        return None, f"Сталася непередбачувана помилка: {e}"