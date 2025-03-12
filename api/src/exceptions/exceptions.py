

class WebSocketException(Exception):

    error_code: str
    message: str

    def __init__(self):
        super().__init__(self.message)

    def to_json(self) -> dict:
        return {
            "error_code": self.error_code,
            "error": self.message
        }


class MethodNotAllowedError(WebSocketException):
    error_code = 400
    message = 'Method is not allowed'


class JsonDecodeError(WebSocketException):
    error_code = 400
    message = 'Json decode error'


class MissingDataError(WebSocketException):
    error_code = 422
    message = "Required fields are missing in client data"


class InternalError(WebSocketException):
    error_code = 500
    message = 'Internal server error'

