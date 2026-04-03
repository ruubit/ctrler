import argparse
import sys

from ctrler.app import RemoteControllerApp


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ctrler: use your phone as a remote controller "
        "for videos playing full-screen in the browser."
    )
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=8000)
    cli_args = parser.parse_args()
    _check_binding_warning(cli_args.host)
    app = RemoteControllerApp(local_ip=cli_args.host, port=cli_args.port)
    app.run()


def _check_binding_warning(host: str):
    if host == "0.0.0.0":
        print(
            "⚠️  WARNING: You are binding to 0.0.0.0, which listens on all network "
            "interfaces. For the purpose of this tool, we recommend binding to a "
            "specific local ip."
        )
        confirmation = input("Do you want to continue? [y/N]: ").strip().lower()
        if confirmation not in ("y", "yes"):
            print("Aborting.")
            sys.exit(1)


if __name__ == "__main__":
    main()
