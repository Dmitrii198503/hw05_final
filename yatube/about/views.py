from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """About author page"""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """About technologies page"""
    template_name = 'about/tech.html'
