"""
Unit tests for ha_core.client module

Tests the HomeAssistantInspector class with mocked Home Assistant API.
Per CLAUDE.md: isolated, repeatable, fast tests with external dependencies mocked.
"""

import pytest
from unittest.mock import MagicMock, PropertyMock, patch
from collections import namedtuple

from ha_core.client import HomeAssistantInspector, setup_logger
from ha_core.exceptions import (
    ConnectionError as HAConnectionError,
    AuthenticationError,
    EntityNotFoundError,
    APIError,
    StateError,
)


# Mock data structures
MockEntity = namedtuple('MockEntity', ['entity_id', 'state'])
MockState = namedtuple('MockState', ['state', 'attributes'])
MockGroup = namedtuple('MockGroup', ['entities'])
MockDomain = namedtuple('MockDomain', ['services'])


@pytest.fixture
def mock_client():
    """Create a mock Home Assistant API client"""
    client = MagicMock()
    client.check_api_running.return_value = True
    client.get_config.return_value = {
        'version': '2025.1.0',
        'location_name': 'Test Home',
    }
    return client


@pytest.fixture
def mock_entities():
    """Create mock entities for testing"""
    light_state = MockState(state='on', attributes={'brightness': 255})
    switch_state = MockState(state='off', attributes={})

    light_entity = MockEntity(entity_id='light.living_room', state=light_state)
    switch_entity = MockEntity(entity_id='switch.kitchen', state=switch_state)

    return {
        'light': MockGroup(entities={'light.living_room': light_entity}),
        'switch': MockGroup(entities={'switch.kitchen': switch_entity}),
    }


@pytest.fixture
def inspector(mock_client):
    """Create an inspector with mocked client"""
    with patch('ha_core.client.Client', return_value=mock_client):
        inspector = HomeAssistantInspector(
            url='http://test.local:8123',
            token='test-token',
            log_level=40  # ERROR level to suppress logs in tests
        )
        return inspector


class TestHomeAssistantInspectorInit:
    """Test initialization and connection verification"""

    def test_init_success(self, mock_client):
        """Test successful initialization"""
        with patch('ha_core.client.Client', return_value=mock_client):
            inspector = HomeAssistantInspector(
                url='http://test.local:8123',
                token='test-token'
            )
            assert inspector.client == mock_client
            mock_client.check_api_running.assert_called_once()

    def test_init_adds_api_path(self, mock_client):
        """Test that /api is added to URL if missing"""
        with patch('ha_core.client.Client', return_value=mock_client) as client_class:
            HomeAssistantInspector(
                url='http://test.local:8123',
                token='test-token'
            )
            client_class.assert_called_once()
            args = client_class.call_args[0]
            assert args[0].endswith('/api')

    def test_init_connection_error(self, mock_client):
        """Test initialization fails with connection error"""
        mock_client.check_api_running.return_value = False

        with patch('ha_core.client.Client', return_value=mock_client):
            with pytest.raises(HAConnectionError):
                HomeAssistantInspector(
                    url='http://test.local:8123',
                    token='test-token'
                )


