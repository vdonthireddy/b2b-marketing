import pytest

@pytest.fixture
async def setup_auth(client):
    res = await client.post(
        "/api/auth/register",
        json={"email": "persona@test.com", "password": "pass", "name": "User", "team_name": "Team"}
    )
    data = res.json()
    return {
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "user": data["user"]
    }

@pytest.mark.asyncio
async def test_create_persona(client, setup_auth):
    headers = setup_auth["headers"]
    
    response = await client.post(
        "/api/personas",
        json={
            "name": "Decision Maker",
            "role_title": "CTO",
            "avatar_color": "#ff0000"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Decision Maker"
    assert data["role_title"] == "CTO"
    assert "id" in data

@pytest.mark.asyncio
async def test_list_personas(client, setup_auth):
    headers = setup_auth["headers"]
    
    await client.post("/api/personas", json={"name": "P1", "avatar_color": "#111"}, headers=headers)
    await client.post("/api/personas", json={"name": "P2", "avatar_color": "#222"}, headers=headers)
    
    response = await client.get("/api/personas", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [p["name"] for p in data]
    assert "P1" in names
    assert "P2" in names

@pytest.mark.asyncio
async def test_link_persona(client, setup_auth):
    headers = setup_auth["headers"]
    
    # 1. Create Persona
    p_res = await client.post("/api/personas", json={"name": "P1", "avatar_color": "#111"}, headers=headers)
    persona = p_res.json()
    
    # 2. Create Journey
    j_res = await client.post("/api/journeys", json={"name": "J1"}, headers=headers)
    journey = j_res.json()
    
    # 3. Link
    l_res = await client.post(
        f"/api/personas/journeys/{journey['id']}/link",
        json={"persona_id": persona["id"]},
        headers=headers
    )
    assert l_res.status_code == 200
    
    # 4. Verify link
    j_get = await client.get(f"/api/journeys/{journey['id']}", headers=headers)
    data = j_get.json()
    assert len(data["personas"]) == 1
    assert data["personas"][0]["id"] == persona["id"]
