import logging
from typing import Callable, Dict, Sequence, Tuple
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
from apigw import Response
from apigw.exceptions import ApiError

logger = logging.getLogger(__name__)


class Router:
    server_name = None
    script_name = "/"
    url_scheme = "https"

    def __init__(self, prefix="") -> None:
        self._prefix = prefix.strip("/")
        self._router = None
        self.url_map = Map()
        self.view_functions = {}

    def _bind_router(self, request: Dict) -> None:
        logger.debug("Binding router")
        self._router = self.url_map.bind(
            server_name=self.server_name or request["headers"].get("host", ""),
            script_name=self.script_name,
            url_scheme=self.url_scheme,
        )

    def add_url_rule(self, rule: str, view_func: Callable, **options: Dict) -> None:
        endpoint = options.get("endpoint") or view_func.__name__
        options["endpoint"] = endpoint

        methods = options.pop("methods", None)
        if methods is None:
            methods = getattr(view_func, "methods", None) or ("GET",)

        logger.debug(
            "Registering rule",
            extra={"rule": rule, "methods": methods, "options": options},
        )
        self.url_map.add(Rule(rule, methods=sorted(methods), **options))

        if view_func is not None:
            old_func = self.view_functions.get(endpoint)
            if old_func is not None and old_func != view_func:
                raise AssertionError(
                    "View function mapping is overwriting an "
                    f"existing endpoint function: {endpoint}"
                )
            self.view_functions[endpoint] = view_func

    def route(self, rule, **options) -> Callable:
        def decorator(func):
            path = f"/{self._prefix}{rule.strip('/')}"
            self.add_url_rule(path, func, **options)
            return func

        return decorator

    def match(self, request: Dict) -> Tuple[Callable, Sequence]:
        if self._router is None:
            self._bind_router(request)

        logger.debug(
            "Matching", extra={"path": request["path"], "method": request["httpMethod"]}
        )
        endpoint, args = self._router.match(request["path"], request["httpMethod"])

        view_func = self.view_functions.get(endpoint)
        return view_func, args

    def handle(self, event: Dict, ctx) -> Dict:
        view_func, args = self.match(event)

        logger.debug("Route match", extra={"view_func": view_func, "arguments": args})

        try:
            response = view_func(event, ctx, **args)
            if isinstance(response, Dict):
                response = Response(status_code=200, body=response)
        except HTTPException as ex:
            response = Response(
                status_code=ex.code,
                body={
                    "error": ex.name.lower().replace(" ", "_").replace("'", ""),
                    "message": ex.description,
                },
            )
        except ApiError as ex:
            response = Response(
                status_code=ex.code,
                body={"error": ex.msg},
            )
        except Exception as ex:  # pylint: disable=broad-except
            logger.exception(ex)

            response = Response.internal_server_error(
                {"error": "Internal Server Error"}
            )

        response.update_headers("transactionId", ctx.aws_request_id)
        return response.generate_response()
