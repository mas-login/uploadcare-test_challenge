from .constants import SOURCE_HOST
from .helpers import fetch


def index(request):
    return fetch(request, SOURCE_HOST)
