from mockmate.weak_topics import record_weak_topics, read_weak_topics
import json
from datetime import datetime
from pathlib import Path

from mockmate.agent import ask_interviewer, evaluate_answer
from mockmate.weak_topics import record_weak_topics

SESSIONS_DIR = Path("workspace/sessions")


def save_session(session, session_file):
    session["updated_at"] = datetime.now().isoformat()
    session_file.write_text(
        json.dumps(session, indent=4),
        encoding="utf-8"
    )


def print_scorecard(scorecard):
    print("\n========== SCORECARD ==========")
    print("Score:", scorecard.score, "/ 10")

    print("\nStrengths:")
    for strength in scorecard.strengths:
        print("-", strength)

    print("\nAreas to improve:")
    for gap in scorecard.gaps:
        print("-", gap)

    print("\nHint:", scorecard.hint)
    print("Next topic:", scorecard.next_topic)
    print("===============================")


def choose_session():
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    existing_sessions = sorted(
        SESSIONS_DIR.glob("session_*.json"),
        reverse=True
    )

    print("\n===================================")
    print("       WELCOME TO MOCKMATE")
    print("  Your AI Mock Interview Assistant")
    print("===================================")

    if existing_sessions:
        print("\nPrevious interviews:")
        for file in existing_sessions:
            print("-", file.stem)

    choice = input(
        "\nEnter a Session ID to resume, "
        "or press Enter for a new interview:\nYou: "
    ).strip()

    if choice:
        session_file = SESSIONS_DIR / f"{choice}.json"

        if not session_file.is_file():
            print("\nSession not found. Starting a new interview.")
            return None, None, False

        session = json.loads(
            session_file.read_text(encoding="utf-8")
        )
        return session, session_file, True

    return None, None, False


def create_session():
    print("\n========== INTERVIEW SETUP ==========")

    role = input(
        "Enter your interview role (or type 'just start'): "
    ).strip()

    if role.lower() == "just start" or not role:
        role = "Software Engineer"
        round_type = "Technical"
        difficulty = "Medium"

        print("\nUsing default settings:")
        print("Role:", role)
        print("Round:", round_type)
        print("Difficulty:", difficulty)
    else:
        round_type = input("Enter interview round: ").strip()
        difficulty = input(
            "Enter difficulty (Easy/Medium/Hard): "
        ).strip()

        round_type = round_type or "Technical"
        difficulty = difficulty or "Medium"

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    session = {
        "session_id": session_id,
        "thread_id": session_id,
        "role": role,
        "round": round_type,
        "difficulty": difficulty,
        "started_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "answers": [],
        "current_question": ""
    }

    session_file = SESSIONS_DIR / f"session_{session_id}.json"
    save_session(session, session_file)

    return session, session_file

def build_weak_topic_context():
    """Prepare previous weak topics for a new interview."""

    weak_topics = read_weak_topics()

    if not weak_topics:
        return "No previously recorded weak topics."

    return "\n".join(
        f"- {topic}" for topic in weak_topics
    )
def build_next_question_prompt(session, last_answer):
    scorecard = last_answer["scorecard"]

    return f"""
Continue the same technical interview.

Candidate role: {session['role']}
Interview round: {session['round']}
Difficulty: {session['difficulty']}

Previous question:
{last_answer['question']}

Candidate's answer:
{last_answer['answer']}

Evaluation score:
{scorecard['score']}/10

Strengths:
{scorecard['strengths']}

Areas to improve:
{scorecard['gaps']}

Next topic:
{scorecard['next_topic']}

Ask exactly ONE new interview question.
Focus on the next topic and adapt the question to the candidate's performance.
Do not reveal the answer.
"""


def evaluate_and_record(question, answer):
    scorecard = evaluate_answer(question, answer)
    print_scorecard(scorecard)

    weak_result = record_weak_topics(scorecard)
    print("\nMockMate:", weak_result)

    return scorecard


def main():
    session, session_file, is_resuming = choose_session()

    if not is_resuming:
        session, session_file = create_session()

    role = session["role"]
    round_type = session["round"]
    difficulty = session["difficulty"]

    thread_id = session.get("thread_id", session["session_id"])
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
        print("\nMockMate: Starting your new interview...")

    question_number = len(session["answers"]) + 1
    question = session["current_question"]

    try:
        # Recover an answer if its evaluation was interrupted.
        if session.get("pending_answer"):
            pending = session["pending_answer"]

            print("\nRecovering your previous answer...")
            print("\nQuestion:", pending["question"])
            print("\nYour answer:", pending["answer"])

            scorecard = evaluate_and_record(
                pending["question"],
                pending["answer"]
            )

            session["answers"].append({
                "question_number": pending["question_number"],
                "question": pending["question"],
                "answer": pending["answer"],
                "scorecard": scorecard.model_dump()
            })

            session.pop("pending_answer", None)
            save_session(session, session_file)

            last_answer = session["answers"][-1]
            next_prompt = build_next_question_prompt(
                session, last_answer
            )

            question = ask_interviewer(next_prompt, thread_id)
            session["current_question"] = question
            save_session(session, session_file)

            question_number = len(session["answers"]) + 1

        # Resume a session without a current question.
        if not question and session["answers"]:
            last_answer = session["answers"][-1]
            next_prompt = build_next_question_prompt(
                session, last_answer
            )

            question = ask_interviewer(next_prompt, thread_id)
            session["current_question"] = question
            save_session(session, session_file)

        # Start a new interview.
        if not question:
            weak_topic_context = build_weak_topic_context()
            
            interview_context = f"""
            Start a technical interview.
            
            Candidate role: {role}
            Interview round: {round_type}
            Difficulty: {difficulty}
            
            Previously identified weak topics:
            {weak_topic_context}
            
            If weak topics exist, prioritize them when choosing
            the interview question. Ask exactly ONE question.
            Do not reveal the answer.
            """

            question = ask_interviewer(interview_context, thread_id)
            session["current_question"] = question
            save_session(session, session_file)

        print("\nMockMate:", question)

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

            # Save answer before evaluation.
            session["pending_answer"] = {
                "question_number": question_number,
                "question": question,
                "answer": answer
            }
            save_session(session, session_file)

            print("\nMockMate: Evaluating your answer...")

            scorecard = evaluate_and_record(question, answer)

            session["answers"].append({
                "question_number": question_number,
                "question": question,
                "answer": answer,
                "scorecard": scorecard.model_dump()
            })

            session.pop("pending_answer", None)
            save_session(session, session_file)

            last_answer = session["answers"][-1]
            next_prompt = build_next_question_prompt(
                session, last_answer
            )

            question = ask_interviewer(next_prompt, thread_id)
            session["current_question"] = question
            save_session(session, session_file)

            print("\nMockMate:", question)
            question_number += 1

    except Exception as error:
        print("\nMockMate encountered an error:")
        print(error)
        print("\nYour session has been saved. You can resume it later.")

    finally:
        save_session(session, session_file)
        print("\nSession saved at", session_file)


if __name__ == "__main__":
    main()
