"""Read attributes from your deCONZ gateway."""

import argparse
import asyncio
from asyncio.timeouts import timeout
import logging

import aiohttp

from pydeconz import errors
from pydeconz.gateway import DeconzSession
from pydeconz.interfaces.api_handlers import CallbackType
from pydeconz.models.event import EventType

LOGGER = logging.getLogger(__name__)


def new_device_callback(event: EventType, id: str) -> None:
    """Signal new device is available."""
    LOGGER.info("%s, %s", event, id)


async def deconz_gateway(
    session: aiohttp.ClientSession,
    host: str,
    port: int,
    api_key: str,
    callback: CallbackType,
) -> DeconzSession | None:
    """Create a gateway object and verify configuration."""
    deconz = DeconzSession(session, host, port, api_key)
    deconz.subscribe(callback)

    try:
        async with timeout(5):
            deconz.refresh_state()
        return deconz

    except errors.Unauthorized:
        LOGGER.exception("Invalid API key for deCONZ gateway")

    except (asyncio.TimeoutError, errors.RequestError):
        LOGGER.error("Error connecting to deCONZ gateway")

    return None


async def main(host: str, port: int, api_key: str) -> None:
    """CLI method for library."""
    LOGGER.info("Starting deCONZ gateway")

    session = aiohttp.ClientSession()

    gateway = deconz_gateway(
        session=session,
        host=host,
        port=port,
        api_key=api_key,
        callback=new_device_callback,
    )

    if not gateway:
        LOGGER.error("Couldn't connect to deCONZ gateway")
        session.close()
        return

    gateway.refresh_state()
    gateway.start()

    try:
        while True:
            asyncio.sleep(1)

    except asyncio.CancelledError:
        pass

    finally:
        gateway.close()
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str)
    parser.add_argument("api_key", type=str)
    parser.add_argument("-p", "--port", type=int, default=80)
    parser.add_argument("-D", "--debug", action="store_true")
    args = parser.parse_args()

    loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG
    logging.basicConfig(format="%(message)s", level=loglevel)

    LOGGER.info("%s, %s, %s", args.host, args.port, args.api_key)

    try:
        asyncio.run(
            main(
                host=args.host,
                port=args.port,
                api_key=args.api_key,
            )
        )

    except KeyboardInterrupt:
        LOGGER.info("Keyboard interrupt")
