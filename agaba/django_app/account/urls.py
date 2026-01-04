# ПЕРЕХОД НА DRF
# from django.urls import path, include
# from . import views


# urlpatterns = [
#     # Аутентификация пользователя.
#     path('auth/', views.auth_user, name='auth_user'),
#     # Проверка OTP для аутентификации пользователя.
#     path('auth/verify/', views.auth_user_verify_otp, name='auth_user_verify_otp'),
#     # ЛИЧНЫЙ КАБИНЕТ ПОЛЬЗОВАТЕЛЯ
#     # Главная страница личного кабинета.
#     path('home/', views.home, name='home'),
#     # Товары продавца.
#     path('products/', views.products, name='products'),
#     # Реклама продавца.
#     path('advertisement/', views.advertisement, name='advertisement'),
#     # Заказы пользователя.
#     path('orders/', views.orders, name='orders'),
#     # Избранные товары пользователя.
#     path('favorites/', views.favorites, name='favorites'),
#     # Сравнение товаров пользователя.
#     path('compare/', views.compare, name='compare'),
#     # Редактирование профиля пользователя.
#     path('profile/', views.profile, name='profile'),
#     # Уведомления пользователя.
#     path('notifications/', views.notifications, name='notifications'),
#     # Баланс пользователя.
#     path('balance/', views.balance, name='balance'),
#     # Отзывы и вопросы пользователя.
#     path('reviews/', views.reviews_view, name='reviews'),
#     # Помощь пользователю.
#     path('help/', views.help, name='help'),
#     # Выход из аккаунта.
#     path('logout/', views.logout_view, name='logout'),
#     # УПРАВЛЕНИЕ ТОВАРАМИ
#     # Добавление нового товара. Шаг выбора категории.
#     path('add_new_product/', views.add_new_product, name='add_new_product'),
#     # Добавление нового товара. Шаг ввода информации о товаре.
#     path('add_new_product/<slug:category_slug>/',
#          views.add_new_product, name='add_new_product_step2'),
#     # Редактирование товара.
#     path('edit_product/<slug:slug>/',
#          views.edit_product, name='edit_product'),
#     # Удаление товара.
#     path('delete_product/<int:pk>/',
#          views.delete_product, name='delete_product'),
#     # Взаимодействие с компаниями пользователя.
#     path('manage_companies/', views.manage_companies, name='manage_companies'),
#     path('add_company/', views.add_company, name='add_company'),
#     path('edit_company/<int:company_id>/', views.edit_company, name='edit_company'),
#     path('remove_company/<int:company_id>/', views.remove_company, name='remove_company'),
    
#     # Добавление товаров в сравнение
#     path('add_to_comparison/<slug:slug>/', views.add_to_comparison, name='add_to_comparison'),
#     # Удаление товаров из сравнения
#     path('remove_from_comparison/<int:product_id>/', views.remove_from_comparison, name='remove_from_comparison'),
#     # Добавление товаров в избранное
#     path('add_to_favorites/<slug:slug>/', views.add_to_favorites, name='add_to_favorites'),
#     # Удаление товаров из избранного
#     path(
#         'remove_from_favorites/<int:product_id>/',
#          views.remove_from_favorites,
#          name='remove_from_favorites'
#     ),
# ]

# #     # Сообщения пользователя.
# #     path('messages/', views.messages_view, name='messages'),
# #     # Отдельное сообщение пользователя.
# #     path('message/<str:pk>/', views.message_item, name='message_item'),
# # path('save_product_image/', views.save_product_image, name='save_product_image'),
#     # Показ заказа.
#     # path('save_product_image/', views.save_product_image, name='save_product_image'),
# # path('<str:tab_id>/', views.account, name='account'),
#     # path('order/<str:order_number>/', views.order_card, name='order'),
#     # Авторизация продавца.
#     # path('auth_seller/', views.auth_seller, name='auth_seller'),
# # Изменение информации пользователя
#     # path('profile/', views.account, name='update_profile'),

urlpatterns = []
