function toggleEditImportForm(id, product_name, category, quantity, price, supplier) {
    document.getElementById('edit-receipt-product-name').value = product_name;
    document.getElementById('edit-receipt-category').value = category;
    document.getElementById('edit-receipt-quantity').value = quantity;
    document.getElementById('edit-receipt-price').value = price;
    document.getElementById('edit-receipt-supplier').value = supplier;

    const form = document.getElementById('edit-form'); // Sửa đúng ID của <form>
    form.action = `/edit_import/${id}/`;

    document.getElementById('edit-product-form').style.display = 'block';
    document.getElementById('edit-overlay').style.display = 'block';
}

function closeEditImportForm() {
    document.getElementById('edit-product-form').style.display = 'none';
    document.getElementById('edit-overlay').style.display = 'none';
}
