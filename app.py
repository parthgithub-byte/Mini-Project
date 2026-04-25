import json
import math
import os
import re
import sqlite3
from io import BytesIO
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()


app = Flask(__name__)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL", "gemini-3.1-flash-lite-preview"
)
GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001"
)
VECTOR_DB_PATH = Path(os.getenv("VECTOR_DB_PATH", "resume_vectors.sqlite3"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "6"))
ROADMAPS = {
    "frontend": {
        "label": "Frontend Developer",
        "icon": "FE",
        "skills": """INTERNET: How browsers work, HTTP/HTTPS, DNS, Hosting
HTML: Semantic HTML, Forms, Accessibility (ARIA), SEO basics
CSS: Flexbox, Grid, Responsive Design, Animations, Sass/SCSS, CSS Variables
JAVASCRIPT: DOM manipulation, ES6+, Fetch/AJAX, Async/Await, TypeScript, Modules
PACKAGE MANAGERS: npm, yarn, pnpm
BUILD TOOLS: Vite, Webpack, Babel, ESLint, Prettier
FRAMEWORKS: React (Hooks, Context, Redux), Vue.js, Angular, Next.js, Svelte
CSS FRAMEWORKS: Tailwind CSS, Bootstrap, Material UI, shadcn/ui
TESTING: Jest, Vitest, Cypress, Playwright, React Testing Library
PERFORMANCE: Core Web Vitals, Lazy Loading, Code Splitting, Lighthouse
VERSION CONTROL: Git, GitHub/GitLab, branching strategies
WEB SECURITY: CORS, CSP, XSS, CSRF prevention
PWA: Service Workers, Web Manifest, Offline support
APIs: REST, GraphQL (Apollo), WebSockets
DEPLOYMENT: Vercel, Netlify, CI/CD, Docker basics, GitHub Actions""",
    },
    "backend": {
        "label": "Backend Developer",
        "icon": "BE",
        "skills": """LANGUAGES: Node.js, Python, Java, Go, PHP, Ruby, C#
DATABASES: PostgreSQL, MySQL, MongoDB, Redis, SQLite
ORM/ODM: Prisma, Sequelize, SQLAlchemy, Mongoose, Hibernate
APIS: REST API Design, GraphQL, gRPC, WebSockets, OpenAPI/Swagger
WEB FRAMEWORKS: Express.js, FastAPI, Django, Spring Boot, NestJS, Laravel, Gin
AUTHENTICATION: JWT, OAuth 2.0, OpenID Connect, bcrypt, Session Management
CACHING: Redis, Memcached, CDN, HTTP Caching
MESSAGE BROKERS: RabbitMQ, Kafka, SQS, Bull/BullMQ
TESTING: Unit tests, Integration tests, TDD, Mocking, Postman, k6
SEARCH: Elasticsearch, Meilisearch, Algolia
DEPLOYMENT: Docker, Kubernetes, CI/CD, Nginx, PM2
CLOUD: AWS (EC2, S3, Lambda, RDS), GCP, Azure
SECURITY: OWASP Top 10, SQL Injection, Rate Limiting, Input Validation
ARCHITECTURE: Microservices, Event-Driven, CQRS, Domain-Driven Design
MONITORING: ELK, Datadog, Prometheus, Grafana""",
    },
    "devops": {
        "label": "DevOps / Cloud Engineer",
        "icon": "DO",
        "skills": """LINUX: Linux CLI, Bash scripting, File system, SSH, Process management
NETWORKING: TCP/IP, DNS, Load Balancers, Firewalls, VPN, HTTP/HTTPS
VERSION CONTROL: Git, GitHub, GitLab, Branching, MRs
CONTAINERS: Docker, Docker Compose, Container registries
ORCHESTRATION: Kubernetes (kubectl, Helm, Operators), EKS, GKE, AKS
CI/CD: Jenkins, GitHub Actions, GitLab CI, CircleCI, ArgoCD, Tekton
IAC: Terraform, Pulumi, CloudFormation, Ansible, Chef, Puppet
CLOUD: AWS (EC2, S3, VPC, IAM, Lambda, EKS, RDS), GCP, Azure
OBSERVABILITY: Prometheus, Grafana, ELK Stack, Datadog, Jaeger, OpenTelemetry
SERVICE MESH: Istio, Linkerd, Consul
SECURITY: DevSecOps, Vault, SAST/DAST, Secrets management, IAM policies
ARTIFACT MGMT: Docker Hub, ECR, Nexus, JFrog Artifactory
GITOPS: ArgoCD, Flux, Helm charts""",
    },
    "datascience": {
        "label": "Data Scientist / ML Engineer",
        "icon": "DS",
        "skills": """PROGRAMMING: Python (primary), R, SQL, Scala
MATH/STATS: Linear Algebra, Calculus, Probability, Statistics, Bayesian inference
DATA TOOLS: pandas, NumPy, Polars, dask, PySpark
VISUALIZATION: Matplotlib, Seaborn, Plotly, Tableau, Streamlit
ML: Scikit-learn, XGBoost, LightGBM, CatBoost, Feature engineering
DEEP LEARNING: TensorFlow, PyTorch, Keras, CNN, RNN, Transformers
NLP: Hugging Face, spaCy, NLTK, LangChain, RAG, LLM fine-tuning
MLOPS: MLflow, W&B, DVC, Airflow, Kubeflow, BentoML, FastAPI serving
DATA ENGINEERING: Apache Spark, Kafka, dbt, Airflow, SQL, NoSQL
CLOUD ML: AWS SageMaker, GCP Vertex AI, Azure ML, Databricks
VECTOR DBs: Pinecone, ChromaDB, Weaviate, FAISS
STATISTICS: A/B testing, Hypothesis testing, Regression, Time series
EXPERIMENTS: MLflow, Weights & Biases, Neptune, Comet""",
    },
    "fullstack": {
        "label": "Full Stack Developer",
        "icon": "FS",
        "skills": """FRONTEND: HTML5, CSS3, JavaScript, TypeScript, React/Vue/Angular, Next.js, Tailwind CSS
BACKEND: Node.js/Express, Python/FastAPI, RESTful APIs, GraphQL, Microservices
DATABASES: PostgreSQL, MySQL, MongoDB, Redis, ORM (Prisma/Sequelize)
AUTHENTICATION: JWT, OAuth 2.0, NextAuth, Passport.js, Session management
TESTING: Jest, Cypress, Playwright, React Testing Library, Supertest
BUILD TOOLS: Vite, Webpack, npm/yarn, ESLint, Prettier
VERSION CONTROL: Git, GitHub/GitLab, PR workflows
CI/CD: GitHub Actions, Vercel, Netlify, Railway, Render
CLOUD: AWS, GCP, Docker, Kubernetes basics, Nginx
SECURITY: OWASP, CORS, CSRF, XSS prevention, HTTPS, Input sanitization
REAL-TIME: WebSockets, Socket.IO, Server-Sent Events
API DESIGN: REST best practices, OpenAPI/Swagger, Rate limiting, Versioning
PERFORMANCE: Core Web Vitals, Caching, CDN, Load testing""",
    },
    "android": {
        "label": "Android Developer",
        "icon": "AD",
        "skills": """LANGUAGES: Kotlin (primary), Java
ANDROID SDK: Activity/Fragment lifecycle, Views, Intents, Services
JETPACK: Compose, ViewModel, LiveData, Room, Navigation, WorkManager, Hilt/Dagger
ARCHITECTURE: MVVM, MVI, Clean Architecture, Repository pattern
NETWORKING: Retrofit, OkHttp, Ktor, REST APIs
ASYNC: Coroutines, Flow, RxJava
DATABASES: Room, SharedPreferences, DataStore, Firebase Firestore
DEPENDENCY INJECTION: Hilt, Dagger 2, Koin
TESTING: JUnit, Espresso, Mockito, Turbine, Robolectric
UI/UX: Material Design 3, Custom views, Animations, Accessibility
FIREBASE: Authentication, Crashlytics, Analytics, FCM
BUILD: Gradle, Build variants, ProGuard/R8, App signing
PUBLISHING: Google Play Store, App Bundle (AAB), Release management
CROSS-PLATFORM: Kotlin Multiplatform, Flutter basics""",
    },
}