class TestSystemStatus:
    """Test system status and configuration methods"""

    def test_is_running_true(self, inspector):
        """Test is_running returns True when API is running"""
        inspector.client.check_api_running.return_value = True
        assert inspector.is_running is True

    def test_is_running_false_on_error(self, inspector):
        """Test is_running returns False on connection error"""
        from homeassistant_api.errors import HomeassistantAPIError
        inspector.client.check_api_running.side_effect = HomeassistantAPIError()
        assert inspector.is_running is False

    def test_config_property(self, inspector):
        """Test config property returns configuration"""
        config = inspector.config
        assert config['version'] == '2025.1.0'
        assert config['location_name'] == 'Test Home'

    def test_config_caching(self, inspector):
        """Test config is cached after first call"""
        _ = inspector.config
        _ = inspector.config
        # Should only call get_config once
        inspector.client.get_config.assert_called_once()

    def test_config_api_error(self, inspector):
        """Test config raises APIError on failure"""
        from homeassistant_api.errors import HomeassistantAPIError
        inspector.client.get_config.side_effect = HomeassistantAPIError()

        with pytest.raises(APIError):
            _ = inspector.config

    def test_version_property(self, inspector):
        """Test version property returns HA version"""
        assert inspector.version == '2025.1.0'

    def test_location_name_property(self, inspector):
        """Test location_name property"""
        assert inspector.location_name == 'Test Home'

    def test_components_property(self, inspector):
        """Test components property returns tuple"""
        inspector.client.get_components.return_value = ('light', 'switch', 'sensor')
        components = inspector.components
        assert components == ('light', 'switch', 'sensor')

    def test_components_error_returns_empty_tuple(self, inspector):
        """Test components returns empty tuple on error"""
        from homeassistant_api.errors import HomeassistantAPIError
        inspector.client.get_components.side_effect = HomeassistantAPIError()
        assert inspector.components == tuple()


class TestEntityDiscovery:
    """Test entity discovery and querying"""

    def test_entities_property(self, inspector, mock_entities):
        """Test entities property returns all entities"""
        inspector.client.get_entities.return_value = mock_entities
        entities = inspector.entities
        assert 'light' in entities
        assert 'switch' in entities

    def test_entities_caching(self, inspector, mock_entities):
        """Test entities are cached"""
        inspector.client.get_entities.return_value = mock_entities
        _ = inspector.entities
        _ = inspector.entities
        inspector.client.get_entities.assert_called_once()

    def test_entities_api_error(self, inspector):
        """Test entities raises APIError on failure"""
        from homeassistant_api.errors import HomeassistantAPIError
        inspector.client.get_entities.side_effect = HomeassistantAPIError()

        with pytest.raises(APIError):
            _ = inspector.entities

    def test_get_entity_success(self, inspector):
        """Test get_entity returns entity"""
        mock_entity = MockEntity('light.bedroom', MockState('on', {}))
        inspector.client.get_entity.return_value = mock_entity

        entity = inspector.get_entity('light.bedroom')
        assert entity.entity_id == 'light.bedroom'

    def test_get_entity_not_found(self, inspector):
        """Test get_entity raises EntityNotFoundError"""
        from homeassistant_api.errors import HomeassistantAPIError
        inspector.client.get_entity.side_effect = HomeassistantAPIError()

        with pytest.raises(EntityNotFoundError):
            inspector.get_entity('light.nonexistent')

    def test_get_entities_by_domain(self, inspector, mock_entities):
        """Test get_entities_by_domain returns filtered entities"""
        inspector.client.get_entities.return_value = mock_entities
        lights = inspector.get_entities_by_domain('light')
        assert len(lights) == 1
        assert lights[0].entity_id == 'light.living_room'

    def test_get_entities_by_domain_not_found(self, inspector, mock_entities):
        """Test get_entities_by_domain with non-existent domain"""
        inspector.client.get_entities.return_value = mock_entities
        sensors = inspector.get_entities_by_domain('sensor')
        assert sensors == []

    def test_list_domains(self, inspector, mock_entities):
        """Test list_domains returns sorted list"""
        inspector.client.get_entities.return_value = mock_entities
        domains = inspector.list_domains()
        assert domains == ['light', 'switch']

    def test_get_entity_count(self, inspector, mock_entities):
        """Test get_entity_count returns total count"""
        inspector.client.get_entities.return_value = mock_entities
        count = inspector.get_entity_count()
        assert count == 2

    def test_get_domain_summary(self, inspector, mock_entities):
        """Test get_domain_summary returns counts by domain"""
        inspector.client.get_entities.return_value = mock_entities
        summary = inspector.get_domain_summary()
        assert summary == {'light': 1, 'switch': 1}


