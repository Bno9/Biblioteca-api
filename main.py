# API de livros

# GET, POST, PUT, DELETE

# POST - Adicionar novos livros (Create)
# GET - Buscar os dados dos livros (Read)
# PUT - Atualizar informações dos livros (Update)
# DELETE - Deletar informações dos livros (Delete)

# CRUD

# Create
# Read
# Update
# Delete

# Query strings são o "?" depois do path
# o "&" funciona que nem o "and" da programação
# http://127.0.0.1:8000/adicionar?id=1&nome=Harry Potter&autor=J.K&ano=2005
# http://127.0.0.1:8000/livros
# http://127.0.0.1:8000/atualizar/id?
# http://127.0.0.1:8000/deletar/id


from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import os
import asyncio
import redis 
import json
from tasks import somar, fatorial
from celery_app import celery_app
from celery.result import AsyncResult
from kafka_producer import enviar_evento_kafka

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

app = FastAPI(
    title="API de livros",
    description="Api para gerenciar livros",
    version="1.0.0",
    contact={
        "name":"Breno",
        "email":"Breno_live2002@hotmail.com"
    }
)

MEU_USUARIO = os.getenv("MEU_USUARIO")
MINHA_SENHA = os.getenv("MINHA_SENHA")

#inicia o import de segurança
security = HTTPBasic()

livros_antigo = {}

#modula a base do banco de dados
class LivroDB(Base):
    __tablename__ = "Livros"
    id = Column(Integer, primary_key=True, index=True)
    nome_livro = Column(String, index=True)
    autor_livro = Column(String, index=True)
    ano_livro = Column(Integer)
 
#modula a classe de livro usando basemodel
class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

Base.metadata.create_all(bind=engine)

def salvar_livros_redis(livro_id: int, livro: Livro):
    redis_client.set(f"livro:{livro_id}", json.dumps(livro.model_dump()))

def deletar_livros_redis(livro_id: int):
    redis_client.delete(f"livro:{livro_id}")

def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Essa função valida usuario e senha
def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, MEU_USUARIO)
    is_password_correct = secrets.compare_digest(credentials.password, MINHA_SENHA)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(        
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"}
        )

async def chamadas_externas_1():
    await asyncio.sleep(2)
    return "Resultado chamada externa 1"

async def chamadas_externas_2():
    await asyncio.sleep(2)
    return "Resultado chamada externa 2"

async def chamadas_externas_3():
    await asyncio.sleep(2)
    return "Resultado chamada externa 3"

@app.get("/chamadas-externas")
async def chamadas_externas():
    tarefa1 = asyncio.create_task(chamadas_externas_1())
    tarefa2 = asyncio.create_task(chamadas_externas_2())
    tarefa3 = asyncio.create_task(chamadas_externas_3())

    resultado1 = await tarefa1
    resultado2 = await tarefa2
    resultado3 = await tarefa3

    return {
        "mensagem": "Todas as chamadas da api foram concluidas com sucesso",
        "Resultado": [resultado1, resultado2, resultado3]
    }

@app.get("/tarefas/recentes")
def listar_tarefas_recentes():
    tarefas_ids = redis_client.lrange("tarefas_ids", 0, -1)
    tarefas_info = []

    for task_id in tarefas_ids:
        resultado = AsyncResult(task_id, app=celery_app)

        tarefas_info.append({
            "task_id": task_id,
            "status": resultado.status,
            "resultado": resultado.result if resultado.ready() else None
        })

    return tarefas_info

@app.get("/debug/redis")
def ver_livros_redis():
    chaves = redis_client.keys("livro:*")
    livros = []

    for chave in chaves:
        valor = redis_client.get(chave)
        ttl = redis_client.ttl(chave)

        livros.append({"Chave": chave, "valor": json.loads(valor), "ttl": ttl})

    return livros

@app.post("/calcular/soma")
def calcular_soma(a: int, b: int):
    tarefa = somar.delay(a, b)
    redis_client.lpush("tarefas_ids", tarefa.id)
    redis_client.ltrim("tarefas_ids", 0, 49)
    return {"task_id": tarefa.id, "status": "Tarefa de soma iniciada"}

@app.post("/calcular/fatorial")
def calcular_fatorial(n: int):
    tarefa = fatorial.delay(n)
    redis_client.lpush("tarefas_ids", tarefa.id)
    redis_client.ltrim("tarefas_ids", 0, 49)
    return {"task_id": tarefa.id, "status": "Tarefa de fatorial iniciada"}

@app.get("/livros")
def get_livros(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(sessao_db),
    Credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page ou limit estão com valores invalidos")
    
    cache_key = f"livros:page={page}&limit={limit}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)
    
    livros = db.query(LivroDB).offset( (page - 1) * limit).limit(limit).all()

    if not livros:
        return {"message": "Não existe nenhum livro"}
    
    total_livros = db.query(LivroDB).count()

    resposta = {
        "page": page,
        "limit": limit,
        "total": total_livros,
        "livros": [{
            "id": livro.id,
            "nome_livro": livro.nome_livro,
            "autor_livro": livro.autor_livro,
            "ano_livro": livro.ano_livro
        } for livro in livros]
    }

    redis_client.setex(cache_key, 30, json.dumps(resposta))

    return resposta

@app.post("/adicionar")
async def post_livros(livro: Livro, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
   db_livro = db.query(LivroDB).filter(LivroDB.nome_livro == livro.nome_livro, LivroDB.autor_livro == livro.autor_livro).first()
   if db_livro:
       raise HTTPException(status_code=400, detail="Esse livro ja existe no banco de dados") 
   
   novo_livro = LivroDB(nome_livro=livro.nome_livro, autor_livro=livro.autor_livro, ano_livro=livro.ano_livro)
   db.add(novo_livro)
   db.commit()
   db.refresh(novo_livro)

   salvar_livros_redis(novo_livro.id, livro)

   enviar_evento_kafka("livros_evento", {
       "evento": "Livro criado", 
       "id": novo_livro.id, 
       "nome_livro": livro.nome_livro
       })

   return{"message": "O livro foi criado com sucesso!"}
    
@app.put("/atualizar/{id}")
async def put_livros(id: int, livro: Livro, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
   db_livro= db.query(LivroDB).filter(LivroDB.id == id).first()
   if not db_livro:
       raise HTTPException(status_code=404, detail="Este livro não foi encontrado no banco de dados")
   
   db_livro.nome_livro = livro.nome_livro
   db_livro.autor_livro = livro.autor_livro
   db_livro.ano_livro = livro.ano_livro
   db.commit()
   db.refresh(db_livro)

   salvar_livros_redis(db_livro.id, livro)

   return {"message": "O livro foi atualizado com sucesso"}
    
@app.delete("/deletar/{id}")
async def delete_livros(id: int, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id).first()

    if not db_livro:
        raise HTTPException(status_code=404, detail="Este livro não foi encontrado no banco de dados")
    
    db.delete(db_livro)
    db.commit()

    deletar_livros_redis(id)

    return{"message":"Seu livro foi deletado com sucesso"}


#testa no postman ou inmsonia