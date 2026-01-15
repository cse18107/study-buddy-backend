import asyncio
from uuid import UUID
import json
from sqlmodel import Session, select
from app.models.question import Question
from app.models.enums import QuestionType
from app.services.prompts import build_prompt_for_evaluation
from app.core.llm import llm

async def evaluate_question_async(question: Question, chain, session: Session):
    """
    Evaluates a single question asynchronously.
    """
    if not question.learnersAnswer:
        question.givenMarks = 0
        return 0
        
    if question.type == QuestionType.Mcq:
        if question.learnersAnswer.strip().lower() == question.answer.strip().lower():
            question.givenMarks = question.assignedMarks
        else:
            question.givenMarks = 0
        return question.givenMarks
    else:
        try:
            response = await chain.ainvoke({
                "question": question.question,
                "model_answer": question.answer,
                "student_answer": question.learnersAnswer,
                "max_marks": question.assignedMarks
            })
            
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            data = json.loads(content)
            
            score = float(data.get("score", 0))
            score = max(0, min(score, question.assignedMarks))
            
            question.givenMarks = score
            return score
        except Exception as e:
            print(f"Error evaluating question {question.id}: {e}")
            question.givenMarks = 0
            return 0

async def evaluate_exam_submission(exam_id: UUID, session: Session):
    """
    Evaluates all questions in an exam asynchronously.
    """
    query = select(Question).where(Question.exam_id == exam_id)
    questions = session.exec(query).all()
    return await evaluate_questions(questions, session)

async def evaluate_questions_by_id(question_ids: list[UUID], session: Session):
    """
    Evaluates a specific list of questions by their IDs.
    """
    questions = []
    for q_id in question_ids:
        q = session.get(Question, q_id)
        if q:
            questions.append(q)
    
    if not questions:
        return 0
        
    return await evaluate_questions(questions, session)

async def evaluate_questions(questions: list[Question], session: Session):
    """
    Core evaluation logic for a list of Question objects.
    """
    prompt_template = build_prompt_for_evaluation()
    chain = prompt_template | llm
    
    tasks = [evaluate_question_async(q, chain, session) for q in questions]
    scores = await asyncio.gather(*tasks)
    
    for q in questions:
        session.add(q)
        
    session.commit()
    return sum(scores)
