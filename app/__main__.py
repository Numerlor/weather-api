from fastapi import FastAPI

from .database import close_database, get_database
from .weather_model import WeatherItem

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
    con = await get_database()
    async with con.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO weather_data(
                station_name, latitude, longitude, local_time, humidity, temperature, wind_speed, wind_angle, clouds
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            tuple(data.dict().values()),
        )
    await con.commit()
    return {"status": "ok"}


@app.get("/weather/")
async def send_weather(name: str | None = None):  # noqa: ANN201
    con = await get_database()
    async with con.cursor() as cur:
        await cur.execute(
            "SELECT * FROM weather_data WHERE station_name=%s",
            (name if name is not None else True,),
        )
        column_names = [descr[0] for descr in cur.description]
        return [
            WeatherItem.parse_obj(dict(zip(column_names, row)))
            for row in await cur.fetchall()
        ]
