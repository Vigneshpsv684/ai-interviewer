from pdf_report import create_interview_pdf
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    send_file,
    redirect,
     url_for
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from werkzeug.utils import secure_filename
import os

from llm import (
    generate_question,
    generate_resume_question,
    evaluate_answer,
    generate_final_report
)

from interviwer import adjust_difficulty

from database import (
    create_tables,
    save_interview,
    save_result,
    get_all_interviews,
    get_interview,
    get_interview_results,
    get_interview_statistics,
    get_score_distribution,
    get_performance_analysis,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_interview_for_user,
)

from voice import speak
from speech import listen

from resume_parser import extract_resume_text

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# =========================================================
# FLASK SECRET KEY
# =========================================================

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY"
)

if not app.secret_key:
    raise RuntimeError(
        "FLASK_SECRET_KEY is not configured."
    )


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

create_tables()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not username or not email or not password:
            return render_template(
                "register.html",
                error="All fields are required."
            )

        if password != confirm_password:
            return render_template(
                "register.html",
                error="Passwords do not match."
            )

        if len(password) < 6:
            return render_template(
                "register.html",
                error="Password must contain at least 6 characters."
            )

        hashed_password = generate_password_hash(
            password
        )

        user_id = create_user(
            username,
            email,
            hashed_password
        )

        if user_id is None:
            return render_template(
                "register.html",
                error="Username or email already exists."
            )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        user = get_user_by_email(email)

        if not user:

            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        if not check_password_hash(
            user[3],
            password
        ):

            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        session.clear()

        session["user_id"] = user[0]
        session["username"] = user[1]
        session["email"] = user[2]
        session["logged_in"] = True

        return redirect(
            url_for("home")
        )

    return render_template(
        "login.html"
    )
@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )
# =========================================================
# STANDARD INTERVIEW
# =========================================================

@app.route("/interview")
def interview():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Get interview details

    role = request.args.get("role")

    experience = request.args.get(
        "experience"
    )

    difficulty = request.args.get(
        "difficulty"
    )

    num_questions = int(
        request.args.get(
            "num_questions",
            5
        )
    )


    # Validate input

    if not role:

        return "Role is required.", 400

    if not experience:

        return "Experience is required.", 400


    # Normalize difficulty

    difficulty = difficulty.strip().capitalize()


    if difficulty not in [
        "Easy",
        "Medium",
        "Hard"
    ]:

        difficulty = "Easy"


    # Generate first question

    question = generate_question(

        role,

        experience,

        difficulty,

        []

    )


    # =====================================================
    # STORE INTERVIEW INFORMATION
    # =====================================================

    session["role"] = role

    session["experience"] = experience

    session["difficulty"] = difficulty

    session["initial_difficulty"] = difficulty

    session["num_questions"] = num_questions

    session["current_question_number"] = 1

    session["previous_questions"] = [
        question
    ]

    session["results"] = []

    # Important:
    # This tells /evaluate that this is
    # a standard interview.

    session["interview_mode"] = "standard"

    # Remove old resume data

    session.pop(
        "resume_text",
        None
    )


    # =====================================================
    # DISPLAY INTERVIEW PAGE
    # =====================================================

    return render_template(

        "interview.html",

        role=role,

        experience=experience,

        difficulty=difficulty,

        question=question,

        question_number=1,

        total_questions=num_questions

    )


# =========================================================
# RESUME-BASED INTERVIEW
# =========================================================

