#  Copyright (c) Code Written and Tested by Ahmed Emad in 31/01/2020, 17:29

from django.contrib import admin

# Register your models here.
from shops.models import (ShopProfileModel, ProductModel,
                          ShopReviewModel, ProductReviewModel, ProductGroupModel, ShopAddressModel, AddOnModel,
                          OptionGroupModel, OptionModel, RelyOn, ShopTagsModel)

admin.site.register(ShopProfileModel)
admin.site.register(ShopTagsModel)
admin.site.register(ProductGroupModel)
admin.site.register(ProductModel)
admin.site.register(OptionGroupModel)
admin.site.register(OptionModel)
admin.site.register(AddOnModel)
admin.site.register(RelyOn)
admin.site.register(ShopAddressModel)
admin.site.register(ShopReviewModel)
admin.site.register(ProductReviewModel)
