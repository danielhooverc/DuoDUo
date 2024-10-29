document.addEventListener("DOMContentLoaded", function () {
    var form = document.querySelector("form");
    form.addEventListener("submit", function (event) {
        var userIDInput = document.getElementById("user_id").value;
        if (!userIDInput) {
            alert("Please enter your UserID.");
            event.preventDefault();  // 阻止表单提交
        }
    });
});

    // 在表单提交之前检查数值字段是否为空
    document.querySelector('form').addEventListener('submit', function(event) {
        // 获取三个数值字段的元素
        const totalReceivedQty = document.getElementById('total_received_qty');
        const totalOrderQty = document.getElementById('total_order_qty');
        const unitWeight = document.getElementById('unit_weight');
        
        // 如果字段为空，设置默认值为 0
        if (totalReceivedQty.value === '') {
            totalReceivedQty.value = 0;
        }
        if (totalOrderQty.value === '') {
            totalOrderQty.value = 0;
        }
        if (unitWeight.value === '') {
            unitWeight.value = 0;
        }
    });

 //新增和修改表单控件跳转；按回车键跳转下一个控件；按方向键上下控件跳转
 //其中part_no,sn和serial_number三个多行文本输入框; 不进行跳转
function initializeFormBehavior() {
    var inputs = document.querySelectorAll('input, select, textarea');
    var excludedTextareas = ['part_no', 'sn', 'tracking_number'];

    inputs.forEach(function (input) {
        input.addEventListener('keydown', function (event) {
            // 检查是否是需要特殊处理的 textarea
            var isExcludedTextarea = this.tagName.toLowerCase() === 'textarea' && 
                                     excludedTextareas.includes(this.id);

            if (event.key === 'Enter' && !isExcludedTextarea) {
                event.preventDefault();
                moveFocus(this, 'next');
            } else if (event.key === 'ArrowDown' && !isExcludedTextarea) {
                event.preventDefault();
                moveFocus(this, 'next');
            } else if (event.key === 'ArrowUp' && !isExcludedTextarea) {
                event.preventDefault();
                moveFocus(this, 'prev');
            }
        });
    });

    function moveFocus(currentElement, direction) {
        var focusableElements = Array.from(document.querySelectorAll('input, select, textarea, button'))
            .filter(el => el.tabIndex !== -1 && !el.disabled && el.type !== 'hidden');
        
        var currentIndex = focusableElements.indexOf(currentElement);
        var nextIndex;

        if (direction === 'next') {
            nextIndex = (currentIndex + 1) % focusableElements.length;
        } else {
            nextIndex = (currentIndex - 1 + focusableElements.length) % focusableElements.length;
        }

        focusableElements[nextIndex].focus();
    }
}

/*
 document.addEventListener("DOMContentLoaded", function() {
        var today = new Date().toISOString().split('T')[0]; // 获取当前日期并转换为 YYYY-MM-DD 格式
        document.getElementById("receiving_date").value = today; // 设置输入字段的值为当前日期
});
*/



// 在 DOM 加载完成后执行初始化函数
document.addEventListener('DOMContentLoaded', initializeFormBehavior);