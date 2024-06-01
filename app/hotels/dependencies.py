from datetime import date

from app.dependencies import DateSearchArgs


class HotelsSearchArgs(DateSearchArgs):  # Used for get requests and their validation
    def __init__(
        self,
        location: str,
        date_from: date,
        date_to: date,
    ):
        super().__init__(date_from, date_to)
        self.location = location
