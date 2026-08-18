"""
SkillForge AI — Phase 3: Skill & Career Knowledge Base (seed data).

Methodology note (for dataset_methodology.md):
  This knowledge base was hand-curated rather than mined statistically from
  job-posting data.  Specifically:
    - Skill list (101 skills): drawn from widely-used technology taxonomies
      (e.g. LinkedIn Skills taxonomy, Stack Overflow Developer Survey 2023),
      filtered to a scope defensible for a single-FYP project.
    - Career-skill importance weights: expert-assigned (1–5) based on common
      hiring criteria for each role.  They are NOT derived from corpus
      analysis or labour-market statistics — this is a disclosed limitation.
    - Prerequisite edges (62): domain-expert judgment on canonical learning
      order, not automated from learner data.
  These limitations are documented in docs/limitations.md and should be
  disclosed in any paper section that presents evaluation numbers.

Data layout:
  SKILLS          — 101 rows, 5 categories
  SKILL_ALIASES   — 26 rows
  PREREQUISITES   — 62 edges  (from_id, to_id, relation_type)
  CAREERS         — 15 rows
  REQUIREMENTS    — 116 rows  (career_id, skill_id, importance, min, pref)
"""

# ─── SKILLS ──────────────────────────────────────────────────────────────────
# Each tuple: (skill_id, name, category, subcategory, difficulty, description)

