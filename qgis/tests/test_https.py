"""End-to-end HTTPS source through the real QGIS provider and Java bridge."""

import hashlib
import http.server
import os
from pathlib import Path
import ssl
import subprocess
import tempfile
import threading
import unittest
from qgis.core import (
    QgsApplication,
    QgsProviderRegistry,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsRectangle,
)
from ibx_browser.client import manager
from ibx_browser.provider import Metadata, uri

app = QgsApplication([], False)
app.initQgis()


class HttpsProviderTests(unittest.TestCase):
    def test_https_range_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            store = directory / "test.p12"
            pem = directory / "test.pem"
            java = Path(
                os.environ.get(
                    "JAVA_HOME",
                    str(Path.home() / ".sdkman/candidates/java/21.0.10-tem"),
                )
            )
            subprocess.run(
                [
                    str(java / "bin/keytool"),
                    "-genkeypair",
                    "-alias",
                    "test",
                    "-keyalg",
                    "RSA",
                    "-storetype",
                    "PKCS12",
                    "-keystore",
                    str(store),
                    "-storepass",
                    "changeit",
                    "-keypass",
                    "changeit",
                    "-dname",
                    "CN=localhost",
                    "-ext",
                    "SAN=dns:localhost,ip:127.0.0.1",
                    "-validity",
                    "1",
                ],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "openssl",
                    "pkcs12",
                    "-in",
                    str(store),
                    "-out",
                    str(pem),
                    "-nodes",
                    "-passin",
                    "pass:changeit",
                ],
                check=True,
                capture_output=True,
            )
            data = Path("demo/quartier.ibx").read_bytes()
            tag = '"' + hashlib.sha256(data).hexdigest() + '"'
            requests = []

            class Handler(http.server.BaseHTTPRequestHandler):
                def log_message(self, *args):
                    pass

                def do_GET(self):
                    value = self.headers.get("Range")
                    assert value is not None
                    start, end = map(int, value[6:].split("-"))
                    requests.append((start, end, self.headers.get("If-Match")))
                    self.send_response(206)
                    self.send_header(
                        "Content-Range", f"bytes {start}-{end}/{len(data)}"
                    )
                    self.send_header("Content-Length", str(end - start + 1))
                    self.send_header("ETag", tag)
                    self.end_headers()
                    self.wfile.write(data[start : end + 1])

            server = http.server.ThreadingHTTPServer(("localhost", 0), Handler)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(pem)
            server.socket = context.wrap_socket(server.socket, server_side=True)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            previous = os.environ.get("JAVA_TOOL_OPTIONS")
            os.environ["JAVA_TOOL_OPTIONS"] = (
                f"-Djavax.net.ssl.trustStore={store} -Djavax.net.ssl.trustStorePassword=changeit"
            )
            try:
                manager.start()
                source = f"https://localhost:{server.server_port}/quartier.ibx"
                d = manager.dataset(source)
                self.assertEqual(0, d.call("metrics")["chunksRead"])
                QgsProviderRegistry.instance().registerProvider(Metadata())
                layer = QgsVectorLayer(
                    uri(source, d.state, "Quartier.Unterhalt.Gebaeude", "Grundriss"),
                    "HTTPS",
                    "ibx",
                )
                self.assertTrue(layer.isValid())
                features = list(
                    layer.getFeatures(
                        QgsFeatureRequest().setFilterRect(
                            QgsRectangle(2600001, 1200001, 2600010, 1200010)
                        )
                    )
                )
                self.assertEqual(1, len(features))
                obj = d.call("object", fid=features[0].id())
                self.assertEqual("g0", obj["tid"])
                target = d.call("object", tid=obj["fields"]["Auftrag"][0]["tid"])
                self.assertEqual(7, len(d.call("related", fid=target["fid"])["items"]))
                self.assertGreater(len(requests), 4)
                self.assertTrue(all(t == tag for _, _, t in requests[1:]))
                self.assertEqual(
                    hashlib.sha256(data).hexdigest(),
                    hashlib.sha256(Path("demo/quartier.ibx").read_bytes()).hexdigest(),
                )
                del layer
            finally:
                if manager.process:
                    manager.process.closeWriteChannel()
                    manager.process.waitForFinished(3000)
                server.shutdown()
                server.server_close()
                thread.join()
                if previous is None:
                    os.environ.pop("JAVA_TOOL_OPTIONS", None)
                else:
                    os.environ["JAVA_TOOL_OPTIONS"] = previous


if __name__ == "__main__":
    unittest.main()
