#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams import IncrementalMixin

class FormanceStream(HttpStream, ABC):
    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.config = config

    @property
    def url_base(self) -> str:
        return self.config["stack_url"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        cursor = response.json().get("cursor")
        if cursor.get("hasMore"):
            return {"cursor": cursor.get("next")}
        return None

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("cursor").get("data")


class IncrementalFormanceStream(FormanceStream, IncrementalMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'start_date' in self.config:
            self._cursor_value = self.config['start_date']
        else:
            self._cursor_value = None

    @property
    def cursor_field(self) -> str:
        return "timestamp"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if stream_state and self.cursor_field in stream_state:
            params = {"startTime": stream_state.get(self.cursor_field)}
        elif 'start_date' in self.config:
            params = {"startTime": self.config['start_date']}
        else:
            params = {}
            
        if next_page_token:
            params.update(**next_page_token)
        return params
    
    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value}
    
    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            if self._cursor_value:
                self._cursor_value = max(self._cursor_value, record[self.cursor_field])
            else:
                self._cursor_value = record[self.cursor_field]
            yield record



class Accounts(FormanceStream):
    primary_key = ""

    def __init__(self, ledger: str, **kwargs):
        super().__init__(**kwargs)
        self.ledger = ledger

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        ledger = self.ledger
        return f"/api/ledger/{ledger}/accounts"

class Balances(FormanceStream):
    primary_key = ""

    def __init__(self, ledger: str, **kwargs):
        super().__init__(**kwargs)
        self.ledger = ledger

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        ledger = self.ledger
        return f"/api/ledger/{ledger}/balances"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("cursor").get("data")
        for element in data:
            for key in element.keys():
                for sub_key in element[key].keys():
                    transformed_record = {}
                    transformed_record["address"] = key
                    transformed_record["asset"] = sub_key
                    transformed_record["balance"] = element[key][sub_key]

                    yield transformed_record

class Transactions(IncrementalFormanceStream):
    primary_key = "txid"

    def __init__(self, ledger: str, **kwargs):
        super().__init__(**kwargs)
        self.ledger = ledger

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        ledger = self.ledger
        return f"/api/ledger/{ledger}/transactions"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("cursor").get("data")
        for element in data:
            if 'preCommitVolumes' in element:
                element['preCommitVolumes'] = self.transform_commit_volumes(element, 'preCommitVolumes')
            if 'postCommitVolumes' in element:
                element['postCommitVolumes'] = self.transform_commit_volumes(element, 'postCommitVolumes')
            yield element

    def transform_commit_volumes(self, element, commit_volumes_name):
        commit_volumes = element[commit_volumes_name]
        transformed_commit_volumes = []
        for address in commit_volumes.keys():
            currencies = []
            for currency in commit_volumes[address].keys():
                currencies.append({
                    "currency": currency,
                    "input": commit_volumes[address][currency].get("input"),
                    "output": commit_volumes[address][currency].get("output"),
                    "balance": commit_volumes[address][currency].get("balance"),
                })
            transformed_commit_volumes.append({
                "address": address,
                "currencies": currencies
            })
        return transformed_commit_volumes
