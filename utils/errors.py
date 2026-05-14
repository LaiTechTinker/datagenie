from flask import jsonify
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _api_err(e: ApiError):
        return jsonify(error=e.message), e.status

    @app.errorhandler(HTTPException)
    def _http_err(e: HTTPException):
        return jsonify(error=e.description), e.code

    @app.errorhandler(Exception)
    def _unhandled(e: Exception):
        app.logger.exception(e)
        return jsonify(error="Internal server error"), 500
