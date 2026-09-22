from database import Base
from sqlalchemy import Column, Integer, String


class EpisodeModel(Base):
  __tablename__ = "episodes"

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String, index=True)
  series = Column(String, index=True)  # "Chaves" ou "Chapolin"
  season = Column(Integer)
  episode_number = Column(Integer)
  synopsis = Column(String)
  video_url = Column(String)  # Link direto do vídeo para assistir