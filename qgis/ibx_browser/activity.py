"""Live, bounded read-activity view for one IBX session."""

from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

from qgis.PyQt.QtCore import QRunnable, QThreadPool, QTimer, Qt, pyqtSignal, QObject
from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QDialog,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


def source_label(source):
    """Return a useful source name without leaking URL parameters or local paths."""
    source = str(source or "")
    if source.startswith(("http://", "https://")):
        parsed = urlsplit(source)
        name = Path(unquote(parsed.path)).name
        host = parsed.hostname or "HTTPS-Quelle"
        return host + (f" / {name}" if name else "")
    return Path(source).name or "IBX-Datei"


class _PollSignals(QObject):
    finished = pyqtSignal(int, object, object)


class _ActivityPoll(QRunnable):
    def __init__(self, dataset, generation, signals):
        super().__init__()
        self.dataset = dataset
        self.generation = generation
        self.signals = signals

    def run(self):
        try:
            result = self.dataset.call("activity")
            self.signals.finished.emit(self.generation, result, None)
        except Exception as exc:
            self.signals.finished.emit(self.generation, None, str(exc))


class _SortableItem(QTableWidgetItem):
    """Table item with a typed sort value separate from its display text."""

    SORT_ROLE = Qt.ItemDataRole.UserRole + 1

    def __lt__(self, other):
        left = self.data(self.SORT_ROLE)
        right = other.data(self.SORT_ROLE)
        if left is None:
            return super().__lt__(other)
        if right is None:
            return super().__lt__(other)
        return left < right


