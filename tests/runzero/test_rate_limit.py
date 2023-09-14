import pytest

from runzero.api import CustomIntegrations
from runzero.types import RateLimitInformation


@pytest.mark.integration_test
def test_client_keeps_last_rate_limit(org_client, temp_custom_integration, integration_config, monkeypatch):
    """
    This test demonstrates rate limit retrieval
    """
    c = org_client
    assert c.last_rate_limit_information is None
    sm = CustomIntegrations(c)

    good_rate_usage = RateLimitInformation(usage_remaining=100, usage_limit=1000, usage_total=100, usage_today=10)
    with monkeypatch.context() as m:
        m.setattr(RateLimitInformation, "from_headers", lambda *args: good_rate_usage)
        sm.get(org_id=integration_config.org_id, custom_integration_id=temp_custom_integration.id)
        rates = c.last_rate_limit_information
        assert rates is not None
        assert rates.usage_limit == 1000
