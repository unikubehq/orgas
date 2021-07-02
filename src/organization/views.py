from django.http import JsonResponse
from django.views.generic import UpdateView

from .models import Organization


class AvatarUploadView(UpdateView):
    model = Organization
    fields = ["avatar_image"]

    def form_valid(self, form):
        """
        override this to simply return a status 200 instead of a redirect to success url
        """
        # TODO check permission
        self.object = form.save()
        # todo thumbnail this image right here?
        return JsonResponse(data={"url": self.object.avatar_image.url}, status=200)
