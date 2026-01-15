from enum import Enum

class SourceType(str, Enum):
    Document = "Document"
    Video = "Video"
    website = "website"

class QuestionType(str, Enum):
    Short = "Short"
    Long = "Long"
    Mcq = "Mcq"

class QuestionDifficulty(str, Enum):
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"

class Status(str, Enum):
    Created = "Created"
    Submitted = "Submitted"
    Evaluated = "Evaluated"
