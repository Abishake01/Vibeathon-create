from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileContent(BaseModel):
    filename: str
    content: str


class ProjectFilesResponse(BaseModel):
    project_id: str
    files: list[FileContent]


class FileUpdate(BaseModel):
    content: str


class FileResponse(BaseModel):
    filename: str
    content: str
    project_id: str


class ChatMessage(BaseModel):
    message: str


class TodoItem(BaseModel):
    id: int
    task: str
    completed: bool


class AIProjectCreate(BaseModel):
    prompt: str
    name: Optional[str] = None
    provider: Optional[str] = "ollama"  # groq, openai, ollama (default)
    design_reference: Optional[str] = None  # design type: "coffee_shop", "tech_startup", "portfolio", etc.
    design_examples: Optional[List[str]] = None  # URLs or descriptions of design examples


class AIProjectResponse(BaseModel):
    project_id: str
    todo_list: list[TodoItem]
    description: str
    remaining_tokens: Optional[int] = None


class TokenInfo(BaseModel):
    remaining: Optional[int]
    limit: int
    used: int


class IntentResponse(BaseModel):
    intent: str  # "create_webpage" | "conversation" | "ideas"
    confidence: float
    response: Optional[str] = None

