from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
class AbstractChannel(ABC):
    """
    An abstract base class for different channel implementations.
    """

    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the channel with configuration.

        Args:
            config (dict): A dictionary containing the configuration parameters.
        """
        pass    

    @abstractmethod
    def notify(self, custom_content: Optional[dict] = None) -> bool:
        """
        Sends a notification through the channel.

        Args:
            custom_content (dict): Optional custom content for the notification.

        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name of the channel.

        Returns:
            str: The name of the channel.
        """
        pass