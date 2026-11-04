"""
Seed script to populate courses, topics, resources, and study groups into Supabase.
"""

import os
import uuid
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing from environment.")
    exit(1)

sb = create_client(url, key)

print("🚀 Starting database seeding...")

# 1. COURSES DATA
COURSES = [
    {
        "id": str(uuid.uuid4()),
        "title": "Advanced Mathematics",
        "subject": "Mathematics",
        "difficulty_level": "intermediate",
        "description": "Comprehensive journey from foundational algebra to calculus, linear algebra, and graph theory.",
        "total_topics": 9,
        "topics": [
            ("Algebraic Structures", "Groups, rings, fields, and foundational abstract algebra concepts."),
            ("Calculus & Analysis", "Limits, derivatives, integrals, and differential equations."),
            ("Statistics & Probability", "Probability distributions, hypothesis testing, and statistical modeling."),
            ("Linear Algebra", "Vector spaces, matrices, eigenvalues, eigenvectors, and linear transformations."),
            ("Probability Theory", "Random variables, expectation, limit theorems, and stochastic processes."),
            ("Trigonometry & Geometry", "Trigonometric functions, identities, vector geometry, and coordinate systems."),
            ("Discrete Mathematics", "Combinatorics, graph theory, logic, and set theory."),
            ("Number Theory", "Prime numbers, modular arithmetic, cryptography, and Diophantine equations."),
            ("Graph Theory", "Graphs, trees, network flows, graph algorithms, and connectivity."),
        ],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Computer Science Fundamentals",
        "subject": "Computer Science",
        "difficulty_level": "intermediate",
        "description": "Master core computational concepts from algorithms and data structures to operating systems and networks.",
        "total_topics": 9,
        "topics": [
            ("Algorithm Design & Analysis", "Asymptotic analysis, greedy algorithms, dynamic programming, and divide-and-conquer."),
            ("Data Structures", "Arrays, linked lists, trees, graphs, heaps, hash tables, and priority queues."),
            ("Object-Oriented Programming", "Encapsulation, inheritance, polymorphism, design patterns, and SOLID principles."),
            ("Database Systems", "Relational databases, SQL, indexing, transactions, ACID properties, and NoSQL."),
            ("Computer Networks", "TCP/IP stack, OSI model, HTTP/HTTPS, routing, DNS, and network sockets."),
            ("Operating Systems", "Process management, threads, memory allocation, virtual memory, and file systems."),
            ("Cybersecurity Essentials", "Encryption, authentication, authorization, web vulnerabilities, and network security."),
            ("Compiler Principles", "Lexical analysis, parsing, AST generation, optimization, and code generation."),
            ("Machine Learning Basics", "Supervised and unsupervised learning algorithms, evaluation, and feature engineering."),
        ],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Modern Biology",
        "subject": "Biology",
        "difficulty_level": "beginner",
        "description": "Explore the living world from cellular machinery and genetics to ecology and organismal physiology.",
        "total_topics": 9,
        "topics": [
            ("Cell Biology", "Cell structure, organelles, membrane transport, and cellular energy production."),
            ("Genetics & Genomics", "DNA replication, transcription, translation, Mendelian genetics, and CRISPR."),
            ("Evolutionary Biology", "Natural selection, speciation, phylogenetics, and population genetics."),
            ("Ecology & Ecosystems", "Biomes, food webs, nutrient cycles, population dynamics, and conservation biology."),
            ("Biochemistry", "Proteins, nucleic acids, lipids, carbohydrates, and metabolic pathways."),
            ("Human Physiology", "Organ systems, homeostasis, nervous system, and cardiovascular function."),
            ("Microbiology", "Bacteria, viruses, fungi, immunology, and host-pathogen interactions."),
            ("Plant Biology", "Photosynthesis, plant anatomy, growth hormones, and vascular systems."),
            ("Animal Behavior & Zoology", "Ethology, animal diversity, adaptation, and comparative anatomy."),
        ],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Physics Mastery",
        "subject": "Physics",
        "difficulty_level": "advanced",
        "description": "Deep dive into physical principles governing the universe, from classical mechanics to quantum physics.",
        "total_topics": 9,
        "topics": [
            ("Classical Mechanics", "Newtonian laws, work-energy theorem, momentum, rotational dynamics, and gravity."),
            ("Electromagnetism", "Electric fields, magnetic forces, Maxwell equations, and electromagnetic waves."),
            ("Thermodynamics", "Laws of thermodynamics, entropy, heat engines, and statistical mechanics."),
            ("Wave Mechanics", "Harmonic oscillators, wave propagation, interference, diffraction, and resonance."),
            ("Optics & Light", "Geometric optics, physical optics, reflection, refraction, and lasers."),
            ("Quantum Physics", "Wave-particle duality, Schrödinger equation, quantum states, and entanglement."),
            ("Relativity Theory", "Special and General Relativity, spacetime geometry, and gravitational waves."),
            ("Nuclear & Particle Physics", "Radioactive decay, nuclear fission/fusion, and the Standard Model."),
            ("Astrophysics & Cosmology", "Stellar evolution, black holes, the Big Bang theory, and dark matter."),
        ],
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Data Science in Practice",
        "subject": "Data Science",
        "difficulty_level": "intermediate",
        "description": "Practical data analysis, machine learning pipelines, visualization, and deep learning techniques.",
        "total_topics": 9,
        "topics": [
            ("Data Wrangling with Pandas", "Data cleaning, filtering, aggregation, merging, and reshaping dataframes."),
            ("Data Visualization", "Matplotlib, Seaborn, interactive plots, and storytelling with data."),
            ("Regression Analysis", "Linear regression, multiple regression, regularization (Ridge/Lasso), and diagnostics."),
            ("Classification Algorithms", "Logistic regression, decision trees, random forests, and SVMs."),
            ("Clustering & Unsupervised Learning", "K-means, hierarchical clustering, PCA, and dimensionality reduction."),
            ("Natural Language Processing", "Text preprocessing, TF-IDF, word embeddings, transformers, and sentiment analysis."),
            ("Deep Learning & Neural Networks", "Perceptrons, backpropagation, CNNs, RNNs, and PyTorch fundamentals."),
            ("Feature Engineering", "Scaling, encoding categorical variables, feature selection, and imputation."),
            ("Model Evaluation & Deployment", "Cross-validation, hyperparameter tuning, ROC-AUC, and API deployment."),
        ],
    },
]

