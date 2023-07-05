#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple, Dict

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth.oauth import Oauth2Authenticator
from source_formance.streams import Accounts, Balances, Transactions


class SourceFormance(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            auth = FormanceAuthenticator(config).get_auth()
            _ = auth.get_auth_header()
            return True, None
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = FormanceAuthenticator(config).get_auth()
        return [
            Accounts(authenticator=auth, config=config, ledger=config["ledger"]),
            Balances(authenticator=auth, config=config, ledger=config["ledger"]),
            Transactions(authenticator=auth, config=config, ledger=config["ledger"]),
        ]


class OAuth(Oauth2Authenticator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload = super().get_refresh_request_body()
        payload["grant_type"] = "client_credentials"
        payload.pop("refresh_token")  # Formance doesn't have Refresh Token parameter
        return payload


class FormanceAuthenticator:
    def __init__(self, config: Dict):
        self.config = config

    def get_auth(self) -> OAuth:
        return OAuth(
            token_refresh_endpoint=self.config["stack_url"]+"/api/auth/oauth/token",
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            refresh_token=None # Formance doesn't have Refresh Token parameter
        )