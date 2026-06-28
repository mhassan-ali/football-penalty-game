import logging
from enum import Enum, auto
from typing import Dict, Set
from core.event_manager import EventManager

logger = logging.getLogger("StateManager")

class State(Enum):
    LOADING = auto()
    MAIN_MENU = auto()
    GAMEPLAY = auto()
    PAUSED = auto()
    REPLAY = auto()
    RESULT = auto()
    SAVING = auto()
    EXIT = auto()

# Legal transition rules based on ARCHITECTURE.md §11
ALLOWED_TRANSITIONS: Dict[State, Set[State]] = {
    State.LOADING: {State.MAIN_MENU, State.GAMEPLAY},
    State.MAIN_MENU: {State.GAMEPLAY, State.SAVING, State.EXIT},
    State.GAMEPLAY: {State.PAUSED, State.REPLAY, State.RESULT, State.EXIT, State.MAIN_MENU},
    State.PAUSED: {State.GAMEPLAY, State.MAIN_MENU, State.SAVING, State.EXIT},
    State.REPLAY: {State.GAMEPLAY},
    State.RESULT: {State.SAVING},
    State.SAVING: {State.MAIN_MENU, State.GAMEPLAY, State.EXIT},
    State.EXIT: set()
}

class StateManager:
    def __init__(self, event_manager: EventManager, initial_state: State = State.LOADING) -> None:
        self._event_manager = event_manager
        self._current_state = initial_state
        logger.info(f"StateManager initialized in state: {self._current_state}")

    @property
    def current_state(self) -> State:
        return self._current_state

    def change_state(self, new_state: State) -> bool:
        """
        Transitions the application to a new state if it is allowed.
        
        Args:
            new_state: State enum target.
            
        Returns:
            True if the state was transitioned.
            
        Raises:
            ValueError: If the transition is illegal.
        """
        if new_state == self._current_state:
            return True

        allowed = ALLOWED_TRANSITIONS.get(self._current_state, set())
        if new_state in allowed:
            old_state = self._current_state
            self._current_state = new_state
            logger.info(f"State transitioned successfully: {old_state} -> {new_state}")
            
            # Publish event
            self._event_manager.publish(
                "state_changed", 
                {"old_state": old_state, "new_state": new_state}
            )
            return True
        else:
            msg = f"Illegal state transition attempted: {self._current_state} -> {new_state}"
            logger.error(msg)
            raise ValueError(msg)