# Clean existing courses and topics to ensure clean re-seed
try:
    print("Cleaning old seed data...")
    sb.table("learning_resources").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    sb.table("topics").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    sb.table("courses").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    sb.table("collaborative_groups").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
except Exception as e:
    print("Clean notice:", e)

# Insert Courses & Topics
inserted_courses = 0
inserted_topics = 0
inserted_resources = 0

for course_data in COURSES:
    topics_list = course_data.pop("topics")
    c_res = sb.table("courses").insert(course_data).execute()
    course_id = course_data["id"]
    inserted_courses += 1

    for idx, (t_title, t_desc) in enumerate(topics_list):
        t_id = str(uuid.uuid4())
        topic_row = {
            "id": t_id,
            "course_id": course_id,
            "title": t_title,
            "description": t_desc,
            "order_index": idx,
        }
        sb.table("topics").insert(topic_row).execute()
        inserted_topics += 1

        # Add 2 learning resources per topic
        resources = [
            {
                "id": str(uuid.uuid4()),
                "topic_id": t_id,
                "type": "video",
                "title": f"Video Lecture: {t_title}",
                "url": f"https://www.youtube.com/results?search_query={t_title.replace(' ', '+')}",
                "source": "YouTube Education",
                "duration": 25,
            },
            {
                "id": str(uuid.uuid4()),
                "topic_id": t_id,
                "type": "article",
                "title": f"Comprehensive Guide to {t_title}",
                "url": f"https://en.wikipedia.org/wiki/Special:Search?search={t_title.replace(' ', '+')}",
                "source": "Wikipedia / Academic Notes",
                "duration": 15,
            },
        ]
        for r in resources:
            sb.table("learning_resources").insert(r).execute()
            inserted_resources += 1

# Insert Study Groups
GROUPS = [
    {
        "id": str(uuid.uuid4()),
        "name": "AI & Machine Learning Circle",
        "description": "Collaborative study group discussing Deep Learning, NLP, and Gemini AI integration.",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Quantum & Classical Physics Society",
        "description": "Weekly problem sets and conceptual deep dives in Mechanics, Quantum, and Relativity.",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Algorithms & Data Structures Prep",
        "description": "Mastering technical interview algorithms, dynamic programming, and system design.",
    },
]

for g in GROUPS:
    try:
        sb.table("collaborative_groups").insert(g).execute()
    except Exception as e:
        print("Group insert notice:", e)

print(f"✅ Seeding complete!")
print(f"   • Courses created: {inserted_courses}")
print(f"   • Topics created: {inserted_topics}")
print(f"   • Resources created: {inserted_resources}")
print(f"   • Study Groups created: {len(GROUPS)}")
