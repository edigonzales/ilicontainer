import uuid
from qgis.PyQt import sip
from qgis.core import QgsTask, QgsApplication


class RequestTask(QgsTask):
    def __init__(self, title, work, success, failure, rpc=None):
        super().__init__(title, QgsTask.Flag.CanCancel)
        self.request_id = str(uuid.uuid4())
        self.work, self.success, self.failure, self.rpc = work, success, failure, rpc
        self.result, self.error = None, None

    def run(self):
        try:
            self.result = self.work(self.request_id)
            return not self.isCanceled()
        except Exception as e:
            self.error = str(e)
            return False

    def finished(self, success):
        if self.isCanceled():
            return
        if success:
            self.success(self.result)
        else:
            self.failure(self.error or "Die Anfrage ist fehlgeschlagen.")

    def cancel(self):
        if sip.isdeleted(self):
            return
        super().cancel()
        if self.rpc:
            # Cancellation is a separate short worker request, never a GUI network call.
            rpc, target = self.rpc, self.request_id
            task = RequestTask(
                "IBX-Anfrage abbrechen",
                lambda _: rpc.call("cancel", target=target),
                lambda _: None,
                lambda _: None,
            )
            QgsApplication.taskManager().addTask(task)


def submit(title, work, success, failure, rpc=None):
    task = RequestTask(title, work, success, failure, rpc)
    QgsApplication.taskManager().addTask(task)
    return task
