from __future__ import annotations
import typing
from functools import partial

try:
    from pyramid.csrf import get_csrf_token
    from pyramid.events import BeforeRender
    from pyramid.renderers import get_renderer, RendererHelper
    from pyramid.request import Request
    from pyramid.path import caller_package
    from pyramid.response import Response
    from pyramid.threadlocal import get_current_registry
    from pyramid.util import hide_attrs
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install pyramid before using jinja2_fragments.pyramid"
    ) from e

try:
    from pyramid_jinja2 import Jinja2TemplateRenderer, IJinja2Environment
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install pyramid_jinja2 before using jinja2_fragments.pyramid"
    ) from e

import jinja2_fragments


class BlockRendererHelper(RendererHelper):

    def render_block(self, block_name, value, system_values, request=None):
        template = self.renderer.template_loader()
        try:
            block_render_func = template.blocks[block_name]
        except KeyError:
            raise jinja2_fragments.BlockNotFoundError(
                f"Block '{block_name}' not found on template '{self.name}'"
            )
        if system_values is None:
            system_values = {
                'view': None,
                'renderer_name': self.name,  # b/c
                'renderer_info': self,
                'context': getattr(request, 'context', None),
                'request': request,
                'req': request,
                'get_csrf_token': partial(get_csrf_token, request),
            }

        system_values = BeforeRender(system_values, value)

        registry = self.registry
        registry.notify(system_values)

        ctx = template.new_context(system_values | value)
        try:
            return ''.join(block_render_func(ctx))  # type: ignore
        except Exception:
            environment = registry.queryUtility(IJinja2Environment, name='.jinja2')
            environment.handle_exception()


def render_block(renderer_name: str, block_name: str, value: dict, request: Request | None = None, package: str | None = None) -> str:
    """Renders a template's block using the registered renderer with the given context.

    Assumes the Jinja2 renderer was registered via ``pyramid_jinja2``
    (to get the Jinja2 environment).

    :param template_name: the name of the template where to find the block to be
        rendered (can be an asset specification)
    :param block_name: the name of the block to be rendered
    :param context: the variables that should be available in the context of the block
    """
    try:
        registry = request.registry
    except AttributeError:
        registry = None
    if package is None:
        package = caller_package()
    helper = BlockRendererHelper(
        name=renderer_name, package=package, registry=registry
    )
    if not isinstance(helper.renderer, Jinja2TemplateRenderer):
        raise RuntimeError("Block rendering requires 'pyramid_jinja2.JinjaTemplateRenderer'")

    with hide_attrs(request, 'response'):
        result = helper.render_block(block_name, value, None, request=request)

    return result


def render_block_to_response(template_name: str, block_name: str, **context: typing.Any) -> Response:
    pass

