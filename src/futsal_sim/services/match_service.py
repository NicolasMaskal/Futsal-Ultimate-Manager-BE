import dataclasses
import random
from dataclasses import dataclass
from typing import Optional, Tuple

from src.futsal_sim.constants import (
    BASE_COINS_MATCH_WIN,
    GOAL_AMOUNT_MU,
    GOAL_AMOUNT_SIGMA,
    GOAL_DIFF_MULTIPLIER,
    GOAL_SKILL_DIFF_PERC_MULTIPLIER,
    MATCH_MAX_MINUTE,
    MAX_GOAL_AMOUNT,
    MIN_GOAL_AMOUNT,
    MULTIPLIER_COIN_DRAW,
    MULTIPLIER_COIN_LOSS,
    MULTIPLIER_SKILL_DIFFERENCE,
)
from src.futsal_sim.models import (
    MatchGoal,
    MatchResult,
    Player,
    PlayerPosition,
    Team,
    TeamLineup,
    TeamSheet,
)

from .business_models import TeamSheetPosition
from .factories import PositionFactory, TeamOpponentFactory
from .team_service import calc_team_skill
from .teamsheet_service import calc_sheet_lineup_average_skill, create_lineup_from_sheet


@dataclass
class PlayerMatchMomentCreator:
    match_result: MatchResult
    goal_minutes: list[int] = dataclasses.field(default_factory=lambda: [])

    def create_moments(self, *, goal_amount: int, lineup: TeamLineup):
        """
        :param goal_amount: how many goal moments should be created for passed lineup
        :param lineup: set of players for which goal moment will be created for
        """
        for _ in range(goal_amount):
            self._create_moment(lineup)
        return self.goal_minutes

    def _create_moment(self, lineup: TeamLineup):
        scorer, scorer_pos = self._generate_scorer(lineup)
        assister = self._generate_assister(lineup, scorer_pos)

        minute = self._generate_random_minute()
        MatchGoal(
            minute=minute, team=lineup.team, goal_scorer=scorer, assister=assister, match=self.match_result
        ).save()

    def _generate_random_minute(self) -> int:
        random_minute = random.randint(1, MATCH_MAX_MINUTE)
        while random_minute in self.goal_minutes:
            random_minute = random.randint(1, MATCH_MAX_MINUTE)

        self.goal_minutes.append(random_minute)
        return random_minute

    @staticmethod
    def _generate_scorer(lineup: TeamLineup) -> Tuple[Player, TeamSheetPosition]:
        """
        :return: Scorer of goal
        """
        position = PositionFactory.generate_goal_scorer_position()
        player = getattr(lineup, position.value)
        player.goals_scored += 1
        player.save()

        return player, position

    @staticmethod
    def _generate_assister(lineup: TeamLineup, scorer_pos: TeamSheetPosition) -> Optional[Player]:
        position = PositionFactory.generate_assist_maker_position(scorer_pos)

        player = None
        if position:
            player = getattr(lineup, position.value)
            player.assists_made += 1
            player.save()

        return player