class TestActiveEntities:
    """Test active entity filtering"""

    def test_get_active_entities(self, inspector, mock_entities):
        """Test get_active_entities filters correctly"""
        inspector.client.get_entities.return_value = mock_entities
        active = inspector.get_active_entities()

        # Only light.living_room is 'on', switch.kitchen is 'off'
        assert 'light' in active
        assert len(active['light']) == 1
        assert active['light'][0].entity_id == 'light.living_room'

    def test_get_active_entities_with_domain_filter(self, inspector, mock_entities):
        """Test get_active_entities with domain filter"""
        inspector.client.get_entities.return_value = mock_entities
        active = inspector.get_active_entities(domains=['light'])

        assert 'light' in active
        assert 'switch' not in active


class TestServiceDiscovery:
    """Test service discovery methods"""

    def test_domains_property(self, inspector):
        """Test domains property returns service domains"""
        mock_services = {
            'turn_on': MagicMock(),
            'turn_off': MagicMock(),
        }
        mock_domains = {
            'light': MockDomain(services=mock_services)
        }
        inspector.client.get_domains.return_value = mock_domains

        domains = inspector.domains
        assert 'light' in domains

    def test_domains_caching(self, inspector):
        """Test domains are cached"""
        inspector.client.get_domains.return_value = {}
        _ = inspector.domains
        _ = inspector.domains
        inspector.client.get_domains.assert_called_once()

    def test_get_services_for_domain(self, inspector):
        """Test get_services_for_domain returns services"""
        mock_services = {
            'turn_on': MagicMock(),
            'turn_off': MagicMock(),
        }
        mock_domains = {
            'light': MockDomain(services=mock_services)
        }
        inspector.client.get_domains.return_value = mock_domains

        domain = inspector.get_services_for_domain('light')
        assert domain is not None
        assert 'turn_on' in domain.services

    def test_list_all_services(self, inspector):
        """Test list_all_services returns service map"""
        mock_services = {
            'turn_on': MagicMock(),
            'turn_off': MagicMock(),
        }
        mock_domains = {
            'light': MockDomain(services=mock_services),
            'switch': MockDomain(services=mock_services),
        }
        inspector.client.get_domains.return_value = mock_domains

        services = inspector.list_all_services()
        assert 'light' in services
        assert 'switch' in services
        assert 'turn_on' in services['light']


class TestConvenienceProperties:
    """Test convenience property shortcuts"""

    def test_lights_property(self, inspector, mock_entities):
        """Test lights property returns light entities"""
        inspector.client.get_entities.return_value = mock_entities
        lights = inspector.lights
        assert len(lights) == 1
        assert lights[0].entity_id == 'light.living_room'

    def test_switches_property(self, inspector, mock_entities):
        """Test switches property returns switch entities"""
        inspector.client.get_entities.return_value = mock_entities
        switches = inspector.switches
        assert len(switches) == 1
        assert switches[0].entity_id == 'switch.kitchen'


class TestCacheManagement:
    """Test cache management"""

    def test_refresh_cache_clears_all_caches(self, inspector, mock_entities):
        """Test refresh_cache clears all cached data"""
        inspector.client.get_entities.return_value = mock_entities

        # Populate caches
        _ = inspector.entities
        _ = inspector.config

        # Clear caches
        inspector.refresh_cache()

        # Verify caches are None
        assert inspector._entities_cache is None
        assert inspector._config_cache is None
        assert inspector._domains_cache is None


class TestLogger:
    """Test logging setup"""

    def test_setup_logger(self):
        """Test setup_logger creates logger with handler"""
        import logging
        logger = setup_logger('test_logger', logging.DEBUG)
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) > 0

    def test_setup_logger_no_duplicate_handlers(self):
        """Test setup_logger doesn't add duplicate handlers"""
        import logging
        logger = setup_logger('test_logger2', logging.INFO)
        handler_count = len(logger.handlers)

        # Call again with same name
        logger = setup_logger('test_logger2', logging.INFO)
        assert len(logger.handlers) == handler_count
