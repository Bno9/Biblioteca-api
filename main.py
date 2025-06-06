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
# o "&" funciona que nem o "and" da programação ]
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

security = HTTPBasic()

livros = {}

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

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
def get_livros(page: int = 1, limit: int = 10, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page ou limite com valores inválidos")
    
    if not livros:
        return {"message": "Não existe nenhum livro"}

    livros_ordenados = sorted(livros.items(), key=lambda x: x[0])

    start = (page - 1) * limit
    end = start + limit

    livros_paginados = [
        {"id": id_livro, "nome_livro": livro_data["nome_livro"], "autor_livro": livro_data["autor_livro"], "ano_livro": livro_data["ano_livro"]}
        for id_livro, livro_data in livros_ordenados[start:end]
    ]

    return {
        "page": page,
        "limit": limit,
        "total": len(livros),
        "livros": livros_paginados
    }

@app.post("/adicionar")
def post_livros(id: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if id in livros:
        raise HTTPException(status_code=400, detail="Esse livro já existe")
    else:
        livros[id] = livro.dict()
        return {"message": "O livro foi criado com sucesso"}
    
@app.put("/atualizar/{id}")
def put_livros(id: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    meu_livro = livros.get(id)
    if id not in livros:
        raise HTTPException(status_code=404, detail="Esse livro não foi encontrado")
    else:
        livros[id] = livro.dict()
        return {"Message": "As informações do seu livro foram atualizadas com sucesso"}
    
@app.delete("/deletar/{id}")
def delete_livros(id: int, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if id not in livros:
        raise HTTPException(status_code=404, detail="Esse livro não foi encontrado")
    else:
        del livros[id]
        return {"message": "O livro foi deletado"}
    
#testa no postman ou inmsonia