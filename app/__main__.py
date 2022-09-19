from fastapi import FastAPI

from .database import close_database, get_database
from .weather_model import WeatherItem

_DB_COLS = [
    "station_name",
    "latitude",
    "longitude",
    "local_time",
    "humidity",
    "temperature",
    "wind_speed",
    "wind_angle",
    "clouds",
]

app = FastAPI()


@app.on_event("shutdown")
async def shutdown() -> None:
    """Close the database on shutdown."""
    await close_database()


@app.get("/")
async def root():  # noqa: ANN201
    return {"message": "Hello World"}


@app.post("/weather/")
async def receive_weather(data: WeatherItem):  # noqa: ANN201
    pool = await get_database()

    async with pool.acquire() as con:
        async with con.cursor() as cur:
            await cur.execute(
                f"""
                INSERT INTO weather_data({', '.join(_DB_COLS)})
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                tuple(data.dict().values()),
            )
        await con.commit()
    return {"status": "ok"}


@app.get("/weather/")
async def send_weather(name: str | None = None):  # noqa: ANN201
    pool = await get_database()

    async with pool.acquire() as con:
        async with con.cursor() as cur:
            await cur.execute(
                f"SELECT {', '.join(_DB_COLS)} FROM weather_data WHERE station_name=%s OR %s",
                (
                    name,
                    name is None,
                ),
            )

            return [
                WeatherItem.parse_obj(dict(zip(_DB_COLS, row)))
                for row in await cur.fetchall()
            ]
