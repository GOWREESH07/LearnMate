import os
import uuid
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()
from app.services.database import get_service_supabase

sb = get_service_supabase()
if not sb:
    print("Error: Could not connect to Supabase service client.")
    exit(1)

uid = "d875d16e-c779-4164-885e-7e89880d1b6c"
print(f"Seeding full module data for user: {uid}")

# 1. Update Profile
print("1. Updating profile...")
sb.table("profiles").upsert({
    "id": uid,
    "name": "Gowreesh",
    "target_career": "Machine Learning Engineer",
    "interests": ["Artificial Intelligence", "Machine Learning", "Data Science", "Python"],
    "study_pace": "moderate",
    "streak_days": 7,
    "onboarding_done": True,
    "updated_at": datetime.utcnow().isoformat(),
}).execute()

# Fetch courses and topics
courses = sb.table("courses").select("id, title, subject").execute().data or []
topics = sb.table("topics").select("id, title, course_id").execute().data or []

topic_by_title = {t["title"]: t["id"] for t in topics}

# 2. Topic Progress (State Pattern)
print("2. Seeding topic progress...")
# Distribute states across topics
states_map = {
    # Mastered
    "Linear Algebra": "mastered",
    "Data Wrangling with Pandas": "mastered",
    "Data Visualization": "mastered",
    "Algebraic Structures": "mastered",
    "Algorithm Design & Analysis": "mastered",
    # Practicing
    "Regression Analysis": "practicing",
    "Classification Algorithms": "practicing",
    "Data Structures": "practicing",
    "Statistics & Probability": "practicing",
    # In Progress
    "Natural Language Processing": "in_progress",
    "Deep Learning & Neural Networks": "in_progress",
    "Machine Learning Basics": "in_progress",
    "Feature Engineering": "in_progress",
    "Clustering & Unsupervised Learning": "in_progress",
}

for title, state in states_map.items():
    t_id = topic_by_title.get(title)
    if t_id:
        sb.table("topic_progress").upsert({
            "user_id": uid,
            "topic_id": t_id,
            "state": state,
            "updated_at": datetime.utcnow().isoformat(),
        }, on_conflict="user_id,topic_id").execute()

# Fill rest of topics as not_started if not set
for t in topics[:20]:
    if t["title"] not in states_map:
        sb.table("topic_progress").upsert({
            "user_id": uid,
            "topic_id": t["id"],
            "state": "not_started",
            "updated_at": datetime.utcnow().isoformat(),
        }, on_conflict="user_id,topic_id").execute()

