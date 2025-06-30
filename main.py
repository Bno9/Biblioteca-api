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

# Vamos acessar nossos endpoints
# E vamos acessar os PATHs desses endpoints
# Query strings são o "?" depois do path
# o "&" funciona que nem o "and" da programação
# http://127.0.0.1:8000/adicionar?id=1&nome=Harry Potter&autor=J.K&ano=2005
# http://127.0.0.1:8000/livros
# http://127.0.0.1:8000/atualizar/id?
# http://127.0.0.1:8000/deletar/id


from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import os

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, session

DATABASE_URL = "sqlite:///./livros.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(
    title="API de livros",
    description="Api para gerenciar livros",
    version="1.0.0",
    contact={
        "name":"Breno",
        "email":"Breno_live2002@hotmail.com"
    }
)

MEU_USUARIO = "admin"
MINHA_SENHA = "admin"

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
 
class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

Base.metadata.create_all(bind=engine)

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


@app.get("/livros")
def get_livros(page: int = 1, limit: int = 10, db: session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page ou limite com valores inválidos")

    livros = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()
    
    if not livros:
        return {"message": "Não existe nenhum livro"}

    total_livros = db.query(LivroDB).count()

    return {
        "page": page,
        "limit": limit,
        "total": total_livros,
        "livros": [{"id": livro.id, "nome_livro": livro.nome_livro, "auto_livro": livro.autor_livro, "ano_livro": livro.ano_livro} for livro in livros]
    }

@app.post("/adicionar")
def post_livros(livro: Livro, db: session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
   db_livro = db.query(LivroDB).filter(LivroDB.nome_livro == livro.nome_livro, LivroDB.autor_livro == livro.autor_livro).first()
   if db_livro:
       raise HTTPException(status_code=400, detail="Esse livro ja existe no banco de dados") 
   
   novo_livro = LivroDB(nome_livro=livro.nome_livro, autor_livro=livro.autor_livro, ano_livro=livro.ano_livro)
   db.add(novo_livro)
   db.commit()
   db.refresh(novo_livro)

   return{"message": "O livro foi criado com sucesso!"}
    
@app.put("/atualizar/{id}")
def put_livros(id: int, livro: Livro, db: session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
   db_livro= db.query(LivroDB).filter(LivroDB.id == id).first()
   if not db_livro:
       raise HTTPException(status_code=404, detail="Este livro não foi encontrado no banco de dados")
   
   db_livro.nome_livro = livro.nome_livro
   db_livro.autor_livro = livro.autor_livro
   db_livro.ano_livro = livro.ano_livro
   db.commit()
   db.refresh(db_livro)

   return {"message": "O livro foi atualizado com sucesso"}
    
@app.delete("/deletar/{id}")
def delete_livros(id: int, db: session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id).first()

    if not db_livro:
        raise HTTPException(status_code=404, detail="Este livro não foi encontrado no banco de dados")
    
    db.delete(db_livro)
    db.commit()

    return{"message":"Seu livro foi deletado com sucesso"}


#testa no postman ou inmsonia