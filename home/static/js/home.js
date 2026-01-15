document.addEventListener("DOMContentLoaded", function () {
    const slideShow = document.querySelector('.slide-show');
    const listImage = document.querySelector('.list-images');
    const imgs = document.querySelectorAll('.list-images img');
    const btnLeft = document.querySelector('.btn-left');
    const btnRight = document.querySelector('.btn-right');
    const indexItems = document.querySelectorAll('.index-item');

    let current = 0;
    let imgWidth = slideShow.clientWidth;
    const totalImages = imgs.length;

    // Cập nhật lại kích thước ảnh khi thay đổi màn hình
    const updateSlideSize = () => {
        imgWidth = slideShow.clientWidth;
        listImage.style.width = `${imgWidth * totalImages}px`; // Đảm bảo chứa đủ ảnh
        imgs.forEach(img => img.style.width = `${imgWidth}px`); // Cập nhật lại từng ảnh
        updateSlidePosition(); // Giữ ảnh đúng vị trí khi resize
    };

    // Cập nhật vị trí của slide
    const updateSlidePosition = () => {
        listImage.style.transform = `translateX(-${current * imgWidth}px)`;
        document.querySelector('.selected').classList.remove('selected');
        indexItems[current].classList.add('selected');
    };

    // Chuyển sang ảnh tiếp theo
    const nextSlide = () => {
        current = (current + 1) % totalImages;
        updateSlidePosition();
    };

    // Quay lại ảnh trước
    const prevSlide = () => {
        current = (current - 1 + totalImages) % totalImages;
        updateSlidePosition();
    };

    // Tự động chuyển ảnh sau 3 giây
    let autoSlide = setInterval(nextSlide, 3000);

    // Sự kiện khi click vào nút điều hướng
    btnRight.addEventListener('click', () => {
        clearInterval(autoSlide);
        nextSlide();
        autoSlide = setInterval(nextSlide, 3000);
    });

    btnLeft.addEventListener('click', () => {
        clearInterval(autoSlide);
        prevSlide();
        autoSlide = setInterval(nextSlide, 3000);
    });

    // Khi thay đổi kích thước màn hình, cập nhật lại kích thước ảnh
    window.addEventListener('resize', updateSlideSize);

    // Khởi chạy cập nhật kích thước ảnh ban đầu
    updateSlideSize();
});
