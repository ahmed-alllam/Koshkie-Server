from rest_framework import serializers

from drivers.serializers import DriverProfileSerializer
from orders.models import OrderModel, OrderItemModel, Choice
from shops.models import ProductModel
from shops.serializers import ShopProfileSerializer, ProductSerializer, AddOnSerializer, OptionGroupSerializer
from users.models import UserAddressModel
from users.serializers import UserProfileSerializer, UserAddressSerializer


class ChoiceSerializer(serializers.ModelSerializer):
    option_group = OptionGroupSerializer(read_only=True)
    option_group_id = OptionGroupSerializer(write_only=True)
    choosed_option = serializers.IntegerField(read_only=True)
    choosed_option_id = serializers.IntegerField(write_only=True)

    # not done make validation for rely on

    class Meta:
        model = Choice
        fields = ('option_group', 'option_group_id', 'choosed_option', 'choosed_option_id')


class OrderItemSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(write_only=True,
                                                    queryset=ProductModel.objects.all())

    add_ons_ids = serializers.ListField(child=serializers.IntegerField(), required=False,
                                        write_only=True)
    add_ons = AddOnSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItemModel
        fields = ('product', 'product_id', 'quantity', 'choices', 'add_ons', 'add_ons_ids',
                  'special_request')
        extra_kwargs = {
            'special_request': {'required': False},
        }

    def validate(self, data):
        product = ProductModel.objects.get(id=data['product_id'])
        add_ons = data['add_ons_ids']
        choices = data['choices']

        for add_on in add_ons:
            if not product.add_ons.filter(sort=add_on).exists():
                raise serializers.ValidationError("add-on Doesn't Exist")

        for choice in choices:
            query = product.option_groups.filter(sort=choice['option_group_id'])
            if query.exists():
                option_group = query.get()
                if not option_group.options.filter(sort=choice['choosed_option_id']).exists():
                    raise serializers.ValidationError("option  Wrong")
            else:
                raise serializers.ValidationError("option group not found")

        return data


class OrderSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    driver = DriverProfileSerializer(read_only=True)
    shops = ShopProfileSerializer(many=True, read_only=True)
    items = OrderItemSerializer(many=True)
    shipping_address = UserAddressSerializer(read_only=True)
    shipping_address_id = serializers.PrimaryKeyRelatedField(write_only=True,
                                                             queryset=UserAddressModel.objects.all())

    class Meta:
        model = OrderModel
        fields = ('user', 'driver', 'shops', 'items', 'ordered_at', 'shipping_address',
                  'shipping_address_id', 'arrived', 'final_price', 'delivery_fee', 'vat')
        read_only_fields = ('user', 'driver', 'shops', 'ordered_at',
                            'arrived', 'final_price', 'delivery_fee', 'vat')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        items = list()

        for item in items_data:
            choices = item.pop('choices')
            add_ons_ids = item.pop('add_ons_ids')
            order_item = OrderItemModel(**item)
            for choice in choices:
                option_group = order_item.product.option_groups.get(sort=choice['option_group_id'])
                choosed_option = option_group.options.get(sort=choice['choosed_option_id'])
                Choice.objects.create(order_item=order_item, option_group=option_group,
                                      choosed_option=choosed_option)
            for add_on_id in add_ons_ids:
                add_on = order_item.product.add_ons.get(sort=add_on_id)
                order_item.add_ons.add(add_on)
            order_item.save()
            items.append(order_item)

        shops = set()
        delivery_fee = 0
        vat = 0
        subtotal = 0

        for item in items:
            shops.add(item.get_shop())
            vat += item.calculate_vat()
            subtotal += item.get_item_price()

        for shop in shops:
            delivery_fee += shop.delivery_fee

        final_price = subtotal + vat + delivery_fee

        order = OrderModel.objects.create(items=items, shops=list(shops), delivery_fee=delivery_fee,
                                          vat=vat, subtotal=subtotal,
                                          final_price=final_price, **validated_data)
        return order

    def update(self, instance, validated_data):
        if not instance.arrived:
            instance.arrived = validated_data.get('arrived', False)
            instance.save()
        return instance
