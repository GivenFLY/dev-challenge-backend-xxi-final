def exception_to_response_data(exception) -> dict:
    """Convert an APIException to a dict that can be used as response data.

    :param exception: The APIExceptionExt to convert.
    :return: A dict that can be used as response data.
    """
    if not hasattr(exception, "extra_data"):
        return {
            "errors": exception.detail,
        }

    return {"errors": exception.detail}
