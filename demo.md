# MockMate – Demo Transcript

## Project Overview

MockMate is an AI-powered mock technical interview agent built using Python, LangChain, LangGraph, and Deep Agents.

## Demo Configuration

- Target Role: ML Engineer
- Interview Round: ML Fundamentals
- Difficulty: Medium

## 1. Starting the Application

Run:

    uv run python main.py

Choose to start a new interview session.

## 2. Interview Question

MockMate generates a technical question based on the selected role and difficulty.

Example question:

What is the difference between supervised learning and unsupervised learning?

## 3. Candidate Answer

Example answer:

Supervised learning uses labelled data to train a model, whereas unsupervised learning uses unlabelled data to discover hidden patterns or groups.

## 4. Answer Evaluation

MockMate evaluates the candidate's answer using a structured scorecard containing:

- Score
- Strengths
- Knowledge gaps
- Improvement hint

## 5. Weak Topic Tracking

MockMate records topics that need improvement and uses saved weak-topic history to guide future practice.

## 6. Session Management

MockMate supports:

- Starting new interviews.
- Resuming existing sessions.
- Deleting sessions with approval.
- Managing weak-topic history with approval.

## 7. Security Testing

The following security checks were performed:

- Parent-directory traversal was blocked.
- Absolute paths were blocked.
- Rejected file overwrites preserved the original file.
- Rejected file deletions preserved the original file.
- Rejected session deletion preserved the session.

## Conclusion

MockMate provides AI-powered interview practice, structured answer evaluation, weak-topic tracking, persistent session management, and workspace security.

Note: The question and answer above are illustrative examples, not a verified live interview transcript.
