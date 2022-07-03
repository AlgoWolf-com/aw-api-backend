import logging
from apigw import Router, Response
from util import validate_json_schema
from datatypes.constants import HttpMethod

logger = logging.getLogger(__name__)
logger.critical("Function startup")

router = Router()


@validate_json_schema(__name__)
def handler(event, ctx):
    return router.handle(event, ctx).generate_response()


@router.route("/message", methods=(HttpMethod.GET,))
def test_ept_post(*_):
    return Response.success({"message": "Hello World!"})
