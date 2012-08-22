from datetime import datetime

from scheme.timezone import UTC
from spire.core import Component, Dependency
from spire.schema import SchemaDependency
from spire.support.daemon import Daemon
from spire.support.logs import LogHelper
from spire.support.threadpool import ThreadPool

from platoon.idler import Idler
from platoon.models import *

log = LogHelper('platoon')

class TaskPackage(object):
    def __init__(self, task, session):
        self.session = session
        self.task = task

    def __repr__(self):
        return repr(self.task)

    def __call__(self):
        session = self.session
        task = session.merge(self.task)

        try:
            task.execute(session)
        except Exception:
            session.rollback()
            log('exception', '%s raised uncaught exception', repr(task))
        else:
            session.commit()

class TaskQueue(Component, Daemon):
    """An asynchronous task queue."""

    idler = Dependency(Idler)
    schema = SchemaDependency('platoon')
    threads = Dependency(ThreadPool)

    def run(self):
        idler = self.idler
        schema = self.schema
        threads = self.threads

        session = schema.session
        pending = session.query(ScheduledTask).with_lockmode('update').filter(
            ScheduledTask.status.in_(('pending', 'retrying')))

        while True:
            idler.idle()
            try:
                tasks = list(pending.filter(ScheduledTask.occurrence <= datetime.now(UTC)))
                if not tasks:
                    continue

                for task in tasks:
                    task.status = 'executing'

                session.commit()
                for task in tasks:
                    log('info', 'processing %s', repr(task))
                    package = TaskPackage(task, schema.get_session(True))
                    threads.enqueue(package)
            finally:
                session.close()
