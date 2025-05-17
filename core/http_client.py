from typing import Dict, Any, Union

import requests
from requests.exceptions import RequestException


class HttpClient:
    def __init__(
            self,
            base_url: str = None,
            timeout: int = 10,
            headers: Dict[str, str] = None
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def get(self, path: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}" if self.base_url else path
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": e.response.status_code if hasattr(e, 'response') else 500
            }

    def post(
            self,
            path: str,
            data: Union[Dict[str, Any], str] = None,
            json: Dict[str, Any] = None,
            headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}" if self.base_url else path
        try:
            response = self.session.post(url, data=data, json=json, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": e.response.status_code if hasattr(e, 'response') else 500
            }

    def put(self, path: str, data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}" if self.base_url else path
        try:
            response = self.session.put(url, data=data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": e.response.status_code if hasattr(e, 'response') else 500
            }

    def delete(self, path: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}" if self.base_url else path
        try:
            response = self.session.delete(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "status_code": response.status_code}
        except RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": e.response.status_code if hasattr(e, 'response') else 500
            }
