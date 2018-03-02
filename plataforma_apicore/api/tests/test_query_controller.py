from flask import url_for
import pytest
from api.server import get_app
from mock import patch
from utils.http import HttpClient, ExecutionResult
import json

from model.domain import conta


def apicore_map():
    res = ExecutionResult(200)
    r = dict()
    r["name"] = "Conta"
    r["systemId"] = "ec498841-59e5-47fd-8075-136d79155705"
    r["processId"] = "61728cac-a576-4643-8e58-82a83b304053"
    r["content"] = "Conta:\r\n  model: conta\r\n  fields:\r\n    saldo:\r\n      column: saldo\r\n    titular:\r\n      column: titular\r\n  filters:\r\n    transferencia: \"id in (:origem, :destino)\"\n    clientes: \"id in ($ids)\"\n  "
    r["id"] = "3bc8b1b3-cd79-480b-99ca-c63de74c4f65"
    r["_metadata"] = dict()
    r["_metadata"]["type"] = "map"
    r["_metadata"]["instance_id"] = "62141389-2ef2-4715-8675-a670ad7a00cc"
    r["_metadata"]["branch"] = "master"
    res.data = [r]
    return res


@pytest.mark.usefixtures('app')
def test_query_invalid_params(app):
    with patch.object(HttpClient, 'get', return_value=apicore_map()) as mock_method:
        client = app.test_client()
        response = client.get('/conta/conta', follow_redirects=True)
        assert response.status_code == 400


@pytest.mark.usefixtures('app')
def test_query_valid_params(app):
    with patch.object(HttpClient, 'get', return_value=apicore_map()) as mock_method:
        client = app.test_client()
        response = client.get('/Conta/Conta', follow_redirects=True)
        assert response.status_code == 200

@pytest.mark.usefixtures('app')
def test_query_valid_params_and_query(app):
    with patch.object(HttpClient, 'get', return_value=apicore_map()) as mock_method:
        client = app.test_client()
        response = client.get(f'/Conta/Conta?filter=transferencia&origem=042f54bc-c5a1-4f9b-8ed7-d8e01ca130bf&destino=042f54bc-c5a1-4f9b-8ed7-d8e01ca130bf', follow_redirects=True)
        assert response.status_code == 200

def test_get_data_from_map_paginated(app):
    from database import create_session

    session = create_session()
    for i in range(100):
        session.add(conta(titular="Fabio", saldo=10000))
    session.commit()

    with patch.object(HttpClient, 'get', return_value=apicore_map()) as mock_method:
        client = app.test_client()
        response = client.get(f'/Conta/Conta?page=1&page_size=10', follow_redirects=True)
        data = json.loads(response.data)
        assert len(data) == 10


def test_get_data_from_map(app):
    from database import create_session
    c = conta(titular="Fabio", saldo=10000)
    c_ = conta(titular="Moneda", saldo=100)
    s = create_session()
    s.add(c)
    s.add(c_)
    s.commit()

    with patch.object(HttpClient, 'get', return_value=apicore_map()) as mock_method:
        client = app.test_client()
        response = client.get(f'/Conta/Conta?filter=transferencia&origem={c.id}&destino={c_.id}', follow_redirects=True)
        resp = json.loads(response.data)
        assert response.status_code == 200
        assert len(resp) == 2
        assert "saldo" and "titular" and "_metadata" in resp[0]
        assert resp[0]["titular"] == "Fabio"
        assert resp[1]["titular"] == "Moneda"
        assert "branch" in resp[0]["_metadata"]
        assert "branch" in resp[1]["_metadata"]
        response = client.get(f'/Conta/Conta?filter=clientes&ids={c.id};{c_.id}')
        assert response.status_code == 200
        assert len(json.loads(response.data)) == 2
