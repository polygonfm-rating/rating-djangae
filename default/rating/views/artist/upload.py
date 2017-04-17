from django.views.generic import TemplateView
from django.shortcuts import render_to_response
from django.template import RequestContext
from rating.forms import UploadArtistsForm
from rating.utils import file
from rating.models import Artist
from django.http import HttpResponseRedirect


class UploadArtistsView(TemplateView):
    template_name = 'admin/rating/artist/upload.html'

    def get_context_data(self, **kwargs):
        context = super(UploadArtistsView, self).get_context_data(**kwargs)
        context['form'] = UploadArtistsForm(self.request.POST,
                                            self.request.FILES) if self.request.POST else UploadArtistsForm()
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if context['form'].is_valid() and 'artists_file' in request.FILES:
            f = request.FILES['artists_file']
            is_russian = 'russian_checkbox' in request.POST
            lines = file.read_uploaded_file(f)
            Artist.objects.create_from_file(lines, is_russian)
            return HttpResponseRedirect('/admin/rating/artist/')

        return render_to_response(self.template_name, context=context,
                                  context_instance=RequestContext(request))
