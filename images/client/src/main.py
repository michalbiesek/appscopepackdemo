import enum
from importlib.resources import contents
from time import sleep
import httpx
import argparse

ARG_DEST = 'dest'
ARG_VARIANT = 'variant'
TIMEOUT = 5

class ReqVariant(enum.Enum):
    VALID_REQ = "valid_req"
    HEADER_INVALID = "header_invalid"
    GET_REQ_BODY = "get_req_body"

    def __str__(self) -> str:
        return self.value

class HttpReqProducer:
    def __init__(self, cli_cfg:dict) -> None:
        self.dest = cli_cfg[ARG_DEST]
        self.variant = cli_cfg[ARG_VARIANT]

    def send_get_request_var(self) -> None:
        """
        Send `GET` request
        """
        header = None
        if self.variant == ReqVariant.GET_REQ_BODY:
            try:
                httpx.request(method="GET", url=f'http://{self.dest}', content="foo_bar")
            except httpx.ConnectError:
                pass
            return
        elif self.variant == ReqVariant.HEADER_INVALID:
            header = {
                'X-Original-URL': 'Evil_url.com',
                'X-rewrite-URL': 'Evil_rewrite_url.com'
            }
        try:
            httpx.get(f'http://{self.dest}', headers=header)
        except httpx.ConnectError:
            pass

    def send_loop(self) -> None:
        while(True):
            self.send_get_request_var()
            sleep(TIMEOUT)

def main() -> None:
    """
    Main function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(f'--{ARG_DEST}', help='Destination', default='0.0.0.0:8000')
    parser.add_argument(f'--{ARG_VARIANT}', choices=ReqVariant, type=ReqVariant, help='choose HTTP request type')

    cli_cfg = vars(parser.parse_args())
    http_gen = HttpReqProducer(cli_cfg)
    http_gen.send_loop()

if __name__ == "__main__":
    main()