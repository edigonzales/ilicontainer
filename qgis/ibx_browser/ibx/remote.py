"""HTTPS byte-range source pinned by a strong ETag.

Mirrors ``ch.interlis.ibx.remote.HttpRangeSource``: every read is a Range
request guarded by ``If-Match``, a full response is only acceptable as an
explicit full download at open time, and an ETag change aborts the session
instead of mixing file states.
"""

import os
import re
import ssl
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request

from .container import HEADER_SIZE, IbxError, LocalSource, Metrics, Source

RANGE_PATTERN = re.compile(r"bytes (\d+)-(\d+)/(\d+)")
MAX_REDIRECTS = 5


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Redirect handling is explicit so HTTPS downgrades can be rejected."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HttpRangeSource(Source):
    def __init__(self, url, options, metrics):
        if isinstance(url, os.PathLike):
            url = os.fspath(url)
        parts = urllib.parse.urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            raise IbxError("Expected HTTP(S) URL")
        self.url = url
        self.options = options
        self.metrics = metrics
        self.connect_timeout = options.get("connectTimeoutMillis", 5000) / 1000.0
        self.read_timeout = options.get("readTimeoutMillis", 10000) / 1000.0
        self.allow_full_download = bool(options.get("allowFullDownload"))
        self.immutable_url = bool(options.get("immutableUrl"))
        self.length = -1
        self.etag = None
        self.snapshot = None
        self.temporary = None
        self.closed = False
        self.initial_header = None
        self.lock = threading.RLock()
        handlers = [_NoRedirect]
        if parts.scheme == "https":
            handlers.append(
                urllib.request.HTTPSHandler(context=ssl.create_default_context())
            )
        self.opener = urllib.request.build_opener(*handlers)
        try:
            self.initial_header = self._fetch(0, HEADER_SIZE, initial=True)
        except Exception:
            self.close()
            raise

    # -- Source interface ---------------------------------------------------

    def revision(self):
        return (self.etag or "snapshot-or-immutable") + ":" + str(self.size())

    def size(self):
        self._ensure_open()
        return self.snapshot.size() if self.snapshot is not None else self.length

    def read(self, offset, count):
        self._ensure_open()
        if offset < 0 or count < 0 or offset > self.size() - count:
            raise IbxError("Range outside remote container")
        if count == 0:
            return b""
        if offset == 0 and count == HEADER_SIZE and self.initial_header is not None:
            return bytes(self.initial_header)
        if self.snapshot is not None:
            return self.snapshot.read(offset, count)
        with self.lock:
            return self._fetch(offset, count, initial=False)

    def close(self):
        self.closed = True
        if self.snapshot is not None:
            self.snapshot.close()
            self.snapshot = None
        if self.temporary is not None:
            try:
                os.unlink(self.temporary)
            except OSError:
                pass
            self.temporary = None

    def _ensure_open(self):
        if self.closed:
            raise IbxError("Source closed")

    # -- HTTP ---------------------------------------------------------------

    def _request(self, url, offset, count):
        headers = {
            "Accept-Encoding": "identity",
            "Range": "bytes=%d-%d" % (offset, offset + count - 1),
        }
        if self.etag is not None:
            headers["If-Match"] = self.etag
        request = urllib.request.Request(url, headers=headers)
        self.metrics.requests += 1
        try:
            return self.opener.open(request, timeout=self.read_timeout), None
        except urllib.error.HTTPError as error:
            # Redirects, 412 and other status codes still carry their headers.
            return None, error
        except (urllib.error.URLError, OSError) as error:
            raise IbxError("HTTPS-Anfrage fehlgeschlagen: %s" % error) from error

    def _fetch(self, offset, count, initial):
        current = self.url
        response = error = None
        for redirects in range(MAX_REDIRECTS + 1):
            response, error = self._request(current, offset, count)
            if error is not None:
                status = error.code
            else:
                status = getattr(response, "status", None) or response.getcode()
            if status not in (301, 302, 303, 307, 308):
                break
            if error is not None:
                location = error.headers.get("Location")
                error.close()
            else:
                location = response.headers.get("Location")
                response.close()
            if redirects >= MAX_REDIRECTS or not location:
                raise IbxError("Invalid/excessive HTTP redirects")
            target = urllib.parse.urljoin(current, location)
            parts = urllib.parse.urlsplit(target)
            if (
                parts.scheme not in ("http", "https")
                or parts.username is not None
                or (
                    urllib.parse.urlsplit(current).scheme == "https"
                    and parts.scheme != "https"
                )
            ):
                raise IbxError("Unsafe HTTP redirect")
            current = target
        try:
            if error is not None:
                status = error.code
                headers = error.headers
                stream = error
            else:
                status = getattr(response, "status", None) or response.getcode()
                headers = response.headers
                stream = response
            encoding = headers.get("Content-Encoding")
            if encoding is not None and encoding.lower() != "identity":
                raise IbxError("Encoded HTTP response invalidates byte ranges")
            response_tag = headers.get("ETag")
            if status == 412 or (self.etag is not None and self.etag != response_tag):
                raise IbxError("Remote container changed (ETag)")
            if status == 200:
                if not initial or not self.allow_full_download:
                    raise IbxError(
                        "Server returned a full response; range access required "
                        "(explicit full download only at open)"
                    )
                return self._full_download(stream)
            if status != 206:
                raise IbxError("HTTP range failed: %s" % status)
            match = RANGE_PATTERN.match(headers.get("Content-Range") or "")
            if not match:
                raise IbxError("Missing/invalid Content-Range")
            start, end, total = (int(group) for group in match.groups())
            if (
                start != offset
                or end != offset + count - 1
                or total <= end
                or (self.length >= 0 and self.length != total)
            ):
                raise IbxError("Content-Range mismatch/container changed")
            if initial:
                self.length = total
                if (
                    response_tag
                    and not response_tag.startswith("W/")
                    and response_tag.startswith('"')
                    and response_tag.endswith('"')
                ):
                    self.etag = response_tag
                elif not self.immutable_url:
                    raise IbxError(
                        "A strong ETag or explicit immutable URL is required"
                    )
            declared = headers.get("Content-Length")
            if declared is not None and int(declared) != count:
                raise IbxError("HTTP response length mismatch")
            return self._body(stream, count)
        finally:
            if error is not None:
                error.close()
            elif response is not None:
                response.close()

    def _body(self, stream, count):
        parts = []
        remaining = count
        while remaining > 0:
            block = stream.read(remaining)
            if not block:
                raise IbxError("Truncated HTTP range")
            parts.append(block)
            remaining -= len(block)
        if stream.read(1):
            raise IbxError("Oversized HTTP range")
        data = b"".join(parts)
        self.metrics.bytesRead += len(data)
        return data

    def _full_download(self, stream):
        handle, path = tempfile.mkstemp(prefix="ibx-snapshot-", suffix=".ibx")
        try:
            with os.fdopen(handle, "wb") as target:
                while True:
                    block = stream.read(65536)
                    if not block:
                        break
                    self.metrics.bytesRead += len(block)
                    target.write(block)
            expected = stream.headers.get("Content-Length")
            if expected is not None and os.path.getsize(path) != int(expected):
                raise IbxError("Truncated full download")
            self.snapshot = LocalSource(path, Metrics())
            self.temporary = path
            self.length = self.snapshot.size()
            return self.snapshot.read(0, min(HEADER_SIZE, self.length))
        except Exception:
            try:
                os.unlink(path)
            except OSError:
                pass
            raise
