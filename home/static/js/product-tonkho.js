document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("product-form");
    const overlay = document.getElementById("overlay");
    const button = document.getElementById("show-form-btn");

    button.addEventListener("click", function () {
        form.style.display = "block";
        overlay.style.display = "block";
    });

    overlay.addEventListener("click", function () {
        form.style.display = "none";
        overlay.style.display = "none";
    });
});

function toggleForm() {
    var form = document.getElementById("product-form");
    var overlay = document.getElementById("overlay");
    
    if (form.style.display === "block") {
        form.style.display = "none";
        overlay.style.display = "none";
    } else {
        form.style.display = "block";
        overlay.style.display = "block";
    }
}

// Cập nhật ảnh sản phẩm khi sửa
function toggleEditForm(productId, productName, categoryId, quantity, imageUrl, purchasePrice, salePrice, description, supplierName) {
    
    console.log("productId:", productId);
    console.log("productName:", productName);
    console.log("categoryId:", categoryId);
    console.log("quantity:", quantity);
    console.log("imageUrl:", imageUrl);
    console.log("purchasePrice:", purchasePrice);
    console.log("salePrice:", salePrice);
    console.log("description:", description);
    console.log("supplierName:", supplierName);


    document.getElementById("edit-product-form").style.display = "block";
    document.getElementById("edit-overlay").style.display = "block";

    document.getElementById("edit-product-name").value = productName;
    document.getElementById("edit-category").value = categoryId;
    document.getElementById("edit-quantity").value = quantity;

    // ✅ Kiểm tra và cập nhật ảnh
    let imageElement = document.getElementById("current-product-image");
    if (imageUrl && imageUrl !== "None") {
        imageElement.src = imageUrl;
        imageElement.style.display = "block";
    } else {
        imageElement.style.display = "none";
    }

    document.getElementById("edit-purchase-price").value = purchasePrice;
    document.getElementById("edit-sale-price").value = salePrice;
    document.getElementById("edit-description").value = description;
    document.getElementById("edit-supplier-name").value = supplierName;


    // Cập nhật action của form
    document.getElementById("edit-form").action = `/product/edit/${productId}/`;
}


// Gửi form sửa sản phẩm với ảnh
document.getElementById("edit-form").addEventListener("submit", function (event) {
    event.preventDefault(); // Ngăn load lại trang

    let formData = new FormData(this);
    let actionUrl = this.action; // Lấy URL từ form

    fetch(actionUrl, {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // ✅ Ẩn form sửa
            document.getElementById("edit-product-form").style.display = "none";
            document.getElementById("edit-overlay").style.display = "none";
            location.reload(); // 🔄 Reload để cập nhật dữ liệu
        } else {
            alert("Lỗi: " + JSON.stringify(data.errors));
        }
    })
    .catch(error => console.error("Lỗi:", error));
});



// Hàm đóng form sửa sản phẩm
function closeEditForm() {
    document.getElementById("edit-product-form").style.display = "none";
    document.getElementById("edit-overlay").style.display = "none";
}


// Tìm kiếm
function searchProducts() {
    const keyword = document.getElementById('searchInput').value;
  
    fetch(`/tonkho/search/?keyword=` + encodeURIComponent(keyword))
      .then(response => response.text())
      .then(html => {
        document.getElementById('productBody').innerHTML = html;
      });
}


// Nút phân loại
function toggleDropdown() {
    document.querySelector('.dropdown').classList.toggle('show');
}

// Đóng dropdown nếu click ra ngoài
function closeDropdownOnClickOutside(e) {
    const dropdown = document.querySelector('.dropdown');
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('show');
    }
}

window.addEventListener('click', closeDropdownOnClickOutside);
