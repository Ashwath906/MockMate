
from unittest.mock import patch

from mockmate.agent import evaluate_answer


valid_scorecard = {
    "score": 8,
    "strengths": [
        "Correct explanation",
        "Good example"
    ],
    "gaps": [
        "Needs more detail",
        "Missing formula"
    ],
    "hint": "Explain the formula.",
    "next_topic": "Decision Trees"
}

invalid_scorecard = {
    "score": 15,
    "strengths": ["Good explanation"],
    "gaps": ["Missing detail", "Missing example"],
    "hint": "Improve the answer.",
    "next_topic": "Decision Trees"
}


with patch("mockmate.agent.model") as mock_model:

    mock_structured = mock_model.with_structured_output.return_value

    mock_structured.invoke.side_effect = [
        invalid_scorecard,
        valid_scorecard
    ]

    result = evaluate_answer(
        "Test question",
        "Test answer"
    )

    print("Retry test passed!")
    print("Number of attempts:", mock_structured.invoke.call_count)
    print("Final score:", result.score)