SKILLS = [
    # ── Programming Languages (12) ────────────────────────────────────────────
    (1,  "Python",                 "Programming Languages", "General Purpose", 2,
     "High-level, interpreted language widely used in data science, ML, and backend dev."),
    (2,  "R",                      "Programming Languages", "Statistical",       3,
     "Statistical computing language favoured in academia and data analysis."),
    (3,  "Java",                   "Programming Languages", "General Purpose",   2,
     "Strongly-typed, object-oriented language used in enterprise software."),
    (4,  "JavaScript",             "Programming Languages", "Web",               2,
     "Primary scripting language of the web; runs in browsers and on Node.js."),
    (5,  "TypeScript",             "Programming Languages", "Web",               3,
     "Statically-typed superset of JavaScript that compiles to plain JS."),
    (6,  "C++",                    "Programming Languages", "Systems",           4,
     "High-performance systems language with low-level memory control."),
    (7,  "Go",                     "Programming Languages", "Systems",           3,
     "Compiled, statically-typed language from Google; designed for concurrency."),
    (8,  "Rust",                   "Programming Languages", "Systems",           5,
     "Memory-safe systems language with no garbage collector."),
    (9,  "Scala",                  "Programming Languages", "Functional/JVM",   4,
     "JVM language blending OOP and functional programming; used in big-data."),
    (10, "MATLAB",                 "Programming Languages", "Scientific",        3,
     "Numeric computing environment widely used in signal processing and engineering."),
    (11, "Bash Scripting",         "Programming Languages", "Scripting",         2,
     "Unix shell scripting for automation, file processing, and system admin tasks."),
    (12, "Swift",                  "Programming Languages", "Mobile",            3,
     "Apple's language for iOS/macOS app development."),

    # ── Data Science & Machine Learning (20) ─────────────────────────────────
    (13, "NumPy",                  "Data Science & ML", "Numerical Computing",   2,
     "Fundamental Python library for N-dimensional arrays and linear algebra."),
    (14, "Pandas",                 "Data Science & ML", "Data Manipulation",     2,
     "Python library for tabular data manipulation using DataFrames."),
    (15, "Scikit-learn",           "Data Science & ML", "Classical ML",          3,
     "Python ML library implementing classical algorithms with a uniform API."),
    (16, "TensorFlow",             "Data Science & ML", "Deep Learning",         4,
     "Google's end-to-end open-source deep-learning framework."),
    (17, "PyTorch",                "Data Science & ML", "Deep Learning",         4,
     "Meta's flexible, dynamic deep-learning framework popular in research."),
    (18, "Keras",                  "Data Science & ML", "Deep Learning",         3,
     "High-level neural-network API; runs on top of TensorFlow."),
    (19, "XGBoost",                "Data Science & ML", "Ensemble Methods",      3,
     "Optimised gradient-boosting library known for tabular-data performance."),
    (20, "LightGBM",               "Data Science & ML", "Ensemble Methods",      3,
     "Microsoft's fast gradient-boosting framework using histogram-based algorithm."),
    (21, "Machine Learning",       "Data Science & ML", "Core Concepts",         3,
     "Discipline of building systems that learn patterns from data."),
    (22, "Deep Learning",          "Data Science & ML", "Core Concepts",         4,
     "Subset of ML using multi-layer neural networks to learn representations."),
    (23, "Natural Language Processing", "Data Science & ML", "NLP",              4,
     "Field of AI enabling machines to understand and generate human language."),
    (24, "Computer Vision",        "Data Science & ML", "Vision",                4,
     "Field of AI enabling machines to interpret and analyse visual data."),
    (25, "Feature Engineering",    "Data Science & ML", "Methodology",           3,
     "Process of transforming raw data into informative features for ML models."),
    (26, "Model Deployment",       "Data Science & ML", "MLOps",                 4,
     "Packaging, serving, monitoring, and versioning ML models in production."),
    (27, "Statistics",             "Data Science & ML", "Mathematics",           3,
     "Mathematical foundation for data analysis: distributions, inference, testing."),
    (28, "Probability Theory",     "Data Science & ML", "Mathematics",           3,
     "Formal study of random phenomena; underpins all probabilistic ML models."),
    (29, "Linear Algebra",         "Data Science & ML", "Mathematics",           3,
     "Study of vectors, matrices, and linear maps; core to neural networks."),
    (30, "Data Visualization",     "Data Science & ML", "Reporting",             2,
     "Communicating insights through charts, dashboards, and interactive plots."),
    (31, "Time Series Analysis",   "Data Science & ML", "Specialisation",        4,
     "Techniques for modelling and forecasting temporally-ordered data."),
    (32, "Reinforcement Learning", "Data Science & ML", "Core Concepts",         5,
     "Training agents via reward signals through interaction with an environment."),

    # ── Data Engineering (10) ─────────────────────────────────────────────────
    (33, "SQL",                    "Data Engineering", "Query Language",          2,
     "Declarative language for relational database querying and manipulation."),
    (34, "PostgreSQL",             "Data Engineering", "Relational Database",     2,
     "Feature-rich, ACID-compliant open-source relational database system."),
    (35, "MongoDB",                "Data Engineering", "NoSQL Database",          2,
     "Document-oriented NoSQL database storing data as BSON documents."),
    (36, "Redis",                  "Data Engineering", "In-Memory Store",         2,
     "In-memory key-value store used for caching and pub/sub messaging."),
    (37, "Apache Spark",           "Data Engineering", "Distributed Computing",   4,
     "Unified analytics engine for large-scale data processing and ML."),
    (38, "Apache Kafka",           "Data Engineering", "Streaming",               4,
     "Distributed event-streaming platform for high-throughput data pipelines."),
    (39, "Apache Airflow",         "Data Engineering", "Workflow Orchestration",  3,
     "Platform for programmatically authoring, scheduling, and monitoring pipelines."),
    (40, "dbt",                    "Data Engineering", "Data Transformation",     3,
     "Data-build tool that transforms raw data in the warehouse using SQL + Jinja."),
    (41, "ETL",                    "Data Engineering", "Methodology",             2,
     "Extract-Transform-Load: foundational pattern for moving data between systems."),
    (42, "Data Warehousing",       "Data Engineering", "Architecture",            3,
     "Design and operation of centralised analytic data stores (e.g. Redshift, BigQuery)."),

    # ── Web Frontend (12) ─────────────────────────────────────────────────────
    (43, "HTML",                   "Web Frontend", "Markup",                      1,
     "HyperText Markup Language: the structural layer of web pages."),
    (44, "CSS",                    "Web Frontend", "Styling",                     1,
     "Cascading Style Sheets: the visual presentation layer of web pages."),
    (45, "React",                  "Web Frontend", "Framework",                   3,
     "Facebook's component-based UI library for building interactive web UIs."),
    (46, "Vue.js",                 "Web Frontend", "Framework",                   2,
     "Progressive JavaScript framework for building user interfaces."),
    (47, "Angular",                "Web Frontend", "Framework",                   3,
     "Google's full-featured TypeScript-based front-end application framework."),
    (48, "Next.js",                "Web Frontend", "Framework",                   3,
     "React meta-framework with file-based routing, SSR, and SSG support."),
    (49, "Tailwind CSS",           "Web Frontend", "Styling",                     2,
     "Utility-first CSS framework for rapidly building custom user interfaces."),
    (50, "GraphQL",                "Web Frontend", "API Protocol",                3,
     "Query language for APIs giving clients control over the data they fetch."),
    (51, "Webpack",                "Web Frontend", "Build Tools",                 3,
     "Module bundler that compiles JavaScript applications and their assets."),
    (52, "Jest",                   "Web Frontend", "Testing",                     2,
     "JavaScript testing framework with a focus on simplicity."),
    (53, "Redux",                  "Web Frontend", "State Management",            3,
     "Predictable state-management container for JavaScript applications."),
    (54, "SASS",                   "Web Frontend", "Styling",                     2,
     "CSS preprocessor adding variables, nesting, and mixins to stylesheets."),

    # ── Web Backend (10) ──────────────────────────────────────────────────────
    (55, "Node.js",                "Web Backend", "Runtime",                      2,
     "JavaScript runtime built on Chrome's V8 engine for server-side execution."),
    (56, "Express.js",             "Web Backend", "Framework",                    2,
     "Minimal Node.js web application framework for REST APIs."),
    (57, "Django",                 "Web Backend", "Framework",                    3,
     "Batteries-included Python web framework with built-in ORM and admin UI."),
    (58, "Flask",                  "Web Backend", "Framework",                    2,
     "Lightweight Python WSGI micro-framework for small to medium web apps."),
    (59, "FastAPI",                "Web Backend", "Framework",                    3,
     "Modern, async Python API framework with automatic OpenAPI docs."),
    (60, "REST API Design",        "Web Backend", "Methodology",                  2,
     "Principles for designing stateless, resource-oriented HTTP APIs."),
    (61, "Microservices",          "Web Backend", "Architecture",                 4,
     "Architectural style structuring an application as independently deployable services."),
    (62, "API Authentication",     "Web Backend", "Security",                     3,
     "Mechanisms for securing APIs: API keys, OAuth 2.0, JWT, sessions."),
    (63, "gRPC",                   "Web Backend", "API Protocol",                 4,
     "High-performance RPC framework from Google using Protocol Buffers."),
    (64, "WebSockets",             "Web Backend", "Real-time",                    3,
     "Protocol for full-duplex communication between client and server."),

    # ── DevOps & Cloud (15) ───────────────────────────────────────────────────
    (65, "Docker",                 "DevOps & Cloud", "Containerisation",          3,
     "Platform for building, running, and shipping applications in containers."),
    (66, "Kubernetes",             "DevOps & Cloud", "Container Orchestration",   4,
     "Open-source system for automating deployment, scaling, and management of containers."),
    (67, "Terraform",              "DevOps & Cloud", "Infrastructure as Code",    3,
     "Open-source IaC tool for declarative provisioning of cloud resources."),
    (68, "AWS",                    "DevOps & Cloud", "Cloud Platform",            3,
     "Amazon Web Services: the leading public cloud platform."),
    (69, "GCP",                    "DevOps & Cloud", "Cloud Platform",            3,
     "Google Cloud Platform: Google's suite of cloud computing services."),
    (70, "Azure",                  "DevOps & Cloud", "Cloud Platform",            3,
     "Microsoft Azure: cloud platform with strong enterprise/hybrid offerings."),
    (71, "CI/CD",                  "DevOps & Cloud", "Automation",               3,
     "Continuous Integration / Continuous Delivery: automating build, test, deploy."),
    (72, "Jenkins",                "DevOps & Cloud", "CI/CD Tools",               3,
     "Open-source automation server for building CI/CD pipelines."),
    (73, "GitHub Actions",         "DevOps & Cloud", "CI/CD Tools",               2,
     "GitHub's integrated CI/CD platform using workflow YAML files."),
    (74, "Linux Administration",   "DevOps & Cloud", "Systems",                   3,
     "Operating, configuring, and troubleshooting Linux-based servers."),
    (75, "Ansible",                "DevOps & Cloud", "Configuration Management",  3,
     "Agentless IT automation and configuration-management tool."),
    (76, "Prometheus",             "DevOps & Cloud", "Monitoring",                3,
     "Open-source systems monitoring and alerting toolkit."),
    (77, "Nginx",                  "DevOps & Cloud", "Web Server",                2,
     "High-performance web server and reverse proxy widely used in deployments."),
    (78, "Grafana",                "DevOps & Cloud", "Monitoring",                2,
     "Open-source platform for monitoring and observability dashboards."),
    (79, "Load Balancing",         "DevOps & Cloud", "Infrastructure",            3,
     "Distributing incoming network traffic across multiple backend servers."),

    # ── General Software Engineering (12) ─────────────────────────────────────
    (80, "Git",                    "Software Engineering", "Version Control",      1,
     "Distributed version-control system for tracking changes in source code."),
    (81, "Agile/Scrum",            "Software Engineering", "Methodology",          2,
     "Iterative software development framework using sprints and ceremonies."),
    (82, "System Design",          "Software Engineering", "Architecture",         4,
     "Designing scalable, reliable, maintainable software systems."),
    (83, "Object-Oriented Programming", "Software Engineering", "Paradigm",       2,
     "Programming paradigm organising code around objects and classes."),
    (84, "Functional Programming", "Software Engineering", "Paradigm",            3,
     "Programming paradigm treating computation as evaluation of mathematical functions."),
    (85, "Unit Testing",           "Software Engineering", "Quality Assurance",   2,
     "Automated testing of individual code units in isolation."),
    (86, "Integration Testing",    "Software Engineering", "Quality Assurance",   3,
     "Testing interactions between combined components or services."),
    (87, "Code Review",            "Software Engineering", "Collaboration",        2,
     "Systematic peer examination of source code changes before merging."),
    (88, "Debugging",              "Software Engineering", "Methodology",          2,
     "Identifying and fixing errors and unexpected behaviour in software."),
    (89, "Design Patterns",        "Software Engineering", "Architecture",         3,
     "Reusable solutions to commonly recurring software design problems (GoF patterns)."),
    (90, "Algorithms & Data Structures", "Software Engineering", "CS Fundamentals", 3,
     "Core CS: sorting, searching, trees, graphs, complexity analysis."),
    (91, "Database Design",        "Software Engineering", "Architecture",         3,
     "Modelling data entities, relationships, normalisation, and indexing."),

    # ── Security (5) ──────────────────────────────────────────────────────────
    (92, "Cybersecurity",          "Security", "Core Concepts",                   3,
     "Practices for protecting systems, networks, and programs from attacks."),
    (93, "OAuth/JWT",              "Security", "Authentication Protocols",        3,
     "OAuth 2.0 authorisation framework and JSON Web Tokens for stateless auth."),
    (94, "HTTPS/TLS",              "Security", "Transport Security",              2,
     "Encrypting data in transit with TLS certificates and HTTPS."),
    (95, "Penetration Testing",    "Security", "Offensive Security",              4,
     "Authorised simulated attacks to identify security vulnerabilities."),
    (96, "OWASP",                  "Security", "Web Security",                    3,
     "OWASP Top-10 web application security risks and mitigation strategies."),

    # ── Mobile Development (5) ────────────────────────────────────────────────
    (97,  "iOS Development",       "Mobile Development", "Native",                4,
     "Building native iPhone/iPad applications using Swift/Xcode."),
    (98,  "Android Development",   "Mobile Development", "Native",                4,
     "Building native Android apps using Kotlin/Java with the Android SDK."),
    (99,  "React Native",          "Mobile Development", "Cross-platform",        3,
     "Building cross-platform mobile apps using React and JavaScript."),
    (100, "Flutter",               "Mobile Development", "Cross-platform",        3,
     "Google's UI toolkit for natively compiled apps from a single Dart codebase."),
    (101, "Mobile UI Design",      "Mobile Development", "UX",                    2,
     "Designing touch-friendly, accessible interfaces for mobile form factors."),
]

