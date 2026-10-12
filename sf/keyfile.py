"""Write the Snowflake private key from the SNOWFLAKE_PRIVATE_KEY secret to a file.

Secrets pasted through a web form often lose their line breaks or pick up carriage returns.
This rebuilds a clean PEM from whatever base64 body is there, and says what it found without
printing any of it.   python -m sf.keyfile <output path>
"""
from __future__ import annotations
import os, re, sys, base64, textwrap

def main():
    raw = os.environ.get("SNOWFLAKE_PRIVATE_KEY", "")
    had_header = "BEGIN" in raw
    body = re.sub(r"-----[A-Z ]+-----", "", raw)
    body = re.sub(r"[^A-Za-z0-9+/=]", "", body)
    print(f"secret: {len(raw)} characters, PEM header {'present' if had_header else 'missing'}, "
          f"base64 body {len(body)} characters")
    try:
        der = base64.b64decode(body, validate=True)
    except Exception:
        der = b""
    if len(der) < 600:
        sys.exit("SNOWFLAKE_PRIVATE_KEY does not contain a private key. Paste the full contents of "
                 "brain_svc_key.p8 (about 1,700 characters, starting -----BEGIN PRIVATE KEY-----).")
    pem = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(textwrap.wrap(body, 64)) + "\n-----END PRIVATE KEY-----\n"
    with open(sys.argv[1], "w") as f:
        f.write(pem)
    os.chmod(sys.argv[1], 0o600)

if __name__ == "__main__":
    main()
