import uuid

import runzero
from runzero.api import OrgsAdmin, Sites

# API keys are required for using the runZero sdk. See https://www.runzero.com/docs/leveraging-the-api/
MY_ACCOUNT_API_KEY = ""  # Account scoped API key. See https://console.runzero.com/account
MY_ORG_API_KEY = ""  # Organization scoped API key. See https://console.runzero.com/organizations

# This Org ID must be associated with the Org scoped API key above.
MY_ORG_ID = uuid.UUID("")  # runZero organization ID. See https://console.runzero.com/organizations

# This Org ID must not be associated with the Org scoped API key above.
OTHER_ORG_ID = uuid.UUID("")  # runZero organization ID. See https://console.runzero.com/organizations


def main():
    """
    In additional to OAuth login, the runZero SDK supports using account scoped Account API Keys as well as organization
    scoped Org API Keys.

    The code below gives an example of working with these API keys
    """

    # create the runzero client - no need to use the oauth_login() method after this
    c = runzero.Client(account_key=MY_ACCOUNT_API_KEY)

    # retrieve all Orgs in your account
    orgs = OrgsAdmin(client=c).get_all()
    print(f"got {len(orgs)} from your account")

    # Because the account key was used in the client above, the client will have access to account level items. However,
    # the SDK and API will limit what can be accessed if the client only has an org key.
    org_only_client = runzero.Client(org_key=MY_ORG_API_KEY)
    try:
        OrgsAdmin(client=org_only_client).get_all()
    except runzero.AuthError:
        print("we got an error because we attempted to retrieve account level data but only had an Org API Key")

    # Despite the error above, the client can still be used to retrieve Org level data from the Org that the key is
    #  associated with.
    sites = Sites(client=org_only_client).get_all(MY_ORG_ID)
    print(f"got {len(sites)} from our org")

    # Below will fail due to using an Org key to request data from an Org that the Org key is not associated with.
    try:
        Sites(client=org_only_client).get_all(OTHER_ORG_ID)
    except runzero.ClientError:
        print("Could not retrieve orgs due to client not having a valid Org key for the requested Org")


if __name__ == "__main__":
    main()
