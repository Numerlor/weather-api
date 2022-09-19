import os

import aiomysql


_database: aiomysql.Connection | None = None


async def get_database() -> aiomysql.Connection:
    """Get the existing database connection, or create a new one."""
    global _database

    if _database is None:
        _database = await aiomysql.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            db=os.environ["DB_NAME"],
        )

        async with _database.cursor() as cur:  # type: ignore
            # fmt: off
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS weather_data(
                id INT AUTO_INCREMENT PRIMARY KEY,
                station_name VARCHAR(128) NOT NULL,
                latitude DECIMAL(8,6) NOT NULL,
                longitude DECIMAL(8,6) NOT NULL,
                local_time DATETIME NOT NULL,
                humidity TINYINT,
                temperature DECIMAL(5,2),
                wind_speed DECIMAL(5,2),
                wind_angle SMALLINT,
                clouds SMALLINT
            )              
            """)

    return _database


async def close_database() -> None:
    """Close the database connection, if any is open."""
    if _database is not None:
        await _database.close()
