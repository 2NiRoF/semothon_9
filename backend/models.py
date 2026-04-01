from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    point = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    match_participants = relationship("MatchParticipant", back_populates="user")
    posts = relationship("Post", back_populates="user")
    reacts = relationship("React", back_populates="user")


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)   # 텀블러, 쓰레기 줍기, 분리수거, 플로깅, 해안 정화
    description = Column(String)
    max_participants = Column(Integer, default=4)

    matches = relationship("Match", back_populates="mission")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    status = Column(String, default="waiting")  # waiting, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    mission = relationship("Mission", back_populates="matches")
    participants = relationship("MatchParticipant", back_populates="match")
    posts = relationship("Post", back_populates="match")


class MatchParticipant(Base):
    __tablename__ = "match_participants"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="participants")
    user = relationship("User", back_populates="match_participants")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_url = Column(String)
    comment = Column(String)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="posts")
    user = relationship("User", back_populates="posts")
    reacts = relationship("React", back_populates="post")


class React(Base):
    __tablename__ = "reacts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    emoji = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="reacts")
    user = relationship("User", back_populates="reacts")
