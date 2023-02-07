# Basic info defining the sport rules
PLAYER_AMOUNT_TEAM_SHEET = 5

MATCH_MAX_MINUTE = 40

MIN_GOAL_AMOUNT = 0

MAX_GOAL_AMOUNT = 15

# Goal generation (Gauss distribution)
GOAL_AMOUNT_MU = 6
GOAL_AMOUNT_SIGMA = 3
GOAL_SKILL_DIFF_PERC_MULTIPLIER = 2


# Used when calculating team skill
TEAM_SKILL_CALC_PLAYER_AMOUNT = 10

MIN_PLAYER_SKILL = 1

# Formula for calculation: (BASE_PRICE - (team_avg + player.skill)*2) * stamina left
BASE_PRICE_FOR_AVERAGE_PLAYER = 50

MIN_PLAYER_SELL_PRICE = 5

MIN_CPU_DIFFICULTY_RATING = 0

MAX_CPU_DIFFICULTY_RATING = 10

BASE_COINS_MATCH_WIN = 200
MULTIPLIER_COIN_DRAW = 0.6
MULTIPLIER_SKILL_DIFFERENCE = 5

GOAL_DIFF_MULTIPLIER = 5

MULTIPLIER_COIN_LOSS = 0.35

# ---------------------------------------------------
# Percentage chances for positions doing an action during a match

# Chances of scoring a goal for each position. Percentages must add up to 100!
ATTACKER_GOAL_PERC = 72
DEFENDER_GOAL_PERC = 26
GK_GOAL_PERC = 2

# Chance of an assist happening
ASSIST_PERC = 60
# Chances of assisting a goal for each position. Percentages must add up to 100!
ATTACKER_ASSIST_PERC = 56
DEFENDER_ASSIST_PERC = 40
GK_ASSIST_PERC = 4

# ----------------------------------------------------
# Multipliers for player skills

# Player favourite position equals playing position
MULTIPLIER_PLAYER_FAV_POS = 1

# Gk playing in a different position
MULTIPLIER_GK_INFIELD = 0.5

# Infield player(attacker defender) playing in a different position
MULTIPLIER_DIFFERENT_INFIELD_POS = 0.75

MULTIPLIER_INFIELD_AS_GK = 0.25


# -----------------------------------------------
# Packs
PLAYER_AMOUNT_IN_PACK = 3
BRONZE_PRICE = 250
SILVER_PRICE = 500
GOLD_PRICE = 750

# Coin generation upper, lower bounds (is added to avg_skill of team)
GOLD_LOWER_BOUND = 0
GOLD_UPPER_BOUND = 8

SILVER_LOWER_BOUND = -4
SILVER_UPPER_BOUND = 4

BRONZE_LOWER_BOUND = -10
BRONZE_UPPER_BOUND = 0

# Player generation used in packs, and during team creation
GK_GENERATION_PERC_CHANCE = 20
DEF_GENERATION_PERC_CHANCE = 40
ATT_GENERATION_PERC_CHANCE = 40

# ---------------------------------------------
# Team Creation
BASE_COIN_AMOUNT = 1000

# Created team will have players with skill in this interval
CREATE_TEAM_PLAYER_AMOUNT_ABOVE_MIN = 2

SKILL_LOWER_BOUND_CREATED_TEAM = 15
SKILL_UPPER_BOUND_CREATED_TEAM = 25

# CPU opponent generation, team and player fake history
CPU_MATCHES_PLAYED_LOWER_BOUND = 0
CPU_MATCHES_PLAYED_UPPER_BOUND = 200
CPU_PLAYER_SKILL_VARIANCE_MULTIPLIER = 0.2

# Same multipliers are used for assists
CPU_ATTACKER_LOWER_CONTRIBUTION_MULTIPLIER = 0.5
CPU_ATTACKER_UPPER_CONTRIBUTION_MULTIPLIER = 4.0

CPU_DEFENDER_LOWER_CONTRIBUTION_MULTIPLIER = 0.25
CPU_DEFENDER_UPPER_CONTRIBUTION_MULTIPLIER = 2.0

CPU_GK_LOWER_CONTRIBUTION_MULTIPLIER = 0.0
CPU_GK_UPPER_CONTRIBUTION_MULTIPLIER = 0.1
