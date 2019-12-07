from django.contrib import admin

# Register your models here.
from shops.models import (ShopProfileModel, ProductModel,
                          ShopReview, ProductReview)

admin.site.register(ShopProfileModel)
admin.site.register(ProductModel)
admin.site.register(ShopReview)
admin.site.register(ProductReview)