class AccessMonitor(QDockWidget):
    """Docked view that polls the active dataset only while the dock is visible."""

    def __init__(self, parent=None):
        super().__init__("IBX · Zugriffsdiagnose", parent)
        self.setObjectName("ibxAccessMonitor")
        self.setMinimumWidth(680)
        self.setMinimumHeight(300)
        self.dataset = None
        self.generation = 0
        self._inflight_generation = None
        self._closing = False
        self._info_dialog = None

        root = QWidget(self)
        layout = QVBoxLayout(root)
        top = QHBoxLayout()
        self.source = QLabel("Keine IBX-Datenquelle ausgewählt")
        self.source.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.refresh_button = QPushButton("Jetzt aktualisieren")
        self.refresh_button.clicked.connect(self.refresh_now)
        self.info_button = QPushButton("Info")
        self.info_button.setToolTip("Erklärung der Spalten und Messwerte öffnen")
        self.info_button.clicked.connect(self.show_info)
        top.addWidget(self.source, 1)
        top.addWidget(self.refresh_button)
        top.addWidget(self.info_button)
        layout.addLayout(top)

        self.status = QLabel("Öffne einen IBX-Layer oder erkunde ein Objekt.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.totals = QLabel("")
        self.totals.setWordWrap(True)
        layout.addWidget(self.totals)

        self.table = QTableWidget(0, 6, root)
        self.table.setHorizontalHeaderLabels(
            ["Zeit", "Vorgang", "Status", "Dauer", "Leseaufwand", "Ergebnis / Meldung"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header_tooltips = [
            "Startzeit des Vorgangs. Neueste Vorgänge stehen standardmässig oben.",
            "Art des Lesezugriffs; optionale technische Details stehen nach dem Punkt.",
            "Wartet, läuft, ist fertig, fehlgeschlagen oder wurde abgebrochen.",
            "Dauer des Vorgangs einschliesslich Wartezeit auf die Lesesitzung.",
            "Zusammengefasste Bytes, Chunkframes, Indexseiten, Cachetreffer und HTTP-Ranges.",
            "Ergebniszahl oder Fehlermeldung des Vorgangs.",
        ]
        for column, tooltip in enumerate(header_tooltips):
            self.table.horizontalHeaderItem(column).setToolTip(tooltip)
        for col in range(5):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
        for column, width in enumerate([68, 175, 80, 65, 130]):
            header.resizeSection(column, width)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.table.setSortingEnabled(True)
        header.setSortIndicator(0, Qt.SortOrder.DescendingOrder)
        self.table.sortItems(0, Qt.SortOrder.DescendingOrder)
        layout.addWidget(self.table, 1)

        self.note = QLabel("Letzte 200 Vorgänge dieser Sitzung · nur im Arbeitsspeicher")
        self.note.setStyleSheet("color: #5f6368;")
        layout.addWidget(self.note)
        self.setWidget(root)
        self.resize(900, 360)

        self._signals = _PollSignals(self)
        self._signals.finished.connect(self._poll_finished)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._poll)
        self.visibilityChanged.connect(self._visibility_changed)
        self._thread_pool = QThreadPool.globalInstance()

    def show_message(self, message):
        self.generation += 1
        self.dataset = None
        self.source.setText("Keine IBX-Datenquelle")
        self.status.setText(message)
        self.totals.clear()
        self.table.setRowCount(0)
        self.refresh_button.setEnabled(False)
        self._timer.stop()
        self.show()
        self.raise_()

    def open_dataset(self, dataset):
        self.generation += 1
        self.dataset = dataset
        self.source.setText(source_label(dataset.source))
        self.source.setToolTip("Dateiname bzw. Hostname; vollständige Pfade und URL-Parameter werden ausgeblendet.")
        self.status.setText("Aktivitätsverlauf wird geladen …")
        self.totals.clear()
        self.table.setRowCount(0)
        self.refresh_button.setEnabled(True)
        self.show()
        self.raise_()
        if self.isVisible():
            QTimer.singleShot(0, self._poll)

    def refresh_now(self):
        if self.dataset is not None:
            self._poll()

    def _visibility_changed(self, visible):
        if visible and self.dataset is not None:
            if not self._timer.isActive():
                self._timer.start()
            self._poll()
        else:
            self._timer.stop()

    def _poll(self):
        if self._closing or self.dataset is None or self._inflight_generation is not None:
            return
        generation = self.generation
        self._inflight_generation = generation
        self.status.setText("Aktualisiere Aktivitätsverlauf …")
        self._thread_pool.start(_ActivityPoll(self.dataset, generation, self._signals))

    def _poll_finished(self, generation, data, error):
        if self._inflight_generation == generation:
            self._inflight_generation = None
        if self._closing or generation != self.generation:
            if self.dataset is not None and self.isVisible():
                QTimer.singleShot(0, self._poll)
            return
        if error:
            self.status.setText(f"Aktivitätsverlauf momentan nicht verfügbar: {error}")
            return

        events = data.get("events", [])
        active = data.get("active", 0)
        now = datetime.now().strftime("%H:%M:%S")
        self.status.setText(
            f"Aktualisiert {now} · {active} Vorgänge laufen oder warten · {len(events)} im Verlauf"
        )
        self.totals.setText(self._totals_text(data.get("totals", {})))
        self._show_events(events)

    def _totals_text(self, totals):
        return (
            "Seit dem Öffnen: "
            f"{_bytes(totals.get('bytesRead', 0))} gelesen · "
            f"Index {_bytes(totals.get('indexBytes', 0))} · "
            f"Daten-Chunks {_bytes(totals.get('chunkBytes', 0))} · "
            f"{totals.get('chunksRead', 0)} Chunkframes · "
            f"{totals.get('indexPages', 0)} Indexseiten · "
            f"{totals.get('cacheHits', 0)} Cachetreffer · "
            f"{totals.get('requests', 0)} HTTP-Range-Anfragen"
        )

    def _show_events(self, events):
        header = self.table.horizontalHeader()
        sort_column = header.sortIndicatorSection()
        sort_order = header.sortIndicatorOrder()
        was_at_top = self.table.verticalScrollBar().value() == 0
        top_item = self.table.item(self.table.rowAt(1), 0) if self.table.rowCount() else None
        top_sequence = top_item.data(Qt.ItemDataRole.UserRole) if top_item else None
        selected = self.table.currentItem()
        selected_seq = selected.data(Qt.ItemDataRole.UserRole) if selected else None
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(events))
        for row, event in enumerate(events):
            started = event.get("startedAt", 0)
            time_text = datetime.fromtimestamp(started / 1000).strftime("%H:%M:%S")
            op = _operation_label(event.get("op", ""))
            detail = event.get("detail") or ""
            if detail:
                op += f" · {detail}"
            state = event.get("state", "running")
            status = {
                "queued": "Wartet …",
                "running": "Läuft …",
                "success": "Fertig",
                "failed": "Fehler",
                "cancelled": "Abgebrochen",
            }.get(state, state)
            elapsed = event.get("elapsedMs", 0)
            if state == "running":
                elapsed = max(0, int(datetime.now().timestamp() * 1000 - started))
            reads = event.get("reads", {})
            result = event.get("error") or _result_text(event, reads)
            cells = [
                time_text,
                op,
                status,
                _duration(elapsed),
                _read_text(reads),
                result,
            ]
            sequence = event.get("sequence", 0)
            sort_values = [
                (started, sequence),
                (op.casefold(),),
                (_status_rank(state), status.casefold()),
                (elapsed,),
                (
                    int(reads.get("bytesRead", 0) or 0),
                    int(reads.get("chunksRead", 0) or 0),
                    int(reads.get("indexPages", 0) or 0),
                    int(reads.get("cacheHits", 0) or 0),
                    int(reads.get("requests", 0) or 0),
                ),
                (result.casefold(),),
            ]
            for column, value in enumerate(cells):
                item = _SortableItem(str(value))
                item.setData(Qt.ItemDataRole.UserRole, sequence)
                item.setData(_SortableItem.SORT_ROLE, sort_values[column])
                tooltip = event.get("error") or str(value)
                if column == 1:
                    tooltip = op
                if tooltip:
                    item.setToolTip(tooltip)
                self.table.setItem(row, column, item)
            if state == "failed":
                status_item = self.table.item(row, 2)
                font = status_item.font()
                font.setBold(True)
                status_item.setFont(font)
            if event.get("sequence") == selected_seq:
                self.table.selectRow(row)
        self.table.setSortingEnabled(True)
        self.table.sortItems(sort_column, sort_order)
        if selected_seq is not None:
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).data(Qt.ItemDataRole.UserRole) == selected_seq:
                    self.table.selectRow(row)
                    break
        if was_at_top:
            self.table.scrollToTop()
        elif top_sequence is not None:
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).data(Qt.ItemDataRole.UserRole) == top_sequence:
                    self.table.scrollToItem(
                        self.table.item(row, 0), QTableWidget.ScrollHint.PositionAtTop
                    )
                    break

    def show_info(self):
        """Show (or raise) a reusable explanation of activity columns and metrics."""
        if self._info_dialog is None:
            dialog = QDialog(self)
            dialog.setWindowTitle("Zugriffsdiagnose verstehen")
            dialog.setObjectName("ibxActivityInfo")
            dialog.setMinimumSize(560, 520)
            layout = QVBoxLayout(dialog)
            browser = QTextBrowser(dialog)
            browser.setObjectName("ibxActivityInfoText")
            browser.setOpenExternalLinks(False)
            browser.setHtml(_info_html())
            layout.addWidget(browser, 1)
            close = QPushButton("Schliessen", dialog)
            close.clicked.connect(dialog.close)
            layout.addWidget(close)
            dialog.finished.connect(lambda _result: self._forget_info_dialog(dialog))
            self._info_dialog = dialog
        self._info_dialog.show()
        self._info_dialog.raise_()
        self._info_dialog.activateWindow()
        return self._info_dialog

    def _forget_info_dialog(self, dialog):
        if self._info_dialog is dialog:
            self._info_dialog = None

    def shutdown(self):
        self._closing = True
        self.generation += 1
        self.dataset = None
        self._timer.stop()
        if self._info_dialog is not None:
            self._info_dialog.close()


