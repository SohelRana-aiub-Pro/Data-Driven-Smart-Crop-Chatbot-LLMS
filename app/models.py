from pydantic import BaseModel


class Query(BaseModel):
    crop: str
    question: str
    language: str

class Response(BaseModel):
    answer: str
#