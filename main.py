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


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="API de livros",
    description="Api para gerenciar livros",
    version="1.0.0",
    contact={
        "name":"Breno",
        "email":"Breno_live2002@hotmail.com"
    }
)

livros = {}

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

@app.get("/livros")
def get_livros():
    if not livros:
        return {"message": "Não existe nenhum livro"}
    else:
        return {"Livros": livros}

@app.post("/adicionar")
def post_livros(id: int, livro: Livro):
    if id in livros:
        raise HTTPException(status_code=400, detail="Esse livro já existe")
    else:
        livros[id] = livro.dict()
        return {"message": "O livro foi criado com sucesso"}
    
@app.put("/atualizar/{id}")
def put_livros(id: int, livro: Livro):
    meu_livro = livros.get(id)
    if id not in livros:
        raise HTTPException(status_code=404, detail="Esse livro não foi encontrado")
    else:
        livros[id] = livro.dict()
        return {"Message": "As informações do seu livro foram atualizadas com sucesso"}
    
@app.delete("/deletar/{id}")
def delete_livros(id: int):
    if id not in livros:
        raise HTTPException(status_code=404, detail="Esse livro não foi encontrado")
    else:
        del livros[id]
        return {"message": "O livro foi deletado"}
    
#testa no postman ou inmsonia