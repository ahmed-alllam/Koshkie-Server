from django.contrib import admin

# Register your models here.
from shops.models import (ShopProfileModel, ProductModel,
                          ShopReviewModel, ProductReviewModel, ProductGroupModel, ShopAddressModel, AddOn)

admin.site.register(ShopProfileModel)
admin.site.register(ProductModel)
admin.site.register(ShopReviewModel)
admin.site.register(ProductReviewModel)
admin.site.register(ProductGroupModel)
admin.site.register(AddOn)
admin.site.register(ShopAddressModel)
