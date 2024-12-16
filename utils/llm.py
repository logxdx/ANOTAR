import json, base64, os
import ollama
import google.generativeai as genai
from openai import OpenAI
from mistralai import Mistral
from groq import Groq
from utils.cypher.key import get_api_key
from dotenv import load_dotenv
from PIL import Image

config = json.load(open("config.json"))
PROVIDER_KEYS = config["PROVIDER_KEYS"]
MODEL_PROVIDER_MAPPING = config["MODEL_PROVIDER_MAPPING"]

ENV_FILE = config["ENV_FILE"]
load_dotenv(ENV_FILE, override=True)

GENERATE_NOTES_SYSTEM_PROMPT = f"""You are a great note taker. Take concise and well-organized notes from the uploaded images or text. Focus on clarity and conciseness, without additional commentary. Capture key information directly, using the following structure:
    Title: Use a relevant and descriptive title.
    Summary: Provide a brief overview summarizing the main points. Hightlight important terms with ==highlight==, **bold**, *italics*, ***Bold & Italic.
    Detailed Notes: Write detailed, structured notes covering all essential details.
    Tables: Reproduce tables with their original information, retaining formatting.
    Equations: Format all equations in LaTeX, ensuring inline LaTeX expressions are within $...$ and all block equations within $$...$$.
    Solution: If the content includes questions, give the formulas required to solve the questions and answer them in brief stating the solution.
    Theory: Provide a brief theory overview for concepts involved.
    If there is no content for a particular heading, skip that heading. Use Markdown Syntax but DO NOT USE the markdown codeblock.
    """

FORMAT_NOTES_SYSTEM_PROMPT = f"""Review the provided text and ensure it is structured correctly in Markdown format, including any embedded LaTeX. Follow these guidelines:
    1. Markdown Structure: Verify that headings, lists, code blocks, and other Markdown elements follow the correct syntax and hierarchy. Ensure proper spacing and indentation, particularly in nested lists, tables, and code blocks. Confirm that all links, images, and other Markdown references are correctly formatted. Do not use ```markdown ``` code block for markdown.
    2. LaTeX Equations: Check each LaTeX expression to ensure it is syntactically correct, fixing any errors in commands, symbols, or structures. If any LaTeX syntax is misplaced or missing (such as $ or $$ for inline or block math), adjust accordingly. Ensure that all inline LaTeX expressions are within $...$ and all block equations within $$...$$.
    3. Corrective Changes: Make suitable corrections to any Markdown or LaTeX syntax that doesn't comply with standard formatting. After completing these checks and corrections, output only the revised Markdown text without additional commentary."""


def get_providers():
    providers = []
    for provider, keys in PROVIDER_KEYS.items():
        use_provider = True
        for key in keys:
            if not get_api_key(key):
                use_provider = False
                break
        if use_provider:
            providers.append(provider)
    return providers

def get_models(providers: [str]):
    generation_models, formatting_models = [], []

    for provider in providers:
        for model, model_type in MODEL_PROVIDER_MAPPING[provider].items():
            if model_type == "multimodal":
                generation_models.append(model)
                formatting_models.append(model)
            else:
                formatting_models.append(model)

    return generation_models, formatting_models

def get_model_provider(model_name):
    for provider, models in MODEL_PROVIDER_MAPPING.items():
        for model in models:
            if model_name == model:
                return provider
    raise UnRegisteredModelError(model_name)

class UnRegisteredModelError(Exception):
    def __init__(self, model_name):
        super().__init__(f"Model '{model_name}' is not registered in config.json")

class MissingAPIKeyError(Exception):
    def __init__(self, provider):
        super().__init__(f"API key for provider '{provider}' is missing or not configured correctly")

def get_provider_api_key(provider_name, key_name):
    api_key = get_api_key(key_name)
    if not api_key:
        raise MissingAPIKeyError(provider_name)
    return api_key

def get_image_data_url(image_file: str, image_format: str) -> str:
    try:
        with open(image_file, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        raise FileNotFoundError
    except Exception as e:
        print(f"{e}. \nCould not read '{image_file}'.")
        return None
    return image_format, image_data


def generate_notes_with_ollama(file=None, image_path=None, ocr_info: str = "", model: str="llama3.2-vision", SYSTEM_PROMPT: str = GENERATE_NOTES_SYSTEM_PROMPT):
    message=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    if file:
        file = file + "\n" + ocr_info
        message.append(
            {
                "role": "user",
                "content": file,
            }
        )

    if image_path:
        image = [f"{get_image_data_url(image_path, 'png')[1]}"]
        message.append(
            {
                "role": "user",
                "content" : ocr_info,
                "images": image,
            }
        )

    options = {
        "temperature": 0.4,
        "num_ctx": 8192,
        "num_thread": 8,
    }

    response = ollama.chat(model = model, messages=message, options=options)
    return response.message.content

def generate_notes_with_gemini(file=None, image_path=None, ocr_info: str = "", model: str="gemini-1.5-flash-8b",  SYSTEM_PROMPT: str = GENERATE_NOTES_SYSTEM_PROMPT):
    gemini_api_key = get_provider_api_key("Google Gemini", "GEMINI_API_KEY")
    
    message = []

    if image_path:
        image = Image.open(image_path)
        message.append(image)
        message.append("\n" + ocr_info)
    
    if file:
        file = file + "\n" + ocr_info
        message.append(file)

    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel(model_name=model, system_instruction=SYSTEM_PROMPT)
    response = model.generate_content(message, generation_config = {"temperature": 0.4, "max_output_tokens": 8192})
    return response.text

def generate_notes_with_gpt(file=None, image_path=None, ocr_info: str = "", model: str="gpt-4o", SYSTEM_PROMPT: str = GENERATE_NOTES_SYSTEM_PROMPT):
    openai_api_key = get_provider_api_key("OpenAI", "OPENAI_API_KEY")
    openai_endpoint = get_provider_api_key("OpenAI", "OPENAI_ENDPOINT")

    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]
    
    if file:
        file = file + "\n" + ocr_info
        messages.append(
            {
                "role": "user",
                "content": file,
            }
        )

    if image_path:
        image_format, image_data = get_image_data_url(image_path, "png")
        image = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/{image_format};base64,{image_data}",
                "detail": "auto"
            }
        }
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{ocr_info}"},
                    image,
                ]
            }
        )

    client = OpenAI(base_url=openai_endpoint, api_key=openai_api_key)
    response = client.chat.completions.create(messages=messages, model=model, temperature=0.4, max_tokens=8192)
    return response.choices[0].message.content

