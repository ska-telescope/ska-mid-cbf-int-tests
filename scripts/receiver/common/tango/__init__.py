"""Tango device client."""

from .dp import TangoClientDP
from .gql import TangoClientGQL


def tango_client(context, device, translations=None):
    """
    Create Tango device client based on test context.

    :param context: test context
    :param device: device name
    :param translations: optional translations for attribute values

    """
    print("CLIENT TEST")
    if context.tango_client == "dp":
        client = TangoClientDP(device, translations=translations)
    elif context.tango_client == "gql":
        client = TangoClientGQL(
            context.tangogql_url, device, translations=translations
        )
    else:
        raise RuntimeError(f"Unknown tango client: {context.tango_client}")

    return client
