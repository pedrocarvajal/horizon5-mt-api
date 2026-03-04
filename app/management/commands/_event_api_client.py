import requests


class EventApiClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        access_token = self._login(api_key)
        self.session.headers["Authorization"] = f"Bearer {access_token}"

    def _login(self, api_key: str) -> str:
        url = f"{self.base_url}/api/v1/auth/login/"
        response = requests.post(url, json={"api_key": api_key}, timeout=30)
        response.raise_for_status()
        return response.json()["data"]["access"]

    def push_event(self, account_id: int, key: str, payload: dict) -> dict:
        url = f"{self.base_url}/api/v1/account/{account_id}/events/"
        response = self.session.post(url, json={"key": key, "payload": payload})
        response.raise_for_status()
        return response.json()

    def poll_event_response(self, account_id: int, event_id: str) -> dict | None:
        url = f"{self.base_url}/api/v1/account/{account_id}/event/{event_id}/response/"
        response = self.session.get(url)
        if response.status_code == requests.codes.ok:
            return response.json()
        return None

    def list_accounts(self) -> dict:
        url = f"{self.base_url}/api/v1/accounts/"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def list_strategies(self) -> dict:
        url = f"{self.base_url}/api/v1/strategies/"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def list_account_snapshots(self, account_id: int, page: int, per_page: int, order_by: str) -> dict:
        url = f"{self.base_url}/api/v1/accounts/snapshots/"
        response = self.session.get(
            url, params={"account_id": account_id, "page": page, "per_page": per_page, "order_by": order_by}
        )
        response.raise_for_status()
        return response.json()

    def list_strategy_snapshots(
        self, strategy_id: str, account_id: int | None, page: int, per_page: int, order_by: str
    ) -> dict:
        url = f"{self.base_url}/api/v1/strategies/snapshots/"
        params: dict = {"strategy_id": strategy_id, "page": page, "per_page": per_page, "order_by": order_by}
        if account_id is not None:
            params["account_id"] = account_id
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
