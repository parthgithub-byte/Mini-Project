# Resume Gap Analyzer

## Abstract

Resume Gap Analyzer is a mini-project that helps users compare a resume against a target job role and generate a skill-gap report. The user can either paste resume text directly or upload a text-based PDF resume. The Flask backend extracts the resume text, combines it with either a predefined roadmap role or a custom target role, and uses Gemini through LangChain to produce a match score, strengths, matched skills, missing skills, and a personalized learning roadmap.

The project is intentionally split into a simple HTML/CSS frontend and a Python backend. This keeps the browser lightweight, avoids exposing the Gemini API key, and places all AI orchestration, validation, and PDF parsing on the server side.

## Tech Stack

| Technology | Used For | Reason |
| --- | --- | --- |
| Python | Backend programming language | Simple, readable, and well-supported for AI, PDF parsing, and web backend work. |
| Flask | Web server and routing | Lightweight framework that is easy to set up for mini-projects and server-rendered pages. |
| Jinja2 | HTML templating | Built into Flask and useful for rendering forms, errors, and AI results without frontend JavaScript. |
| HTML5 | Page structure and form inputs | Provides standard form submission, radio options, textarea input, and PDF upload support. |
| CSS3 | Styling and responsive UI | Keeps the frontend dependency-free while supporting responsive layouts and selected radio-card styling. |
| LangChain | AI orchestration | Provides a clean prompt-model-parser chain, making it easier to extend the AI workflow later. |
| Gemini | Resume analysis LLM | Generates the skill-gap analysis, match score, strengths, and roadmap recommendations. |
| langchain-google-genai | Gemini integration for LangChain | Connects LangChain with Google's Gemini models using the server-side API key. |
| pypdf | PDF text extraction | Parses text-based resume PDFs so users do not have to manually copy/paste resume content. |
| python-dotenv | Environment variable loading | Loads `GEMINI_API_KEY` from `.env` during local development. |

## Features

- Analyze resumes for predefined roles such as Frontend, Backend, DevOps, Data Science, Full Stack, and Android.
- Add a custom target role when the predefined options do not fit.
- Paste resume text manually or upload a text-based PDF resume.
- Generate match score, summary, strengths, matched skills, missing skills, and a learning roadmap.
- Keep Gemini API key on the backend only.
- Use plain HTML and CSS in the browser, with no React or frontend JavaScript.

## Data Science and AI Knowledge Used

This project uses applied data science and AI concepts to turn unstructured resume content into a structured skill-gap report.

- Natural language processing is used because resumes are free-form text, and the system needs to understand skills, experience, tools, projects, and evidence from written content.
- Prompt engineering is used to guide Gemini to compare the resume against a target role and return a consistent JSON response.
- Information extraction is used to identify matched skills, missing skills, evidence from the resume, and priority levels.
- Classification-style reasoning is used when the model groups missing skills into high, medium, and low priority.
- Recommendation logic is used when the model generates a personalized learning roadmap and suggests resources.
- PDF text extraction is used as a preprocessing step so uploaded resumes can be converted into text before AI analysis.
- Output normalization is used in the backend to keep the AI response consistent before rendering it in the UI.

## Web Development Knowledge Used

This project uses core web development concepts to build a clean server-rendered application with a lightweight frontend.

- Flask routing is used to handle `GET /` for the form page and `POST /analyze` for resume analysis.
- HTML forms are used for role selection, custom role input, resume text input, and PDF upload.
- Multipart form handling is used so the backend can receive uploaded PDF files.
- Jinja templating is used to render dynamic results, validation errors, selected roles, and AI-generated roadmap sections.
- CSS is used for responsive layout, cards, buttons, role selectors, result sections, and dark-mode-friendly colors.
- Backend validation is used to check resume length, custom role input, file type, file size, and missing API key configuration.
- Environment variables are used to keep the Gemini API key outside the browser and source code.
- Separation of concerns is followed by keeping backend logic in `app.py`, page markup in `templates/index.html`, and styling in `static/styles.css`.

## Setup

Open PowerShell in the project folder:

```powershell
cd "C:\Users\HP\Documents\New project"
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```env
GEMINI_API_KEY=your_api_key_here
```

Start the Flask app:

```powershell
python app.py
```

Open the app in your browser:

```text
http://127.0.0.1:5000
```

## Usage

1. Choose a predefined target role, or select `Custom role` and enter your own role title.
2. Paste resume text, upload a text-based PDF resume, or provide both.
3. Click `Analyze gaps`.
4. Review the match score, strengths, missing skills, and personalized roadmap.

If both pasted text and a PDF are provided, the uploaded PDF is analyzed.

## Project Structure

```text
.
+-- app.py
+-- requirements.txt
+-- templates/
|   +-- index.html
+-- static/
|   +-- styles.css
+-- .env.example
+-- README.md
```

## Notes

- PDF upload works best with text-based PDFs. Scanned image-only PDFs may not contain extractable text.
- The default Gemini model can be changed with `GEMINI_MODEL` in `.env`.
- The app is designed for local mini-project/demo use, not production deployment as-is.