def _operation_label(op):
    return {
        "open": "Datei öffnen",
        "describe": "Modellbeschreibung lesen",
        "catalog": "Layerkatalog lesen",
        "baskets": "Basketliste lesen",
        "query": "Kartenobjekte abfragen",
        "next": "Nächste Ergebnisseite lesen",
        "object": "Ein Objekt lesen",
        "related": "Beziehungen nachschlagen",
        "export": "Export (nur Java-CLI)",
        "closeCursor": "Abfrage schliessen",
    }.get(op, op or "IBX-Vorgang")


def _bytes(value):
    value = max(0, int(value or 0))
    units = ["B", "KiB", "MiB", "GiB"]
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.0f} {unit}" if unit == "B" else f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{value} B"


def _duration(value):
    value = max(0, int(value or 0))
    if value < 1000:
        return f"{value} ms"
    return f"{value / 1000:.1f} s"


def _status_rank(state):
    return {
        "queued": 0,
        "running": 1,
        "success": 2,
        "failed": 3,
        "cancelled": 4,
    }.get(state, 5)


def _info_html():
    return """
    <h2>Was zeigt die Zugriffsdiagnose?</h2>
    <p>Hier sehen Sie, welche Arbeit IBX für QGIS ausführt und wie viel dabei
    tatsächlich aus der Datei gelesen wird. Die Messwerte helfen, langsame
    Zugriffe zu verstehen; sie beschreiben keine fachlichen Dateninhalte.</p>

    <h3>Spalten</h3>
    <dl>
      <dt><b>Zeit</b></dt>
      <dd>Startzeit des Vorgangs. Neue Vorgänge erscheinen standardmässig oben.
      Durch Klick auf einen Spaltentitel können Sie nach dieser Spalte sortieren.</dd>
      <dt><b>Vorgang</b></dt>
      <dd>Welche Aufgabe IBX erledigt hat, zum Beispiel ein Objekt lesen,
      Kartenobjekte abfragen oder Beziehungen nachschlagen. Ergänzende Angaben
      wie Klasse oder FID sind technische Suchhinweise.</dd>
      <dt><b>Status</b></dt>
      <dd><b>Wartet</b> wartet auf die Lesesitzung; <b>Läuft</b> ist noch aktiv;
      <b>Fertig</b> wurde abgeschlossen. <b>Fehler</b> und <b>Abgebrochen</b>
      erklären, warum kein normales Ergebnis vorliegt.</dd>
      <dt><b>Dauer</b></dt>
      <dd>Vergangene Zeit vom Start bis zum Ende. Sie enthält auch die Zeit,
      in der der Vorgang auf exklusiven Zugriff auf dieselbe Lesesitzung wartet.</dd>
      <dt><b>Leseaufwand</b></dt>
      <dd>Bytes sind tatsächlich gelesene Dateidaten. Chunkframes sind
      Datenseiten, Indexseiten dienen der gezielten Suche. Cachetreffer bedeuten,
      dass benötigte Inhalte aus einem Speicher-Cache kamen; deshalb kann ein
      Vorgang wenige oder keine zusätzlichen Bytes lesen. HTTP-Ranges zählen
      angeforderte Teilbereiche einer HTTPS-Datei.</dd>
      <dt><b>Ergebnis / Meldung</b></dt>
      <dd>Bei Listen- und Abfragevorgängen die Anzahl der gelieferten Einträge
      sowie eine Aufteilung des Leseaufwands. Bei Fehlern steht hier die
      konkrete Fehlermeldung.</dd>
    </dl>

    <h3>Summen und Verlauf</h3>
    <p><b>Seit dem Öffnen</b> zeigt kumulative Summen seit dem Öffnen der Quelle,
    einschliesslich der Kosten für Öffnen und Beschreibung. Der Verlauf enthält
    dagegen nur die letzten 200 Vorgänge im Arbeitsspeicher. Er wird nicht auf
    Disk gespeichert; die Summen können daher grösser sein als die Summe der
    sichtbaren Zeilen.</p>
    <p>Bytes, Chunks und Indexseiten werden je Vorgang zusammengefasst.
    Die Tabelle listet nicht jeden einzelnen Dateibereich auf. HTTP-Range-Anfragen
    gibt es nur bei Quellen, die über HTTP(S) gelesen werden.</p>
    """


