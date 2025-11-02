"""
Custom exception hierarchy for Home Assistant integration.

This module defines a shared exception hierarchy used across the ha_core package
and related modules. All exceptions inherit from HomeAssistantError base class.

Per CLAUDE.md guidelines:
- Never use generic Exception - always use specific exceptions
- Catch specific exception types in try-except blocks
- Create focused exception classes for different failure modes
"""


class HomeAssistantError(Exception):
    """
    Base exception for all Home Assistant integration errors.

    All custom exceptions in this project should inherit from this class.
    """
    pass


class ConnectionError(HomeAssistantError):
    """
    Raised when unable to connect to Home Assistant instance.

    This could be due to:
    - Network connectivity issues
    - Wrong URL/hostname
    - Home Assistant service not running
    - Firewall blocking access
    """
    pass


class AuthenticationError(HomeAssistantError):
    """
    Raised when authentication with Home Assistant fails.

    This typically means:
    - Invalid or expired access token
    - Token lacks necessary permissions
    - Token has been revoked
    """
    pass


class EntityNotFoundError(HomeAssistantError):
    """
    Raised when a requested entity does not exist.

    This happens when:
    - Entity ID doesn't exist in Home Assistant
    - Entity was removed/renamed
    - Typo in entity_id
    """
    pass


class ServiceCallError(HomeAssistantError):
    """
    Raised when a Home Assistant service call fails.

    This can occur when:
    - Service doesn't exist
    - Invalid parameters passed to service
    - Service execution failed
    - Entity doesn't support the service
    """
    pass


class StateError(HomeAssistantError):
    """
    Raised when entity state is invalid or unexpected.

    Examples:
    - State value is None when value expected
    - State format doesn't match expected type
    - State attributes missing required fields
    """
    pass


class ConfigurationError(HomeAssistantError):
    """
    Raised when configuration is invalid or incomplete.

    This includes:
    - Missing required environment variables
    - Invalid .env file format
    - Missing credentials
    - Invalid configuration values
    """
    pass


class APIError(HomeAssistantError):
    """
    Raised when Home Assistant API returns an error response.

    This is for HTTP-level errors:
    - 400 Bad Request
    - 404 Not Found
    - 500 Internal Server Error
    - Unexpected API responses
    """
    pass


class TimeoutError(HomeAssistantError):
    """
    Raised when an operation times out.

    This happens when:
    - API request takes too long
    - State change doesn't occur within expected time
    - Entity doesn't respond
    """
    pass


class DeviceError(HomeAssistantError):
    """
    Raised when a device operation fails.

    Device-specific errors for:
    - Govee devices
    - Broadlink IR blasters
    - Zigbee devices
    - Other smart home hardware
    """
    pass
