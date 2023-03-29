import pytest

from runzero.api import OrgsAdmin, Sites
from runzero.client import AuthError, Client


@pytest.mark.integration_test
def test_client_account_token(account_client):
    """
    This test ensures we can use a valid account token to interact with an account and org scope API
    """
    c = account_client
    o = OrgsAdmin(client=c)
    orgs = o.get_all()
    assert len(orgs) >= 1


@pytest.mark.integration_test
def test_client_organization_token(org_client, integration_config):
    """
    This test ensures we can use a valid organization token to interact with an organization scope API
    """
    s = Sites(client=org_client)
    sites = s.get_all(integration_config.org_id)
    assert len(sites) >= 1


@pytest.mark.integration_test
def test_client_organization_token_for_account_api_is_auth_error(org_client, integration_config):
    """
    This test ensures we cannot use a valid organization token to interact with an account scope API
    """
    with pytest.raises(AuthError):
        OrgsAdmin(client=org_client).get_all()


@pytest.mark.integration_test
def test_client_oauth_login(integration_config):
    """
    This test ensures we can use the client id and secret to retrieve a valid OAuth token and use that OAuth token
    for both account and organization scope APIs
    """

    c = Client(server_url=integration_config.url, validate_certificate=integration_config.validate_cert)
    assert c._use_token is False
    c.oauth_login(integration_config.client_id, integration_config.client_secret)
    assert c._use_token is True
    assert c.oauth_token_is_expired is False
    orgs = OrgsAdmin(client=c).get_all()
    assert len(orgs) >= 1


@pytest.mark.integration_test
def test_client_oauth_login_fail(integration_config):
    """
    This test ensures the appropriate exception is raised when OAuth fails.
    """
    c = Client(server_url=integration_config.url, validate_certificate=integration_config.validate_cert)
    assert c._use_token is False
    with pytest.raises(AuthError):
        c.oauth_login(integration_config.client_id, "fail")


@pytest.mark.integration_test
def test_client_auth_attempt_with_server_down(integration_config):
    """
    This test ensures the appropriate exception is raised when OAuth fails.
    """
    c = Client(server_url="https://server.not.there", validate_certificate=integration_config.validate_cert)
    with pytest.raises(AuthError):
        c.oauth_login(integration_config.client_id, integration_config.client_secret)
