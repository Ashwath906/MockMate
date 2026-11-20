

from mockmate.agent import ask_interviewer


def main():
    print("\n===================================")
    print("       WELCOME TO MOCKMATE")
    print("  Your AI Mock Interview Assistant")
    print("===================================\n")

    print("Let's set up your interview.\n")

    role = input("MockMate: What role are you preparing for? \nYou: ").strip()

    if role.lower() == "just start":
        role = "Software Engineer"
        round_type = "Technical"
        difficulty = "Medium"

        print("\nMockMate: I'll use these defaults:")
        print(f"Role: {role}")
        print(f"Round: {round_type}")
        print(f"Difficulty: {difficulty}")

    else:
        round_type = input(
            "\nMockMate: Which interview round? "
            "(ML fundamentals, DSA, or behavioural)\nYou: "
        ).strip()

        difficulty = input(
            "\nMockMate: Choose difficulty "
            "(Easy, Medium, or Hard)\nYou: "
        ).strip()

    interview_context = f"""
    Candidate role: {role}
    Interview round: {round_type}
    Difficulty: {difficulty}

    Start the interview.
    Ask exactly ONE relevant interview question.
    Do not provide its answer.
    Wait for the candidate's response.
    """

    print("\nMockMate: Preparing your interview...\n")

    try:
        question = ask_interviewer(interview_context)
        print("MockMate:", question)

        while True:
            answer = input("\nYou: ").strip()

            if answer.lower() in ["exit", "quit", "stop"]:
                print("\nMockMate: Thank you for attending!")
                print("Your interview has ended.")
                break

            if not answer:
                print("MockMate: Please enter your answer.")
                continue

            next_prompt = f"""
            The candidate answered the previous question:

            {answer}

            Briefly acknowledge the response without giving a scorecard.
            Ask exactly ONE new interview question based on:
            Role: {role}
            Round: {round_type}
            Difficulty: {difficulty}

            Do not reveal the expected answer.
            Wait for the candidate's next response.
            """

            print("\nMockMate: Thinking...\n")

            response = ask_interviewer(next_prompt)
            print("MockMate:", response)

    except Exception as error:
        print("\nMockMate: An error occurred.")
        print("Details:", error)


if __name__ == "__main__":
    main()
