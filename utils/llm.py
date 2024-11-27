import ollama, base64, os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from openai import OpenAI
from io import BytesIO

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
github_api_key = os.getenv("GITHUB_API_KEY")
openai_endpoint = os.getenv("OPENAI_ENDPOINT")

SYSTEM_PROMPT = f"""You are a great note taker. Take concise and well-organized notes from the uploaded images or text. Focus on clarity and conciseness, without additional commentary. Capture key information directly, using the following structure:
    Title: Use a relevant and descriptive title.
    Summary: Provide a brief overview summarizing the main points.
    Detailed Notes: Write detailed, structured notes covering all essential details.
    Tables: Reproduce tables with their original information, retaining formatting.
    Equations: Format all equations in LaTeX, ensuring inline LaTeX expressions are within $...$ and all block equations within $$...$$.
    Solution: If the content includes questions, give the formulas required to solve the questions and answer them in brief stating the solution.
    Theory: Provide a brief theory overview for concepts involved.
    If there is nothing to write under a particular heading, skip them. Use Markdown Syntax.
    """


def get_image_data_url(image_file: str, image_format: str) -> str:
    """
    Helper function to convert an image file to a data URL string for OpenAI API.
    """
    try:
        with open(image_file, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Could not read '{image_file}'.")
        return None
    return f"data:image/{image_format};base64,{image_data}"


def generated_notes_from_images(file=None, image_path=None, ocr_enhance_info: list[str] = None, model: str="llama3.2-vision"):
    prompt = ""
    if ocr_enhance_info is not None:
        info = "\n".join(ocr_enhance_info)
        prompt = f"""
        Here are some text extracted from the image with OCR program, it might help you to check the information when you are not sure:
        {info}
        """

    print(f"Generating Notes using model: {model}")

    if model.startswith("ollama"):
        if file:
            prompt = file + "\n\n" + prompt
        message ={
                    "role": "user",
                    "content": prompt,
                }
        if image_path:
            image = Image.open(image_path)
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            message['images'] = [buffer]

        response = ollama.chat(model = model[7:], messages=[message])
        results = response['message']['content']

    elif model.startswith("gemini"):
        message = []
        if image_path:
            image = Image.open(image_path)
            message.append(image)
            message.append("\n\n")
        if file:
            message.append(file)
            message.append("\n\n")
        
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(model_name=model, system_instruction=prompt)
        response = model.generate_content(message)
        results = response.text

    elif model.startswith("gpt"):
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": [],
            }]
        if file:
            file = {
                "type": "text",
                "text": file
            }
            messages[1]["content"].append(file)
        if image_path:
            image_data_url = get_image_data_url(image_path, "png")
            image = {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data_url,
                        "detail": "auto"
                    }}
            messages[1]["content"].append(image)
        
        client = OpenAI(base_url=openai_endpoint, api_key=github_api_key)
        response = client.chat.completions.create(messages=messages, model=model, temperature=0.5, max_tokens=6000)
        results = response.choices[0].message.content

    notes = ""
    for line in results:
        notes += line
    return notes

def format_notes(notes: str, model: str="ollama-mistral"):
    prompt = f"""
    Review the provided text and ensure it is structured correctly in Markdown format, including any embedded LaTeX. Follow these guidelines:

    1. Markdown Structure:
    Verify that headings, lists, code blocks, and other Markdown elements follow the correct syntax and hierarchy.
    Ensure proper spacing and indentation, particularly in nested lists, tables, and code blocks.
    Confirm that all links, images, and other Markdown references are correctly formatted.
    Do not use '''markdown ''' code block for markdown.
    
    2. LaTeX Equations:
    Check each LaTeX expression to ensure it is syntactically correct, fixing any errors in commands, symbols, or structures.
    If any LaTeX syntax is misplaced or missing (such as $ or $$ for inline or block math), adjust accordingly.
    Ensure that all inline LaTeX expressions are within $...$ and all block equations within $$...$$.
    
    3. Corrective Changes:
    Make suitable corrections to any Markdown or LaTeX syntax that doesn't comply with standard formatting, Don't write the markdown in a code block.
    
    After completing these checks and corrections, output only the revised Markdown text without additional commentary.
    Here's the provided text: {notes}"""

    print(f"Formatting Notes Structure using model: {model}")

    if model.startswith("ollama"):
        message ={
                    "role": "user",
                    "content": prompt,
                }
        response = ollama.chat(
            model = model[7:],
            messages=[message]
            )
        results = response['message']['content']

    elif model.startswith("gemini"):
        message = [prompt]
        model = genai.GenerativeModel(model)
        response = model.generate_content(message)
        results = response.text

    elif model.startswith("gpt"):
        messages=[
            {
                "role": "user",
                "content": prompt
            }]        
        client = OpenAI(base_url=openai_endpoint, api_key=github_api_key)
        response = client.chat.completions.create(messages=messages, model=model, temperature=0.2, max_tokens=4096)
        results = response.choices[0].message.content
            
    notes = ""
    for line in results:
        notes += line
    yield notes

