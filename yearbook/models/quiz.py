from pydantic import BaseModel


class Quiz(BaseModel):
    name: str
    desc: str
    questions: list[str]
