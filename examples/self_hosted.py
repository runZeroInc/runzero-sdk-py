import runzero

# API keys are required for using the runZero sdk. See https://www.runzero.com/docs/leveraging-the-api/
MY_CLIENT_ID = ""  # OAuth client id. See https://console.runzero.com/account/api/clients
MY_CLIENT_SECRET = ""  # OAuth client secret. See https://console.runzero.com/account/api/clients

MY_INSTANCE = "https://my-instance.com:8001"  # This is the url for your self-hosted instance. Port can be specified.


def main():
    """
    Self-hosted runZero users can take advantage of the SDK as well.

    In the code below gives an example of pointing the runZero client to a self-hosted instance and even uses a specific
    port for connecting.
    """

    # create the client with the `server_url` kwarg set
    c = runzero.Client(server_url=MY_INSTANCE)

    # log in to your self-hosted instance using OAuth
    c.oauth_login(MY_CLIENT_ID, MY_CLIENT_SECRET)
    print("successfully logged in to your self-hosted instance")

    # retrieve all Orgs in your self-hosted instance
    orgs = runzero.OrgsAdmin(client=c).get_all()
    print(f"got {len(orgs)} from your self hosted instance")


if __name__ == "__main__":
    main()