# ─── SKILL ALIASES ────────────────────────────────────────────────────────────
# Each tuple: (skill_id, alias_text)
SKILL_ALIASES = [
    (1,  "py"),
    (4,  "JS"),
    (4,  "ECMAScript"),
    (5,  "TS"),
    (11, "Shell Scripting"),
    (13, "numpy"),
    (14, "pandas"),
    (15, "sklearn"),
    (15, "scikit learn"),
    (16, "TF"),
    (17, "torch"),
    (21, "ML"),
    (22, "DL"),
    (23, "NLP"),
    (24, "CV"),
    (33, "structured query language"),
    (34, "Postgres"),
    (34, "PG"),
    (45, "ReactJS"),
    (45, "React.js"),
    (49, "Tailwind"),
    (60, "REST"),
    (60, "RESTful"),
    (65, "containerisation"),
    (66, "K8s"),
    (80, "version control"),
]

assert len(SKILL_ALIASES) == 26, f"Expected 26 aliases, got {len(SKILL_ALIASES)}"

# ─── SKILL PREREQUISITES ─────────────────────────────────────────────────────
# Each tuple: (from_skill_id, to_skill_id, relation_type)
# "from" must be mastered BEFORE learning "to" (relation_type='prerequisite'),
# or they are strongly complementary (relation_type='related').

