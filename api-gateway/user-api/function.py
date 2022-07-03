import logging
from apigw import Router, Response
from util import validate_json_schema, hide_errors
from datatypes.constants import HttpMethod

logger = logging.getLogger(__name__)
logger.critical("Function startup")

router = Router()


@validate_json_schema(__name__)
@hide_errors()
def handler(event, ctx):
    return router.handle(event, ctx).generate_response()


@router.route("/")
def index(*_):
    return Response.success({"message": "Hello World"})


@router.route("/", methods=(HttpMethod.POST,))
def index_post(*_, headers=None, body=None):
    return Response.success({"message": "Posted!"})


@router.route("/test-endpoint", methods=(HttpMethod.POST,))
def test_ept_post(*_, body=None):
    return {"message": "TEST DONE!"}
