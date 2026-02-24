from backend.database.connection import mongodb


config_collection = mongodb.get_collection("configuracoes")


class ConfiguracaoService:
    @staticmethod
    def get_margem_alerta_estoque():
        config = config_collection.find_one({"chave": "margem_alerta_estoque"})
        if not config:
            return 0
        return float(config.get("valor", 0))

    @staticmethod
    def set_margem_alerta_estoque(valor: float):
        if valor < 0:
            raise ValueError("Margem nao pode ser negativa.")
        config_collection.update_one(
            {"chave": "margem_alerta_estoque"},
            {
                "$set": {
                    "valor": float(valor),
                    "descricao": "Percentual de margem aplicado sobre estoque minimo para gerar alertas.",
                }
            },
            upsert=True,
        )
