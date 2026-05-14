import sys
import os
import pytest
from fastapi.testclient import TestClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


from celery_app import celery_app
from main import app

client = TestClient(app)

class TestOperaçõesMatemáticas:

    def test_soma_dois_numeros(self):
        resultado = soma(2, 3)
        assert resultado == 5
        assert isinstance(resultado, int)
    
    def test_subtração_dois_numeros(self):
        resultado = subtracao(5, 2)
        assert resultado == 3
        assert isinstance(resultado, int)

    def test_multiplicação_dois_numeros(self):
        resultado = multiplicacao(4, 3)
        assert resultado == 12
        assert isinstance(resultado, int)
    

def soma(a,b):
    return a + b

def subtracao(a,b):
    return a - b

def multiplicacao(a,b):
    return a * b

def test_configuração_celery():
    assert celery_app.main == "tarefas_livros"
    assert celery_app.conf.task_track_started == True
    assert celery_app.conf.result_expires == 3600
    assert celery_app.conf.result_persistent == True
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.result_serializer == "json"
    assert "json" in celery_app.conf.accept_content

def test_soma_dois_numeros():
    resultado = soma(2, 3)
    assert resultado == 5
    assert isinstance(resultado, int)


"""
def test_resultado_valido_endpoint_calcular_soma(client):
    response = client.post("/calcular/soma", json={"a": 4, "b": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == 9
    assert isinstance(data["resultado"], int)

def test_hello_world(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello, World!"
"""