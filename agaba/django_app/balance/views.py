import os

from dadata import Dadata
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv

load_dotenv()


@login_required
def get_company_info(request):
    """Получение информации ДаДата по частичному ИНН."""
    query = request.GET.get('query')

    TOKEN_DADATA = os.getenv('TOKEN_DADATA')
    if not TOKEN_DADATA:
        return JsonResponse({"error": "API ключ DaData не настроен"}, status=500)

    dadata = Dadata(TOKEN_DADATA)

    try:
        result = dadata.suggest("party", query)
        if result:
            companies = [{
                "name": company["value"],
                "inn": company["data"]["inn"],
                "kpp": company["data"].get("kpp", ""),
                "address": company["data"]["address"].get("value", ""),
                "ogrn": company["data"].get("ogrn", ""),
            } for company in result]
            return JsonResponse({"companies": companies})
        else:
            return JsonResponse({"error": "Компании не найдены"}, status=404)
    except Exception as e:
        print(f"Ошибка при запросе к DaData: {e}")
        return JsonResponse({"error": str(e)}, status=500)
