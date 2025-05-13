from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.testclient import TestClient

# Inicializa o aplicativo FastAPI
app = FastAPI()

# Rota básica
@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Rota com parâmetros de consulta (query parameters)
@app.get("/greet")
def greet(name: str):
    return {"message": f"Hello {name}"}

# Rota com parâmetros de caminho (path parameters)
@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello {name}"}

# Rota POST com validação de dados (usando o modelo Pydantic)
class Item(BaseModel):
    name: str
    description: str

# Simulando um banco de dados em memória para os itens
items_db = {}

@app.post("/items/")
def create_item(item: Item):
    item_id = len(items_db) + 1
    items_db[item_id] = item
    return {"id": item_id, "name": item.name, "description": item.description}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, "name": items_db[item_id].name, "description": items_db[item_id].description}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = item
    return {"id": item_id, "name": item.name, "description": item.description}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return {"message": f"Item {item_id} has been deleted."}

# Simulando um banco de dados em memória para os workshops
workshops_db = {}

@app.put("/workshop/{id}")
def put_workshop(id: int, nome: str = None):
    if id in workshops_db:
        workshops_db[id] = nome
        return {"Nova aula": nome}
    else:
        raise HTTPException(status_code=404, detail="Workshop não encontrado")

@app.delete("/workshop/{id}")
def delete_workshop(id: int):
    if id in workshops_db:
        del workshops_db[id]
        return {"message": f"Workshop {id} excluído com sucesso."}
    else:
        raise HTTPException(status_code=404, detail="Workshop não encontrado")

# Rota com os métodos GET, POST, PUT e DELETE para /greet/{name}
@app.route("/greet/{name}", methods=["GET", "POST", "PUT", "DELETE"])
async def greet_post_put_delete(request: Request, name: str):
    if request.method == "GET":
        return {"message": f"Hello {name} from GET"}
    elif request.method == "POST":
        return {"message": f"Hello {name} from POST"}
    elif request.method == "PUT":
        return {"message": f"Hello {name} from PUT"}
    elif request.method == "DELETE":
        return {"message": f"Goodbye {name} from DELETE"}

# Inicializa o TestClient para testar o aplicativo
client = TestClient(app)

# Casos de teste para a rota /greet/{name}
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_greet_with_query_param():
    response = client.get("/greet?name=John")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello John"}

def test_greet_with_path_param():
    response = client.get("/greet/Alice")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Alice"}

def test_greet_post_put_delete_get():
    response = client.get("/greet/Alice")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Alice from GET"}

def test_greet_post_put_delete_post():
    response = client.post("/greet/Alice")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Alice from POST"}

def test_greet_post_put_delete_put():
    response = client.put("/greet/Alice")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Alice from PUT"}

def test_greet_post_put_delete_delete():
    response = client.delete("/greet/Alice")
    assert response.status_code == 200
    assert response.json() == {"message": "Goodbye Alice from DELETE"}

# Casos de teste para a rota /items/
def test_create_item():
    response = client.post("/items/", json={"name": "Laptop", "description": "A high-end gaming laptop"})
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["name"] == "Laptop"

def test_read_item():
    # Criar um item antes de tentar ler
    response = client.post("/items/", json={"name": "Laptop", "description": "A high-end gaming laptop"})
    item_id = response.json()["id"]
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Laptop"
    assert response.json()["description"] == "A high-end gaming laptop"

def test_update_item():
    # Criar um item antes de tentar atualizar
    response = client.post("/items/", json={"name": "Laptop", "description": "A high-end gaming laptop"})
    item_id = response.json()["id"]
    response = client.put(f"/items/{item_id}", json={"name": "Laptop Pro", "description": "A more powerful gaming laptop"})
    assert response.status_code == 200
    assert response.json()["name"] == "Laptop Pro"
    assert response.json()["description"] == "A more powerful gaming laptop"

def test_delete_item():
    # Criar um item antes de tentar excluir
    response = client.post("/items/", json={"name": "Laptop", "description": "A high-end gaming laptop"})
    item_id = response.json()["id"]
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Item {item_id} has been deleted."

def test_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

# Casos de teste para a rota /workshop/{id}
def test_create_workshop():
    # Criar workshop antes de usar
    workshops_db[1] = "Cliente-Servidor com API"
    response = client.get("/workshop/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Cliente-Servidor com API"}

def test_update_workshop():
    workshops_db[1] = "API com FastAPI"
    response = client.put("/workshop/1", params={"nome": "Novo Workshop API"})
    assert response.status_code == 200
    assert response.json() == {"Nova aula": "Novo Workshop API"}

def test_delete_workshop():
    workshops_db[1] = "Cliente-Servidor com API"
    response = client.delete("/workshop/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Workshop 1 excluído com sucesso."}

def test_workshop_not_found():
    response = client.put("/workshop/999", params={"nome": "Workshop Inexistente"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Workshop não encontrado"}

    response = client.delete("/workshop/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Workshop não encontrado"}

# Rodar todos os testes
if __name__ == "__main__":
    import pytest
    pytest.main()
