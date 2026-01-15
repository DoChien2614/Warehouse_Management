from django.db import models
from django.contrib.auth.models import User


class Store(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class StoreUser(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'store')  # Một người dùng chỉ có một vai trò tại một store

    def __str__(self):
        return f"{self.user.username} - {self.store.name} - {self.role}"

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('ao', 'Áo'),
        ('quan', 'Quần'),
        ('vay', 'Váy'),
        ('tat', 'Tất'),
        ('giay', 'Giày'),
        ('dep', 'Dép'),
        ('mu', 'Mũ'),
        ('thatlung', 'Thắt Lưng'),
        ('khac', 'Khác'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    store_user = models.ForeignKey(StoreUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)  # Tên sản phẩm
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)  # Loại sản phẩm
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)  # Giá nhập
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)  # Giá bán
    description = models.TextField(blank=True, null=True)  # Mô tả sản phẩm
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)  # Ảnh sản phẩm
    date_added = models.DateTimeField(auto_now_add=True)  # Ngày thêm sản phẩm
    date_updated = models.DateTimeField(auto_now=True)  # Ngày cập nhật cuối
    supplier = models.CharField(max_length=255, blank=True, null=True)  # Tên nhà cung cấp
    quantity = models.IntegerField(default=0) # Thêm trường quantity

    def __str__(self):
        return self.name


class ImportReceipt(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    store_user = models.ForeignKey(StoreUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)  # Tên sản phẩm
    category = models.CharField(max_length=50)  # Loại sản phẩm
    quantity = models.IntegerField()  # Số lượng
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)  # Giá nhập
    date_added = models.DateTimeField(auto_now_add=True)  # Ngày nhập
    supplier = models.CharField(max_length=255, blank=True, null=True)  # Nhà cung cấp

    def __str__(self):
        return f"Phiếu nhập #{self.id} - {self.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('shipping', 'shipping'),
        ('completed', 'completed'),
        ('canceled', 'canceled'),
        ('returned', 'returned'),
    ]
    total_value = models.DecimalField(max_digits=30, decimal_places=2, default=0.00)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    store_user = models.ForeignKey(StoreUser, on_delete=models.CASCADE, null=True, blank=True)
    order_code = models.CharField(max_length=20, default="Unknown")  # Mã đơn hàng
    customer_name = models.CharField(max_length=100, default="Unknown")  # Tên khách hàng
    customer_address = models.CharField(max_length=100, default="Unknown")  # Địa chỉ khách hàng
    customer_phone = models.CharField(max_length=15, default="Unknown")
    order_date = models.DateField()  # Ngày đặt
    shipping_unit = models.CharField(max_length=100, default="Unknown")  # Đơn vị vận chuyển
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='shipping')  # Trạng thái đơn hàng
    products = models.ManyToManyField(Product, through='OrderProduct')  # Liên kết với sản phẩm qua bảng phụ OrderProduct

    def update_total_value(self):
        from django.db.models import Sum, F, DecimalField
        total = self.order_products.aggregate(
            total=Sum(F('quantity') * F('product__sale_price'), output_field=DecimalField())
        )['total'] or 0
        self.total_value = total
        self.save(update_fields=['total_value'])

    def __str__(self):
        return self.order_code


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    # warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True) # Xóa trường warehouse
    def __str__(self):
        return f"{self.product.name} x {self.quantity} ({self.order.order_code})" # Cập nhật __str__

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.update_total_value()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.order.update_total_value()