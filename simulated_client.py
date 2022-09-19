import dataclasses
import datetime
import itertools
import json
import os
import random
import traceback

import httpx
import trio


def _random_from_range(range_: range) -> float:
    """Generate a random float in the `range_` range."""
    return random.uniform(range_.start, range_.stop)


@dataclasses.dataclass
class MockStation:
    """Mock weather station that sends requests within the specified params."""

    name: str
    lat: float = 0
    lon: float = 0
    tz_offset: int = 0
    humidity_range: range = range(0, 100)
    temperature_range: range = range(-20, 40)
    wind_speed_range: range = range(0, 100)
    wind_angle_range: range = range(0, 360)
    clouds_range: range = range(0, 100)
    report_interval: int = 5
    max_reports: int | None = None

    async def generate_reports(self, client: httpx.AsyncClient) -> None:
        """
        Make `max_reports` (infinite if None) requests with random weather data points.

        The class' fields are used to define the bounds of the random data.
        Requests are made every `report_interval` seconds +- 20%.
        """
        if self.max_reports is None:
            request_iterable = itertools.count()
        else:
            request_iterable = range(self.max_reports)

        for request_n in request_iterable:
            await trio.sleep(self.report_interval * random.uniform(0.8, 1.2))
            humidity = _random_from_range(self.humidity_range)
            temperature = _random_from_range(self.temperature_range)
            wind_speed = _random_from_range(self.wind_speed_range)
            wind_angle = _random_from_range(self.wind_angle_range)
            clouds = _random_from_range(self.clouds_range)

            offset_time = datetime.datetime.now(
                tz=datetime.timezone(datetime.timedelta(seconds=self.tz_offset))
            )
            params = dict(
                station_name=self.name,
                latitude=self.lat,
                longitude=self.lon,
                local_time=offset_time.isoformat(),
                humidity=humidity,
                temperature=temperature,
                wind_speed=wind_speed,
                wind_angle=wind_angle,
                clouds=clouds,
            )

            print(f"Sending request {request_n=} with {params=}")  # noqa: T201
            try:
                response = await client.post(os.environ["API_URL"], json=params)
                response.raise_for_status()
            except Exception:
                print("Failed request")  # noqa: T201
                traceback.print_exc()
                continue

            try:
                response_json = response.json()
            except json.JSONDecodeError:
                print("Failed request")  # noqa: T201
                traceback.print_exc()
            else:
                if response_json.get("status") != "ok":
                    print(  # noqa: T201
                        "Failed request, received response:", response_json
                    )


MOCK_STATIONS = [
    MockStation("station 1"),
    MockStation(
        "station 2",
        lat=35,
        lon=65,
        tz_offset=18_000,
        report_interval=10,
        temperature_range=range(20),
    ),
    MockStation("station 3", clouds_range=range(0, 50), humidity_range=range(0, 75)),
    MockStation("station 4", max_reports=10, report_interval=2),
    MockStation(
        "station 5", wind_angle_range=range(40, 100), wind_speed_range=range(0, 200)
    ),
]


async def main() -> None:
    async with httpx.AsyncClient() as client:
        async with trio.open_nursery() as nursery:
            for station in MOCK_STATIONS:
                nursery.start_soon(station.generate_reports, client)


trio.run(main)
