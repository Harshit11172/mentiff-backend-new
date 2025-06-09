import json
from django.http import JsonResponse
from django.views import View
from django.conf import settings

class DataView(View):
    def get(self, request):
        # Load JSON data from the file
        with open(settings.BASE_DIR / 'static_files/university.json') as univ_file:
            data = json.load(univ_file)
        return JsonResponse(data, safe=False)


class FAQDataView(View):
    def get(self, request):
        # Load JSON data from the file
        with open(settings.BASE_DIR / 'static_files/FAQ.json') as faq_file:
            data = json.load(faq_file)
        return JsonResponse(data, safe=False)