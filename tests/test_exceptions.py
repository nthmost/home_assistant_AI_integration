"""
Unit tests for ha_core.exceptions module

Tests the custom exception hierarchy per CLAUDE.md guidelines.
"""

import pytest

from ha_core.exceptions import (
    HomeAssistantError,
    ConnectionError,
    AuthenticationError,
    EntityNotFoundError,
    ServiceCallError,
    StateError,
    ConfigurationError,
    APIError,
    TimeoutError,
    DeviceError,
)


class TestExceptionHierarchy:
    """Test that all exceptions inherit from HomeAssistantError"""

    def test_base_exception(self):
        """Test HomeAssistantError is an Exception"""
        assert issubclass(HomeAssistantError, Exception)

    def test_connection_error_inherits_base(self):
        """Test ConnectionError inherits from HomeAssistantError"""
        assert issubclass(ConnectionError, HomeAssistantError)

    def test_authentication_error_inherits_base(self):
        """Test AuthenticationError inherits from HomeAssistantError"""
        assert issubclass(AuthenticationError, HomeAssistantError)

    def test_entity_not_found_error_inherits_base(self):
        """Test EntityNotFoundError inherits from HomeAssistantError"""
        assert issubclass(EntityNotFoundError, HomeAssistantError)

    def test_service_call_error_inherits_base(self):
        """Test ServiceCallError inherits from HomeAssistantError"""
        assert issubclass(ServiceCallError, HomeAssistantError)

    def test_state_error_inherits_base(self):
        """Test StateError inherits from HomeAssistantError"""
        assert issubclass(StateError, HomeAssistantError)

    def test_configuration_error_inherits_base(self):
        """Test ConfigurationError inherits from HomeAssistantError"""
        assert issubclass(ConfigurationError, HomeAssistantError)

    def test_api_error_inherits_base(self):
        """Test APIError inherits from HomeAssistantError"""
        assert issubclass(APIError, HomeAssistantError)

    def test_timeout_error_inherits_base(self):
        """Test TimeoutError inherits from HomeAssistantError"""
        assert issubclass(TimeoutError, HomeAssistantError)

    def test_device_error_inherits_base(self):
        """Test DeviceError inherits from HomeAssistantError"""
        assert issubclass(DeviceError, HomeAssistantError)


class TestExceptionInstantiation:
    """Test that exceptions can be instantiated and raised"""

    def test_raise_base_exception(self):
        """Test raising HomeAssistantError"""
        with pytest.raises(HomeAssistantError, match="base error"):
            raise HomeAssistantError("base error")

    def test_raise_connection_error(self):
        """Test raising ConnectionError"""
        with pytest.raises(ConnectionError, match="connection failed"):
            raise ConnectionError("connection failed")

    def test_raise_authentication_error(self):
        """Test raising AuthenticationError"""
        with pytest.raises(AuthenticationError, match="auth failed"):
            raise AuthenticationError("auth failed")

    def test_raise_entity_not_found_error(self):
        """Test raising EntityNotFoundError"""
        with pytest.raises(EntityNotFoundError, match="entity not found"):
            raise EntityNotFoundError("entity not found")

    def test_raise_service_call_error(self):
        """Test raising ServiceCallError"""
        with pytest.raises(ServiceCallError, match="service failed"):
            raise ServiceCallError("service failed")

    def test_raise_state_error(self):
        """Test raising StateError"""
        with pytest.raises(StateError, match="invalid state"):
            raise StateError("invalid state")

    def test_raise_configuration_error(self):
        """Test raising ConfigurationError"""
        with pytest.raises(ConfigurationError, match="config invalid"):
            raise ConfigurationError("config invalid")

    def test_raise_api_error(self):
        """Test raising APIError"""
        with pytest.raises(APIError, match="api failed"):
            raise APIError("api failed")

    def test_raise_timeout_error(self):
        """Test raising TimeoutError"""
        with pytest.raises(TimeoutError, match="operation timed out"):
            raise TimeoutError("operation timed out")

    def test_raise_device_error(self):
        """Test raising DeviceError"""
        with pytest.raises(DeviceError, match="device failed"):
            raise DeviceError("device failed")


class TestExceptionCatching:
    """Test that specific exceptions can be caught as base exception"""

    def test_catch_specific_as_base(self):
        """Test catching ConnectionError as HomeAssistantError"""
        try:
            raise ConnectionError("connection failed")
        except HomeAssistantError as e:
            assert str(e) == "connection failed"
        else:
            pytest.fail("Exception was not caught")

    def test_catch_multiple_specific_exceptions(self):
        """Test catching multiple specific exceptions"""
        exceptions = [
            ConnectionError("conn"),
            APIError("api"),
            EntityNotFoundError("entity"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except (ConnectionError, APIError, EntityNotFoundError) as e:
                assert isinstance(e, HomeAssistantError)
            else:
                pytest.fail(f"Exception {exc} was not caught")

    def test_specific_exception_pattern(self):
        """Test CLAUDE.md pattern: catch specific, not generic"""
        # This is the recommended pattern from CLAUDE.md
        def risky_operation():
            raise EntityNotFoundError("entity.light.missing")

        # GOOD: Catch specific exception
        try:
            risky_operation()
        except EntityNotFoundError as e:
            assert "missing" in str(e)
        else:
            pytest.fail("Should have caught EntityNotFoundError")

    def test_exception_chaining(self):
        """Test exception chaining with 'from' keyword"""
        original = ValueError("original error")

        try:
            try:
                raise original
            except ValueError as e:
                raise APIError("wrapped error") from e
        except APIError as e:
            assert str(e) == "wrapped error"
            assert e.__cause__ == original
        else:
            pytest.fail("Should have caught APIError")


class TestExceptionMessages:
    """Test that exception messages are preserved"""

    def test_exception_with_message(self):
        """Test exception message is preserved"""
        message = "This is a detailed error message"
        exc = ConnectionError(message)
        assert str(exc) == message

    def test_exception_with_formatted_message(self):
        """Test exception with formatted message"""
        entity_id = "light.bedroom"
        exc = EntityNotFoundError(f"Entity '{entity_id}' not found")
        assert entity_id in str(exc)

    def test_exception_without_message(self):
        """Test exception can be raised without message"""
        exc = HomeAssistantError()
        # Should not raise an error
        assert exc is not None
