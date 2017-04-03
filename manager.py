from abc import ABCMeta, abstractmethod
from asyncio import Future
from typing import Dict, List, Tuple, NewType, Any

PlayerID = NewType("PlayerID", int)
CanJoinBack = NewType("CanJoinBack", bool)

class Status(metaclass=ABCMeta):
    pass


class AsyncGame(metaclass=ABCMeta):
    frequency: int
    gameid: int
    is_over: bool

    @classmethod
    @abstractmethod
    def create(cls, future: Future, gameid: int, players: List[PlayerID], config: Any) -> None:
        """Create a new game

        Args:
            cls: this class
            future: the future
            gameid: unique game identifier
            players: list of unique player identifier joining this game
            config: parsed yaml config file

        Future -> Tuple(Game, Status):
            Game instance, game creation Status (sent to the players within the game)"""
        pass

    @abstractmethod
    def play(future: Future) -> None:
        """For real-time based game, play a tick and retrieve a status

        Future results -> Status:
            The status of which happened"""
        pass

    @abstractmethod
    def get_events_for(future: Future, playerid: int) -> List[str]:
        """Get the list of events playable by the given player

        Args:
            playerid: unique identifier of the player

        Returns:
            a list of events available in the current context"""
        pass

    @abstractmethod
    def play_event_for(future: Future, playerid: int, event: str, **kwargs: Any) -> None:
        """Play a specific event in the player context

        Args:
            playerid: unique identifier of the player
            event: name of the event played
            kwargs: any event-related value needed

        Future results -> None"""
        pass

    @abstractmethod
    def kick(future: Future, playerid: int) -> None:
        """Handle a player disconnection

        Args:
            playerid: unique identifier of the player

        Future results -> CanJoinBack:
            Whether the user can join back this very game on reconnection"""
        pass
