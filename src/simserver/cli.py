import argparse
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = PROJECT_ROOT / ".dev" / "tools"

JAVA_SOURCE = TOOLS_DIR / "EncryptConfig.java"
CERT_SCRIPT = TOOLS_DIR / "generate-server-cert.sh"


def encrypt() -> None:
    subprocess.run(
        ["javac", str(JAVA_SOURCE)],
        cwd=PROJECT_ROOT,
        check=True,
    )

    subprocess.run(
        ["java", "-cp", str(TOOLS_DIR), "EncryptConfig"],
        cwd=PROJECT_ROOT,
        check=True,
    )


def generate_server_cert(ca_key: str, ca_crt: str, server_ip: str) -> None:
    subprocess.run(
        [
            "bash",
            str(CERT_SCRIPT),
            ca_key,
            ca_crt,
            server_ip,
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="SIMServe development tools.")

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "encrypt",
        help="Encrypt the SIMServe config for the APK.",
    )

    cert_parser = subparsers.add_parser(
        "generate-server-cert",
        help="Generate a server certificate signed by the CA.",
    )

    cert_parser.add_argument(
        "ca_key",
        help="Path to the CA private key.",
    )

    cert_parser.add_argument(
        "ca_crt",
        help="Path to the CA certificate.",
    )

    cert_parser.add_argument(
        "server_ip",
        help="Server IP address.",
    )

    args = parser.parse_args()

    if args.command == "encrypt":
        encrypt()
    elif args.command == "generate-server-cert":
        generate_server_cert(
            args.ca_key,
            args.ca_crt,
            args.server_ip,
        )


if __name__ == "__main__":
    main()
