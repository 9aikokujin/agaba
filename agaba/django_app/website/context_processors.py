# from datetime import datetime
# from .models import Category


# def catalog_root_categories(request):
#     # groups = Group.objects.prefetch_related('subgroups').all()
#     root_categories = Category.objects.filter(parent__isnull=True).order_by('id')
#     return {'root_categories': root_categories}