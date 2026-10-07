from io import BytesIO

from reportlab.lib import colors

from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT
)

from reportlab.lib.pagesizes import A4

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.units import mm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)


def create_interview_pdf(
    interview,
    results
):

    """
    Generate a PDF interview report.

    interview:
        Tuple containing interview information
        from the interviews table.

    results:
        List of interview question results.
    """


    # =========================================================
    # PDF BUFFER
    # =========================================================

    buffer = BytesIO()


    # =========================================================
    # PDF DOCUMENT
    # =========================================================

    document = SimpleDocTemplate(

        buffer,

        pagesize=A4,

        rightMargin=18 * mm,

        leftMargin=18 * mm,

        topMargin=18 * mm,

        bottomMargin=18 * mm
    )


    # =========================================================
    # STYLES
    # =========================================================

    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(

        "ReportTitle",

        parent=styles["Title"],

        fontName="Helvetica-Bold",

        fontSize=24,

        leading=29,

        alignment=TA_CENTER,

        textColor=colors.HexColor(
            "#111827"
        ),

        spaceAfter=8
    )


    subtitle_style = ParagraphStyle(

        "ReportSubtitle",

        parent=styles["Normal"],

        fontName="Helvetica",

        fontSize=10,

        leading=15,

        alignment=TA_CENTER,

        textColor=colors.HexColor(
            "#6B7280"
        ),

        spaceAfter=22
    )


    section_style = ParagraphStyle(

        "SectionTitle",

        parent=styles["Heading2"],

        fontName="Helvetica-Bold",

        fontSize=16,

        leading=20,

        textColor=colors.HexColor(
            "#111827"
        ),

        spaceBefore=12,

        spaceAfter=10
    )


    normal_style = ParagraphStyle(

        "NormalText",

        parent=styles["Normal"],

        fontName="Helvetica",

        fontSize=9.5,

        leading=14,

        textColor=colors.HexColor(
            "#374151"
        ),

        spaceAfter=6
    )


    small_style = ParagraphStyle(

        "SmallText",

        parent=styles["Normal"],

        fontName="Helvetica",

        fontSize=8.5,

        leading=12,

        textColor=colors.HexColor(
            "#4B5563"
        )
    )


    question_style = ParagraphStyle(

        "Question",

        parent=styles["Normal"],

        fontName="Helvetica-Bold",

        fontSize=10,

        leading=15,

        textColor=colors.HexColor(
            "#111827"
        ),

        spaceAfter=7
    )


    score_style = ParagraphStyle(

        "Score",

        parent=styles["Normal"],

        fontName="Helvetica-Bold",

        fontSize=14,

        leading=18,

        textColor=colors.HexColor(
            "#4F46E5"
        ),

        alignment=TA_CENTER
    )


    # =========================================================
    # STORY
    # =========================================================

    story = []


    # =========================================================
    # TITLE
    # =========================================================

    story.append(
        Paragraph(
            "AI INTERVIEW REPORT",
            title_style
        )
    )


    story.append(
        Paragraph(
            "AI Interviewer Performance Report",
            subtitle_style
        )
    )


    # =========================================================
    # INTERVIEW INFORMATION
    # =========================================================

    story.append(
        Paragraph(
            "Interview Information",
            section_style
        )
    )


    interview_id = interview[0]

    role = interview[1]

    experience = interview[2]

    difficulty = interview[3]

    total_questions = interview[4]

    questions_answered = interview[5]

    total_score = interview[6]

    average_score = interview[7]

    overall_summary = interview[8]

    final_assessment = interview[9]


    information_data = [

        [
            Paragraph(
                "<b>Interview ID</b>",
                small_style
            ),

            Paragraph(
                str(interview_id),
                small_style
            )
        ],

        [
            Paragraph(
                "<b>Role</b>",
                small_style
            ),

            Paragraph(
                str(role),
                small_style
            )
        ],

        [
            Paragraph(
                "<b>Experience</b>",
                small_style
            ),

            Paragraph(
                str(experience),
                small_style
            )
        ],

        [
            Paragraph(
                "<b>Difficulty</b>",
                small_style
            ),

            Paragraph(
                str(difficulty),
                small_style
            )
        ],

        [
            Paragraph(
                "<b>Total Questions</b>",
                small_style
            ),

            Paragraph(
                str(total_questions),
                small_style
            )
        ],

        [
            Paragraph(
                "<b>Questions Answered</b>",
                small_style
            ),

            Paragraph(
                str(questions_answered),
                small_style
            )
        ]

    ]


    information_table = Table(

        information_data,

        colWidths=[
            48 * mm,
            115 * mm
        ]
    )


    information_table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#EEF2FF")
            ),

            (
                "BACKGROUND",
                (1, 0),
                (1, -1),
                colors.white
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.6,
                colors.HexColor("#D1D5DB")
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#E5E7EB")
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )


    story.append(
        information_table
    )


    story.append(
        Spacer(
            1,
            15
        )
    )


    # =========================================================
    # PERFORMANCE SUMMARY
    # =========================================================

    story.append(
        Paragraph(
            "Performance Summary",
            section_style
        )
    )


    performance_data = [

        [
            Paragraph(
                "<b>Total Score</b>",
                small_style
            ),

            Paragraph(
                "<b>Average Score</b>",
                small_style
            ),

            Paragraph(
                "<b>Questions</b>",
                small_style
            )
        ],

        [
            Paragraph(
                f"{total_score}",
                score_style
            ),

            Paragraph(
                f"{average_score:.2f} / 10",
                score_style
            ),

            Paragraph(
                f"{questions_answered}",
                score_style
            )
        ]

    ]


    performance_table = Table(

        performance_data,

        colWidths=[
            54 * mm,
            54 * mm,
            54 * mm
        ]
    )


    performance_table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#F3F4F6")
            ),

            (
                "BACKGROUND",
                (0, 1),
                (-1, 1),
                colors.white
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.6,
                colors.HexColor("#D1D5DB")
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#E5E7EB")
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                10
            )

        ])
    )


    story.append(
        performance_table
    )


    story.append(
        Spacer(
            1,
            15
        )
    )


    # =========================================================
    # OVERALL SUMMARY
    # =========================================================

    story.append(
        Paragraph(
            "Overall Summary",
            section_style
        )
    )


    story.append(
        Paragraph(
            str(
                overall_summary
                or "No overall summary available."
            ),
            normal_style
        )
    )


    # =========================================================
    # FINAL ASSESSMENT
    # =========================================================

    story.append(
        Paragraph(
            "Final Assessment",
            section_style
        )
    )


    story.append(
        Paragraph(
            str(
                final_assessment
                or "No final assessment available."
            ),
            normal_style
        )
    )


    # =========================================================
    # QUESTION-BY-QUESTION RESULTS
    # =========================================================

    story.append(
        PageBreak()
    )


    story.append(
        Paragraph(
            "Question-by-Question Evaluation",
            section_style
        )
    )


    if not results:

        story.append(
            Paragraph(
                "No question results are available.",
                normal_style
            )
        )


    else:

        for index, result in enumerate(
            results,
            start=1
        ):

            question = result[0]

            answer = result[1]

            score = result[2]

            feedback = result[3]

            strengths = result[4]

            improvements = result[5]


            # ---------------------------------------------
            # QUESTION
            # ---------------------------------------------

            story.append(
                Paragraph(
                    f"Question {index}",
                    section_style
                )
            )


            story.append(
                Paragraph(
                    str(question),
                    question_style
                )
            )


            # ---------------------------------------------
            # SCORE
            # ---------------------------------------------

            score_data = [

                [
                    Paragraph(
                        "<b>Score</b>",
                        small_style
                    ),

                    Paragraph(
                        f"{score} / 10",
                        score_style
                    )
                ]

            ]


            score_table = Table(

                score_data,

                colWidths=[
                    35 * mm,
                    130 * mm
                ]
            )


            score_table.setStyle(

                TableStyle([

                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, 0),
                        colors.HexColor("#EEF2FF")
                    ),

                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#D1D5DB")
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE"
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    )

                ])
            )


            story.append(
                score_table
            )


            story.append(
                Spacer(
                    1,
                    8
                )
            )


            # ---------------------------------------------
            # ANSWER
            # ---------------------------------------------

            story.append(
                Paragraph(
                    "<b>Candidate Answer</b>",
                    normal_style
                )
            )


            story.append(
                Paragraph(
                    str(
                        answer
                        or "No answer provided."
                    ),
                    small_style
                )
            )


            story.append(
                Spacer(
                    1,
                    5
                )
            )


            # ---------------------------------------------
            # FEEDBACK
            # ---------------------------------------------

            story.append(
                Paragraph(
                    "<b>AI Feedback</b>",
                    normal_style
                )
            )


            story.append(
                Paragraph(
                    str(
                        feedback
                        or "No feedback available."
                    ),
                    small_style
                )
            )


            story.append(
                Spacer(
                    1,
                    5
                )
            )


            # ---------------------------------------------
            # STRENGTHS
            # ---------------------------------------------

            story.append(
                Paragraph(
                    "<b>Strengths</b>",
                    normal_style
                )
            )


            story.append(
                Paragraph(
                    str(
                        strengths
                        or "No strengths recorded."
                    ),
                    small_style
                )
            )


            story.append(
                Spacer(
                    1,
                    5
                )
            )


            # ---------------------------------------------
            # IMPROVEMENTS
            # ---------------------------------------------

            story.append(
                Paragraph(
                    "<b>Areas for Improvement</b>",
                    normal_style
                )
            )


            story.append(
                Paragraph(
                    str(
                        improvements
                        or "No improvement suggestions recorded."
                    ),
                    small_style
                )
            )


            story.append(
                Spacer(
                    1,
                    12
                )
            )


            # Divider

            divider = Table(

                [[""]],

                colWidths=[
                    165 * mm
                ],

                rowHeights=[
                    0.5
                ]
            )


            divider.setStyle(

                TableStyle([

                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#E5E7EB")
                    )

                ])
            )


            story.append(
                divider
            )


            story.append(
                Spacer(
                    1,
                    8
                )
            )


    # =========================================================
    # FOOTER FUNCTION
    # =========================================================

    def add_page_number(
        canvas,
        doc
    ):

        canvas.saveState()


        canvas.setFont(
            "Helvetica",
            8
        )


        canvas.setFillColor(
            colors.HexColor("#6B7280")
        )
        page_number = canvas.getPageNumber()

        canvas.drawCentredString(

            A4[0] / 2,

            10 * mm,

            f"AI Interviewer • Page {page_number}"

        )

       
        


        canvas.restoreState()


    # =========================================================
    # BUILD PDF
    # =========================================================

    document.build(

        story,

        onFirstPage=add_page_number,

        onLaterPages=add_page_number
    )


    # =========================================================
    # RETURN PDF
    # =========================================================

    buffer.seek(0)

    return buffer