@dataclass
class MatchInProgress:
    player_skill: int
    cpu_skill: int
    player_team: Team
    cpu_team: Team
    player_lineup: TeamLineup
    cpu_lineup: TeamLineup
    player_goals: int = 0
    cpu_goals: int = 0

    def play_match(self) -> MatchResult:
        goal_amount = self._generate_goal_amount()

        for i in range(goal_amount):
            self._add_goal_to_score()

        match_result = self._create_match_result()
        self._create_moments(match_result)
        return match_result

    def _create_moments(self, match_result: MatchResult):
        goal_moment_creator = PlayerMatchMomentCreator(match_result=match_result)
        goal_moment_creator.create_moments(goal_amount=self.player_goals, lineup=self.player_lineup)
        goal_moment_creator.create_moments(goal_amount=self.cpu_goals, lineup=self.cpu_lineup)

    def _create_match_result(self) -> MatchResult:
        coins = self._update_player_team_with_result()
        match = MatchResult(
            player_team=self.player_team,
            cpu_team=self.cpu_team,
            player_lineup=self.player_lineup,
            cpu_lineup=self.cpu_lineup,
            player_goals=self.player_goals,
            cpu_goals=self.cpu_goals,
            coins_reward=coins,
        )
        match.save()
        return match

    @staticmethod
    def _generate_goal_amount() -> int:
        goal_gen = round(random.gauss(GOAL_AMOUNT_MU, GOAL_AMOUNT_SIGMA) + 0.5)
        return sorted((MIN_GOAL_AMOUNT, goal_gen, MAX_GOAL_AMOUNT))[1]

    def _add_goal_to_score(self):
        player_goal_chance = 50 + GOAL_SKILL_DIFF_PERC_MULTIPLIER * (self.player_skill - self.cpu_skill)

        seed = random.randint(1, 100)
        if seed < player_goal_chance:
            self.player_goals += 1
        else:
            self.cpu_goals += 1

    def _update_player_team_with_result(self) -> int:
        """
        :return: coins gained
        """
        self._update_players()
        added_coins_for_win = BASE_COINS_MATCH_WIN + MULTIPLIER_SKILL_DIFFERENCE * (self.cpu_skill - self.player_skill)
        goal_diff_effect = GOAL_DIFF_MULTIPLIER * (self.player_goals - self.cpu_goals)
        if self.player_goals > self.cpu_goals:
            self.player_team.wins += 1
            self.cpu_team.loses += 1
            added_coins = added_coins_for_win + goal_diff_effect
        elif self.player_goals == self.cpu_goals:
            self.player_team.draws += 1
            self.cpu_team.draws += 1
            added_coins = round(added_coins_for_win * MULTIPLIER_COIN_DRAW)
        else:
            self.player_team.loses += 1
            self.cpu_team.wins += 1
            added_coins = round(added_coins_for_win * MULTIPLIER_COIN_LOSS)
            added_coins += goal_diff_effect

        added_coins = max(added_coins, 0)
        self.player_team.coins += added_coins
        self.player_team.save()
        return added_coins

    def regen_stamina(self):
        for player in self.player_team.players.all():
            if player not in self.player_lineup.players:
                stamina_boost = random.randint(30, 40)
                player.stamina_left = min(player.stamina_left + stamina_boost, 100)
                player.save()

    def _update_players(self):
        self.regen_stamina()
        for (player, position) in self.player_lineup.players_with_positions:
            player.matches_played += 1
            stamina_drained = random.randint(10, 20)
            if position == PlayerPosition.GOALKEEPER:
                # Goalkeepers aren't as tired as other positions
                stamina_drained = round(0.5 * stamina_drained)

            new_stamina = player.stamina_left - stamina_drained
            new_stamina = min(100, new_stamina)
            player.stamina_left = max(1, new_stamina)
            player.save()


def play_match_against_cpu(*, player_team_sheet: TeamSheet, difficulty_rating: int) -> MatchResult:
    player_team = player_team_sheet.team
    player_lineup = create_lineup_from_sheet(player_team_sheet)

    team_skill = calc_team_skill(player_team)
    opponent_factory = TeamOpponentFactory(difficulty_rating=difficulty_rating, player_skill=team_skill)
    cpu_team, cpu_lineup = opponent_factory.create_cpu_team()

    player_lineup_skill = calc_sheet_lineup_average_skill(player_lineup)
    cpu_lineup_skill = calc_sheet_lineup_average_skill(cpu_lineup)

    match = MatchInProgress(
        player_skill=player_lineup_skill,
        cpu_skill=cpu_lineup_skill,
        player_team=player_team,
        cpu_team=cpu_team,
        player_lineup=player_lineup,
        cpu_lineup=cpu_lineup,
    )
    match_res = match.play_match()
    return match_res
