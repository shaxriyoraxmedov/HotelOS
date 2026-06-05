# Cleaning Service v1.0

from contextlib import asynccontextmanager
from fastapi import FastAPI
from router import router
from database import init_db, seed_db, AsyncSessionLocal
from redis_client import broker, Channels
    

def on_room_vacated(data: dict) -> None:
    room_number = data.get("room_number")
    if not room_number:
        return

    print(f"[CLEANING] {room_number} xona bo'shatildi, tozalash vazifasi yaratilmoqda...")

    import asyncio
    import uuid
    from datetime import datetime
    from models import CleaningTaskModel, CleanerModel, CleaningStatus
    from sqlalchemy import select, update

    async def _create_task():
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CleaningTaskModel).where(
                    CleaningTaskModel.room_number == room_number,
                    CleaningTaskModel.status != CleaningStatus.COMPLETED
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"[CLEANING] {room_number} uchun allaqachon vazifa mavjud")
                return

            result = await session.execute(
                select(CleanerModel).where(CleanerModel.is_available == True)
            )
            cleaners = result.scalars().all()
            cleaner = cleaners[0] if cleaners else None

            task = CleaningTaskModel(
                id=str(uuid.uuid4()),
                room_number=room_number,
                status=CleaningStatus.IN_PROGRESS if cleaner else CleaningStatus.PENDING,
                assigned_to=cleaner.employee_id if cleaner else None,
                created_at=datetime.now(),
                started_at=datetime.now() if cleaner else None
            )
            session.add(task)

            if cleaner:
                await session.execute(
                    update(CleanerModel)
                    .where(CleanerModel.employee_id == cleaner.employee_id)
                    .values(is_available=False)
                )

            await session.commit()
            print(f"[CLEANING] {room_number} tozalash vazifasi yaratildi")

            broker.publish(Channels.DASHBOARD_UPDATE, {
                "event": "cleaning_started",
                "room_number": room_number,
                "assigned_to": cleaner.employee_id if cleaner else None,
                "started_at": datetime.now().isoformat()
            })

    # FastAPI event loop ni olish
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(_create_task(), loop)
        else:
            loop.run_until_complete(_create_task())
    except Exception as e:
        print(f"[CLEANING] Event loop xatosi: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[CLEANING] Servis ishga tushmoqda...")

    await init_db()

    async with AsyncSessionLocal() as session:
        await seed_db(session)

    # Avval subscribe — keyin start!
    broker.subscribe(Channels.ROOM_VACATED, on_room_vacated)

    broker.start()

    print("[CLEANING] Servis tayyor")

    yield

    print("[CLEANING] Servis to'xtatilmoqda...")


app = FastAPI(
    title="HotelOS — Cleaning Service",
    description="GrandStay mehmonxonasi tozalash servisi",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api/cleaning", tags=["Cleaning"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "cleaning-service"}