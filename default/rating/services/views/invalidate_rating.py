from django.views.generic import TemplateView
from django.template import RequestContext
from rating.services.sources.total.formula import TotalRatingFormula


class InvalidateRatingView(TemplateView):
    template_name = 'services/total/invalidate_rating_view.html'

    def get_context_data(self, **kwargs):
        context = super(InvalidateRatingView, self).get_context_data(**kwargs)
        context['formula_version'] = TotalRatingFormula().version
        return context

    def post(self, request, *args, **kwargs):

        TotalRatingFormula().increase_version()

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
