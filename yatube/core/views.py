from django.shortcuts import render
from http.client import INTERNAL_SERVER_ERROR, FORBIDDEN, NOT_FOUND


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию;
    # выводить её в шаблон пользовательской страницы 404 мы не станем
    template = 'core/404.html'
    return render(
        request,
        template,
        {'path': request.path},
        NOT_FOUND
    )


def csrf_failure(request, reason=''):
    template = 'core/403csrf.html'
    return render(
        request,
        template
    )


def page_forbidden(request, exception):
    template = 'core/403.html'
    return render(
        request,
        template,
        {'path': request.path},
        FORBIDDEN
    )


def page_internal_server_error(request):
    template = 'core/500.html'
    return render(
        request,
        template,
        {'path': request.path},
        INTERNAL_SERVER_ERROR
    )