TYPE_COLORS = {
    "course": "#1D9E75",
    "docs": "#378ADD",
    "book": "#D85A30",
    "video": "#D4537E",
    "practice": "#7F77DD",
}

MAX_PDF_BYTES = 8 * 1024 * 1024
_VECTOR_STORE_READY = False

ANALYSIS_PROMPT_TEMPLATE = """You are an expert career coach. Analyze this resume against the {role_label} skill roadmap.

RESUME:
{resume}

TARGET ROLE:
{role_label}

SKILL ROADMAP CONTEXT:
{skills_context}

Return ONLY a valid JSON object (no markdown, no backticks, no extra text):
{{"matchScore":<integer 0-100>,"summary":"<2-3 sentence overall assessment>","strengths":["<s1>","<s2>","<s3>"],"matchedSkills":[{{"skill":"<>","category":"<>","evidence":"<brief evidence from resume>"}}],"missingSkills":[{{"skill":"<>","category":"<>","priority":"high|medium|low","why":"<why this matters for this role>"}}],"roadmap":[{{"phase":"<phase name>","duration":"<e.g. 2-3 weeks>","skills":["<s1>","<s2>"],"resources":[{{"name":"<resource name>","url":"<real url>","type":"course|docs|book|video|practice"}}]}}]}}"""


