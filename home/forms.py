from django import forms
import re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import Product, Order, Store, ImportReceipt
from datetime import datetime


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Tài Khoản', max_length=30)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Mật Khẩu', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Nhập Lại Mật Khẩu', widget=forms.PasswordInput())

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2 and password1:
                return password2
        raise forms.ValidationError("Mật khẩu không hợp lệ")

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError("Tên tài khoản có kí tự đặt biệt")
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError("Tài khoản đã tồn tại")

    def save(self):
        User.objects.create_user(username=self.cleaned_data['username'],
                                 email=self.cleaned_data['email'],
                                 password=self.cleaned_data['password1'])


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# Chiến
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['date_added', 'date_updated', 'store_user', 'store']  # Loại bỏ user và store
        labels = {
            'name': 'Tên sản phẩm',
            'category': 'Loại sản phẩm',
            'quantity': 'Số lượng',
            'image': 'Ảnh sản phẩm',
            'purchase_price': 'Giá nhập',
            'sale_price': 'Giá bán',
            'description': 'Mô tả',
            'supplier': 'Tên nhà cung cấp',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # user = kwargs.pop('user', None)  # Không cần pop user nữa
        super(ProductForm, self).__init__(*args, **kwargs)
        # if user:
        #     self.fields['warehouse'].queryset = Warehouse.objects.filter(user=user)  # Không cần filter warehouse nữa
        if 'date_added' in self.fields:
            self.fields['date_added'].disabled = True
        if 'last_updated' in self.fields:
            self.fields['last_updated'].disabled = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        # if hasattr(self, 'user') and self.user:  # Xử lý user ở view nếu cần
        #     instance.user = self.user
        # if hasattr(self, 'store') and self.store:  # Xử lý store ở view nếu cần
        #     instance.store = self.store
        if commit:
            instance.save()
        return instance


class ImportReceiptForm(forms.ModelForm):
    class Meta:
        model = ImportReceipt
        fields = ['name', 'category', 'quantity', 'sale_price', 'supplier']
        labels = {
            'name': 'Tên sản phẩm',
            'category': 'Loại sản phẩm',
            'quantity': 'Số lượng',
            'sale_price': 'Giá nhập',
            'supplier': 'Nhà cung cấp',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.store = kwargs.pop('store', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if self.store:
            instance.store = self.store
        if commit:
            instance.save()
        return instance


# Tùng
class OrderForm(forms.ModelForm):
    order_products = forms.CharField(label='Sản phẩm', required=True)
    order_date = forms.CharField(label='Ngày đặt (dd/mm/yyyy)')

    class Meta:
        model = Order
        fields = [
            'order_code', 'customer_name', 'customer_address', 'customer_phone',
            'order_date', 'shipping_unit', 'order_products'
        ]
        labels = {
            'order_code': 'Mã đơn hàng',
            'customer_name': 'Tên khách hàng',
            'customer_address': 'Địa chỉ khách hàng',
            'customer_phone': 'Số điện thoại khách hàng',
            'order_date': 'Ngày đặt',
            'shipping_unit': 'Đơn vị vận chuyển',
            'order_products': 'Sản phẩm trong đơn hàng'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.store = kwargs.pop('store', None)
        super(OrderForm, self).__init__(*args, **kwargs)

    def clean_order_date(self):
        date_str = self.cleaned_data['order_date']
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
            return date_obj
        except ValueError:
            raise forms.ValidationError('Ngày không hợp lệ. Vui lòng nhập đúng định dạng dd/mm/yyyy.')

    def save(self, commit=True):
        order = super().save(commit=False)
        if self.user:
            order.user = self.user
        if self.store:
            order.store = self.store
        if commit:
            order.save()
        return order

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Tên cửa hàng', 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(StoreForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


class AddEmployeeForm(forms.Form):
    username = forms.CharField(max_length=100, label='Tên đăng nhập')
    role = forms.ChoiceField(choices=[('staff', 'Nhân viên'), ('manager', 'Quản lý')], label='Vai trò')