def _read_text(reads):
    parts = [_bytes(reads.get("bytesRead", 0))]
    chunks = reads.get("chunksRead", 0)
    index_pages = reads.get("indexPages", 0)
    cache_hits = reads.get("cacheHits", 0)
    ranges = reads.get("requests", 0)
    if chunks:
        parts.append(f"{chunks} Chunkframes")
    if index_pages:
        parts.append(f"{index_pages} Indexseiten")
    if cache_hits:
        parts.append(f"{cache_hits} Cachetreffer")
    if ranges:
        parts.append(f"{ranges} Ranges")
    return " · ".join(parts)


def _result_text(event, reads):
    count = event.get("resultCount")
    if count is not None:
        return (
            f"{count} Ergebnisse · Index {_bytes(reads.get('indexBytes', 0))} · "
            f"Daten-Chunks {_bytes(reads.get('chunkBytes', 0))}"
        )
    if event.get("state") == "queued":
        return "Wartet auf die Lesesitzung"
    if event.get("state") == "running":
        return "Lesezugriff läuft"
    if reads.get("bytesRead", 0) == 0:
        return "Keine zusätzlichen Dateibytes"
    return (
        f"Index {_bytes(reads.get('indexBytes', 0))} · "
        f"Daten-Chunks {_bytes(reads.get('chunkBytes', 0))}"
    )
