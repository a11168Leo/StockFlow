from backend.database.connection import mongodb

def testar_conexao():
    col = mongodb.get_collection("teste_conexao")
    col.insert_one({"status": "ok"})
    print("✅ MongoDB Atlas conectado com sucesso!")

if __name__ == "__main__":
    testar_conexao()
