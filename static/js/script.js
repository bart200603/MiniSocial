// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const messageInput = document.getElementById('message-input');
    const submitBtn = document.getElementById('submit-btn');
    const messagesContainer = document.getElementById('messages-container');

    // 提交消息的函数
    function submitMessage() {
        const message = messageInput.value.trim();
        
        // 检查消息是否为空
        if (!message) {
            alert('请输入消息内容！');
            return;
        }
        
        // 创建FormData对象用于发送数据
        const formData = new FormData();
        formData.append('msg', message);
        
        // 发送POST请求到后端
        fetch('/submit', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                // 清空输入框
                messageInput.value = '';
                // 立即获取最新消息
                fetchMessages();
            } else {
                alert('消息发送失败，请重试！');
            }
        })
        .catch(error => {
            console.error('提交消息出错:', error);
            alert('网络错误，请检查连接！');
        });
    }

    // 获取所有消息的函数
    function fetchMessages() {
        fetch('/messages')
        .then(response => response.json())
        .then(messages => {
            // 清空消息容器
            messagesContainer.innerHTML = '';
            
            // 如果没有消息
            if (messages.length === 0) {
                const emptyMessage = document.createElement('div');
                emptyMessage.className = 'message-item';
                emptyMessage.textContent = '暂无消息，快来发送第一条吧！';
                messagesContainer.appendChild(emptyMessage);
                return;
            }
            
            // 遍历消息并添加到页面
            messages.forEach((msg, index) => {
                const messageElement = document.createElement('div');
                messageElement.className = 'message-item';
                messageElement.textContent = `${index + 1}. ${msg}`;
                messagesContainer.appendChild(messageElement);
            });
        })
        .catch(error => {
            console.error('获取消息出错:', error);
        });
    }

    // 点击提交按钮时提交消息
    submitBtn.addEventListener('click', submitMessage);
    
    // 按下回车键时提交消息
    messageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            submitMessage();
        }
    });

    // 页面加载时获取消息
    fetchMessages();
    
    // 每隔5秒自动获取最新消息
    setInterval(fetchMessages, 5000);
}); 