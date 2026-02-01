import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from deep_translator import GoogleTranslator
from gtts import gTTS
import uuid
from app.config import MODEL_NAME, FAQ

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype="auto"
)

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

def get_crop_advice(crop: str, question: str, language: str) -> str:
    # Translate question to English
    if language != "en":
        question_en = GoogleTranslator(source=language, target="en").translate(question)
    else:
        question_en = question

    # Check FAQ fallback
    for key, answer in FAQ.items():
        if key in question_en.lower():
            return answer if language == "en" else GoogleTranslator(source="en", target=language).translate(answer)

    # Prompt engineering
    prompt = (
        f"You are an agricultural expert. "
        f"A farmer growing {crop} asks: {question_en}. "
        f"Provide clear, practical farming advice only. "
        f"Do not mention economics, incomes, or statistics."
    )

    try:
        result = generator(prompt, max_length=200, num_return_sequences=1, temperature=0.7, do_sample=True)
        answer_en = result[0]["generated_text"].replace(prompt, "").strip()
    except Exception as e:
        answer_en = f"Error generating advice: {str(e)}"

    # Sanitize nonsense
    if not answer_en or "farmer earns" in answer_en.lower():
        answer_en = "Please monitor soil moisture and provide irrigation or fertilizer only when necessary. Avoid irrelevant details."

    # Translate back
    if language != "en":
        return GoogleTranslator(source="en", target=language).translate(answer_en)
    return answer_en

def generate_tts(answer: str, language: str) -> str:
    if not answer.strip():
        answer = "No advice available."

    lang_map = {"en": "en", "ar": "ar", "ko": "ko", "bn": "bn"}
    tts = gTTS(text=answer, lang=lang_map.get(language, "en"))

    os.makedirs("app/static", exist_ok=True)
    filename = f"app/static/answer_{uuid.uuid4().hex}.mp3"
    tts.save(filename)

    return "/static/" + os.path.basename(filename)
#