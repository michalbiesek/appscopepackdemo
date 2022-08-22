import argparse
import ssl
from flask import Flask

app = Flask(__name__)
ARG_PORT = 'port'

@app.route('/')
def index():
    return 'Web App with Python Flask!'


def main() -> None:
    """
    Main function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(f'--{ARG_PORT}', help='port', default='1234')
    cli_cfg = vars(parser.parse_args())
    port = cli_cfg[ARG_PORT]

    app.run(host='0.0.0.0', port=port, ssl_context=('server.pem', 'server.key'))

if __name__ == "__main__":
    main()