@app.route(
    "/resume-interview",
    methods=["POST"]
)
def resume_interview():
    if "user_id" not in session:
        return redirect(url_for("login"))
    # Get uploaded resume

    resume = request.files.get(
        "resume"
    )


    # Get form information

    experience = request.form.get(
        "experience"
    )

    difficulty = request.form.get(
        "difficulty",
        "Easy"
    )

    num_questions = int(
        request.form.get(
            "num_questions",
            5
        )
    )


    # =====================================================
    # VALIDATE RESUME
    # =====================================================

    if not resume:

        return (
            "Resume is required.",
            400
        )


    if not resume.filename:

        return (
            "Invalid resume.",
            400
        )
    safe_filename = secure_filename(
    resume.filename
)

    if not safe_filename:
        return "Invalid resume filename.", 400

    # Get extension

    extension = os.path.splitext(
        resume.filename
    )[1].lower()


    # Only allow PDF and DOCX

    if extension not in [
        ".pdf",
        ".docx"
    ]:

        return (
            "Only PDF and DOCX resumes "
            "are supported.",
            400
        )


    # =====================================================
    # VALIDATE EXPERIENCE
    # =====================================================

    if not experience:

        return (
            "Experience is required.",
            400
        )


    # =====================================================
    # NORMALIZE DIFFICULTY
    # =====================================================

    difficulty = difficulty.strip().capitalize()


    if difficulty not in [
        "Easy",
        "Medium",
        "Hard"
    ]:

        difficulty = "Easy"


    # =====================================================
    # CREATE UPLOAD DIRECTORY
    # =====================================================

    upload_folder = os.path.join(app.root_path, "uploads")
    os.makedirs(upload_folder, exist_ok=True)


    # =====================================================
    # SAVE RESUME
    # =====================================================

    safe_filename = secure_filename(resume.filename)
    file_path = os.path.join(upload_folder, safe_filename)


    resume.save(file_path)


    # =====================================================
    # EXTRACT RESUME TEXT
    # =====================================================

    try:
        resume_text = extract_resume_text(file_path)
    except Exception as error:
        return (
            f"Could not read resume: {error}",
            500
        )

    try:
        os.remove(file_path)
    except OSError:
        pass

    session["resume_text"] = resume_text


    # Check extracted text

    if not resume_text.strip():

        return (
            "Could not extract text "
            "from the resume.",
            400
        )


    # =====================================================
    # GENERATE FIRST RESUME QUESTION
    # =====================================================

    question = generate_resume_question(

        resume_text,

        experience,

        difficulty,

        []

    )


    # =====================================================
    # STORE RESUME INTERVIEW INFORMATION
    # =====================================================

    session["role"] = "Resume-Based Interview"

    session["experience"] = experience

    session["difficulty"] = difficulty

    session["initial_difficulty"] = difficulty

    session["num_questions"] = num_questions

    session["current_question_number"] = 1

    session["previous_questions"] = [
        question
    ]

    session["results"] = []


    # Store resume text

    session["resume_text"] = resume_text


    # Tell the evaluation route
    # that this is a resume interview

    session["interview_mode"] = "resume"


    # =====================================================
    # DISPLAY INTERVIEW PAGE
    # =====================================================

    return render_template(

        "interview.html",

        role="Resume-Based Interview",

        experience=experience,

        difficulty=difficulty,

        question=question,

        question_number=1,

        total_questions=num_questions

    )


# =========================================================
# EVALUATE ANSWER
# =========================================================

@app.route(
    "/evaluate",
    methods=["POST"]
)
def evaluate():

    # Get JSON data

    data = request.get_json()


    question = data.get(
        "question"
    )

    answer = data.get(
        "answer"
    )


    # =====================================================
    # VALIDATE INPUT
    # =====================================================

    if not question or not answer:

        return jsonify({

            "error":
            "Question and answer are required."

        }), 400


    # =====================================================
    # AI EVALUATION
    # =====================================================

    evaluation = evaluate_answer(

        question,

        answer

    )


    if evaluation is None:

        return jsonify({

            "error":
            "Could not evaluate the answer."

        }), 500


    # Get score

    score = int(
        evaluation["score"]
    )


    # =====================================================
    # STORE CURRENT RESULT
    # =====================================================

    result = {

        "question": question,

        "answer": answer,

        "score": score,

        "feedback":
            evaluation["feedback"],

        "strengths":
            evaluation["strengths"],

        "improvements":
            evaluation["improvements"]

    }


    # Get previous results

    results = session.get(
        "results",
        []
    )


    # Add current result

    results.append(
        result
    )


    # Save back to session

    session["results"] = results


    # =====================================================
    # GET INTERVIEW INFORMATION
    # =====================================================

    current_question_number = session.get(

        "current_question_number",

        1

    )


    total_questions = session.get(

        "num_questions",

        5

    )


    current_difficulty = session.get(

        "difficulty",

        "Easy"

    )


    role = session.get(
        "role"
    )


    experience = session.get(
        "experience"
    )


    initial_difficulty = session.get(

        "initial_difficulty",

        current_difficulty

    )


    interview_mode = session.get(

        "interview_mode",

        "standard"

    )


    # =====================================================
    # CHECK IF INTERVIEW IS COMPLETED
    # =====================================================

    if current_question_number >= total_questions:


        # -------------------------------------------------
        # Calculate total score
        # -------------------------------------------------

        total_score = sum(

            item["score"]

            for item in results

        )


        # -------------------------------------------------
        # Calculate average score
        # -------------------------------------------------

        average_score = (

            total_score /
            len(results)

        )


        # -------------------------------------------------
        # Generate final AI report
        # -------------------------------------------------

        final_report = generate_final_report(

            results,

            role,

            experience

        )


        # =================================================
        # SAVE COMPLETE INTERVIEW
        # =================================================

        interview_id = save_interview(
            session["user_id"],
            role,

            experience,

            initial_difficulty,

            total_questions,

            len(results),

            total_score,

            average_score,

            final_report[
                "overall_summary"
            ],

            final_report[
                "final_assessment"
            ]

        )


        # =================================================
        # SAVE EACH QUESTION RESULT
        # =================================================

        for item in results:

            save_result(

                interview_id,

                item["question"],

                item["answer"],

                item["score"],

                item["feedback"],

                item["strengths"],

                item["improvements"]

            )


        # Store interview ID

        session["interview_id"] = (
            interview_id
        )


        # =================================================
        # FINAL RESPONSE
        # =================================================

        return jsonify({

            "completed": True,

            "score": score,

            "feedback":
                evaluation["feedback"],

            "strengths":
                evaluation["strengths"],

            "improvements":
                evaluation["improvements"],

            "final_report":
                final_report,

            "total_score":
                total_score,

            "average_score":
                average_score

        })


    # =====================================================
    # ADAPTIVE DIFFICULTY
    # =====================================================

    new_difficulty = adjust_difficulty(

        current_difficulty,

        score

    )


    # Save new difficulty

    session["difficulty"] = (
        new_difficulty
    )


    # =====================================================
    # MOVE TO NEXT QUESTION
    # =====================================================

    next_question_number = (

        current_question_number + 1

    )


    session["current_question_number"] = (

        next_question_number

    )


    # =====================================================
    # GET PREVIOUS QUESTIONS
    # =====================================================

    previous_questions = session.get(

        "previous_questions",

        []

    )


    # =====================================================
    # GENERATE NEXT QUESTION
    # =====================================================

    if interview_mode == "resume":

        # Resume-based question

        resume_text = session.get(

            "resume_text",

            ""

        )


        next_question = generate_resume_question(

            resume_text,

            experience,

            new_difficulty,

            previous_questions

        )

    else:

        # Standard question

        next_question = generate_question(

            role,

            experience,

            new_difficulty,

            previous_questions

        )


    # =====================================================
    # ADD QUESTION TO HISTORY
    # =====================================================

    previous_questions.append(

        next_question

    )


    session["previous_questions"] = (

        previous_questions

    )


    # =====================================================
    # SEND NEXT QUESTION
    # =====================================================

    return jsonify({

        "completed": False,

        "score": score,

        "feedback":
            evaluation["feedback"],

        "strengths":
            evaluation["strengths"],

        "improvements":
            evaluation["improvements"],

        "next_question":
            next_question,

        "next_difficulty":
            new_difficulty,

        "question_number":
            next_question_number,

        "total_questions":
            total_questions

    })


