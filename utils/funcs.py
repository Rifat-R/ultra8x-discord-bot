from datetime import datetime
from dateutil import parser
import disnake




def parse_date(date:str) -> datetime:
    try:
        parsed_date = parser.parse(date).strftime("%m/%d/%Y, %H:%M:%S")
    except TypeError:
        parsed_date = date.strftime("%m/%d/%Y, %H:%M:%S")
        return parsed_date
    