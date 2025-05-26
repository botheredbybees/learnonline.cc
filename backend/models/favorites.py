from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID, uuid4


class QuestBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_public: bool = False
    is_introductory: bool = False  # Flag for quests accessible to guests
    quest_type: Literal["mentor_created", "qualification_based", "skillset_based", "introductory"]
    source_id: Optional[str] = None
    experience_points: int = 100


class QuestCreate(QuestBase):
    unit_ids: List[int]  # List of unit IDs to include in the quest


class QuestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    experience_points: Optional[int] = None
    unit_ids: Optional[List[int]] = None  # Updated list of unit IDs


class QuestUnit(BaseModel):
    unit_id: int
    sequence_number: int
    is_required: bool = True

    class Config:
        orm_mode = True


class Quest(QuestBase):
    id: UUID = Field(default_factory=uuid4)
    creator_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class QuestDetail(Quest):
    units: List[QuestUnit] = []

    class Config:
        orm_mode = True


class FavoriteTrainingPackage(BaseModel):
    training_package_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class FavoriteUnit(BaseModel):
    unit_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class FavoriteQuest(BaseModel):
    quest_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class AddFavorite(BaseModel):
    id: str  # ID of the item to favorite (training_package_id, unit_id, or quest_id)


class FavoritesResponse(BaseModel):
    training_packages: List[FavoriteTrainingPackage]
    units: List[FavoriteUnit]
    quests: List[FavoriteQuest]
    

class GuestProgress(BaseModel):
    guest_id: str
    quest_id: UUID
    unit_progress: dict  # JSON serialized progress data
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    class Config:
        orm_mode = True


class GuestProgressCreate(BaseModel):
    guest_id: str
    quest_id: str
    unit_progress: dict
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class UserQuestProgress(BaseModel):
    user_id: UUID
    quest_id: UUID
    status: Literal["not_started", "in_progress", "completed"] = "in_progress"
    progress_data: dict = {}
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class TransferGuestProgress(BaseModel):
    guest_id: str
