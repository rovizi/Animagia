from database import engine, get_db
import models
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
import models as db_models
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Cria as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Animagia - API de Chaves e Chapolin",
    description="Mega acervo com 1000 episódios hospedado no ecossistema Animagia",
    version="4.1.0",
)


class EpisodeSchema(BaseModel):
  id: int
  title: str
  series: str
  season: int
  episode_number: int
  synopsis: str
  video_url: str

  class Config:
    from_attributes = True


# Função para popular a base automaticamente com 1000 episódios (500 Chaves + 500 Chapolin)
def popular_dados_iniciais():
  db = SessionLocal()
  total = db.query(db_models.EpisodeModel).count()
  if total == 0:
    episodios = []

    # --- 500 Episódios de Chaves ---
    for i in range(1, 501):
      temporada = (i % 8) + 1
      tipo = "Raro/Perdido" if i % 3 == 0 else "Clássico"
      episodios.append({
          "title": f"Chaves - Episódio #{i} ({tipo} T{temporada})",
          "series": "Chaves",
          "season": 1970 + (i % 10),
          "episode_number": i,
          "synopsis": (
              f"Episódio {tipo.lower()} da série Chaves, parte do acervo"
              f" completo da vila no Animagia."
          ),
          "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      })

    # --- 500 Episódios de Chapolin ---
    for i in range(1, 501):
      temporada = (i % 8) + 1
      tipo = "Raro/Perdido" if i % 3 == 0 else "Clássico"
      episodios.append({
          "title": f"Chapolin - Episódio #{i} ({tipo} T{temporada})",
          "series": "Chapolin",
          "season": 1970 + (i % 10),
          "episode_number": i,
          "synopsis": (
              f"Episódio {tipo.lower()} do Chapolin Colorado, defendendo os"
              f" indefesos no Animagia."
          ),
          "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      })

    for item in episodios:
      db.add(db_models.EpisodeModel(**item))
    db.commit()
  db.close()


@app.on_event("startup")
def startup_event():
  popular_dados_iniciais()


# Rota HTML de Streaming com a marca Animagia
@app.get("/", response_class=HTMLResponse)
def home(
    series: str = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
  limit = 30
  skip = (page - 1) * limit

  query = db.query(db_models.EpisodeModel)
  if series:
    query = query.filter(db_models.EpisodeModel.series.ilike(f"%{series}%"))

  total_episodios = query.count()
  episodios = query.offset(skip).limit(limit).all()

  series_param = f"&series={series}" if series else ""
  prev_page = page - 1 if page > 1 else None
  next_page = page + 1 if (skip + limit) < total_episodios else None

  html = f"""
    <html>
        <head>
            <title>Animagia - Acervo de Chaves e Chapolin</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #121212; color: #fff; margin: 0; padding: 20px; }}
                h1 {{ color: #ffcc00; text-align: center; }}
                .menu {{ text-align: center; margin-bottom: 20px; }}
                .menu a {{ background: #333; color: #fff; padding: 8px 15px; text-decoration: none; border-radius: 5px; margin: 0 5px; font-weight: bold; }}
                .menu a:hover {{ background: #ffcc00; color: #000; }}
                .container {{ display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; }}
                .card {{ background: #1e1e1e; border: 1px solid #333; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); width: 280px; padding: 15px; display: flex; flex-direction: column; justify-content: space-between; }}
                .card h3 {{ margin-top: 0; color: #ff5555; font-size: 15px; }}
                .badge {{ background: #ffcc00; color: #000; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; display: inline-block; margin-bottom: 8px; }}
                .btn {{ background: #e50914; color: white; text-decoration: none; padding: 8px; text-align: center; border-radius: 5px; font-weight: bold; margin-top: 10px; font-size: 14px; }}
                .btn:hover {{ background: #b20710; }}
                .pagination {{ text-align: center; margin-top: 30px; }}
                .pagination a {{ background: #e50914; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 0 10px; }}
                .pagination a:hover {{ background: #b20710; }}
                p {{ color: #ccc; font-size: 13px; }}
            </style>
        </head>
        <body>
            <h1>✨ Animagia - Chaves & Chapolin (1000 Episódios)</h1>
            <div class="menu">
                <a href="/">Ver Todos</a>
                <a href="/?series=Chaves">Apenas Chaves (500)</a>
                <a href="/?series=Chapolin">Apenas Chapolin (500)</a>
            </div>
            <div class="container">
    """

  for ep in episodios:
    html += f"""
            <div class="card">
                <div>
                    <span class="badge">{ep.series} - Ano {ep.season}</span>
                    <h3>{ep.title}</h3>
                    <p>{ep.synopsis}</p>
                </div>
                <a class="btn" href="{ep.video_url}" target="_blank">▶ Assistir Episódio</a>
            </div>
        """

  html += """
            </div>
            <div class="pagination">
    """
  if prev_page:
    html += f'<a href="/?page={prev_page}{series_param}">⬅ Página Anterior</a>'
  if next_page:
    html += f'<a href="/?page={next_page}{series_param}">Próxima Página ➡</a>'

  html += """
            </div>
        </body>
    </html>
    """
  return html


@app.get("/episodes", response_model=list[EpisodeSchema])
def list_episodes(
    series: str = Query(None),
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
):
  query = db.query(db_models.EpisodeModel)
  if series:
    query = query.filter(db_models.EpisodeModel.series.ilike(f"%{series}%"))
  return query.offset(skip).limit(limit).all()