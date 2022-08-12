from utils import database as db, constants as const
import math

def get_exact_level(user_id:int) -> float:
    """Gets exact flaot value of user's level and how far he is from
       the next level. 

    Args:
        user_id (int): Discord user ID

    Returns:
        float: Level
    """
    current_xp = db.get_xp(user_id)
    level = math.log(current_xp / const.STARTING_VALUE, const.MULTIPLIER)
    return level


def get_next_level_xp(user_id:int) -> int:
    level = db.get_level(user_id)
    next_level_xp = 800 * (1.25** (level+1))
    next_level_xp = int(round(next_level_xp, -1))
    return next_level_xp
     
    