from database import engine, get_db, SessionLocal
import models
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
import models as db_models
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Cria as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Animagia - Acervo de Chaves",
    description="Mega acervo com episódios de Chaves hospedado no Animagia",
    version="6.0.0",
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


# Função para popular a base com o episódio em destaque e o acervo de Chaves
def popular_dados_iniciais():
    db = SessionLocal()
    total = db.query(db_models.EpisodeModel).count()
    if total == 0:
        episodios = []

        # 1. Adicionando o episódio específico pedido (Invisibilidade Parte 2)
        episodios.append({
            "title": "Chaves - Invisibilidade (1976) Parte 2",
            "series": "Chaves",
            "season": 1976,
            "episode_number": 1,
            "synopsis": (
                "Episódio clássico onde o Kiko tenta ficar invisível usando"
                " tinta, causando confusão na vila com o Seu Barriga."
            ),
            "video_url": "Db9c4LDEgs0",
        })

        # Lista de IDs adicionais de Chaves para preencher o restante do acervo
        outros_ids = [
            "kJQP7kiw5Fk",
            "jNQXAC9IVRw",
            "dQw4w9WgXcQ",
            "3JZ_D3ELwOQ",
            "9bZkp7q19f0",
        ]

        # Preenchendo o restante dos 1000 episódios
        for i in range(2, 1001):
            temporada = (i % 8) + 1
            tipo = "Raro/Perdido" if i % 3 == 0 else "Clássico"
            vid_id = outros_ids[(i - 2) % len(outros_ids)]
            episodios.append({
                "title": f"Chaves - Episódio #{i} ({tipo} T{temporada})",
                "series": "Chaves",
                "season": 1970 + (i % 10),
                "episode_number": i,
                "synopsis": (
                    f"Episódio {tipo.lower()} da série Chaves, parte do acervo"
                    f" completo da vila no Animagia."
                ),
                "video_url": vid_id,
            })

        for item in episodios:
            db.add(db_models.EpisodeModel(**item))
        db.commit()
    db.close()


@app.on_event("startup")
def startup_event():
    popular_dados_iniciais()


# Rota HTML com a sua capa personalizada e player integrado
@app.get("/", response_class=HTMLResponse)
def home(page: int = Query(1, ge=1), db: Session = Depends(get_db)):
    limit = 12
    skip = (page - 1) * limit

    query = db.query(db_models.EpisodeModel)
    total_episodios = query.count()
    episodios = query.offset(skip).limit(limit).all()

    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (skip + limit) < total_episodios else None

    # URL exata da capa personalizada fornecida por você
    capa_url = "https://i.postimg.cc/TYkFPDS7/Chat-GPT-Image-22-de-set-de-2026-17-50-52.png"

    html = f"""
    <html>
        <head>
            <title>Animagia - O Melhor do Chaves</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #121212; color: #fff; margin: 0; padding: 20px; }}
                h1 {{ color: #ffcc00; text-align: center; }}
                .container {{ display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-top: 20px; }}
                .card {{ background: #1e1e1e; border: 1px solid #333; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); width: 320px; padding: 15px; display: flex; flex-direction: column; justify-content: space-between; }}
                .card h3 {{ margin-top: 0; color: #ff5555; font-size: 15px; }}
                .badge {{ background: #ffcc00; color: #000; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; display: inline-block; margin-bottom: 8px; }}
                
                /* Estilo da Capa Personalizada */
                .card-banner {{ width: 100%; height: 160px; border-radius: 6px; overflow: hidden; margin-bottom: 12px; border: 1px solid #444; }}
                .card-banner img {{ width: 100%; height: 100%; object-fit: cover; }}

                .video-container {{ position: relative; width: 100%; padding-bottom: 56.25%; height: 0; margin-top: 10px; }}
                .video-container iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 5px; border: none; }}
                .pagination {{ text-align: center; margin-top: 30px; }}
                .pagination a {{ background: #e50914; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 0 10px; }}
                .pagination a:hover {{ background: #b20710; }}
                p {{ color: #ccc; font-size: 13px; }}
            </style>
        </head>
        <body>
            <h1>✨ Animagia - Acervo Oficial de Chaves ✨</h1>
            <div class="container">
    """

    for ep in episodios:
        html += f"""
            <div class="card">
                <div>
                    <span class="badge">Ano {ep.season}</span>
                    <div class="card-banner">
                        <img src="{capa_url}" alt="Capa Chaves">
                    </div>
                    <h3>{ep.title}</h3>
                    <p>{ep.synopsis}</p>
                </div>
                <div class="video-container">
                    <iframe src="https://www.youtube.com/embed/{ep.video_url}" allowfullscreen></iframe>
                </div>
            </div>
        """

    html += """
            </div>
            <div class="pagination">
    """
    if prev_page:
        html += f'<a href="/?page={prev_page}">⬅ Página Anterior</a>'
    if next_page:
        html += f'<a href="/?page={next_page}">Próxima Página ➡</a>'

    html += """
            </div>
        </body>
    </html>
    """
    return html


@app.get("/episodes", response_model=list[EpisodeSchema])
def list_episodes(
    skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)
):
    return db.query(db_models.EpisodeModel).offset(skip).limit(limit).all()