# =========================================================
# INTERVIEW HISTORY
# =========================================================

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    interviews = get_all_interviews()

    statistics = get_interview_statistics()

    score_distribution = get_score_distribution()

    performance = get_performance_analysis()

    return render_template(
        "history.html",
        interviews=interviews,
        statistics=statistics,
        score_distribution=score_distribution,
        performance=performance
    )

# =========================================================
# INTERVIEW DETAILS
# =========================================================

@app.route(
    "/history/<int:interview_id>"
)
def interview_details(
    interview_id
):
    if "user_id" not in session:
        return redirect(url_for("login"))

    results = get_interview_results(

        interview_id

    )


    return render_template(

        "interview_details.html",

        results=results

    )


@app.route("/history/<int:interview_id>/pdf")
def download_interview_pdf(interview_id):

    # =====================================================
    # GET INTERVIEW
    # =====================================================
    if "user_id" not in session:
        return redirect(url_for("login"))
    interview = get_interview(
        interview_id,
        session["user_id"]
    )


    if not interview:

        return "Interview not found.", 404


    # =====================================================
    # GET QUESTION RESULTS
    # =====================================================

    results = get_interview_results(
        interview_id
    )

    # =====================================================
    # GENERATE PDF
    # =====================================================

    pdf_buffer = create_interview_pdf(
        interview,
        results
    )


    # =====================================================
    # FILE NAME
    # =====================================================

    role = interview[1]

    safe_role = "".join(

        character
        for character in str(role)

        if character.isalnum()
        or character in " _-"

    ).strip()


    if not safe_role:

        safe_role = "interview"


    filename = (
        f"AI_Interview_Report_"
        f"{safe_role}_"
        f"{interview_id}.pdf"
    )


    # =====================================================
    # SEND PDF
    # =====================================================

    return send_file(

        pdf_buffer,

        mimetype="application/pdf",

        as_attachment=True,

        download_name=filename
    )
# =========================================================
# TEXT TO SPEECH
# =========================================================

@app.route(
    "/speak",
    methods=["POST"]
)
def speak_question():

    data = request.get_json()


    question = data.get(
        "question"
    )


    if not question:

        return jsonify({

            "error":
            "Question is required."

        }), 400


    speak(
        question
    )


    return jsonify({

        "success": True

    })


# =========================================================
# SPEECH TO TEXT
# =========================================================

@app.route(
    "/listen",
    methods=["POST"]
)
def listen_answer():

    answer = listen()


    if not answer:

        return jsonify({

            "error":
            "Could not understand your answer."

        }), 400


    return jsonify({

        "answer": answer

    })

@app.errorhandler(413)
def request_entity_too_large(error):

    return (
        "File is too large. "
        "Maximum resume size is 5 MB.",
        413
    )
# =========================================================
# RUN FLASK APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
