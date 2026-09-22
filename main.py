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
    version="13.0.0",
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


# Função para popular a base com os dados iniciais
def popular_dados_iniciais():
    db = SessionLocal()
    total = db.query(db_models.EpisodeModel).count()
    if total == 0:
        primeiro_video_id = "Db9c4LDEgs0"

        episodios_chaves = [
            {
                "title": (
                    "Maratona Completa - Chaves (Todos os Episódios da"
                    " Playlist)"
                ),
                "series": "Chaves",
                "season": 1976,
                "episode_number": 1,
                "synopsis": (
                    "Aqui você assiste a todos os episódios de Chaves em"
                    " sequência contínua. Divirta-se com as confusões na vila"
                    " mais famosa da televisão!"
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


# Rota HTML com o botão personalizado contendo a silhueta do Chaves
@app.get("/", response_class=HTMLResponse)
def home(db: Session = Depends(get_db)):
    capa_url = "https://i.postimg.cc/TYkFPDS7/Chat-GPT-Image-22-de-set-de-2026-17-50-52.png"
    playlist_id = "PLjME5p95AbaS9R79_uQ3KDKMV-ZpKcidO"
    video_inicial = "Db9c4LDEgs0"

    html = f"""
    <html>
        <head>
            <title>Animagia - Maratona Chaves</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #121212; color: #fff; margin: 0; padding: 20px; text-align: center; }}
                h1 {{ color: #ffcc00; margin-bottom: 5px; }}
                p.subtitle {{ color: #aaa; margin-bottom: 30px; font-size: 14px; }}
                
                .main-container {{
                    display: flex; justify-content: center; align-items: center; margin-top: 10px;
                }}
                
                .card {{
                    background: #18181b; border: 1px solid #27272a; border-radius: 12px;
                    box-shadow: 0 10px 20px rgba(0,0,0,0.6); width: 320px; overflow: hidden;
                    text-align: left; display: flex; flex-direction: column; position: relative;
                }}
                
                .media-container {{ position: relative; width: 100%; height: 420px; background: #000; }}
                .media-container img.banner {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                
                .year-badge {{
                    position: absolute; top: 12px; left: 12px;
                    background: rgba(0, 0, 0, 0.7); color: #fff; font-weight: bold; font-size: 11px;
                    padding: 3px 7px; border-radius: 4px; border: 1px solid #3f3f46;
                    z-index: 2;
                }}

                .age-badge {{
                    position: absolute; top: 12px; right: 12px;
                    background: #16a34a; color: #fff; font-weight: bold; font-size: 11px;
                    padding: 3px 8px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.5);
                    z-index: 2;
                }}
                
                .play-overlay {{
                    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center;
                    cursor: pointer; transition: background 0.3s ease;
                }}
                .play-overlay:hover {{ background: rgba(0, 0, 0, 0.2); }}
                
                /* Botão circular com destaque em amarelo e a silhueta temática */
                .chaves-btn {{
                    width: 70px; height: 70px; background: #ffcc00; border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.8); transition: transform 0.2s ease;
                }}
                .play-overlay:hover .chaves-btn {{ transform: scale(1.1); }}
                
                /* Estilização da silhueta do personagem dentro do botão */
                .chaves-btn svg {{ width: 42px; height: 42px; fill: #121212; }}

                .video-slot {{ display: none; width: 100%; height: 420px; }}
                .video-slot iframe {{ width: 100%; height: 100%; border: none; }}

                .card-content {{ padding: 16px; display: flex; flex-direction: column; gap: 6px; }}
                .title-row {{ display: flex; justify-content: space-between; align-items: center; }}
                .card-title {{ font-size: 15px; font-weight: bold; color: #fff; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 260px; }}
                
                .info-icon {{
                    width: 20px; height: 20px; border: 1px solid #71717a; border-radius: 50%;
                    display: flex; align-items: center; justify-content: center; color: #a1a1aa; font-size: 11px; font-weight: bold; cursor: pointer;
                }}
                
                .card-genre {{ font-size: 12px; color: #a1a1aa; margin: 0; }}
                
                .duration-row {{ display: flex; align-items: center; gap: 5px; font-size: 12px; color: #a1a1aa; margin-top: 4px; }}
                .duration-row svg {{ width: 13px; height: 13px; fill: #a1a1aa; }}
            </style>
            <script>
                function playPlaylist() {{
                    const container = document.getElementById('media-wrapper');
                    container.innerHTML = '<div class="video-slot" style="display:block;"><iframe src="https://www.youtube.com/embed/{video_inicial}?list={playlist_id}&autoplay=1" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>';
                }}
            </script>
        </head>
        <body>
            <h1>✨ Animagia - Catálogo Oficial ✨</h1>
            <p class="subtitle">Sua central de maratonas contínuas</p>
            
            <div class="main-container">
                <div class="card">
                    <div class="media-container" id="media-wrapper">
                        <div class="year-badge">1976</div>
                        <div class="age-badge">Livre</div>
                        <img src="{capa_url}" class="banner" alt="Capa Chaves">
                        <div class="play-overlay" onclick="playPlaylist()">
                            <div class="chaves-btn" title="Iniciar Maratona do Chaves">
                                <!-- Silhueta estilizada remetendo ao chapéu/boneco clássico -->
                                <svg viewBox="0 0 24 24">
                                    <path d="M12 2C9.5 2 7.5 4 7.5 6.5C7.5 7.8 8.1 9 9 9.8V11C9 12.1 9.9 13 11 13H13C14.1 13 15 12.1 15 11V9.8C15.9 9 16.5 7.8 16.5 6.5C16.5 4 14.5 2 12 2M5 15C3.34 15 2 16.34 2 18V21H22V18C22 16.34 20.66 15 19 15H5Z"/>
                                </svg>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card-content">
                        <div class="title-row">
                            <h3 class="card-title" title="Chaves: A Série Completa">Chaves: A Série Completa...</h3>
                            <div class="info-icon" title="Mais informações">i</div>
                        </div>
                        <p class="card-genre">Comédia, Desenhos 24h, Infantil</p>
                        <div class="duration-row">
                            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
                            <span>Maratona Contínua</span>
                        </div>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    return html


@app.get("/episodes", response_model=list[EpisodeSchema])
def list_episodes(
    skip: int = 0, limit: int, db: Session = Depends(get_db)
):
    return db.query(db_models.EpisodeModel).offset(skip).limit(limit).all()
