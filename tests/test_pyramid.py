import pytest
from pyramid.request import Request
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid import testing
from webtest import TestApp

from jinja2_fragments.pyramid import render_block


def simple_page(request: Request) -> Response:
    template = 'templates/simple_page.html.jinja2'
    if request.GET.get('only_content', '').lower() != 'false':
        return Response(render_block(template, 'content', {}))
    else:
        return render_to_response(template, {})


@pytest.fixture(scope='session')
def pyramid_app():
    config = testing.setUp(settings={
        'jinja2.trim_blocks': True,
        'jinja2.lstrip_blocks': True,
    })
    config.include('pyramid_jinja2')
    # simple
    config.add_route('simple-page', '/simple_page')
    config.add_view(simple_page, route_name='simple-page')
    app = config.make_wsgi_app()
    yield TestApp(app)
    testing.tearDown()


@pytest.mark.parametrize(
    "only_content, html_name",
    [
        (False, "simple_page.html"),
        (True, "simple_page_content.html")
    ]
)
def test_pyramid_simple_page(pyramid_app, get_html, only_content, html_name):
    response = pyramid_app.get("/simple_page", params={"only_content": only_content})

    expected = get_html(html_name)
    assert response.text == expected
