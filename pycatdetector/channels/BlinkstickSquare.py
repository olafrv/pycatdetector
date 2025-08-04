import requests
import logging
from typing import Optional, Dict, Any
from .AbstractChannel import AbstractChannel

class BlinkstickSquare(AbstractChannel):
    """
    BlinkstickSquare channel implementation that sends HTTP GET requests
    to control a BlinkStick Square device via a web API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the BlinkstickSquare channel.
        
        Args:
            config (dict): A dictionary containing the configuration parameters.
        """
        self.url = config.get('url')
        self.querystring = config.get('querystring')
        self.authorization = config.get('authorization')
        self.timeout = config.get('timeout')
        self.logger = logging.getLogger(__name__)

    def get_name(self) -> str:
        """
        Returns the name of the class.

        Returns:
            str: The name of the class.
        """
        return self.__class__.__name__


    def notify(self, custom_content: Optional[dict] = None) -> bool:
        """
        Send notification by making HTTP GET request to BlinkStick Square API.
        
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        try:
            # Construct the full URL with query parameters
            full_url = f"{self.url}?{self.querystring}"

            if custom_content is not None:
                self.logger.debug(f"Custom content provided but not used: {custom_content}")
            
            # Prepare headers
            headers = {}
            if self.authorization:
                headers['Authorization'] = self.authorization
            
            # Make the GET request
            response = requests.get(full_url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                self.logger.info(f"BlinkstickSquare notification sent successfully to {self.url}")
                return True
            else:
                self.logger.error(f"BlinkstickSquare notification failed: HTTP {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"BlinkstickSquare notification failed with exception: {e}")
            return False
        except Exception as e:
            self.logger.error(f"BlinkstickSquare unexpected error: {e}")
            return False

