from django.contrib import admin

# Register your models here.
from shops.models import (ShopProfileModel, ProductModel,
                          ShopReviewModel, ProductReviewModel, ProductCategoryModel, ShopAddressModel, AddOn)

admin.site.register(ShopProfileModel)
admin.site.register(ProductModel)
admin.site.register(ShopReviewModel)
admin.site.register(ProductReviewModel)
admin.site.register(ProductCategoryModel)
admin.site.register(AddOn)
admin.site.register(ShopAddressModel)
