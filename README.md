# ANOTAR: Automated Note-taking and Organization with Text Analysis and Retrieval

ANOTAR represents a sophisticated computational framework designed to revolutionize the way users synthesize and organize information from diverse input formats, such as images and PDF documents. By combining advanced text extraction, summarization, and organization capabilities, ANOTAR caters to researchers, professionals, and academics who seek efficient methods for distilling and managing critical information.

## Features

- **Input Versatility**: Accepts both image and PDF file formats, ensuring broad applicability across use cases.
- **Advanced OCR (Optical Character Recognition)**: Utilizes state-of-the-art language models to extract textual data accurately from scanned or handwritten inputs, converting them into machine-readable formats.
- **Comprehensive PDF Parsing**: Analyzes PDF structures to systematically retrieve and format embedded textual content, including complex layouts.
- **Structured Output**: Generates well-organized notes, including summaries, bullet points, and tagged sections, optimized for easy review and application.

## Installation

To install and use ANOTAR, follow the steps below:

### Prerequisites

1. Python (version 3.9 or higher).
2. [pip](https://pip.pypa.io/en/stable/) for package management.
3. (**Optional**) Virtual environment tools like [venv](https://docs.python.org/3/library/venv.html) or [conda](https://docs.conda.io/).

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

    > **Note**: To enable GPU acceleration for OCR, install [torch with CUDA](https://pytorch.org/get-started/locally/) before installing `easyocr`.

   ```bash
   pip install -r requirements.txt
   ```

4. Copy the `.env.example` file to `.env`:

   ```bash
   cp .env.example .env # On Windows: copy .env.example .env
   ```

### Troubleshooting

- **Dependency Errors**: Ensure you are using the correct Python version and have installed all dependencies listed in `requirements.txt`.
- **Environment Issues**: Activate the virtual environment before running commands.
- **GPU Setup**: If GPU acceleration is not working, verify your CUDA installation and PyTorch configuration.

## Usage

1. Launch the application from the root directory:
   ```bash
   streamlit run main.py
   ```

2. Open the application in your browser at [http://localhost:8501](http://localhost:8501).

3. Configure settings:
   - Add API keys for desired providers via the settings page.
   - Set the path to your Obsidian vault directory.
     > **Note**: Obsidian is preferred due to its native markdown support, but it is not required. The default path is: `<user_name>/Documents/ANOTAR`.

4. Begin processing files:
   - Upload an image or PDF.
   - Review and export the generated notes.

### Example Workflow

1. Upload a scanned research paper as a PDF.
2. ANOTAR extracts and summarizes the text, organizing key points with headings, tables, and equations.
3. Explore the notes directly in your Obsidian vault or the built-in file viewer for further review.

## Project Structure

- **`main.py`**: The primary Streamlit execution script.
- **`pages/`**: Contains the Streamlit pages for the user interface.
- **`utils/`**: Houses core functionalities, including OCR, PDF parsing, and note synthesis.
- **`requirements.txt`**: Lists all dependencies required for execution.

## Contributing

We welcome contributions from the community! To get involved:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of feature"
   ```
4. Push the branch to your forked repository:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request for review.

## License

This project is licensed under the MIT License. For more details, see the [LICENSE](LICENSE) file.

## Prospective Enhancements

- **Multilingual OCR Support**: Expand OCR capabilities to support multiple languages for global accessibility.
- **Interactive Note Editing**: Develop a user-friendly interface for refining generated notes.
- **Cloud Storage Integration**: Enable seamless file management with cloud services like Google Drive and Dropbox.
- **AI-Powered Insights**: Add features for contextual analysis and tagging of extracted information.

## Contact

For further inquiries, suggestions, or collaboration opportunities, contact us via [email](mailto:logxdx158@gmail.com?subject=[ANOTAR]). Additionally, join the discussion on [GitHub Discussions](https://github.com/logxdx/ANOTAR/discussions).

---

**ANOTAR: Transforming the way you synthesize and organize information.**