def get_analysis_chain(api_key):
    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import PromptTemplate
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as exc:
        raise RuntimeError(
            "LangChain Gemini dependencies are not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    prompt = PromptTemplate.from_template(ANALYSIS_PROMPT_TEMPLATE)
    model = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=api_key,
        temperature=0.3,
        max_output_tokens=4096,
    )
    return prompt | model | StrOutputParser()


def get_embedding_model(api_key):
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
    except ImportError as exc:
        raise RuntimeError(
            "LangChain Gemini dependencies are not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    return GoogleGenerativeAIEmbeddings(
        model=GEMINI_EMBEDDING_MODEL,
        google_api_key=api_key,
    )


def build_roadmap_documents():
    documents = []
    for role_key, roadmap in ROADMAPS.items():
        for index, line in enumerate(roadmap["skills"].splitlines()):
            if not line.strip():
                continue
            category, _, skills = line.partition(":")
            category = category.strip() or "GENERAL"
            text = (
                f"Role: {roadmap['label']}\n"
                f"Category: {category}\n"
                f"Important skills: {skills.strip() or line.strip()}"
            )
            documents.append(
                {
                    "id": f"{role_key}-{index}",
                    "text": text,
                    "metadata": {
                        "role_key": role_key,
                        "role_label": roadmap["label"],
                        "category": category,
                    },
                }
            )
    return documents


