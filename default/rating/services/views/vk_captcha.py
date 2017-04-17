from django.views.generic import TemplateView
from django.template import RequestContext
from rating.services.datastore.managers import VkRatingStatusManager, VkRatingStatus, ServiceStatus


class VkCaptchaView(TemplateView):
    template_name = 'services/vk/captcha_view.html'

    def get_context_data(self, **kwargs):
        context = super(VkCaptchaView, self).get_context_data(**kwargs)
        state = VkRatingStatusManager.last_state_by_status(ServiceStatus.IN_PROGRESS)
        if state and state.captcha_required and not state.captcha_value:
            context['captcha_required'] = True
            context['captcha_img'] = state.captcha_img
            context['captcha_sid'] = state.captcha_sid
            context['state_id'] = state.key.id()
        return context

    def post(self, request, *args, **kwargs):

        if 'captcha_text_id' in request.POST and 'captcha_sid_hidden_id' in request.POST and 'state_hidden_id' in request.POST:
            try:
                captcha_text = request.POST['captcha_text_id']
                captcha_sid = request.POST['captcha_sid_hidden_id']
                state_id = long(request.POST['state_hidden_id'])
                state = VkRatingStatus.get_by_id(state_id)
                if state and str(state.captcha_sid) == captcha_sid and captcha_text:
                    state.captcha_value = captcha_text.strip()
                    state.put()
            except ValueError:
                pass

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
