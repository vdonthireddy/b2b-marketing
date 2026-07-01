import pytest

@pytest.fixture
async def setup_auth(client):
    # Register a user to get tokens and user/team IDs
    res = await client.post(
        "/api/auth/register",
        json={"email": "leads@test.com", "password": "pass", "name": "User", "team_name": "Team"}
    )
    data = res.json()
    return {
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "user": data["user"]
    }

@pytest.mark.asyncio
async def test_leads_crud(client, setup_auth):
    headers = setup_auth["headers"]
    
    # 1. Create a journey
    j_res = await client.post("/api/journeys", json={"name": "Test Journey"}, headers=headers)
    assert j_res.status_code == 200
    journey = j_res.json()
    journey_id = journey["id"]
    stage_id = journey["stages"][0]["id"]
    
    # 2. Create a lead
    lead_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@company.com",
        "company": "Acme Corp",
        "job_title": "VP Marketing",
        "status": "new",
        "value": 15000.0,
        "journey_id": journey_id,
        "stage_id": stage_id
    }
    create_res = await client.post("/api/leads", json=lead_data, headers=headers)
    assert create_res.status_code == 200
    lead = create_res.json()
    assert lead["first_name"] == "John"
    assert lead["company"] == "Acme Corp"
    assert lead["value"] == 15000.0
    lead_id = lead["id"]
    
    # 3. List leads
    list_res = await client.get("/api/leads", headers=headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["id"] == lead_id
    
    # 4. Filter leads by journey
    filtered_res = await client.get(f"/api/leads?journey_id={journey_id}", headers=headers)
    assert filtered_res.status_code == 200
    assert filtered_res.json()["total"] == 1
    
    # 5. Get lead by ID
    get_res = await client.get(f"/api/leads/{lead_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["first_name"] == "John"
    
    # 6. Update lead
    update_data = {"status": "contacted", "value": 20000.0}
    update_res = await client.put(f"/api/leads/{lead_id}", json=update_data, headers=headers)
    assert update_res.status_code == 200
    updated_lead = update_res.json()
    assert updated_lead["status"] == "contacted"
    assert updated_lead["value"] == 20000.0
    
    # 7. Delete lead
    delete_res = await client.delete(f"/api/leads/{lead_id}", headers=headers)
    assert delete_res.status_code == 200
    
    # 8. Verify deleted
    get_res2 = await client.get(f"/api/leads/{lead_id}", headers=headers)
    assert get_res2.status_code == 404
