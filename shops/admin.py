#  Copyright (c) Code Written and Tested by Ahmed Emad in 06/01/2020, 16:28

from django.contrib import admin

# Register your models here.
from shops.models import (ShopProfileModel, ProductModel,
                          ShopReviewModel, ProductReviewModel, ProductGroupModel, ShopAddressModel, AddOn,
                          OptionGroupModel, OptionModel, RelyOn)

admin.site.register(ShopProfileModel)
admin.site.register(ProductGroupModel)
admin.site.register(ProductModel)
admin.site.register(OptionGroupModel)
admin.site.register(OptionModel)
admin.site.register(AddOn)
admin.site.register(RelyOn)
admin.site.register(ShopAddressModel)
admin.site.register(ShopReviewModel)
admin.site.register(ProductReviewModel)
