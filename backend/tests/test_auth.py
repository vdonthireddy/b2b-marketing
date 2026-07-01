import pytest

@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "securepassword",
            "name": "New User",
            "team_name": "Test Team"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "newuser@test.com"
    assert data["user"]["role"] == "admin" # First user in team should be admin

@pytest.mark.asyncio
async def test_login_user(client):
    # Register first
    await client.post(
        "/api/auth/register",
        json={"email": "loginuser@test.com", "password": "securepassword", "name": "User", "team_name": "Team"}
    )
    
    # Then login
    response = await client.post(
        "/api/auth/login",
        json={"email": "loginuser@test.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401
