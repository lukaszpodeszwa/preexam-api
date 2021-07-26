import time
from typing import Dict, List, Optional, Tuple, Union

import api.accounts.history as history
import api.database as db
import api.quizzes.schema as schema
from api.common import ServiceRequest, ServiceResponse
from api.errors import ApiError, api_error
from api.middlewares import require_auth, validate


def _get_current_quiz(user_id: int) -> dict:
    account = db.db.accounts.find_one({"_id": user_id}, {"current_quiz": True})
    return account.get("current_quiz")


@require_auth()
def start(r: ServiceRequest, quiz_id: int) -> ServiceResponse:
    """Begin solving question. Add session to user account."""

    quiz = db.db.quizzes.find_one(
        {"_id": quiz_id}, {"questions_ids": True, "_id": True, "is_exam": True}
    )
    if not quiz:
        return ServiceResponse(404, errors=api_error("quiz_not_found"))

    quiz["out_of"] = len(quiz["questions_ids"])  # type: ignore
    quiz["answered"] = []
    quiz["correct_answers"] = 0
    quiz["started_at"] = int(time.time())
    res = db.update_one("accounts", r.user_session.user_id, {"current_quiz": quiz})
    return res


def _end(user_id: int):
    """End a quiz and write resoults to history."""
    current_quiz = _get_current_quiz(user_id)
    questions = db.db.questions.find(
        {"_id": {"$in": current_quiz["questions_ids"]}},
        projection={"sub_questions": True},
    )

    out_of = 0
    for q in questions:
        if "sub_questions" in q:
            out_of += len(q["sub_questions"])
        out_of += 1
    current_quiz["out_of"] = out_of
    del current_quiz["questions_ids"]
    del current_quiz["answered"]
    current_quiz["quiz_id"] = current_quiz["_id"]
    del current_quiz["_id"]
    current_quiz["ended_at"] = int(time.time())
    history.add(current_quiz, user_id)
    db.update_one("accounts", user_id, {"current_quiz": None})
    return None


def _check_question(
    question: Dict, answer_content: Dict
) -> Tuple[List[Dict], Optional[ApiError]]:
    if "correct_answers" in question and "answer_indexes" not in answer_content:
        return None, api_error("question_answer_mismatch", extra_info=["answer_indexes"])  # type: ignore
    elif "sub_questions" in question and "sub_answers" not in answer_content:
        return None, api_error("question_answer_mismatch", extra_info=["sub_answers"])  # type: ignore

    def check_answers(answers, correct_answers) -> Dict:
        if sorted(correct_answers) == sorted(answers):
            return {"correct": True}
        else:
            if question.get("view_correct_answers"):
                return {
                    "correct": False,
                    "correct_answer": correct_answers,
                }
            else:
                return {"correct": False}

    results: List[Dict] = []
    if "sub_questions" in question:
        if len(answer_content["sub_answers"]) != len(question["sub_questions"]):
            return api_error("wrong_number_of_answers")  # type: ignore

        for sq in question["sub_questions"]:
            # TODO: Use binary search or smth.
            answer = [
                sa["answer_indexes"]
                for sa in answer_content["sub_answers"]
                if sa["question_id"] == sq["_id"]
            ][0]
            if not answer:
                return None, api_error("question_index_out_of_range")  # type: ignore
            res = check_answers(answer, sq["correct_answers"])
            res["question_id"] = f'{question["_id"]}.{sq["_id"]}'
            results.append(res)
        return results, None
    res = check_answers(answer_content["answer_indexes"], question["correct_answers"])
    res["question_id"] = f'{question["_id"]}'
    results.append(res)
    results[0]["question_id"] = question["_id"]
    return results, None


@validate(schema.SINGLE_ANSWER)
@require_auth()
def single_answer(r: ServiceRequest) -> ServiceResponse:
    current_quiz = _get_current_quiz(r.user_session.user_id)

    if not current_quiz:
        return ServiceResponse(403, errors=api_error("quiz_session_not_started"))

    if current_quiz.get("is_exam"):
        return ServiceResponse(409, errors=api_error("quiz_is_not_short"))

    question_index = current_quiz.get("current_question_index", 0)

    question = db.db.questions.find_one(
        {"_id": current_quiz["questions_ids"][question_index]}
    )

    results, error = _check_question(question, r.content)
    if error:  # type:ignore
        return ServiceResponse(422, errors=error)
    correct_answers = len([r for r in results if r["correct"]])
    db.db.accounts.update_one(
        {"_id": r.user_session.user_id},
        {
            "$push": {
                "current_quiz.answered": current_quiz["questions_ids"][question_index]
            },
            "$inc": {"current_quiz.correct_answers": correct_answers},
            "$set": {"current_quiz.current_question_index": question_index + 1},
            "$inc": {"current_quiz.out_of": len(results)},
        },
    )

    if question_index == len(current_quiz["questions_ids"]) - 1:
        _end(r.user_session.user_id)

    return ServiceResponse(200, results)


@validate(schema.BULK_ANSWER)
@require_auth()
def bulk_answer(r: ServiceRequest) -> ServiceResponse:
    """Enables answering all questions at once. Automaticly ends a quiz."""
    current_quiz = _get_current_quiz(r.user_session.user_id)
    if not current_quiz:
        return ServiceResponse(403, errors=api_error("quiz_session_not_started"))

    if not current_quiz.get("is_exam"):
        return ServiceResponse(409, errors=api_error("quiz_is_not_long"))

    answered_ids = [a["question_id"] for a in r.content]
    if sorted(current_quiz["questions_ids"]) != sorted(answered_ids):
        return ServiceResponse(
            409,
            errors=api_error(
                "missing_answers",
                entities=[
                    _id
                    for _id in current_quiz["questions_ids"]
                    if _id not in answered_ids
                ],
            ),
        )

    questions = db.db.questions.find({"_id": {"$in": current_quiz["questions_ids"]}})

    correct_answers = 0
    results: List[Dict] = []
    for q in questions:
        answer = [a for a in r.content if a["question_id"] == q["_id"]][0]
        sub_results, error = _check_question(q, answer)
        if error:  # type:ignore
            return ServiceResponse(422, errors=error)
        correct_answers += len([r for r in sub_results if r["correct"]])
        results += sub_results
    db.db.accounts.update_one(
        {"_id": r.user_session.user_id},
        {
            "$inc": {"current_quiz.correct_answers": correct_answers},
            "$inc": {"current_quiz.out_of": len(results)},
            # All questions must be answered to end a quiz.
            "$set": {"current_quiz.answered": current_quiz["questions_ids"]},
        },
    )

    _end(r.user_session.user_id)

    return ServiceResponse(
        200,
        {
            "results": results,
            "correct_answers": correct_answers,
            "out_of": len(results),
        }
    )