SKILL_PREREQUISITES = [
    # NumPy / Pandas / Scikit-learn need Python
    (1,  13, "prerequisite"),   # Python → NumPy
    (1,  14, "prerequisite"),   # Python → Pandas
    (13, 14, "prerequisite"),   # NumPy → Pandas
    (1,  15, "prerequisite"),   # Python → Scikit-learn
    (13, 15, "prerequisite"),   # NumPy → Scikit-learn
    (14, 15, "prerequisite"),   # Pandas → Scikit-learn
    (15, 21, "related"),        # Scikit-learn ↔ Machine Learning

    # Deep Learning stack
    (1,  16, "prerequisite"),   # Python → TensorFlow
    (13, 16, "prerequisite"),   # NumPy → TensorFlow
    (21, 16, "prerequisite"),   # Machine Learning → TensorFlow
    (1,  17, "prerequisite"),   # Python → PyTorch
    (13, 17, "prerequisite"),   # NumPy → PyTorch
    (21, 17, "prerequisite"),   # Machine Learning → PyTorch
    (16, 18, "prerequisite"),   # TensorFlow → Keras
    (15, 19, "prerequisite"),   # Scikit-learn → XGBoost
    (15, 20, "prerequisite"),   # Scikit-learn → LightGBM

    # Machine Learning needs stats + linear algebra
    (1,  21, "prerequisite"),   # Python → Machine Learning
    (27, 21, "prerequisite"),   # Statistics → Machine Learning
    (29, 21, "prerequisite"),   # Linear Algebra → Machine Learning

    # Deep Learning → NLP / CV / RL
    (21, 22, "prerequisite"),   # Machine Learning → Deep Learning
    (17, 22, "related"),        # PyTorch ↔ Deep Learning
    (22, 23, "prerequisite"),   # Deep Learning → NLP
    (21, 23, "prerequisite"),   # Machine Learning → NLP
    (22, 24, "prerequisite"),   # Deep Learning → Computer Vision
    (29, 24, "related"),        # Linear Algebra ↔ Computer Vision
    (22, 32, "prerequisite"),   # Deep Learning → Reinforcement Learning

    # Feature Engineering / Model Deployment
    (14, 25, "prerequisite"),   # Pandas → Feature Engineering
    (21, 25, "prerequisite"),   # Machine Learning → Feature Engineering
    (21, 26, "prerequisite"),   # Machine Learning → Model Deployment
    (65, 26, "related"),        # Docker ↔ Model Deployment

    # Math chain
    (27, 28, "related"),        # Statistics ↔ Probability Theory
    (27, 31, "prerequisite"),   # Statistics → Time Series Analysis
    (14, 31, "prerequisite"),   # Pandas → Time Series Analysis

    # Data Visualisation
    (1,  30, "prerequisite"),   # Python → Data Visualization
    (14, 30, "prerequisite"),   # Pandas → Data Visualization

    # Web: TypeScript on top of JS
    (4,  5,  "prerequisite"),   # JavaScript → TypeScript

    # Frontend frameworks
    (4,  45, "prerequisite"),   # JavaScript → React
    (43, 45, "prerequisite"),   # HTML → React
    (44, 45, "prerequisite"),   # CSS → React
    (4,  46, "prerequisite"),   # JavaScript → Vue.js
    (5,  47, "prerequisite"),   # TypeScript → Angular
    (45, 48, "prerequisite"),   # React → Next.js
    (45, 53, "prerequisite"),   # React → Redux

    # Backend
    (4,  55, "related"),        # JavaScript ↔ Node.js
    (55, 56, "prerequisite"),   # Node.js → Express.js
    (1,  57, "prerequisite"),   # Python → Django
    (1,  58, "prerequisite"),   # Python → Flask
    (1,  59, "prerequisite"),   # Python → FastAPI

    # Databases
    (33, 34, "related"),        # SQL ↔ PostgreSQL
    (33, 37, "prerequisite"),   # SQL → Apache Spark
    (1,  37, "prerequisite"),   # Python → Apache Spark
    (1,  39, "prerequisite"),   # Python → Apache Airflow

    # DevOps chain
    (65, 66, "prerequisite"),   # Docker → Kubernetes
    (80, 71, "prerequisite"),   # Git → CI/CD
    (71, 73, "prerequisite"),   # CI/CD → GitHub Actions
    (71, 72, "prerequisite"),   # CI/CD → Jenkins
    (74, 75, "related"),        # Linux Administration ↔ Ansible
    (74, 76, "related"),        # Linux Administration ↔ Prometheus

    # Security / mobile
    (60, 93, "prerequisite"),   # REST API Design → OAuth/JWT
    (60, 63, "related"),        # REST API Design ↔ gRPC
    (45, 99, "prerequisite"),   # React → React Native
    (4,  99, "prerequisite"),   # JavaScript → React Native
]

