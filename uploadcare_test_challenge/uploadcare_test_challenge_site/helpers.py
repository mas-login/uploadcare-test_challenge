from requests import get
from bs4 import BeautifulSoup, element, dammit
from re import split
from urllib.parse import urlparse, urlunparse

from django.http import HttpResponse

from .constants import SOURCE_HOST, WORD_DELIMITER_PATTERN, WORD_LENGTH


def complete_content(content, emoji_gen):
    parts = split(WORD_DELIMITER_PATTERN, content)
    processed_parts = [
        (part + emoji_gen() if len(part) == WORD_LENGTH else part)
        for part in parts
    ]

    return ''.join(processed_parts)


def complete_tag(tag, host, emoji_gen):
    processable = {
        'a': 'href',
        'img': 'src',
        'use': 'xlink:href',
    }

    if tag.name in processable and processable.get(tag.name) in tag.attrs:
        url_parts = urlparse(tag.attrs[processable[tag.name]])
        if url_parts.netloc == SOURCE_HOST:
            url_parts = url_parts._replace(scheme='http', netloc=host)
            tag.attrs[processable[tag.name]] = url_parts.geturl()

    for content in tag.contents:
        if isinstance(content, element.Comment):
            content.replaceWith('<!--{}-->'.format(content))

    for content in tag.contents:
        if tag.name in ['script', 'style']:
            continue

        if isinstance(content, element.NavigableString):
            content.replaceWith(complete_content(content, emoji_gen))


def has_ancestor(el, search_name):
    while el:
        if getattr(el, 'name', None) == search_name:
            return True

        el = getattr(el, 'parent', None)

    return False


def custom_formatter(el):
    if has_ancestor(el, 'pre'):
        return dammit.EntitySubstitution.substitute_html(el)
    else:
        return str(el)


def complete_request_text(text, host, emoji_gen):
    soup = BeautifulSoup(text, features='lxml')
    for tag in soup.findAll(None, recursive=True):
        complete_tag(tag, host, emoji_gen)

    return str(soup.prettify(formatter=custom_formatter))


def fetch(request, source_host):
    url = urlunparse(('https', source_host, request.path, None, None, None))

    try:
        resp = get(url)
    except Exception as e:
        return HttpResponse(
            'Exception ({}) was raised '.format(str(e)),
            status=500
        )

    if resp.status_code != 200:
        return HttpResponse(resp.text, status=resp.status_code)

    if request.META.get('HTTP_ACCEPT', '').split(',')[0] != 'text/html':
        return HttpResponse(
            resp.content,
            content_type=resp.headers['Content-Type']
        )

    return HttpResponse(resp.text)
