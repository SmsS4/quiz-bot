from yearbook import models


class QuizHandler:
    def __init__(self, quiz: models.quiz.Quiz):
        self.quiz = quiz
        self.answers: list[str] = []
        self.current_question = 0

    def next_question(self) -> str | None:
        if self.current_question == len(self.quiz.questions):
            return None
        self.current_question += 1
        return self.quiz.questions[self.current_question - 1]

    def new_message(self, answer: str) -> None:
        self.answers.append(answer)
