import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from router import router
from database import init_db, seed_db, AsyncSessionLocal
from redis_client import broker, Channels

# Global event loop
_event_loop = None


def on_room_cleaned(data: dict) -> None:
    room_number = data.get("room_number")
    if not room_number:
        return

    print(f"[RECEPTION] {room_number} xona holati Clean ga yangilanmoqda...")

    from datetime import datetime
    from sqlalchemy import update
    from database import RoomModel
    from models import RoomStatus

    async def _update_room():
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(RoomModel)
                .where(RoomModel.room_number == room_number)
                .values(
                    status=RoomStatus.CLEAN,
                    cleaned_at=datetime.now()
                )
            )
            await session.commit()
            print(f"[RECEPTION] {room_number} xona holati Clean ga yangilandi")

    global _event_loop
    if _event_loop is not None:
        asyncio.run_coroutine_threadsafe(_update_room(), _event_loop)
    else:
        print("[RECEPTION] Event loop topilmadi!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _event_loop
    _event_loop = asyncio.get_event_loop()

    print("[RECEPTION] Servis ishga tushmoqda...")

    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_db(session)

    broker.subscribe(Channels.ROOM_CLEANED, on_room_cleaned)
    broker.start()

    print("[RECEPTION] Servis tayyor")

    yield

    print("[RECEPTION] Servis to'xtatilmoqda...")


app = FastAPI(
    title="HotelOS — Reception Service",
    description="GrandStay mehmonxonasi qabulxona servisi",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api/reception", tags=["Reception"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "reception-service"}