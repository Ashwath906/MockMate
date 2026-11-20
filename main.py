
import json
from datetime import datetime
from pathlib import Path

from mockmate.agent import ask_interviewer, evaluate_answer


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

    session = {
        "role": role,
        "round": round_type,
        "difficulty": difficulty,
        "started_at": datetime.now().isoformat(),
        "answers": []
    }

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    sessions_dir = Path("workspace/sessions")
    sessions_dir.mkdir(parents=True, exist_ok=True)

    session_file = sessions_dir / f"session_{session_id}.json"

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

        question_number = 1

        while True:
            answer = input("\nYou: ").strip()

            if answer.lower() in ["exit", "quit", "stop"]:
                print("\nMockMate: Thank you for attending!")
                print("Your interview has ended.")
                break

            if not answer:
                print("MockMate: Please enter your answer.")
                continue

            print("\nMockMate: Evaluating your answer...\n")

            scorecard = evaluate_answer(question, answer)

            print(f"Score: {scorecard.score}/10")

            print("\nStrengths:")
            for strength in scorecard.strengths:
                print("-", strength)

            print("\nAreas to improve:")
            for gap in scorecard.gaps:
                print("-", gap)

            print("\nHint:", scorecard.hint)
            print("Next topic:", scorecard.next_topic)

            session["answers"].append({
                "question_number": question_number,
                "question": question,
                "answer": answer,
                "scorecard": scorecard.model_dump()
            })

            session["updated_at"] = datetime.now().isoformat()

            session_file.write_text(
                json.dumps(session, indent=4),
                encoding="utf-8"
            )

            next_prompt = f"""
            The candidate answered the previous question:

            {answer}

            The evaluation suggested this next topic:
            {scorecard.next_topic}

            Briefly acknowledge the response.
            Ask exactly ONE new interview question based on:
            Role: {role}
            Round: {round_type}
            Difficulty: {difficulty}

            Do not reveal the expected answer.
            Wait for the candidate's next response.
            """

            print("\nMockMate: Thinking...\n")

            question = ask_interviewer(next_prompt)
            print("MockMate:", question)

            question_number += 1

    except Exception as error:
        print("\nMockMate: An error occurred.")
        print("Details:", error)

    finally:
        if session["answers"]:
            session["ended_at"] = datetime.now().isoformat()
            session_file.write_text(
                json.dumps(session, indent=4),
                encoding="utf-8"
            )
            print(f"\nMockMate: Session saved at {session_file}")


if __name__ == "__main__":
    main()