"""
http provides http i/o and authentication to the Client and is only intended for use by the client.

Primarily, this is a container to prevent requests, auth details, and lower-level HTTP errors from
making their way into your code and our tests.

Therefore, there is no public package-level API exposed here.
"""
