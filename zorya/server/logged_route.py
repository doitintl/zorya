"""logged_route.py"""
from fastapi import Request
from fastapi.routing import APIRoute

from zorya.logging import Logger


class LoggedRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            try:
                body = await request.json()
            except ValueError:
                body = await request.body()
                body = body.decode("utf-8")

            logger = Logger(request=request)
            logger(
                "request",
                body=body,
            )

            response = await original_route_handler(request)

            logger(
                "response",
                body=decode_body(response.body),
            )
            return response

        return custom_route_handler


def decode_body(body: bytes, codec: str = "utf-8") -> str:
    return body.decode(codec)
