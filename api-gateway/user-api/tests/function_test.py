import json
import pathlib
from function import handler
from testing.mock import LambdaContext

current_dir = pathlib.Path(__file__).parent.resolve()


def test_message_ept_good_request() -> None:
    """Test /message endpoint with good request"""
    with open(
        f"{current_dir}/data/test_message_ept_good_request.json", "r", encoding="utf-8"
    ) as file:
        request = json.load(file)

    result = handler(request, LambdaContext())
    assert result["statusCode"] == 200 and result["body"] == json.dumps(
        {"message": "Hello World!"}
    )


def test_message_ept_no_headers() -> None:
    """Test /message endpoint with no headers"""
    with open(
        f"{current_dir}/data/test_message_ept_no_headers.json", "r", encoding="utf-8"
    ) as file:
        request = json.load(file)

    result = handler(request, LambdaContext())
    assert result["statusCode"] == 400 and result["body"] == json.dumps(
        {"error": "Unable to parse body request"}
    )
