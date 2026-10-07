id="x7q2km"
def adjust_difficulty(current_difficulty, score):

    difficulties = ["Easy", "Medium", "Hard"]

    # Remove extra spaces and handle lowercase input
    current_difficulty = current_difficulty.strip().capitalize()

    # If invalid difficulty is entered,
    # start from Easy
    if current_difficulty not in difficulties:

        current_difficulty = "Easy"

    current_index = difficulties.index(current_difficulty)

    # ==============================
    # INCREASE DIFFICULTY
    # ==============================

    if score >= 8:

        if current_index < 2:
            current_index += 1

    # ==============================
    # DECREASE DIFFICULTY
    # ==============================

    elif score <= 4:

        if current_index > 0:
            current_index -= 1

    # ==============================
    # SCORE 5-7
    # KEEP SAME DIFFICULTY
    # ==============================

    return difficulties[current_index]