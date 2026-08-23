from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage as LangAIMessage
from django.conf import settings

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",  # Gemini 3.1 Flash-Lite Preview
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.7,
        max_tokens=1024,
    )


def build_system_prompt(lesson=None):
    base = """Ты — дружелюбный ИИ-ассистент курса PythonOku. 
Ты помогаешь ученикам изучать Python на русском языке.
Отвечай чётко, с примерами кода. Если ученик ошибается — поправь мягко.
Код всегда оборачивай в ```python ... ```.
Не отвечай на вопросы не связанные с программированием и Python."""

    if lesson:
        base += f"""

Сейчас ученик проходит урок: «{lesson.title}»
Описание урока: {lesson.description or 'нет описания'}
Содержание урока: {lesson.content[:1500] if lesson.content else 'нет содержания'}

Отвечай в контексте этого урока. Если вопрос выходит за рамки — можешь ответить, 
но напомни что сейчас они изучают: «{lesson.title}»."""

    return base


def chat_with_ai(user_message: str, history: list, lesson=None) -> str:
    llm = get_llm()

    messages = [SystemMessage(content=build_system_prompt(lesson))]

    for msg in history:
        if msg.role == 'user':
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(LangAIMessage(content=msg.content))

    messages.append(HumanMessage(content=user_message))

    response = llm.invoke(messages)

    # Извлекаем текст — content может быть строкой или списком блоков
    if isinstance(response.content, str):
        return response.content
    elif isinstance(response.content, list):
        return "".join(
            block.get("text", "")
            for block in response.content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(response.content)