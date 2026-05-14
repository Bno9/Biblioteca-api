from tasks import somar, fatorial

def test_somar():
    resultado = somar.apply(args=[5,3]).get()
    assert resultado == 8


def test_fatorial():
    resultado = fatorial.apply(args=[5]).get()
    assert resultado == 120

def test_celery_configuração():
    from celery_app import celery_app
    assert celery_app.main == "tarefas_livros"
    assert celery_app.conf.task_track_started == True
    assert celery_app.conf.result_expires == 3600
    assert celery_app.conf.result_persistent == True
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.result_serializer == "json"
    assert "json" in celery_app.conf.accept_content