def get_vector_connection():
    if VECTOR_DB_PATH.parent != Path("."):
        VECTOR_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(VECTOR_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS roadmap_vectors (
            id TEXT PRIMARY KEY,
            role_key TEXT NOT NULL,
            role_label TEXT NOT NULL,
            category TEXT NOT NULL,
            text TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS vector_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    return conn


def ensure_roadmap_vector_store(api_key):
    global _VECTOR_STORE_READY
    if _VECTOR_STORE_READY:
        return

    documents = build_roadmap_documents()
    expected_count = len(documents)
    with get_vector_connection() as conn:
        current_count = conn.execute(
            "SELECT COUNT(*) FROM roadmap_vectors"
        ).fetchone()[0]
        stored_model = conn.execute(
            "SELECT value FROM vector_metadata WHERE key = 'embedding_model'"
        ).fetchone()
        stored_count = conn.execute(
            "SELECT value FROM vector_metadata WHERE key = 'document_count'"
        ).fetchone()

        store_matches = (
            current_count == expected_count
            and stored_model
            and stored_model[0] == GEMINI_EMBEDDING_MODEL
            and stored_count
            and stored_count[0] == str(expected_count)
        )
        if store_matches:
            _VECTOR_STORE_READY = True
            return

        conn.execute("DELETE FROM roadmap_vectors")
        conn.execute("DELETE FROM vector_metadata")
        embedder = get_embedding_model(api_key)
        texts = [doc["text"] for doc in documents]
        embeddings = embedder.embed_documents(
            texts,
            task_type="RETRIEVAL_DOCUMENT",
        )
        conn.executemany(
            """
            INSERT INTO roadmap_vectors
                (id, role_key, role_label, category, text, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    doc["id"],
                    doc["metadata"]["role_key"],
                    doc["metadata"]["role_label"],
                    doc["metadata"]["category"],
                    doc["text"],
                    json.dumps(embedding),
                )
                for doc, embedding in zip(documents, embeddings)
            ],
        )
        conn.executemany(
            "INSERT INTO vector_metadata (key, value) VALUES (?, ?)",
            [
                ("embedding_model", GEMINI_EMBEDDING_MODEL),
                ("document_count", str(expected_count)),
            ],
        )
        conn.commit()
    _VECTOR_STORE_READY = True


def cosine_similarity(left, right):
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def query_roadmap_vectors(query_embedding, role_key=""):
    sql = (
        "SELECT role_label, category, text, embedding "
        "FROM roadmap_vectors"
    )
    params = ()
    if role_key:
        sql += " WHERE role_key = ?"
        params = (role_key,)

    with get_vector_connection() as conn:
        rows = conn.execute(sql, params).fetchall()

    scored = []
    for role_label, category, text, embedding_json in rows:
        embedding = json.loads(embedding_json)
        scored.append(
            {
                "score": cosine_similarity(query_embedding, embedding),
                "role_label": role_label,
                "category": category,
                "text": text,
            }
        )
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:RAG_TOP_K]


def retrieve_roadmap_context(resume, role_context, api_key):
    ensure_roadmap_vector_store(api_key)
    embedder = get_embedding_model(api_key)
    query = (
        f"Target role: {role_context['label']}\n"
        f"Resume excerpt: {resume[:1500]}"
    )
    query_embedding = embedder.embed_query(
        query,
        task_type="RETRIEVAL_QUERY",
    )
    retrieved = query_roadmap_vectors(
        query_embedding,
        role_context.get("role_key", ""),
    )

    if not retrieved:
        return role_context["skills_context"]

    chunks = []
    for item in retrieved:
        chunks.append(
            f"[Retrieved: {item['role_label']} / {item['category']}]\n"
            f"{item['text']}"
        )

    if role_context.get("role_key"):
        intro = (
            "Use these retrieved roadmap chunks from the local SQLite vector "
            "store as the primary skill context:"
        )
    else:
        intro = (
            "No predefined roadmap was selected. Use these retrieved chunks "
            "from similar roadmap roles as supporting context, then infer any "
            f"additional skills needed for {role_context['label']}:"
        )
    return f"{intro}\n\n" + "\n\n".join(chunks)


def get_message_text(message):
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)


def parse_json_response(text):
    clean = re.sub(r"```(?:json)?|```", "", text or "").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", clean, flags=re.DOTALL)
        if not match:
            raise ValueError("Gemini did not return a JSON object.")
        return json.loads(match.group(0))


def normalize_result(result):
    result["matchScore"] = max(0, min(100, int(result.get("matchScore", 0) or 0)))
    for key in ("strengths", "matchedSkills", "missingSkills", "roadmap"):
        if not isinstance(result.get(key), list):
            result[key] = []
    result["summary"] = result.get("summary") or "No summary was returned."
    return result


def extract_pdf_text(file_storage):
    if not file_storage or not file_storage.filename:
        return ""

    filename = file_storage.filename.lower()
    if not filename.endswith(".pdf"):
        raise ValueError("Please upload a PDF file.")

    pdf_bytes = file_storage.read()
    if not pdf_bytes:
        return ""
    if len(pdf_bytes) > MAX_PDF_BYTES:
        raise ValueError("Please upload a PDF smaller than 8 MB.")

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "PDF parsing dependency is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        page_text = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise ValueError(
            "Could not read text from that PDF. Please paste the resume text instead."
        ) from exc

    text = "\n\n".join(part.strip() for part in page_text if part.strip()).strip()
    if not text:
        raise ValueError(
            "No selectable text was found in that PDF. Please paste the resume text instead."
        )
    return text


def get_role_context(role, custom_role=""):
    if role in ROADMAPS:
        roadmap = ROADMAPS[role]
        return {
            "label": roadmap["label"],
            "icon": roadmap["icon"],
            "role_key": role,
            "skills_context": (
                f"Use this roadmap.sh-style skill list for {roadmap['label']}:\n"
                f"{roadmap['skills']}"
            ),
        }

    label = custom_role.strip()
    return {
        "label": label,
        "icon": "CR",
        "role_key": "",
        "skills_context": (
            "No predefined roadmap was selected. Infer a practical, current, "
            f"roadmap.sh-style skill roadmap for a {label}. Include core "
            "technical skills, tools, testing practices, deployment or delivery "
            "skills where relevant, and role-specific best practices."
        ),
    }


def analyze_resume(resume, role_context):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured on the server.")

    chain = get_analysis_chain(api_key)
    skills_context = retrieve_roadmap_context(resume, role_context, api_key)
    response_text = chain.invoke(
        {
            "role_label": role_context["label"],
            "resume": resume[:6000],
            "skills_context": skills_context,
        }
    )
    return normalize_result(parse_json_response(get_message_text(response_text)))


def split_gaps(missing_skills):
    groups = {"high": [], "medium": [], "low": []}
    for skill in missing_skills or []:
        priority = str(skill.get("priority", "low")).lower()
        if priority not in groups:
            priority = "low"
        groups[priority].append(skill)
    return groups


@app.get("/")
def index():
    return render_template(
        "index.html",
        roles=ROADMAPS,
        selected_role="frontend",
        custom_role="",
        role_display=ROADMAPS["frontend"],
        resume="",
        uploaded_filename="",
        resume_source="",
        result=None,
        error="",
        type_colors=TYPE_COLORS,
    )


@app.get("/analyze")
def analyze_get():
    return redirect(url_for("index"))


@app.post("/analyze")
def analyze():
    pasted_resume = request.form.get("resume", "").strip()
    resume = pasted_resume
    selected_role = request.form.get("role", "frontend")
    custom_role = request.form.get("custom_role", "").strip()
    resume_pdf = request.files.get("resume_pdf")
    uploaded_filename = resume_pdf.filename if resume_pdf and resume_pdf.filename else ""
    resume_source = "pasted text" if resume else ""
    error = ""
    result = None
    gap_groups = None
    role_context = None

    if uploaded_filename:
        try:
            resume = extract_pdf_text(resume_pdf)
            resume_source = f"PDF upload: {uploaded_filename}"
        except Exception as exc:
            error = f"Error: {exc}"

    if not error and selected_role == "custom":
        if len(custom_role) < 2:
            error = "Please enter a custom target role."
        else:
            role_context = get_role_context(selected_role, custom_role)
    elif not error and selected_role in ROADMAPS:
        role_context = get_role_context(selected_role)
    elif not error:
        error = "Please choose a valid target role."
        selected_role = "frontend"
        role_context = get_role_context(selected_role)

    if not error and len(resume) < 50:
        error = "Please paste resume text or upload a text-based resume PDF with at least 50 characters."

    if not error:
        try:
            result = analyze_resume(resume, role_context)
            gap_groups = split_gaps(result.get("missingSkills"))
        except Exception as exc:
            error = f"Error: {exc}"

    if role_context is None:
        role_context = get_role_context(selected_role, custom_role)

    return render_template(
        "index.html",
        roles=ROADMAPS,
        selected_role=selected_role,
        custom_role=custom_role,
        role_display=role_context,
        resume=pasted_resume,
        uploaded_filename=uploaded_filename,
        resume_source=resume_source,
        result=result,
        gap_groups=gap_groups,
        error=error,
        type_colors=TYPE_COLORS,
    )


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(debug=debug, use_reloader=False)
