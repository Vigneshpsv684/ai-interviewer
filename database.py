
import sqlite3
from abc import ABC, abstractmethod


class interview(ABC):
    """Abstract interface for interview data access and persistence."""

    @abstractmethod
    def save(
        self,
        user_id,
        role,
        experience,
        difficulty,
        total_questions,
        questions_answered,
        total_score,
        average_score,
        overall_summary,
        final_assessment,
    ):
        """Persist a completed interview and return its database id."""
        raise NotImplementedError

    @abstractmethod
    def save_result(
        self,
        interview_id,
        question,
        answer,
        score,
        feedback,
        strengths,
        improvements,
    ):
        """Persist a single answer result for an interview."""
        raise NotImplementedError

    @abstractmethod
    def get_all(self, user_id=None):
        """Return stored interviews, optionally scoped to a user."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, interview_id, user_id=None):
        """Fetch a single interview by id, optionally scoped to a user."""
        raise NotImplementedError

    @abstractmethod
    def get_results(self, interview_id):
        """Fetch all question results for a given interview."""
        raise NotImplementedError

    @abstractmethod
    def get_statistics(self, user_id):
        """Return aggregate interview statistics for a user."""
        raise NotImplementedError

    @abstractmethod
    def get_score_distribution(self, user_id):
        """Return a list of average scores across interviews for a user."""
        raise NotImplementedError

    @abstractmethod
    def get_performance_analysis(self, user_id):
        """Return recent performance trend and level for a user."""
        raise NotImplementedError


class Interview(interview):
    """Concrete interview repository backed by the SQLite database."""

    def save(
        self,
        user_id,
        role,
        experience,
        difficulty,
        total_questions,
        questions_answered,
        total_score,
        average_score,
        overall_summary,
        final_assessment,
    ):
        return save_interview(
            user_id,
            role,
            experience,
            difficulty,
            total_questions,
            questions_answered,
            total_score,
            average_score,
            overall_summary,
            final_assessment,
        )

    def save_result(
        self,
        interview_id,
        question,
        answer,
        score,
        feedback,
        strengths,
        improvements,
    ):
        return save_result(
            interview_id,
            question,
            answer,
            score,
            feedback,
            strengths,
            improvements,
        )

    def get_all(self, user_id=None):
        return get_all_interviews(user_id)

    def get_by_id(self, interview_id, user_id=None):
        if user_id is None:
            return get_interview(interview_id)
        return get_interview_for_user(interview_id, user_id)

    def get_results(self, interview_id):
        return get_interview_results(interview_id)

    def get_statistics(self, user_id):
        return get_interview_statistics(user_id)

    def get_score_distribution(self, user_id):
        return get_score_distribution(user_id)

    def get_performance_analysis(self, user_id):
        return get_performance_analysis(user_id)


class user(ABC):
    """Abstract interface for user data access and persistence."""

    @abstractmethod
    def create_user(self, username, email, password):
        """Create a new user and return the generated user id."""
        raise NotImplementedError

    @abstractmethod
    def get_user_by_email(self, email):
        """Fetch a user by email address."""
        raise NotImplementedError

    @abstractmethod
    def get_user_by_id(self, user_id):
        """Fetch a user by their internal id."""
        raise NotImplementedError


class User(user):
    """Concrete user repository backed by the SQLite database."""

    def create_user(self, username, email, password):
        return create_user(username, email, password)

    def get_user_by_email(self, email):
        return get_user_by_email(email)

    def get_user_by_id(self, user_id):
        return get_user_by_id(user_id)


# ==============================
# DATABASE CONNECTION
# ==============================

def get_connection():

    connection = sqlite3.connect("interviews.db")

    return connection


# ==============================
# CREATE TABLES
# ==============================

def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            experience TEXT,
            difficulty TEXT,
            total_questions INTEGER,
            questions_answered INTEGER,
            total_score INTEGER,
            average_score REAL,
            overall_summary TEXT,
            final_assessment TEXT
        )
    """)
    try:
        cursor.execute("""
            ALTER TABLE interviews
            ADD COLUMN user_id INTEGER
        """)
    except sqlite3.OperationalError:
        pass
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER,
            question TEXT,
            answer TEXT,
            score INTEGER,
            feedback TEXT,
            strengths TEXT,
            improvements TEXT,
            FOREIGN KEY (interview_id) REFERENCES interviews(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# ==============================
# SAVE INTERVIEW
# ==============================

def save_interview(
    user_id,
    role,
    experience,
    difficulty,
    total_questions,
    questions_answered,
    total_score,
    average_score,
    overall_summary,
    final_assessment
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO interviews (

            user_id,
            role,
            experience,
            difficulty,
            total_questions,
            questions_answered,
            total_score,
            average_score,
            overall_summary,
            final_assessment

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        user_id,
        role,
        experience,
        difficulty,
        total_questions,
        questions_answered,
        total_score,
        average_score,
        overall_summary,
        final_assessment

    ))


    interview_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return interview_id


# ==============================
# SAVE QUESTION RESULT
# ==============================

def save_result(
    interview_id,
    question,
    answer,
    score,
    feedback,
    strengths,
    improvements
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO interview_results (

            interview_id,
            question,
            answer,
            score,
            feedback,
            strengths,
            improvements

        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (

        interview_id,
        question,
        answer,
        score,
        feedback,
        strengths,
        improvements

    ))


    connection.commit()

    connection.close()

def get_all_interviews(user_id=None):

    connection = get_connection()
    cursor = connection.cursor()

    if user_id is None:
        cursor.execute("""
            SELECT
                id,
                role,
                experience,
                difficulty,
                total_questions,
                questions_answered,
                total_score,
                average_score,
                overall_summary,
                final_assessment
            FROM interviews
            ORDER BY id DESC
        """)
        interviews = cursor.fetchall()
    else:
        cursor.execute("""
            SELECT
                id,
                role,
                experience,
                difficulty,
                total_questions,
                questions_answered,
                total_score,
                average_score,
                overall_summary,
                final_assessment
            FROM interviews
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,))
        interviews = cursor.fetchall()

    connection.close()

    return interviews

def get_interview_results(interview_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            question,
            answer,
            score,
            feedback,
            strengths,
            improvements
        FROM interview_results
        WHERE interview_id = ?
        ORDER BY id
    """, (interview_id,))

    results = cursor.fetchall()

    connection.close()

    return results
def get_interview_statistics(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Total interviews
    cursor.execute("""
        SELECT COUNT(*)
        FROM interviews
        WHERE user_id = ?
    """, (user_id,))

    total_interviews = cursor.fetchone()[0]

    # Average score across all interviews
    cursor.execute("""
        SELECT AVG(average_score)
        FROM interviews
        WHERE user_id = ?
    """, (user_id,))

    overall_average = cursor.fetchone()[0]

    # Best interview score
    cursor.execute("""
        SELECT MAX(average_score)
        FROM interviews
        WHERE user_id = ?
    """, (user_id,))

    best_score = cursor.fetchone()[0]

    # Lowest interview score
    cursor.execute("""
        SELECT MIN(average_score)
        FROM interviews
        WHERE user_id = ?
    """, (user_id,))

    lowest_score = cursor.fetchone()[0]

    # Total questions answered
    cursor.execute("""
        SELECT SUM(questions_answered)
        FROM interviews
        WHERE user_id = ?
    """, (user_id,))

    total_questions_answered = cursor.fetchone()[0]

    # Average questions per interview
    cursor.execute("""
        SELECT AVG(questions_answered)
        FROM interviews
        WHERE user_id = ?
    """, (user_id,))

    average_questions = cursor.fetchone()[0]

    connection.close()

    # Handle empty database
    if overall_average is None:
        overall_average = 0

    if best_score is None:
        best_score = 0

    if lowest_score is None:
        lowest_score = 0

    if total_questions_answered is None:
        total_questions_answered = 0

    if average_questions is None:
        average_questions = 0

    return {
        "total_interviews": total_interviews,
        "overall_average": overall_average,
        "best_score": best_score,
        "lowest_score": lowest_score,
        "total_questions_answered": total_questions_answered,
        "average_questions": average_questions
    }


def get_score_distribution(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT average_score
        FROM interviews
        WHERE user_id = ?
        ORDER BY id
    """, (user_id,))

    scores = cursor.fetchall()

    connection.close()

    return [
        score[0]
        for score in scores
    ]


def get_performance_analysis(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Get interview scores in latest-first order for the current user
    cursor.execute("""
        SELECT id, average_score, questions_answered
        FROM interviews
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    interviews = cursor.fetchall()

    connection.close()

    if not interviews:
        return {
            "recent_average": 0,
            "previous_average": 0,
            "improvement": 0,
            "performance_level": "No Data"
        }

    # Latest interview score
    recent_average = interviews[0][1]

    # Previous interviews
    previous_scores = [
        interview[1]
        for interview in interviews[1:]
    ]

    if previous_scores:

        previous_average = (
            sum(previous_scores) /
            len(previous_scores)
        )

    else:

        previous_average = 0

    # Improvement
    if previous_average > 0:

        improvement = (
            (recent_average - previous_average)
            / previous_average
        ) * 100

    else:

        improvement = 0

    # Performance level
    if recent_average >= 8:
        performance_level = "Excellent"

    elif recent_average >= 6:
        performance_level = "Good"

    elif recent_average >= 4:
        performance_level = "Average"

    else:
        performance_level = "Needs Improvement"

    return {
        "recent_average": round(recent_average, 2),
        "previous_average": round(previous_average, 2),
        "improvement": round(improvement, 2),
        "performance_level": performance_level
    }
def get_interview(interview_id, user_id=None):

    connection = get_connection()

    cursor = connection.cursor()

    if user_id is None:
        cursor.execute("""
            SELECT
                id,
                role,
                experience,
                difficulty,
                total_questions,
                questions_answered,
                total_score,
                average_score,
                overall_summary,
                final_assessment
            FROM interviews
            WHERE id = ?
        """, (interview_id,))
    else:
        cursor.execute("""
            SELECT
                id,
                role,
                experience,
                difficulty,
                total_questions,
                questions_answered,
                total_score,
                average_score,
                overall_summary,
                final_assessment
            FROM interviews
            WHERE id = ?
            AND user_id = ?
        """, (interview_id, user_id))

    interview = cursor.fetchone()

    connection.close()

    return interview
def create_user(username, email, password):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO users (
                username,
                email,
                password
            )
            VALUES (?, ?, ?)
        """, (
            username,
            email,
            password
        ))

        connection.commit()

        user_id = cursor.lastrowid

        connection.close()

        return user_id

    except sqlite3.IntegrityError:

        connection.close()

        return None
def create_user(username, email, password):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO users (
                username,
                email,
                password
            )
            VALUES (?, ?, ?)
        """, (
            username,
            email,
            password
        ))

        connection.commit()

        user_id = cursor.lastrowid

        connection.close()

        return user_id

    except sqlite3.IntegrityError:

        connection.close()

        return None


def get_user_by_email(email):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            email,
            password
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    connection.close()

    return user


def get_user_by_id(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            email
        FROM users
        WHERE id = ?
    """, (user_id,))

    user = cursor.fetchone()

    connection.close()

    return user
def get_interview_for_user(
    interview_id,
    user_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            role,
            experience,
            difficulty,
            total_questions,
            questions_answered,
            total_score,
            average_score,
            overall_summary,
            final_assessment
        FROM interviews
        WHERE id = ?
        AND user_id = ?
    """, (
        interview_id,
        user_id
    ))

    interview = cursor.fetchone()

    connection.close()

    return interview