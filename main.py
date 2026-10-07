
from llm import (
    generate_question,
    evaluate_answer,
    generate_final_report
)

from voice import speak
from speech import listen
from interviwer import adjust_difficulty

from database import (
    create_tables,
    save_interview,
    save_result
)


# ==============================
# CREATE DATABASE TABLES
# ==============================

create_tables()


# ==============================
# CANDIDATE DETAILS
# ==============================

role = input("Enter your role: ")

experience = input("Enter experience level: ")

difficulty = input(
    "Enter difficulty (Easy/Medium/Hard): "
)

difficulty = difficulty.strip().capitalize()

num_questions = int(
    input("Enter number of questions: ")
)


# ==============================
# VARIABLES
# ==============================

total_score = 0

results = []

previous_questions = []


# ==============================
# START INTERVIEW
# ==============================

print("\n==============================")
print("       AI INTERVIEWER")
print("==============================\n")


for i in range(num_questions):

    print(f"\nQuestion {i + 1}")
    print("------------------------------")


    # ==============================
    # GENERATE QUESTION
    # ==============================

    question = generate_question(
        role,
        experience,
        difficulty,
        previous_questions
    )


    # Store question so Gemini
    # does not repeat it
    previous_questions.append(question)


    # ==============================
    # DISPLAY QUESTION
    # ==============================

    print("\nAI Question:")
    print(question)


    # ==============================
    # AI SPEAKS QUESTION
    # ==============================

    speak(question)


    # ==============================
    # RECORD ANSWER
    # ==============================

    input(
        "\nPress Enter and start speaking..."
    )

    answer = listen()


    # ==============================
    # CHECK ANSWER
    # ==============================

    if not answer:

        print("\nNo answer detected.")

        continue


    # ==============================
    # DISPLAY ANSWER
    # ==============================

    print("\nYour Answer:")
    print(answer)


    # ==============================
    # EVALUATE ANSWER
    # ==============================

    evaluation = evaluate_answer(
        question,
        answer
    )


    # Safety check
    if evaluation is None:

        print("\nEvaluation failed.")

        continue


    score = evaluation["score"]


    # ==============================
    # UPDATE SCORE
    # ==============================

    total_score += score


    # ==============================
    # ADAPT DIFFICULTY
    # ==============================

    difficulty = adjust_difficulty(
        difficulty,
        score
    )


    print(
        f"\nNext Question Difficulty: "
        f"{difficulty}"
    )


    # ==============================
    # SHOW EVALUATION
    # ==============================

    print("\nEvaluation")
    print("------------------------------")

    print(
        f"Score: {score}/10"
    )

    print("\nFeedback:")

    print(
        evaluation["feedback"]
    )

    print("\nStrengths:")

    print(
        evaluation["strengths"]
    )

    print("\nImprovements:")

    print(
        evaluation["improvements"]
    )


    # ==============================
    # STORE RESULT
    # ==============================

    results.append({

        "question": question,

        "answer": answer,

        "score": score,

        "feedback":
            evaluation["feedback"],

        "strengths":
            evaluation["strengths"],

        "improvements":
            evaluation["improvements"]

    })


# ==============================
# INTERVIEW COMPLETED
# ==============================

print("\n==============================")
print("       INTERVIEW COMPLETED")
print("==============================")


answered_questions = len(results)


# ==============================
# CHECK ANSWERS
# ==============================

if answered_questions > 0:

    average_score = (
        total_score /
        answered_questions
    )


    print(
        f"\nQuestions Answered: "
        f"{answered_questions}"
    )


    print(
        f"Total Score: "
        f"{total_score}/"
        f"{answered_questions * 10}"
    )


    print(
        f"Average Score: "
        f"{average_score:.2f}/10"
    )


    # ==============================
    # FINAL REPORT
    # ==============================

    print("\n==============================")
    print("       FINAL INTERVIEW REPORT")
    print("==============================")


    final_report = generate_final_report(
        results,
        role,
        experience
    )


    # ==============================
    # DISPLAY FINAL REPORT
    # ==============================

    print("\nOverall Summary:")

    print(
        final_report["overall_summary"]
    )


    print("\nStrengths:")

    for strength in final_report["strengths"]:

        print(f"- {strength}")


    print("\nWeaknesses:")

    for weakness in final_report["weaknesses"]:

        print(f"- {weakness}")


    print("\nTechnical Skills:")

    for skill in final_report["technical_skills"]:

        print(f"- {skill}")


    print("\nAreas for Improvement:")

    for improvement in final_report["improvements"]:

        print(f"- {improvement}")


    print("\nFinal Assessment:")

    print(
        final_report["final_assessment"]
    )


    # ==============================
    # SAVE INTERVIEW
    # ==============================

    interview_id = save_interview(

        role,

        experience,

        difficulty,

        num_questions,

        answered_questions,

        total_score,

        average_score,

        final_report["overall_summary"],

        final_report["final_assessment"]

    )


    # ==============================
    # SAVE EACH QUESTION RESULT
    # ==============================

    for result in results:

        save_result(

            interview_id,

            result["question"],

            result["answer"],

            result["score"],

            result["feedback"],

            result["strengths"],

            result["improvements"]

        )


    print(
        "\nInterview saved successfully!"
    )

    print(
        f"Interview ID: {interview_id}"
    )


else:

    print("\nNo questions were answered.")


# ==============================
# END
# ==============================

print(
    "\nThank you for attending the interview!"
)