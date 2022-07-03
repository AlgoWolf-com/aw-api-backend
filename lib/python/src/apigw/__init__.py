import json
import logging
import inspect
import traceback
from typing import Callable, Dict, List, Tuple
from datatypes.constants import HttpMethod

logger = logging.getLogger(__name__)


class Response:
    def __init__(
        self,
        status_code: int = 200,
        body: Dict = None,
        headers: Dict = None,
        is_base64_encoded: bool = False,
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.headers = headers
        self.is_base64_encoded = is_base64_encoded

    @classmethod
    def success(
        cls, body: Dict = None, headers: Dict = None, is_base64_encoded: bool = False
    ):
        return cls(
            status_code=200,
            body=body,
            headers=headers,
            is_base64_encoded=is_base64_encoded,
        )

    def generate_response(self):
        headers = {
            **{"Content-Type": "application/json"},
            **({} if self.headers is None else self.headers),
        }
        body = {} if self.body is None else self.body

        return {
            "isBase64Encoded": self.is_base64_encoded,
            "statusCode": self.status_code,
            "headers": headers,
            "body": json.dumps(body),
        }


class Router:
    def __init__(self) -> None:
        self.routes = {}

    def _add_route(
        self, path: str, methods: Tuple[HttpMethod], func: Callable, keys: List
    ):
        if path not in self.routes:
            self.routes[path] = {}

        for method in methods:
            self.routes[path][method] = {"func": func, "keys": keys}

    def _route_exists(self, path: str, method: str) -> bool:
        if path not in self.routes:
            return Response(status_code=404, body={"error": "Resource not found"})

        if method not in self.routes[path]:
            return Response(status_code=405, body={"error": "Method not allowed"})

    def _get_params(self, multi_value_params: Dict) -> Dict:
        params = {}
        for key in multi_value_params:
            if len(multi_value_params[key]) == 1:
                params[key] = multi_value_params[key][0]
            elif len(multi_value_params[key]) > 1:
                params[key] = multi_value_params[key]
        return params

    def route(self, path: str, methods: Tuple[HttpMethod] = (HttpMethod.GET,)) -> None:
        def outer(func: Callable) -> None:
            sig = inspect.signature(func)
            keys = [
                param.name
                for param in sig.parameters.values()
                if param.kind == param.KEYWORD_ONLY
            ]

            self._add_route(path, methods, func, keys)

        return outer

    def handle(self, event, ctx) -> Response:
        path = event["path"]
        method = HttpMethod(event["httpMethod"])
        event["params"] = self._get_params(event["multiValueQueryStringParameters"])

        bad_request_res = self._route_exists(path, method)
        if bad_request_res is not None:
            return bad_request_res

        try:
            route_val = self.routes[path][method]
            kwargs = {key: event[key] for key in route_val["keys"]}
            res = route_val["func"](event, ctx, **kwargs)
        except Exception:  # pylint: disable=broad-except
            logger.error(traceback.format_exc())
            return Response(status_code=500, body={"error": "Internal Server Error"})

        if res is None:
            return Response(status_code=200, body={})
        if isinstance(res, dict):
            return Response(status_code=200, body=res)
        if isinstance(res, Response):
            return res

        logging.error("Response body was not correct type.")
        return Response(status_code=500, body={"error": "Internal Server Error"})