# 3. Quizzes & Questions
print("3. Seeding quizzes & questions...")
quiz_data = [
    {
        "topic": "Linear Algebra",
        "title": "Linear Algebra Essentials Quiz",
        "difficulty": "intermediate",
        "questions": [
            {
                "question_text": "What is the result of multiplying a matrix by its inverse?",
                "options": ["Zero matrix", "Identity matrix", "Diagonal matrix", "Transpose matrix"],
                "correct_answer": "Identity matrix",
                "explanation": "Multiplying any invertible matrix by its inverse yields the identity matrix I."
            },
            {
                "question_text": "What does an eigenvalue of a matrix represent?",
                "options": ["A scalar that scales the eigenvector", "The determinant of the matrix", "The rank of the matrix", "The dimension of the null space"],
                "correct_answer": "A scalar that scales the eigenvector",
                "explanation": "If Av = λv, then λ is the eigenvalue scaling eigenvector v without changing its direction."
            },
            {
                "question_text": "What is the dot product of two orthogonal vectors?",
                "options": ["1", "0", "-1", "Undefined"],
                "correct_answer": "0",
                "explanation": "Two vectors are perpendicular (orthogonal) if and only if their dot product equals 0."
            },
            {
                "question_text": "Which operation is NOT valid for matrices A and B of unequal dimensions?",
                "options": ["Scalar multiplication", "Transpose of A", "Element-wise addition", "Trace calculation"],
                "correct_answer": "Element-wise addition",
                "explanation": "Matrix addition requires both matrices to have the exact same dimensions."
            },
            {
                "question_text": "What does the rank of a matrix signify?",
                "options": ["Number of columns", "Number of linearly independent rows or columns", "Total number of elements", "Value of the largest element"],
                "correct_answer": "Number of linearly independent rows or columns",
                "explanation": "The rank represents the maximum number of linearly independent row or column vectors."
            }
        ]
    },
    {
        "topic": "Machine Learning Basics",
        "title": "ML Foundations Assessment",
        "difficulty": "beginner",
        "questions": [
            {
                "question_text": "Which of the following is a supervised learning task?",
                "options": ["K-Means Clustering", "Linear Regression", "PCA Dimensionality Reduction", "Anomaly Detection"],
                "correct_answer": "Linear Regression",
                "explanation": "Linear regression uses labeled ground-truth training data, making it supervised."
            },
            {
                "question_text": "What is overfitting in a machine learning model?",
                "options": ["Model performs well on training data but poorly on test data", "Model cannot learn the training data patterns", "Model requires too much GPU memory", "Model has too few parameters"],
                "correct_answer": "Model performs well on training data but poorly on test data",
                "explanation": "Overfitting happens when a model learns noise in the training set and fails to generalize."
            },
            {
                "question_text": "What is the primary purpose of the validation set?",
                "options": ["To train model weights", "To tune hyperparameters and prevent overfitting", "To present final accuracy to clients", "To augment image data"],
                "correct_answer": "To tune hyperparameters and prevent overfitting",
                "explanation": "Validation sets provide an unbiased evaluation while tuning hyperparameters."
            },
            {
                "question_text": "Which metric is best for evaluating an imbalanced classification dataset?",
                "options": ["Accuracy", "F1-Score / PR-AUC", "Mean Squared Error", "R-squared"],
                "correct_answer": "F1-Score / PR-AUC",
                "explanation": "Accuracy can be misleading on imbalanced classes; F1-score balances precision and recall."
            },
            {
                "question_text": "What does Gradient Descent optimize?",
                "options": ["The learning rate", "The objective/loss function", "The batch size", "The number of hidden layers"],
                "correct_answer": "The objective/loss function",
                "explanation": "Gradient descent iteratively adjusts parameters to minimize the loss function."
            }
        ]
    },
    {
        "topic": "Data Wrangling with Pandas",
        "title": "Pandas Data Mastery",
        "difficulty": "beginner",
        "questions": [
            {
                "question_text": "Which Pandas function is used to handle missing values?",
                "options": ["df.dropna() or df.fillna()", "df.clean()", "df.remove_empty()", "df.null_fix()"],
                "correct_answer": "df.dropna() or df.fillna()",
                "explanation": "dropna removes missing values, while fillna replaces them with a specified value or strategy."
            },
            {
                "question_text": "How do you group data by a column and calculate the mean?",
                "options": ["df.group_by('col').mean()", "df.groupby('col').mean()", "df.aggregate('col', 'mean')", "df.cluster('col').avg()"],
                "correct_answer": "df.groupby('col').mean()",
                "explanation": "df.groupby('col').mean() is the canonical syntax in Pandas."
            },
            {
                "question_text": "What does df.merge() perform by default?",
                "options": ["Outer join", "Inner join", "Left join", "Cross join"],
                "correct_answer": "Inner join",
                "explanation": "Pandas merge defaults to how='inner'."
            },
            {
                "question_text": "Which attribute returns the dimensions of a DataFrame?",
                "options": ["df.length", "df.size", "df.shape", "df.dims"],
                "correct_answer": "df.shape",
                "explanation": "df.shape returns a tuple (num_rows, num_columns)."
            },
            {
                "question_text": "How can you filter rows where column 'age' is greater than 25?",
                "options": ["df[df['age'] > 25]", "df.filter('age > 25')", "df.select(age > 25)", "df.where('age' > 25)"],
                "correct_answer": "df[df['age'] > 25]",
                "explanation": "Boolean indexing with df[df['age'] > 25] selects matching rows."
            }
        ]
    }
]

