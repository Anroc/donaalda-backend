from django.contrib.staticfiles import views as static
from rest_framework import views
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework_swagger.renderers import SwaggerUIRenderer, BaseRenderer


class StaticSwaggerRenderer(BaseRenderer):
    media_type = 'application/openapi+json'
    charset = None
    format="openapi"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return static.serve(renderer_context['request'], 'swagger.json')


@api_view()
@permission_classes([])
@renderer_classes([StaticSwaggerRenderer, SwaggerUIRenderer])
def static_swagger_view(request, *args, **kwargs):
    # This is a bit of a hack. Neither our own StaticSwaggerRenderer nor the
    # SwaggerUIRenderer use the actual response they get in any way. However the
    # SwaggerUI requires that the actual schema is available at the same url
    # with a different format argument which is why we need the
    # StaticSwaggerRenderer as an actual Renderer class.
    return response.Response(None)
