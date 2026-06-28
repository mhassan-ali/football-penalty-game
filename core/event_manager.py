import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger("EventManager")

class EventManager:
    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """
        Subscribe a handler to an event type.
        
        Args:
            event_type: Name of the event to listen to.
            handler: Callable triggered when the event is published.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.debug(f"Subscribed handler to event: {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """
        Unsubscribe a handler from an event type.
        
        Args:
            event_type: Name of the event.
            handler: Registered callback to remove.
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                logger.debug(f"Unsubscribed handler from event: {event_type}")
            except ValueError:
                logger.warning(f"Handler not found for event: {event_type}")

    def publish(self, event_type: str, data: Any = None) -> None:
        """
        Publish an event to all subscribed handlers.
        
        Args:
            event_type: Name of the event.
            data: Arbitrary payload to pass to handlers.
        """
        if event_type not in self._handlers:
            logger.debug(f"Published event '{event_type}' with no subscribers.")
            return

        # Create a copy of the list to prevent issues if a handler modifies subscribers during dispatch
        handlers = list(self._handlers[event_type])
        logger.debug(f"Publishing event '{event_type}' to {len(handlers)} subscribers.")
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Error executing subscriber for event '{event_type}': {e}", exc_info=True)
