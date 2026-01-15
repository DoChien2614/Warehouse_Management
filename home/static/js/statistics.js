document.addEventListener('DOMContentLoaded', function () {
    // Ẩn tất cả các phần thống kê khi trang tải xong
    document.querySelectorAll('.stat-section').forEach(function (section) {
        section.style.display = 'none';
    });

    // Gắn sự kiện click cho từng nút chính
    document.getElementById('btn-import').addEventListener('click', function () {
        toggleSection('import-stats');
    });

    document.getElementById('btn-export').addEventListener('click', function () {
        toggleSection('export-stats');
    });

    document.getElementById('btn-revenue').addEventListener('click', function () {
        toggleSection('revenue-stats');
    });

    // Hàm hiển thị/ẩn phần thống kê
    function toggleSection(sectionId) {
        const sections = document.querySelectorAll('.stat-section');

        sections.forEach(function (section) {
            if (section.id === sectionId) {
                const isHidden = section.style.display === 'none' || section.style.display === '';
                section.style.display = isHidden ? 'block' : 'none';

                if (isHidden) {
                    section.classList.add('fade-in');
                    setTimeout(function () {
                        section.classList.remove('fade-in');
                    }, 500);
                }
            } else {
                section.style.display = 'none';
            }
        });
    }

    // Xử lý click để ẩn/hiện nội dung con (ví dụ tiêu đề nhỏ <h5>)
    const toggleSections = document.querySelectorAll('.toggle-section');

    toggleSections.forEach(function (section) {
        section.addEventListener('click', function () {
            const content = this.nextElementSibling;

            if (content) {
                const isHidden = content.style.display === 'none' || content.style.display === '';
                content.style.display = isHidden ? 'block' : 'none';
            }
        });
    });
});
