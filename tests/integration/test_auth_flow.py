def _create_admin_and_login(client):
    admin_payload = {
        "nome": "Administrador",
        "email": "admin@stockflow.local",
        "senha": "Senha123!",
        "perfil": "admin",
    }
    create_res = client.post("/usuarios/", json=admin_payload)
    assert create_res.status_code == 200

    login_payload = {
        "email": admin_payload["email"],
        "senha": admin_payload["senha"],
    }
    login_res = client.post("/auth/login", json=login_payload)
    assert login_res.status_code == 200
    return login_res.json()


def test_health_and_metrics_endpoints(test_client):
    live_res = test_client.get("/health/live")
    ready_res = test_client.get("/health/ready")
    metrics_res = test_client.get("/metrics")

    assert live_res.status_code == 200
    assert ready_res.status_code == 200
    assert metrics_res.status_code == 200
    assert "stockflow_http_requests_total" in metrics_res.text


def test_auth_and_protected_endpoint(test_client):
    tokens = _create_admin_and_login(test_client)
    auth_header = {"Authorization": f"Bearer {tokens['access_token']}"}

    produtos_res = test_client.get("/produtos/", headers=auth_header)

    assert produtos_res.status_code == 200
    assert isinstance(produtos_res.json(), list)


def test_refresh_and_logout_flow(test_client):
    tokens = _create_admin_and_login(test_client)

    refresh_res = test_client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_res.status_code == 200

    new_tokens = refresh_res.json()
    logout_res = test_client.post(
        "/auth/logout",
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert logout_res.status_code == 200

    reused_res = test_client.post(
        "/auth/refresh",
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert reused_res.status_code == 401
