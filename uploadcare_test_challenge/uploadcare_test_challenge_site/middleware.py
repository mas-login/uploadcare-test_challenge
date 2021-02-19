from .constants import EMOJIES
from .helpers import complete_request_text

from django.http import HttpResponse


class EmojiRotationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.n = -1

    def emoji_gen(self):
        self.n += 1

        return EMOJIES[self.n % len(EMOJIES)]

    def __call__(self, request):
        response = self.get_response(request)

        if request.META.get('HTTP_ACCEPT', '').split(',')[0] != 'text/html':
            return response

        if response.status_code != 200:
            return response

        content = complete_request_text(
            response.content,
            request.get_host(),
            self.emoji_gen
        )

        return HttpResponse(content)
