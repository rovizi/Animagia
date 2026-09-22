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
    title="Animagia - Maratona Chaves",
    description="Todos os episódios reunidos em uma única capa interativa",
    version="10.0.0",
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


# Função para popular a base com todos os episódios do link fornecido vinculados à playlist
def popular_dados_iniciais():
    db = SessionLocal()
    total = db.query(db_models.EpisodeModel).count()
    if total == 0:
        playlist_id = "PLjME5p95AbaS9R79_uQ3KDKMV-ZpKcidO"
        primeiro_video_id = "Db9c4LDEgs0"

        episodios_chaves = [
            {
                "title": (
                    "Maratona Completa - Chaves (Todos os Episódios da"
                    " Playlist)"
                ),
                "series": "Chaves",
                "season": 1970,
                "episode_number": 1,
                "synopsis": (
                    "Assista a todos os episódios de Chaves em sequência"
                    " contínua através da playlist oficial completa."
                ),
                "video_url": primeiro_video_id,
            }
        ]

        db.add(db_models.EpisodeModel(**episodios_chaves[0]))
        db.commit()
    db.close()


@app.on_event("startup")
def startup_event():
    popular_dados_iniciais()


# Rota HTML com uma única capa centralizada, botão com silhueta e player de playlist sequencial
@app.get("/", response_class=HTMLResponse)
def home(db: Session = Depends(get_db)):
    # URL exata da sua capa personalizada fornecida
    capa_url = "https://i.postimg.cc/TYkFPDS7/Chat-GPT-Image-22-de-set-de-2026-17-50-52.png"
    
    # ID da Playlist completa de Chaves fornecida pelo usuário
    playlist_id = "PLjME5p95AbaS9R79_uQ3KDKMV-ZpKcidO"
    video_inicial = "Db9c4LDEgs0"

    html = f"""
    <html>
        <head>
            <title>Animagia - Maratona Chaves</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #121212; color: #fff; margin: 0; padding: 20px; text-align: center; }}
                h1 {{ color: #ffcc00; margin-bottom: 10px; }}
                p.subtitle {{ color: #ccc; margin-bottom: 30px; font-size: 15px; }}
                
                .main-container {{
                    display: flex; justify-content: center; align-items: center; margin-top: 20px;
                }}
                
                .card {{
                    background: #1e1e1e; border: 1px solid #333; border-radius: 12px;
                    box-shadow: 0 8px 16px rgba(0,0,0,0.7); width: 600px; max-width: 100%; padding: 20px;
                    display: flex; flex-direction: column; align-items: center;
                }}
                
                .card h3 {{ color: #ff5555; font-size: 20px; margin: 15px 0 10px 0; }}
                .badge {{ background: #ffcc00; color: #000; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-bottom: 15px; display: inline-block; }}
                
                /* Estilo da Única Capa com Botão de Play Interativo */
                .media-container {{ position: relative; width: 100%; height: 340px; border-radius: 8px; overflow: hidden; border: 1px solid #444; background: #000; }}
                .media-container img.banner {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                
                .play-overlay {{
                    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(0, 0, 0, 0.45); display: flex; align-items: center; justify-content: center;
                    cursor: pointer; transition: background 0.3s ease;
                }}
                .play-overlay:hover {{ background: rgba(0, 0, 0, 0.25); }}
                
                /* Botão com a silhueta do rosto/chapéu do Chaves */
                .chaves-btn {{
                    width: 75px; height: 75px; background: #ffcc00; border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    box-shadow: 0 6px 15px rgba(0,0,0,0.8); transition: transform 0.2s ease;
                }}
                .play-overlay:hover .chaves-btn {{ transform: scale(1.1); }}
                .chaves-btn svg {{ width: 42px; height: 42px; fill: #121212; }}

                .video-slot {{ display: none; width: 100%; height: 340px; }}
                .video-slot iframe {{ width: 100%; height: 100%; border-radius: 8px; border: none; }}

                p.desc {{ color: #bbb; font-size: 14px; margin-top: 10px; line-height: 1.4; }}
            </style>
            <script>
                function playPlaylist() {{
                    const container = document.getElementById('media-wrapper');
                    // Carrega a playlist contínua completa do YouTube
                    container.innerHTML = '<div class="video-slot" style="display:block;"><iframe src="https://www.youtube.com/embed/{video_inicial}?list={playlist_id}&autoplay=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>';
                }}
            </script>
        </head>
        <body>
            <h1>✨ Animagia - Maratona Oficial de Chaves ✨</h1>
            <p class="subtitle">Todos os episódios reunidos em um único acervo contínuo</p>
            
            <div class="main-container">
                <div class="card">
                    <div>
                        <span class="badge">Acervo Completo (Playlist Oficial)</span>
                        <div class="media-container" id="media-wrapper">
                            <img src="{capa_url}" class="banner" alt="Capa Chaves">
                            <div class="play-overlay" onclick="playPlaylist()">
                                <div class="chaves-btn" title="Assistir Maratona Completa">
                                    <!-- Silhueta / Ícone do Chaves -->
                                    <svg viewBox="0 0 24 24">
                                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V7h2v5zm4 4h-2v-2h2v2zm0-4h-2V7h2v5z"/>
                                    </svg>
                                </div>
                            </div>
                        </div>
                        <h3>Chaves - Todos os Episódios em Sequência</h3>
                        <p class="desc">Clique na capa para iniciar a maratona. Os episódios passarão automaticamente em sequência diretamente na tela.</p>
                    </div>
                </div>
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
