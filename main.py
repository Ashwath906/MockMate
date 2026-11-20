
import json
from datetime import datetime
from pathlib import Path

from mockmate.agent import ask_interviewer, evaluate_answer

SESSIONS_DIR = Path("workspace/sessions")


def save_session(session, session_file):
    session["updated_at"] = datetime.now().isoformat()

    session_file.write_text(
        json.dumps(session, indent=4),
        encoding="utf-8"
    )


def choose_session():
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    existing_sessions = sorted(
        SESSIONS_DIR.glob("session_*.json"),
        reverse=True
    )

    print("\n===================================")
    print("       WELCOME TO MOCKMATE")
    print("  Your AI Mock Interview Assistant")
    print("===================================\n")

    if existing_sessions:
        print("Previous interviews:")

        for file in existing_sessions:
            print("-", file.stem)

    choice = input(
        "\nEnter a Session ID to resume, "
        "or press Enter for a new interview:\nYou: "
    ).strip()

    if choice:
        session_file = SESSIONS_DIR / f"{choice}.json"

        if not session_file.is_file():
            print("MockMate: Session not found. Starting a new interview.")

        else:
            session = json.loads(
                session_file.read_text(encoding="utf-8")
            )

            return session, session_file, True

    return None, None, False


def create_session():
    print("\nLet's set up your interview.\n")

    role = input(
        "MockMate: What role are you preparing for?\nYou: "
    ).strip()

    if role.lower() == "just start":
        role = "Software Engineer"
        round_type = "Technical"
        difficulty = "Medium"

        print("\nMockMate: I'll use these defaults:")
        print("Role:", role)
        print("Round:", round_type)
        print("Difficulty:", difficulty)

    else:
        round_type = input(
            "\nMockMate: Which interview round? "
            "(ML fundamentals, DSA, or behavioural)\nYou: "
        ).strip()

        difficulty = input(
            "\nMockMate: Choose difficulty "
            "(Easy, Medium, or Hard)\nYou: "
        ).strip()

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    session = {
        "session_id": session_id,
        "thread_id": session_id,
        "role": role,
        "round": round_type,
        "difficulty": difficulty,
        "started_at": datetime.now().isoformat(),
        "answers": [],
        "current_question": ""
    }

    session_file = SESSIONS_DIR / f"session_{session_id}.json"

    save_session(session, session_file)

    return session, session_file


def main():
    session, session_file, is_resuming = choose_session()

    if not is_resuming:
        session, session_file = create_session()

    # Restore interview details
    role = session["role"]
    round_type = session["round"]
    difficulty = session["difficulty"]

    # Use the same thread ID when resuming
    thread_id = session.get("thread_id", session["session_id"])

    # Support older session files
    session["thread_id"] = thread_id
    session.setdefault("current_question", "")
    session.setdefault("answers", [])

    print("\n===================================")
    print("          INTERVIEW DETAILS")
    print("===================================")

    print("Role:", role)
    print("Round:", round_type)
    print("Difficulty:", difficulty)

    if is_resuming:
        print("\nMockMate: Resuming your previous interview...")
    else:
        print("\nMockMate: Starting a new interview...")

    question_number = len(session["answers"]) + 1
    question = session["current_question"]

    try:

        # Recover an answer that was saved but not evaluated
        if session.get("pending_answer"):
            pending = session["pending_answer"]

            print("\nMockMate: Found an answer waiting for evaluation.")
            print("MockMate: Evaluating your previous answer...\n")

            # Save the answer before calling Gemini
            session["pending_answer"] = {
                "question_number": question_number,
                "question": question,
                "answer": answer
            }

            save_session(session, session_file)

            print("\nMockMate: Evaluating your answer...\n")

            # Evaluate the saved answer
            scorecard = evaluate_answer(question, answer)

            session["answers"].append({
                "question_number": pending["question_number"],
                "question": pending["question"],
                "answer": pending["answer"],
                "scorecard": scorecard.model_dump()
            })

            del session["pending_answer"]
            save_session(session, session_file)

            next_prompt = f"""
            The candidate answered:
            {pending["answer"]}

            The evaluation suggested this next topic:
            {scorecard.next_topic}

            Role: {role}
            Round: {round_type}
            Difficulty: {difficulty}

            Ask exactly ONE new interview question.
            Do not reveal its answer.
            """

            question = ask_interviewer(next_prompt, thread_id)
            session["current_question"] = question
            save_session(session, session_file)

        # Resume an old session that has saved answers
        # but does not have a saved current question.
        if is_resuming and session["answers"] and not question:

            last_answer = session["answers"][-1]

            next_prompt = f"""
            Continue the candidate's existing interview.

            Previous question:
            {last_answer["question"]}

            Candidate's answer:
            {last_answer["answer"]}

            Previous evaluation:
            {json.dumps(last_answer["scorecard"])}

            Role: {role}
            Round: {round_type}
            Difficulty: {difficulty}

            Ask exactly ONE new interview question.
            Focus on the recommended next topic:
            {last_answer["scorecard"]["next_topic"]}

            Do not reveal its answer.
            """

            question = ask_interviewer(next_prompt, thread_id)

            session["current_question"] = question
            save_session(session, session_file)

        # Start a new interview if there is no question yet
        if not question:

            interview_context = f"""
            Candidate role: {role}
            Interview round: {round_type}
            Difficulty: {difficulty}

            Start the interview.
            Ask exactly ONE relevant interview question.
            Do not provide its answer.
            Wait for the candidate's response.
            """

            question = ask_interviewer(interview_context, thread_id)

            session["current_question"] = question
            save_session(session, session_file)

        print("\nMockMate:", question)

        # Main interview loop
        while True:

            answer = input("\nYou: ").strip()

            if answer.lower() in ["exit", "quit", "stop"]:

                print("\nMockMate: Your interview has been paused.")

                print("You can resume it later using this Session ID:")
                print(session["session_id"])

                break

            if not answer:
                print("MockMate: Please enter your answer.")
                continue

            print("\nMockMate: Evaluating your answer...\n")

            # Evaluate candidate's answer
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

            # Save answer and scorecard
            session["answers"].append({
                "question_number": question_number,
                "question": question,
                "answer": answer,
                "scorecard": scorecard.model_dump()
            })
            session.pop("pending_answer", None)
            # Save immediately
            save_session(session, session_file)

            # Generate next interview question
            next_prompt = f"""
            The candidate answered the previous question:

            {answer}

            The evaluation suggested this next topic:
            {scorecard.next_topic}

            Role: {role}
            Round: {round_type}
            Difficulty: {difficulty}

            Briefly acknowledge the response.
            Ask exactly ONE new interview question.
            Do not reveal its expected answer.
            Wait for the candidate's response.
            """

            print("\nMockMate: Thinking...\n")

            question = ask_interviewer(next_prompt, thread_id)

            session["current_question"] = question

            save_session(session, session_file)

            print("MockMate:", question)

            question_number += 1

    except Exception as error:

        print("\nMockMate: An error occurred.")
        print("Details:", error)

    finally:

        save_session(session, session_file)

        print(f"\nMockMate: Session saved at {session_file}")


if __name__ == "__main__":
    main()