def generate_notes_with_mistralai(file=None, image_path=None, ocr_info: str = "", model: str="pixtral-12b-2409", SYSTEM_PROMPT: str = GENERATE_NOTES_SYSTEM_PROMPT):
    mistralai_api_key = get_provider_api_key("Mistral AI", "MISTRALAI_API_KEY")

    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]
    
    if file:
        file = file + "\n" + ocr_info
        messages.append(
            {
                "role": "user",
                "content": file,
            }
        )

    if image_path:
        image_format, image_data = get_image_data_url(image_path, "png")
        image = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/{image_format};base64,{image_data}",
                "detail": "auto"
            }
        }
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{ocr_info}"},
                    image,
                ]
            }
        )

    client = Mistral(api_key=mistralai_api_key)
    response = client.chat.complete(messages=messages, model=model, temperature=0.4, max_tokens=8192)
    return response.choices[0].message.content

def generate_notes_with_groq(file=None, image_path=None, ocr_info: str = "", model: str="mixtral-8x7b-32768", SYSTEM_PROMPT: str = GENERATE_NOTES_SYSTEM_PROMPT):
    groq_api_key = get_provider_api_key("Groq", "GROQ_API_KEY")

    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]
    
    if file:
        file = file + "\n" + ocr_info
        messages.append(
            {
                "role": "user",
                "content": file,
            }
        )

    if image_path:
        image_format, image_data = get_image_data_url(image_path, "png")
        image = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/{image_format};base64,{image_data}",
                "detail": "auto"
            }
        }
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{ocr_info}"},
                    image,
                ]
            }
        )

    client = Groq(api_key=groq_api_key)
    response = client.chat.completions.create(messages=messages, model=model, temperature=0.4, max_tokens=8192)
    return response.choices[0].message.content


def generate_notes(file=None, image_path=None, ocr_enhance_info: str = "", model: str="gemini-1.5-flash-8b"):
    results = None

    ocr_info = ""
    if len(ocr_enhance_info) > 0:
        info = "\n".join(ocr_enhance_info)
        ocr_info = f"""I'm sharing text extracted from image/pdf using OCR. This additional text can help verify or supplement the information in our discussion. Please review the extracted text for accuracy and reference it as needed: {info}"""

    provider = get_model_provider(model)
    print(f"Generating Notes using model: {model, provider}")

    if provider == "Google Gemini":
        results = generate_notes_with_gemini(file=file, image_path=image_path, ocr_info=ocr_info, model=model, SYSTEM_PROMPT=GENERATE_NOTES_SYSTEM_PROMPT)
    elif provider == "OpenAI":
        results = generate_notes_with_gpt(file=file, image_path=image_path, ocr_info=ocr_info, model=model, SYSTEM_PROMPT=GENERATE_NOTES_SYSTEM_PROMPT)
    elif provider == "Mistral AI":
        results = generate_notes_with_mistralai(file=file, image_path=image_path, ocr_info=ocr_info, model=model, SYSTEM_PROMPT=GENERATE_NOTES_SYSTEM_PROMPT)
    elif provider == "Groq":
        results = generate_notes_with_groq(file=file, image_path=image_path, ocr_info=ocr_info, model=model, SYSTEM_PROMPT=GENERATE_NOTES_SYSTEM_PROMPT)
    elif provider == "Ollama":
        results = generate_notes_with_ollama(file=file, image_path=image_path, ocr_info=ocr_info, model=model, SYSTEM_PROMPT=GENERATE_NOTES_SYSTEM_PROMPT)

    notes = ""
    for line in results:
        notes += line

    print("Notes generated successfully!")
    return notes

def format_notes(notes: str, model: str="gemini-1.5-flash-8b"):
    results = None

    provider = get_model_provider(model)
    print(f"Formatting Notes Structure using model: {model, provider}")

    if provider == "Google Gemini":
        results = generate_notes_with_gemini(file=notes, model=model, SYSTEM_PROMPT=FORMAT_NOTES_SYSTEM_PROMPT)
    elif provider == "OpenAI":
        results = generate_notes_with_gpt(file=notes, model=model, SYSTEM_PROMPT=FORMAT_NOTES_SYSTEM_PROMPT)
    elif provider == "Mistral AI":
        results = generate_notes_with_mistralai(file=notes, model=model, SYSTEM_PROMPT=FORMAT_NOTES_SYSTEM_PROMPT)
    elif provider == "Groq":
        results = generate_notes_with_groq(file=notes, model=model, SYSTEM_PROMPT=FORMAT_NOTES_SYSTEM_PROMPT)
    elif provider == "Ollama":
        results = generate_notes_with_ollama(file=notes, model=model, SYSTEM_PROMPT=FORMAT_NOTES_SYSTEM_PROMPT)
    
    notes = ""
    for line in results:
        notes += line

    print("Notes formatted successfully!")
    return notes
