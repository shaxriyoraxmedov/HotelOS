# HotelOS — Real Vaqtli Mehmonxona Boshqaruv Tizimi

## Ishga tushirish

### Talablar
- Docker Desktop
- Docker Compose

### Ishga tushirish
```bash
docker-compose up --build
```

### Servislar
| Servis | Port |
|--------|------|
| API Gateway | http://localhost:8000 |
| Dashboard | http://localhost:3000 |
| Swagger UI | http://localhost:8000/docs |

### Git log
c9ea3b1 Fix: use run_coroutine_threadsafe for room_cleaned handler in reception
2773e6f Fix: save event loop globally for broker thread handler
a6abb6e Fix: use run_coroutine_threadsafe for broker handler
88a4806 Fix: subscribe before broker start in cleaning service
e8e14a7 Fix: on_room_vacated async to sync wrapper for broker thread
585b5b0 Fix: add healthcheck to PostgreSQL services
934b054 Docs: add git log to README
26f9b85 Config: docker compose services
2a6c8e1 Docs: dashboard
174bce0 Docs: api gateway
391c660 Docs: maintenance service
1422860 Docs: room service
f5b76d1 Docs: cleaning service
a5a9d4d Docs: reception service
8e246c2 Docs: reception service
152abc3 Docs: add README with setup instructions
dbe298c Initial commit: HotelOS project structure with all services