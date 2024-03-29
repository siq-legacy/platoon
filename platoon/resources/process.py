from mesh.standard import *
from scheme import *

from platoon.resources.executor import Endpoint

class Process(Resource):
    """A process."""

    name = 'process'
    version = 1

    class schema:
        id = UUID(nonnull=True, oncreate=True, operators='equal')
        queue_id = Token(nonempty=True, operators='equal')
        tag = Text(nonempty=True, operators='equal')
        timeout = Integer()
        status = Enumeration('pending initiating executing completed failed aborted timedout',
            oncreate=False, operators='equal in')
        input = Field()
        output = Field(oncreate=False)
        progress = Field(oncreate=False)
        state = Field(oncreate=False)
        started = DateTime(utc=True, readonly=True)
        ended = DateTime(utc=True, readonly=True)

    class update(Resource.update):
        schema = {
            'status': Enumeration('aborted completed failed'),
            'output': Field(),
            'progress': Field(),
            'state': Field(),
        }

InitiationResponse = Structure({
    'status': Enumeration('executing completed failed', nonempty=True),
    'progress': Field(),
    'output': Field(),
    'state': Field(),
}, nonnull=True)