assert len(SKILL_PREREQUISITES) == 62, (
    f"Expected 62 prerequisite edges, got {len(SKILL_PREREQUISITES)}"
)

# ─── CAREERS ─────────────────────────────────────────────────────────────────
# Each tuple: (career_id, name, description)

CAREERS = [
    (1,  "Data Scientist",
     "Analyses complex data to extract insights and build predictive models."),
    (2,  "Machine Learning Engineer",
     "Designs, trains, and deploys ML models into production systems at scale."),
    (3,  "Data Engineer",
     "Builds and maintains data pipelines, warehouses, and streaming infrastructure."),
    (4,  "Frontend Developer",
     "Builds user interfaces and client-side logic for web applications."),
    (5,  "Backend Developer",
     "Designs and implements server-side APIs, databases, and business logic."),
    (6,  "Full Stack Developer",
     "Handles both frontend and backend concerns across the full web stack."),
    (7,  "DevOps Engineer",
     "Bridges development and operations: CI/CD, containerisation, and infrastructure."),
    (8,  "Cloud Architect",
     "Designs scalable, cost-efficient cloud infrastructure across one or more providers."),
    (9,  "Software Engineer",
     "Designs, writes, tests, and maintains general-purpose software systems."),
    (10, "NLP Engineer",
     "Specialises in language models, text processing, and conversational AI."),
    (11, "Computer Vision Engineer",
     "Builds systems that interpret images and video using deep learning."),
    (12, "Business Intelligence Analyst",
     "Turns data into actionable reports, dashboards, and strategic insights."),
    (13, "Site Reliability Engineer",
     "Ensures production systems are reliable, scalable, and observable."),
    (14, "Mobile Developer",
     "Builds cross-platform or native mobile applications for iOS/Android."),
    (15, "Security Engineer",
     "Designs and implements security controls, reviews code, and runs assessments."),
]

