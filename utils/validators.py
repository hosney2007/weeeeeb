"""Shared input-validation helpers.

Centralizes the "is this number field actually a number" checks so every
form in the project (registration, booking, contact, book payment...)
validates phone numbers the same way instead of each route reinventing
its own half-checked regex.
"""
import re

# Egyptian mobile numbers: 11 digits, starting 010/011/012/015.
PHONE_REGEX = re.compile(r"^01[0125][0-9]{8}$")


def is_valid_phone(value):
    """Return True if `value` looks like a real Egyptian mobile number."""
    if not value:
        return False
    value = value.strip()
    return bool(PHONE_REGEX.match(value))


def clean_phone(value):
    """Strip spaces/dashes people paste in, e.g. '010 123 45678' -> '01012345678'."""
    if not value:
        return ""
    return re.sub(r"[\s\-]", "", value.strip())


def email_domain_exists(email):
    """False only when the email's domain definitely does not exist
    (e.g. a typo like gmial.con). Network problems never block a signup."""
    try:
        import dns.resolver
    except ImportError:
        return True
    domain = email.rsplit("@", 1)[-1]
    try:
        dns.resolver.resolve(domain, "MX", lifetime=3)
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except dns.resolver.NoAnswer:
        try:
            dns.resolver.resolve(domain, "A", lifetime=3)
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return False
        except Exception:
            return True
    except Exception:
        return True


# ---- mailbox existence check (best effort) --------------------------------
_UNKNOWN_USER_PHRASES = (
    "does not exist", "doesn't exist", "no such user", "user unknown",
    "unknown user", "mailbox not found", "mailbox unavailable",
    "invalid recipient", "recipient rejected", "doesn't have a",
    "does not have a", "account that you tried to reach does not exist",
    "address rejected", "no mailbox",
)


def _is_unknown_mailbox(code, message):
    """True only when the mail server clearly says this mailbox doesn't exist."""
    if code not in (550, 551, 552, 553, 554):
        return False
    if isinstance(message, bytes):
        message = message.decode("utf-8", "ignore")
    text = (message or "").lower()
    if any(w in text for w in ("quota", "full", "storage", "too large", "size")):
        return False
    return "5.1.1" in text or any(p in text for p in _UNKNOWN_USER_PHRASES)


def email_mailbox_status(email, sender=None, timeout=6):
    """Ask the recipient's mail server whether the mailbox exists (no email sent).

    Returns False  -> the server definitely says the mailbox does not exist
            True   -> the server accepted the address
            None   -> couldn't tell (port 25 blocked, timeout, catch-all...);
                      callers must NOT reject the signup in this case.
    """
    import os
    if os.environ.get("EMAIL_MAILBOX_CHECK", "1") == "0":
        return None
    try:
        import dns.resolver
        import smtplib
    except ImportError:
        return None

    domain = email.rsplit("@", 1)[-1]
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=3)
        hosts = [str(r.exchange).rstrip(".") for r in sorted(answers, key=lambda r: r.preference)]
    except Exception:
        return None

    mail_from = sender if sender and "@" in sender else "postmaster@" + domain
    for host in hosts[:2]:
        try:
            server = smtplib.SMTP(timeout=timeout)
            server.connect(host, 25)
            server.ehlo_or_helo_if_needed()
            server.mail(mail_from)
            code, message = server.rcpt(email)
            try:
                server.quit()
            except Exception:
                pass
            if _is_unknown_mailbox(code, message):
                return False
            if 200 <= code < 300:
                return True
            return None
        except Exception:
            continue
    return None
