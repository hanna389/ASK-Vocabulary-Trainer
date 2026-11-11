import os
import sys
import gradio as gr
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_path = os.path.join(parent_dir, 'src')
sys.path.append(src_path)

from dictionary import DictionaryManager
from quiz import QuizManager

dict_manager = DictionaryManager()
quiz_manager = QuizManager(dict_manager)

with gr.Blocks(title="Тренажер лексики") as demo:
    gr.Markdown("# 🧠 Тренажер лексики")

    with gr.Column(visible=True) as menu_col:
        gr.Markdown("### Головне меню")
        btn_to_add = gr.Button("➕ Додати слово", variant="primary")
        btn_to_dict = gr.Button("📖 Словник")
        btn_to_quiz = gr.Button("🎯 Квіз", variant="primary")

    with gr.Column(visible=False) as add_col:
        gr.Markdown("## Додавання нового слова")
        word_input = gr.Textbox(label="Іноземне слово", placeholder="Наприклад: apple")
        translation_input = gr.Textbox(label="Переклад", placeholder="Наприклад: яблуко")
        with gr.Row():
            add_save_btn = gr.Button("Зберегти слово", variant="primary")
            back_from_add = gr.Button("⬅️ Назад до меню")
        add_status = gr.Markdown()

    with gr.Column(visible=False) as dict_col:
        gr.Markdown("## Ваш словник")
        vocab_table = gr.Dataframe(value=dict_manager.df, interactive=False)
        with gr.Row():
            export_btn = gr.DownloadButton("💾 Завантажити словник", value="vocabulary.csv", variant="primary")
        back_from_dict = gr.Button("⬅️ Назад до меню")
        export_status = gr.Markdown()

    with gr.Column(visible=False) as quiz_setup_col:
        gr.Markdown("## Налаштування квізу")
        quiz_count_input = gr.Number(value=5, label="Скільки слів ви хочете перевірити?", precision=0)
        with gr.Row():
            start_game_btn = gr.Button("🚀 Почати квіз", variant="primary")
            back_from_setup = gr.Button("⬅️ Назад до меню")

    with gr.Column(visible=False) as quiz_game_col:
        gr.Markdown("## Тренажер (Квіз)")
        quiz_prompt_box = gr.Markdown()
        user_quiz_answer = gr.Textbox(label="Введіть ваш варіант перекладу: ")
        with gr.Row():
            submit_quiz_ans_btn = gr.Button("Відповісти", variant="primary")
            skip_word_btn = gr.Button("⏭️ Пропустити слово")
            finish_quiz_btn = gr.Button("🛑 Завершити квіз", variant="stop")

    with gr.Column(visible=False) as quiz_results_col:
        gr.Markdown("## Підсумки квізу")
        results_highlight_output = gr.HighlightedText(
            label="Аналіз відповідей",
            combine_adjacent=False,
            color_map={"Правильно": "green", "Помилка": "red"}
        )
        with gr.Row():
            restart_quiz_btn = gr.Button("🔄 Почати знову", variant="primary")
            back_to_menu_res = gr.Button("🏠 Назад до меню")

    screens = [menu_col, add_col, dict_col, quiz_setup_col, quiz_game_col, quiz_results_col]

    def switch(active_idx):
        return [gr.update(visible=(i == active_idx)) for i in range(len(screens))]

    # --- НАВІГАЦІЯ ---
    btn_to_add.click(fn=lambda: switch(1), outputs=screens)
    btn_to_dict.click(fn=lambda: (dict_manager.reload(), *switch(2)), outputs=[vocab_table, *screens])
    btn_to_quiz.click(fn=lambda: switch(3), outputs=screens)

    for btn in [back_from_add, back_from_dict, back_from_setup, back_to_menu_res]:
        btn.click(fn=lambda: switch(0), outputs=screens)

    restart_quiz_btn.click(fn=lambda: switch(3), outputs=screens)

    # --- ДОДАВАННЯ СЛОВА ---
    def handle_add(w, t):
        msg, df = dict_manager.add_word(w, t)
        return msg, df, "", ""

    add_save_btn.click(
        fn=handle_add,
        inputs=[word_input, translation_input],
        outputs=[add_status, vocab_table, word_input, translation_input]
    )

    # --- ЕКСПОРТ СЛОВНИКА ---
    def handle_export():
        dict_manager.save_data(dict_manager.df)
        return "✅ Словник успішно збережено!"

    export_btn.click(
        fn=handle_export,
        outputs=[export_status]
    )

    # --- ЛОГІКА КВІЗУ ---
    def start_q(count):
        err, success = quiz_manager.start_quiz(pos_filter="Всі", count=int(count), direction="Іноземна -> Переклад")
        if not success:
            return err, *switch(3) 
        question_text = quiz_manager.next_question()
        
        if isinstance(question_text, tuple):
            question_text = question_text[0]
            
        return question_text, *switch(4)

    start_game_btn.click(
        fn=start_q,
        inputs=[quiz_count_input],
        outputs=[quiz_prompt_box, *screens]
    )

    def process_ans(ans):
        if not quiz_manager.current_item:
            return "Немає активного питання.", "", *switch(4)
        
        quiz_manager.evaluate_answer(ans)
        
        if quiz_manager.queue:
            return quiz_manager.next_question(), "", *switch(4)
        else:
            results, err = quiz_manager.finish_quiz()
            return "", get_highlighted_res(), *switch(5)

    def process_skip():
        if quiz_manager.current_item:
            correct_ans = quiz_manager.current_item["translation"]
            quiz_manager.incorrect_list.append((quiz_manager.current_item["word"], correct_ans))
            quiz_manager.correct_words_history.append(correct_ans)
            quiz_manager.user_answers_history.append("")
            quiz_manager.asked_count += 1
            quiz_manager.dictionary.update_success(quiz_manager.current_item["word"], False)
            
        if quiz_manager.queue:
            return quiz_manager.next_question(), "", *switch(4)
        else:
            results, err = quiz_manager.finish_quiz()
            return "", get_highlighted_res(), *switch(5)

    def process_finish():
        results, err = quiz_manager.finish_quiz()
        return "", get_highlighted_res(), *switch(5)

    def get_highlighted_res():
        data = []
        for w in quiz_manager.correct_list:
            data.append((f"{w} ", "Правильно"))
        for item in quiz_manager.incorrect_list:
            if isinstance(item, tuple):
                w, c_ans = item
                data.append((f"{w} (прав: {c_ans}) ", "Помилка"))         
        return data

    submit_quiz_ans_btn.click(
        fn=process_ans,
        inputs=[user_quiz_answer],
        outputs=[quiz_prompt_box, results_highlight_output, *screens]
    )

    skip_word_btn.click(
        fn=process_skip,
        outputs=[quiz_prompt_box, results_highlight_output, *screens]
    )

    finish_quiz_btn.click(
        fn=process_finish,
        outputs=[quiz_prompt_box, results_highlight_output, *screens]
    )

custom_css = """
.gradio-container {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%) !important;
}
button.primary {
    background: #111111 !important;
    border: 1px solid #111111 !important;
    color: white !important;
    border-radius: 8px !important;
}
button.primary:hover {
    background: #333333 !important;
}
button.stop {
    background: #d9534f !important;
    border: 1px solid #d9534f !important;
    color: white !important;
    border-radius: 8px !important;
}
button.stop:hover {
    background: #c9302c !important;
}
"""

if __name__ == "__main__":
    demo.launch(css=custom_css, debug=True)