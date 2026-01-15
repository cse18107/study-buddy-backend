from fastapi import FastAPI
from app.api import rag, upload, learner, source, classroom, practice, exam, question, auth, image, user
from app.core.database import init_db
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="RAG Pipeline API",
    description="API for uploading documents and querying a RAG pipeline.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()



# Include the API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/users", tags=["Users"])
app.include_router(upload.router, prefix="/api", tags=["Document Ingestion"])
app.include_router(rag.router, prefix="/api", tags=["RAG Query"])
app.include_router(learner.router, prefix="/api/learners", tags=["Learners"])
app.include_router(source.router, prefix="/api/sources", tags=["Sources"])
app.include_router(classroom.router, prefix="/api/classrooms", tags=["Classrooms"])
app.include_router(practice.router, prefix="/api/practices", tags=["Practices"])
app.include_router(exam.router, prefix="/api/exams", tags=["Exams"])
app.include_router(question.router, prefix="/api/questions", tags=["Questions"])
app.include_router(image.router, prefix="/api/images", tags=["Images"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG API. Visit /docs for documentation."}