assert len(CAREERS) == 15, f"Expected 15 careers, got {len(CAREERS)}"

# ─── CAREER-SKILL REQUIREMENTS ───────────────────────────────────────────────
# Each tuple: (career_id, skill_id, importance, minimum_proficiency, preferred_proficiency)
# importance:             1=nice-to-have … 5=essential
# minimum_proficiency:    floor for a hireable candidate
# preferred_proficiency:  target for a strong candidate

CAREER_SKILL_REQUIREMENTS = [
    # ── 1. Data Scientist (8 skills) ─────────────────────────────────────────
    (1,  1,  5, 3, 5),  # Python
    (1,  21, 5, 3, 5),  # Machine Learning
    (1,  27, 5, 3, 5),  # Statistics
    (1,  14, 4, 3, 4),  # Pandas
    (1,  15, 4, 3, 4),  # Scikit-learn
    (1,  33, 4, 2, 4),  # SQL
    (1,  30, 3, 2, 4),  # Data Visualization
    (1,  25, 4, 2, 4),  # Feature Engineering

    # ── 2. Machine Learning Engineer (8 skills) ───────────────────────────────
    (2,  1,  5, 4, 5),  # Python
    (2,  21, 5, 4, 5),  # Machine Learning
    (2,  22, 5, 3, 5),  # Deep Learning
    (2,  17, 4, 2, 4),  # PyTorch
    (2,  26, 5, 3, 5),  # Model Deployment
    (2,  65, 4, 2, 4),  # Docker
    (2,  82, 4, 2, 4),  # System Design
    (2,  90, 4, 3, 4),  # Algorithms & Data Structures

    # ── 3. Data Engineer (8 skills) ──────────────────────────────────────────
    (3,  1,  5, 3, 5),  # Python
    (3,  33, 5, 4, 5),  # SQL
    (3,  37, 5, 3, 5),  # Apache Spark
    (3,  38, 4, 2, 4),  # Apache Kafka
    (3,  39, 4, 2, 4),  # Apache Airflow
    (3,  41, 5, 3, 5),  # ETL
    (3,  42, 4, 3, 4),  # Data Warehousing
    (3,  65, 3, 2, 4),  # Docker

    # ── 4. Frontend Developer (8 skills) ─────────────────────────────────────
    (4,  43, 5, 4, 5),  # HTML
    (4,  44, 5, 4, 5),  # CSS
    (4,  4,  5, 4, 5),  # JavaScript
    (4,  45, 5, 3, 5),  # React
    (4,  5,  4, 2, 4),  # TypeScript
    (4,  49, 3, 2, 4),  # Tailwind CSS
    (4,  80, 4, 3, 4),  # Git
    (4,  52, 3, 2, 3),  # Jest

    # ── 5. Backend Developer (8 skills) ──────────────────────────────────────
    (5,  1,  4, 3, 5),  # Python
    (5,  33, 5, 4, 5),  # SQL
    (5,  34, 4, 3, 4),  # PostgreSQL
    (5,  60, 5, 3, 5),  # REST API Design
    (5,  59, 4, 2, 4),  # FastAPI
    (5,  65, 4, 2, 4),  # Docker
    (5,  62, 4, 3, 4),  # API Authentication
    (5,  80, 4, 3, 4),  # Git

    # ── 6. Full Stack Developer (8 skills) ───────────────────────────────────
    (6,  4,  5, 4, 5),  # JavaScript
    (6,  5,  4, 2, 4),  # TypeScript
    (6,  45, 4, 3, 4),  # React
    (6,  55, 4, 3, 4),  # Node.js
    (6,  33, 4, 3, 4),  # SQL
    (6,  60, 5, 3, 5),  # REST API Design
    (6,  80, 4, 3, 4),  # Git
    (6,  65, 3, 2, 3),  # Docker

    # ── 7. DevOps Engineer (8 skills) ────────────────────────────────────────
    (7,  65, 5, 4, 5),  # Docker
    (7,  66, 5, 3, 5),  # Kubernetes
    (7,  71, 5, 4, 5),  # CI/CD
    (7,  74, 5, 4, 5),  # Linux Administration
    (7,  67, 4, 3, 4),  # Terraform
    (7,  68, 4, 3, 4),  # AWS
    (7,  80, 4, 3, 4),  # Git
    (7,  11, 4, 3, 4),  # Bash Scripting

    # ── 8. Cloud Architect (8 skills) ────────────────────────────────────────
    (8,  68, 5, 4, 5),  # AWS
    (8,  67, 5, 4, 5),  # Terraform
    (8,  66, 4, 3, 4),  # Kubernetes
    (8,  65, 4, 3, 4),  # Docker
    (8,  82, 5, 4, 5),  # System Design
    (8,  74, 4, 3, 4),  # Linux Administration
    (8,  71, 4, 3, 4),  # CI/CD
    (8,  79, 4, 3, 4),  # Load Balancing

    # ── 9. Software Engineer (8 skills) ──────────────────────────────────────
    (9,  90, 5, 4, 5),  # Algorithms & Data Structures
    (9,  82, 5, 3, 5),  # System Design
    (9,  83, 4, 3, 4),  # Object-Oriented Programming
    (9,  80, 5, 4, 5),  # Git
    (9,  85, 4, 3, 4),  # Unit Testing
    (9,  89, 4, 3, 4),  # Design Patterns
    (9,  1,  4, 3, 4),  # Python
    (9,  33, 3, 2, 3),  # SQL

    # ── 10. NLP Engineer (7 skills) ──────────────────────────────────────────
    (10, 1,  5, 4, 5),  # Python
    (10, 23, 5, 4, 5),  # Natural Language Processing
    (10, 22, 5, 3, 5),  # Deep Learning
    (10, 17, 4, 3, 4),  # PyTorch
    (10, 21, 5, 3, 5),  # Machine Learning
    (10, 26, 4, 2, 4),  # Model Deployment
    (10, 27, 3, 2, 3),  # Statistics

    # ── 11. Computer Vision Engineer (7 skills) ───────────────────────────────
    (11, 1,  5, 4, 5),  # Python
    (11, 24, 5, 4, 5),  # Computer Vision
    (11, 22, 5, 4, 5),  # Deep Learning
    (11, 17, 5, 3, 5),  # PyTorch
    (11, 29, 4, 3, 4),  # Linear Algebra
    (11, 26, 4, 2, 4),  # Model Deployment
    (11, 13, 4, 3, 4),  # NumPy

    # ── 12. Business Intelligence Analyst (7 skills) ──────────────────────────
    (12, 33, 5, 4, 5),  # SQL
    (12, 30, 5, 4, 5),  # Data Visualization
    (12, 27, 4, 3, 4),  # Statistics
    (12, 34, 3, 2, 3),  # PostgreSQL
    (12, 14, 3, 2, 3),  # Pandas
    (12, 42, 4, 3, 4),  # Data Warehousing
    (12, 1,  3, 2, 3),  # Python

    # ── 13. Site Reliability Engineer (8 skills) ──────────────────────────────
    (13, 74, 5, 4, 5),  # Linux Administration
    (13, 65, 5, 4, 5),  # Docker
    (13, 66, 5, 4, 5),  # Kubernetes
    (13, 76, 5, 3, 5),  # Prometheus
    (13, 78, 4, 3, 4),  # Grafana
    (13, 71, 4, 3, 4),  # CI/CD
    (13, 11, 4, 3, 4),  # Bash Scripting
    (13, 1,  4, 3, 4),  # Python

    # ── 14. Mobile Developer (7 skills) ──────────────────────────────────────
    (14, 99, 5, 3, 5),  # React Native
    (14, 4,  5, 4, 5),  # JavaScript
    (14, 5,  4, 2, 4),  # TypeScript
    (14, 101, 4, 3, 4), # Mobile UI Design
    (14, 80, 4, 3, 4),  # Git
    (14, 60, 4, 3, 4),  # REST API Design
    (14, 52, 3, 2, 3),  # Jest

    # ── 15. Security Engineer (8 skills) ─────────────────────────────────────
    (15, 92, 5, 4, 5),  # Cybersecurity
    (15, 96, 5, 3, 5),  # OWASP
    (15, 94, 5, 4, 5),  # HTTPS/TLS
    (15, 93, 4, 3, 4),  # OAuth/JWT
    (15, 95, 4, 3, 4),  # Penetration Testing
    (15, 74, 4, 3, 4),  # Linux Administration
    (15, 1,  4, 3, 4),  # Python
    (15, 60, 3, 2, 3),  # REST API Design
]

assert len(CAREER_SKILL_REQUIREMENTS) == 116, (
    f"Expected 116 career-skill requirement rows, got {len(CAREER_SKILL_REQUIREMENTS)}"
)

if __name__ == "__main__":
    print(f"Skills:                      {len(SKILLS)}")
    print(f"Aliases:                     {len(SKILL_ALIASES)}")
    print(f"Prerequisite edges:          {len(SKILL_PREREQUISITES)}")
    print(f"Careers:                     {len(CAREERS)}")
    print(f"Career-skill requirements:   {len(CAREER_SKILL_REQUIREMENTS)}")
