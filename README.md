# ANOTAR: Automated Note-taking and Organization with Text Analysis and Retrieval

ANOTAR represents a sophisticated computational framework designed to facilitate the automated synthesis of notes from diverse input formats, including images and PDF documents. By leveraging advanced text extraction and summarization techniques, this tool caters to the needs of researchers, professionals, and academics seeking efficient methods for information distillation and organization.

## Features

- **Input Versatility**: Capable of ingesting both image and PDF file formats, ensuring adaptability to a wide range of use cases.
- **Advanced OCR (Optical Character Recognition)**: Employs state-of-the-art LLMs to accurately extract textual data from scanned or handwritten inputs, rendering them machine-readable.
- **Comprehensive PDF Parsing**: Analyzes PDF structures to systematically retrieve and format embedded textual content.
- **Structured Output**: Produces well-organized notes optimized for review and further application.

## Installation

To install & use ANOTAR, adhere to the following setup instructions:

### Prerequisites

1. Python (version 3.9 or higher).
2. [pip](https://pip.pypa.io/en/stable/) for package management.
3. (***Optional***) Virtual environment management tools such as [venv](https://docs.python.org/3/library/venv.html) or [conda](https://docs.conda.io/).

### Installation Procedure

1. Clone the repository:
   ```bash
   git clone https://github.com/logxdx/ANOTAR.git
   cd ANOTAR
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
    
    > ***Note***: To use gpu acceleration for ocr, please install [torch with cuda](https://pytorch.org/get-started/locally/) before installing easyocr

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Execute from the root directory:
   ```bash
   streamlit run main.py
   ```

2. Access the application at http://localhost:8501

3. Navigate to the settings page, and add the API keys of the providers you want to use.

4. Set the path to your vault directory.
> **Note**: The default path is: `<user_name>/Documents/ANOTAR`

## Project Structure

- **`main.py`**: Serves as the primary streamlit execution script.
- **`pages/`**: Contains the Streamlit pages for user interface.
- **`utils/`**: Encapsulates core functionalities, including OCR, PDF parsing, and note synthesis.
- **`requirements.txt`**: Enumerates the dependencies necessary for execution.

## Contributing

Engagement from the community is encouraged. To contribute:

1. Fork the repository.
2. Establish a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your modifications:
   ```bash
   git commit -m "Description of feature"
   ```
4. Push the branch to your repository:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request for review.

## License

This project is distributed under the MIT License. Refer to the [LICENSE](LICENSE) file for detailed information.

## Prospective Enhancements

- Expansion of OCR support to include multiple languages.
- Development of an interactive note-editing interface.
- Cloud storage integration for seamless file management.

## Contact

For further inquiries, suggestions, or collaboration opportunities, please reach out via [mail](mailto:logxdx158@gmail.com?subject=[ANOTAR]).

---

ANOTAR: Transforming the way you synthesize and organize information.

