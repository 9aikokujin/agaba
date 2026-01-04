# import hashlib
# import random
# import string
# from unidecode import unidecode
# from django.http import JsonResponse
# from django.shortcuts import render
# # # Для склонения слов
# # import pymorphy2


# def calculate_file_hash(file):
#     hash_md5 = hashlib.md5()
#     for chunk in file.chunks():
#         hash_md5.update(chunk)
#     return hash_md5.hexdigest()


# def generate_random_string(length=5):
#     return ''.join(
#         random.choices(string.digits, k=length))


# def generate_translit_link(name):
#     # Transliterate the name to ASCII
#     transliterated_name = unidecode(name)
#     # Replace spaces with underscores and remove non-alphanumeric characters
#     link = ''.join(
#         c if c.isalnum() or c == '-' else '-' for c in transliterated_name)
#     # Convert to lowercase
#     link = link.lower() + ' ' + generate_random_string()
#     return link


# def render_or_main_fetch(
#         request, render_template_name, context, fetch_template_name):

#     if request.GET.get('fetch'):
#         main_content = render(
#             request, fetch_template_name, context).content.decode('utf-8')
#         return JsonResponse({'main_content': main_content,
#                              'browser_tab_name': context['browser_tab_name']})

#     return render(request, render_template_name, context)


# # MORPH = pymorphy2.MorphAnalyzer()


# # def pluralize_ru(number, word):
# #     """Склоняет слово в зависимости от числа."""
# #     parsed_word = MORPH.parse(word)[0]
# #     return parsed_word.make_agree_with_number(number).word