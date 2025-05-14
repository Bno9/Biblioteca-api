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

app = FastAPI()

livros = {

}

@app.get("/livros")
def get_livros():
    if not livros:
        return {"message": "Não existe nenhum livro"}
    else:
        return {"Livros": livros}

@app.post("/adicionar")
def post_livros(id: int, nome: str, autor: str, ano: int):
    if id in livros:
        raise HTTPException(status_code=400, detail="Esse livro já existe")
    else:
        livros[id] = {"nome": nome, "autor": autor, "ano": ano}
        return {"message": "O livro foi criado com sucesso"}
    
@app.put("/atualizar/{id}")
def put_livros(id: int, nome: str, autor: str, ano: int):
    livro = livros.get(id)
    if not livros:
        raise HTTPException(status_code=404, detail="Esse livro não foi encontrado")
    else:
        if nome:
            livro["nome"] = nome
        if autor:
            livro["autor"] = autor
        if ano:
            livro["ano"] = ano

        return {"Message": "As informações do seu livro foram atualizadas com sucesso"}
    
@app.delete("/deletar/{id}")
def delete_livros(id: int):
    if id not in livros:
        raise HTTPException(status_code=404, detail="Esse livro não foi encontrado")
    else:
        del livros[id]
        return {"message": "O livro foi deletado"}
    
#testa no postman ou inmsonia