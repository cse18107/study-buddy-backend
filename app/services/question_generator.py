from typing import Any, List, Dict
from uuid import UUID
import json
from sqlmodel import Session
from app.services.vector_store import get_retriever
from app.services.prompts import build_prompt_for_question_generation
from app.core.llm import llm
from app.models.question import Question
from app.models.enums import QuestionType, QuestionDifficulty
from app.services.content_generator import process_hierarchy

def generate_practice_questions(
    practice_id: UUID,
    source_hierarchy: Any,
    document_id: str,
    session: Session
) -> None:
    """
    Generates questions (MCQ, Short, Long) for each topic in the hierarchy
    and links them to the given practice_id.
    """
    flat_nodes = process_hierarchy(source_hierarchy)
    
    # RAG setup
    retriever = get_retriever(namespace=document_id)
    prompt_template = build_prompt_for_question_generation()
    chain = prompt_template | llm
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    for node in flat_nodes:
        topic = node.get("topic", "")
        important_points = node.get("importantPoints", "")
        level = node.get("level", 1)
        
        rag_query = (
            f"Generate questions for: {topic}\n"
            f"Important Points: {important_points}"
        )
        
        # 1. Retrieve Context
        retrieved_docs = retriever.invoke(rag_query)
        context_str = format_docs(retrieved_docs)
        
        # 2. Generate JSON Questions
        try:
            response = chain.invoke({
                "context": context_str,
                "topic": topic,
                "importantPoints": important_points,
                "level": level
            })
            
            content = response.content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            
            # 3. Store Questions
            # data should have keys: "mcq", "short", "long"
            
            # --- MCQs ---
            mcqs = data.get("mcq", [])
            for q in mcqs:
                question = Question(
                    type=QuestionType.Mcq,
                    question=q.get("question"),
                    options=q.get("options", []),
                    answer=q.get("answer"),
                    assignedMarks=q.get("marks", 1),
                    difficulty=QuestionDifficulty.Easy, # Default
                    practice_id=practice_id
                )
                session.add(question)
                
            # --- Short Questions ---
            shorts = data.get("short", [])
            for q in shorts:
                question = Question(
                    type=QuestionType.Short,
                    question=q.get("question"),
                    answer=q.get("answer"),
                    assignedMarks=q.get("marks", 3),
                    difficulty=QuestionDifficulty.Medium,
                    practice_id=practice_id
                )
                session.add(question)
                
            # --- Long Questions ---
            longs = data.get("long", [])
            for q in longs:
                question = Question(
                    type=QuestionType.Long,
                    question=q.get("question"),
                    answer=q.get("answer"),
                    assignedMarks=q.get("marks", 5),
                    difficulty=QuestionDifficulty.Hard,
                    practice_id=practice_id
                )
                session.add(question)
                
            session.commit()
            
        except Exception as e:
            print(f"Error generating questions for topic {topic}: {e}")
            continue

def generate_exam_questions(
    exam_id: UUID,
    source_hierarchy: Any,
    document_id: str,
    session: Session
) -> None:
    """
    Generates questions (MCQ, Short, Long) for each topic in the hierarchy
    and links them to the given exam_id.
    """
    # Logic is identical, just linking to exam_id
    flat_nodes = process_hierarchy(source_hierarchy)
    
    retriever = get_retriever(namespace=document_id)
    prompt_template = build_prompt_for_question_generation()
    chain = prompt_template | llm
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    for node in flat_nodes:
        topic = node.get("topic", "")
        important_points = node.get("importantPoints", "")
        level = node.get("level", 1)
        
        rag_query = f"Generate questions for: {topic}"
        retrieved_docs = retriever.invoke(rag_query)
        context_str = format_docs(retrieved_docs)
        
        try:
            response = chain.invoke({
                "context": context_str,
                "topic": topic,
                "importantPoints": important_points,
                "level": level
            })
            
            content = response.content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            
            mcqs = data.get("mcq", [])
            for q in mcqs:
                question = Question(
                    type=QuestionType.Mcq,
                    question=q.get("question"),
                    options=q.get("options", []),
                    answer=q.get("answer"),
                    assignedMarks=q.get("marks", 1),
                    difficulty=QuestionDifficulty.Easy,
                    exam_id=exam_id
                )
                session.add(question)
                
            shorts = data.get("short", [])
            for q in shorts:
                question = Question(
                    type=QuestionType.Short,
                    question=q.get("question"),
                    answer=q.get("answer"),
                    assignedMarks=q.get("marks", 3),
                    difficulty=QuestionDifficulty.Medium,
                    exam_id=exam_id
                )
                session.add(question)
                
            longs = data.get("long", [])
            for q in longs:
                question = Question(
                    type=QuestionType.Long,
                    question=q.get("question"),
                    answer=q.get("answer"),
                    assignedMarks=q.get("marks", 5),
                    difficulty=QuestionDifficulty.Hard,
                    exam_id=exam_id
                )
                session.add(question)
            
            session.commit()

        except Exception as e:
            print(f"Error generating exam questions for topic {topic}: {e}")
            continue
