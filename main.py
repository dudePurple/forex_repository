from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from chatgpt_helper import get_answer as chatgpt_answer
from settings import DEFAULT_ANSWER
from supporter import Supporter

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def generate_answer(question: str):
    supporter = Supporter(question, faqs_filename='FAQ_cleaned.json')
    answer = supporter.find_answer()
    if answer == Supporter.NOT_FOUND:
        answer = chatgpt_answer(question)

    return answer


@app.get("/")
def read_root(request: Request, answer: str = None):
    return templates.TemplateResponse("index.html", {"request": request, "answer": answer})


@app.post("/")
def get_answer(request: Request, message: str = Form(None)):
    if not message:
        answer = DEFAULT_ANSWER
    else:
        answer = generate_answer(message)
    return read_root(request, answer)
