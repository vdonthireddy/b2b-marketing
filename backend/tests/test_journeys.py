import pytest

@pytest.fixture
async def setup_auth(client):
    # Register a user to get tokens and user/team IDs
    res = await client.post(
        "/api/auth/register",
        json={"email": "journey@test.com", "password": "pass", "name": "User", "team_name": "Team"}
    )
    data = res.json()
    return {
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "user": data["user"]
    }

@pytest.mark.asyncio
async def test_create_journey(client, setup_auth):
    headers = setup_auth["headers"]
    
    response = await client.post(
        "/api/journeys",
        json={"name": "Test Journey", "description": "A test journey map"},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Journey"
    assert "id" in data
    assert len(data["stages"]) == 8  # Default stages

@pytest.mark.asyncio
async def test_list_journeys(client, setup_auth):
    headers = setup_auth["headers"]
    
    # Create journey
    await client.post("/api/journeys", json={"name": "J1"}, headers=headers)
    
    # List journeys
    response = await client.get("/api/journeys", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["name"] == "J1"

@pytest.mark.asyncio
async def test_add_stage_item(client, setup_auth):
    headers = setup_auth["headers"]
    
    # 1. Create Journey
    j_res = await client.post("/api/journeys", json={"name": "J1"}, headers=headers)
    journey = j_res.json()
    stage_id = journey["stages"][0]["id"]
    
    # 2. Add goal to stage
    res = await client.post(
        f"/api/journeys/stages/{stage_id}/goal",
        json={"text": "Test Goal"},
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["text"] == "Test Goal"

@pytest.mark.asyncio
async def test_duplicate_journey_name(client, setup_auth):
    headers = setup_auth["headers"]

    # 1. Create a journey
    res1 = await client.post("/api/journeys", json={"name": "Unique Journey"}, headers=headers)
    assert res1.status_code == 200

    # 2. Try creating another journey with the same name -> Expect 400
    res2 = await client.post("/api/journeys", json={"name": "Unique Journey"}, headers=headers)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]

    # 3. Create a different journey
    res3 = await client.post("/api/journeys", json={"name": "Unique Journey 2"}, headers=headers)
    assert res3.status_code == 200
    j2_id = res3.json()["id"]

    # 4. Try updating the second journey to the first name -> Expect 400
    res4 = await client.put(f"/api/journeys/{j2_id}", json={"name": "Unique Journey"}, headers=headers)
    assert res4.status_code == 400
    assert "already exists" in res4.json()["detail"]
