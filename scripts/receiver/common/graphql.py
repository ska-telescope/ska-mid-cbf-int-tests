"""GraphQL client."""

import requests


class GraphQLClient:
    """
    Simple GraphQL client.

    :param url: URL of GraphQL endpoint
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, url: str):
        self._url = url

    def execute(self, query: str, variables: dict = None):
        """
        Execute query on GraphQL server.

        :param query: query to execute (can be query or mutation)
        :param variables: variables for query

        """
        data = {"query": query, "variables": variables}
        response = requests.post(url=self._url, json=data, timeout=10.0)
        response.raise_for_status()
        return response.json()
