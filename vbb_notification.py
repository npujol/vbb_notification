import click
import time
import requests
import datetime as dt
from collections import namedtuple
from plyer import notification as plyerNotification

URL_BASE = "https://v5.vbb.transport.rest/"

Station = namedtuple("Station", ["id", "name", "location_id", "latitude", "longitude"])
Journey = namedtuple(
    "Journey",
    ["id", "departure", "plannedDeparture", "departureDelay", "line", "mode"],
)


class ObjectNotFound(Exception):
    pass


class Notification:
    def __init__(
        self,
        msg="This is a message >_<.",
        interval=50,
    ):
        self.message = msg
        self.interval = interval

    def send_notification(self):
        now = dt.datetime.now()
        plyerNotification.notify(
            title=f"""It's already {now.strftime('%H:%M')}, 
                    it's time to go!"""
            message=self.message,
            timeout=self.interval,
        )


class VBBJourney:
    def __init__(self, your_location, address_to_go):
        self.from_station = self._get_station(your_location)
        self.to_station = self._get_station(address_to_go)

    def _get_station(self, location):
        try:
            payload = {"query": location, "results": "1"}
            response = requests.get(url=f"{URL_BASE}locations", params=payload)
        except Exception as e:
            raise e

        if response.status_code == 200:
            data = response.json()[0]
            station = Station(
                data["id"],
                data["name"],
                data["location"]["id"],
                data["location"]["latitude"],
                data["location"]["longitude"],
            )
            return station

        raise ObjectNotFound("The object was not founded.")

    def get_journey(self):
        try:
            payload = {
                "from": {self.from_station.id},
                "from.latitude": {self.from_station.latitude},
                "from.longitude": {self.from_station.longitude},
                "to.id": {self.to_station.id},
                "to.name": {self.to_station.name},
                "to.latitude": {self.to_station.latitude},
                "to.longitude": {self.to_station.longitude},
                "results": "1",
            }
            response = requests.get(
                url=f"{URL_BASE}journeys",
                params=payload,
            )
        except Exception as e:
            raise e
        if response.status_code == 200:
            if response.json()["journeys"][0]:
                data = response.json()["journeys"][0]["legs"][0]
                journey = Journey(
                    data["tripId"],
                    data["departure"],
                    data["plannedDeparture"],
                    data["departureDelay"],
                    data["line"]["name"],
                    data["line"]["mode"],
                )
                return journey

        raise ObjectNotFound("The object was not founded.")

    def get_message(self):
        journey = self.get_journey()
        return f"""
                
                Your {journey.mode} is almost at the station.
                Journey information is as follows: 
                 - Line name: {journey.line}
                 - Origin: {self.from_station.name}
                 - Destiny:{self.to_station.name}
                 - Departure: {journey.departure}
                 - Planned Departure: {journey.plannedDeparture}
                 - Departure Delay {journey.departureDelay}
                """


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--your_location",
    prompt="Keywords about your current location",
    default="pankow",
    help="Keywords about your current location",
)
@click.option(
    "--address_to_go",
    prompt="Keywords about the location you want to reach",
    default="alexanderplatz",
    help="Keywords about the location you want to reach",
)
@click.option(
    "--time_to_go",
    prompt="Time to make the daily commute (hh:mm)",
    default="18:00",
    help="Time to make the daily commute (hh:mm)",
)
@click.option(
    "--time_before",
    prompt="Advance notice time (number)",
    default=1,
    help="Advance notice time (int)",
)
def setup_VBBJourney(your_location, address_to_go, time_to_go, time_before):
    vbb = VBBJourney(your_location, address_to_go)
    hour, minute = map(int, time_to_go.split(":"))

    while True:
        # Sleep until X minutes before the desired time.
        t = dt.datetime.today()
        desired_time = dt.datetime(t.year, t.month, t.day, hour, minute)
        minutes = dt.timedelta(minutes=time_before)
        future = desired_time - minutes

        if t.hour >= hour:
            # future += datetime.timedelta(days=1)
            future += datetime.timedelta(minute=15)

        time.sleep((future - t).total_seconds())

        msg = vbb.get_message()
        notification = Notification(msg)
        notification.send_notification()


if __name__ == "__main__":
    cli()
