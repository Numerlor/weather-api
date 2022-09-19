import datetime

from pydantic.class_validators import validator
from pydantic.main import BaseModel


class WeatherItem(BaseModel):
    """A single weather datapoint."""

    station_name: str
    latitude: float
    longitude: float
    local_time: datetime.datetime
    humidity: int | None = None
    temperature: float | None = None
    wind_speed: float | None = None
    wind_angle: int | None = None
    clouds: int | None = None

    @validator("station_name")
    def name_not_too_long(cls, value: str) -> str:
        if len(value) > 128:
            raise ValueError("Name must contain at most 128 characters.")
        return value

    @validator("latitude")
    def latitude_valid(cls, value: float) -> float:
        if not -90 <= value <= 90:
            raise ValueError("latitude must be between -90 - 90 degrees.")
        return value

    @validator("longitude")
    def longitude_valid(cls, value: float) -> float:
        if not -180 <= value <= 180:
            raise ValueError("longitude must be between -180 - 180 degrees.")
        return value

    @validator("local_time")
    def time_not_naive(cls, value: datetime.datetime) -> datetime.datetime:
        return value  # todo mysql removing the tzinfo?
        if value.tzinfo is None:
            raise ValueError("local_time must be timezone aware.")
        return value

    @validator("humidity")
    def humidity_valid(cls, value: int | None) -> int | None:
        if value is not None and not 0 <= value <= 100:
            raise ValueError("Humidity must be between 0-100.")
        return value

    @validator("temperature")
    def temperature_valid(cls, value: float | None) -> float | None:
        if value is not None and not -273.15 <= value <= 100:
            raise ValueError("A valid temperature value has to be specified.")
        return value

    @validator("wind_speed")
    def speed_valid(cls, value: int | None) -> int | None:
        if value is not None and not 0 <= value < 1000:
            raise ValueError("Wind must be between 0-999.")
        return value

    @validator("wind_angle")
    def angle_valid(cls, value: int | None) -> int | None:
        if value is not None and not 0 <= value <= 360:
            raise ValueError("Wind angle must be specified in degrees.")
        return value

    @validator("clouds")
    def clouds_valid(cls, value: int | None) -> int | None:
        if value is not None and not 0 <= value <= 100:
            raise ValueError("Cloud coverage must be between 0-100.")
        return value