created_quiz_ids = []
for q in quiz_data:
    t_id = topic_by_title.get(q["topic"])
    if not t_id:
        continue
    # Check if quiz exists
    existing = sb.table("quizzes").select("id").eq("topic_id", t_id).eq("title", q["title"]).execute().data
    if existing:
        qid = existing[0]["id"]
    else:
        qid = str(uuid.uuid4())
        sb.table("quizzes").insert({
            "id": qid,
            "topic_id": t_id,
            "title": q["title"],
            "difficulty": q["difficulty"],
            "generated_by": "ai",
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
        for idx, qq in enumerate(q["questions"]):
            sb.table("quiz_questions").insert({
                "id": str(uuid.uuid4()),
                "quiz_id": qid,
                "question_text": qq["question_text"],
                "options": qq["options"],
                "correct_answer": qq["correct_answer"],
                "explanation": qq["explanation"],
            }).execute()
    created_quiz_ids.append((qid, q["title"]))

# 4. Quiz Attempts
print("4. Seeding quiz attempts...")
past_dates = [
    datetime.utcnow() - timedelta(days=5),
    datetime.utcnow() - timedelta(days=3),
    datetime.utcnow() - timedelta(days=1),
]
scores = [90.0, 80.0, 100.0]

for idx, (qid, qtitle) in enumerate(created_quiz_ids[:3]):
    sb.table("quiz_attempts").insert({
        "id": str(uuid.uuid4()),
        "user_id": uid,
        "quiz_id": qid,
        "score": scores[idx % len(scores)],
        "answers": {"q1": "correct", "q2": "correct", "q3": "correct"},
        "completed_at": past_dates[idx % len(past_dates)].isoformat(),
    }).execute()

# 5. Study Plans & Items (Builder Pattern)
print("5. Seeding study plan items...")
existing_plans = sb.table("study_plans").select("id").eq("user_id", uid).execute().data or []
if not existing_plans:
    plan_id = str(uuid.uuid4())
    sb.table("study_plans").insert({
        "id": plan_id,
        "user_id": uid,
        "title": "ML Fundamentals Sprint",
        "goal": "Master Machine Learning and Deep Learning Foundations",
        "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=30)).isoformat(),
        "status": "active",
    }).execute()
else:
    plan_id = existing_plans[0]["id"]

# Add study plan items
study_topics = [
    ("Linear Algebra", 0, True),
    ("Machine Learning Basics", 2, True),
    ("Regression Analysis", 4, False),
    ("Classification Algorithms", 7, False),
    ("Deep Learning & Neural Networks", 10, False),
    ("Natural Language Processing", 14, False),
]

for title, day_offset, completed in study_topics:
    t_id = topic_by_title.get(title)
    if t_id:
        sb.table("study_plan_items").insert({
            "id": str(uuid.uuid4()),
            "study_plan_id": plan_id,
            "topic_id": t_id,
            "scheduled_date": (date.today() + timedelta(days=day_offset)).isoformat(),
            "duration_minutes": 45,
            "completed": completed,
        }).execute()

# 6. Achievements (Decorator / Gamification Pattern)
print("6. Seeding achievements...")
achievements_list = [
    ("First Step Taken", "Completed your very first study module session.", "trophy"),
    ("7-Day Streak Master", "Maintained an unbroken study streak for 7 consecutive days.", "flame"),
    ("Math Wizard", "Achieved 90%+ mastery on the Linear Algebra assessment.", "zap"),
    ("AI Pioneer", "Began the journey toward becoming a Machine Learning Engineer.", "star"),
]

for title, desc, icon in achievements_list:
    sb.table("achievements").insert({
        "id": str(uuid.uuid4()),
        "user_id": uid,
        "title": title,
        "description": desc,
        "badge_icon": icon,
        "earned_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
    }).execute()

# 7. Performance Predictions
print("7. Seeding performance predictions...")
predictions_list = [
    ("Linear Algebra", 94.5, 0.92, "High quiz average and steady practice indicate advanced mastery of vector spaces."),
    ("Regression Analysis", 88.0, 0.85, "Consistent engagement with prerequisite math suggests strong regression comprehension."),
    ("Deep Learning & Neural Networks", 84.0, 0.80, "Solid foundational algorithms readiness; practice with PyTorch will accelerate mastery."),
]

for title, pred_score, conf, rationale in predictions_list:
    t_id = topic_by_title.get(title)
    if t_id:
        sb.table("performance_predictions").upsert({
            "user_id": uid,
            "topic_id": t_id,
            "predicted_score": pred_score,
            "confidence": conf,
            "rationale": rationale,
            "generated_at": datetime.utcnow().isoformat(),
        }, on_conflict="user_id,topic_id").execute()

# 8. Collaborative Groups & Group Members
print("8. Seeding collaborative groups & memberships...")
groups = [
    {
        "id": str(uuid.uuid4()),
        "name": "AI & Machine Learning Circle",
        "description": "Collaborative study group discussing Deep Learning, NLP, and Gemini AI models.",
        "created_by": uid,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Data Science Pioneers",
        "description": "Hands-on data analysis and model building with Pandas, Scikit-Learn, and PyTorch.",
        "created_by": uid,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Algorithms & Math Prep",
        "description": "Weekly deep dives into core algorithms, dynamic programming, and mathematical proofs.",
        "created_by": uid,
    },
]

for g in groups:
    sb.table("collaborative_groups").upsert(g).execute()
    sb.table("group_members").upsert({
        "group_id": g["id"],
        "user_id": uid,
        "joined_at": datetime.utcnow().isoformat(),
    }, on_conflict="group_id,user_id").execute()

# 9. Notifications (Observer Pattern)
print("9. Seeding notifications...")
notifications_list = [
    ("achievement_unlocked", "Achievement Unlocked!", "You earned the '7-Day Streak Master' badge! Keep up the momentum!"),
    ("study_reminder", "Study Session Today", "Your session on 'Regression Analysis' is scheduled for today (45 min)."),
    ("quiz_generated", "Practice Quiz Ready", "Test your knowledge on 'Classification Algorithms' with a 5-question AI quiz."),
    ("recommendation", "Career Path Recommendation", "Based on your goal as Machine Learning Engineer, we recommend exploring 'Deep Learning & Neural Networks'."),
]

for n_type, title, msg in notifications_list:
    sb.table("notifications").insert({
        "id": str(uuid.uuid4()),
        "user_id": uid,
        "type": n_type,
        "title": title,
        "message": msg,
        "read": False,
        "metadata": {"action": "open"},
        "created_at": datetime.utcnow().isoformat(),
    }).execute()

print("✅ All modules populated with rich data tailored to Gowreesh (Machine Learning Engineer)!")
