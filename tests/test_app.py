import asyncio
from httpx import AsyncClient, ASGITransport
from src.app import app


def test_get_activities():
    # Arrange
    transport = ASGITransport(app=app)

    async def run():
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Act
            response = await ac.get('/activities')

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert 'Chess Club' in data

    asyncio.run(run())


def test_signup_and_remove():
    # Arrange
    activity = 'Chess Club'
    email = 'testuser@example.com'
    transport = ASGITransport(app=app)

    async def run():
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Arrange (ensure clean state)
            r0 = await ac.get('/activities')
            if email in r0.json()[activity]['participants']:
                await ac.delete(f"/activities/{activity}/participants", params={'email': email})

            # Act: signup the participant
            r = await ac.post(f"/activities/{activity}/signup", params={'email': email})

            # Assert: signup succeeded and participant is present
            assert r.status_code == 200
            r2 = await ac.get('/activities')
            assert email in r2.json()[activity]['participants']

            # Act: remove the participant
            r3 = await ac.delete(f"/activities/{activity}/participants", params={'email': email})

            # Assert: removal succeeded and participant is gone
            assert r3.status_code == 200
            r4 = await ac.get('/activities')
            assert email not in r4.json()[activity]['participants']

    asyncio.run(run())
