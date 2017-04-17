from django.views.generic import View
from django.http import HttpResponse
from rating.artists_file import ArtistsWriter
from rating.services.datastore import rating_artist


class DownloadArtistsView(View):

    def get(self, request, *args, **kwargs):
        russian = request.path.endswith('rus')
        file_name = "artists_rus" if russian else "artists_foreign"

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}.txt"'.format(file_name)

        writer = ArtistsWriter(response)
        writer.write(rating_artist.query().filter(rating_artist.is_russian == russian).
                     order(rating_artist.name).fetch(batch_size=1000))

        return response
