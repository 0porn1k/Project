async function deleteUserRequest() {
    const input = document.getElementById('delete-input').value;
    const statusP = document.getElementById('delete-status');
    const token = localStorage.getItem('token');

    if (!input) return;

    // Определяем, что ввел админ: ID (число) или Username (строка)
    const isId = !isNaN(input);
    const param = isId ? `user_id=${input}` : `username=${input}`;

    try {
        const response = await fetch(`http://127.0.0.1:8000/admin/delete-user?${param}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const data = await response.json();

        statusP.classList.remove('hidden');
        if (response.ok) {
            statusP.innerText = data.detail;
            statusP.className = "mt-4 text-sm text-green-400";
            document.getElementById('delete-input').value = ''; // Очищаем поле
        } else {
            statusP.innerText = "Ошибка: " + data.detail;
            statusP.className = "mt-4 text-sm text-red-400";
        }
    } catch (error) {
        console.error("Ошибка при удалении:", error);
    }
}
        // Загрузка данных админа
        async function loadAdminData() {
            const token = localStorage.getItem('token');
            if (!token) {
                window.location.href = 'index.html';
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:8000/admin/stats', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    document.getElementById('admin-content').classList.remove('hidden');
                    document.getElementById('admin-data').innerText = data.stats || data.detail;
                } else if (response.status === 403) {
                    document.getElementById('error-msg').classList.remove('hidden');
                    setTimeout(() => window.location.href = 'profile.html', 3000);
                } else {
                    window.location.href = 'index.html';
                }
            } catch (error) {
                console.error("Ошибка сети:", error);
            }
        }


        async function deleteUserRequest() {
            const input = document.getElementById('delete-input').value.trim();
            const statusP = document.getElementById('delete-status');
            const token = localStorage.getItem('token');

            if (!input) {
                alert("Пожалуйста, введите логин или ID");
                return;
            }

            // Проверяем, введено число (ID) или текст (Username)
            const isId = !isNaN(input) && input.length > 0;
            const param = isId ? `user_id=${input}` : `username=${input}`;

            try {
                const response = await fetch(`http://127.0.0.1:8000/admin/delete-user?${param}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                const data = await response.json();
                
                statusP.classList.remove('hidden');
                statusP.innerText = data.detail;
                
                if (response.ok) {
                    statusP.className = "mt-4 text-sm text-green-400 font-bold";
                    document.getElementById('delete-input').value = ''; // Очистка поля
                } else {
                    statusP.className = "mt-4 text-sm text-red-400 font-bold";
                }
            } catch (error) {
                statusP.classList.remove('hidden');
                statusP.innerText = "Ошибка сервера";
                statusP.className = "mt-4 text-sm text-red-400";
            }
        }
async function addPurchaseRequest() {
    const itemName = document.getElementById('purchase-item').value.trim();
    const price = document.getElementById('purchase-price').value;
    const statusP = document.getElementById('purchase-status');
    const token = localStorage.getItem('token');

    if (!itemName || !price) {
        alert("Заполните название и цену!");
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/admin/add-purchases', {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            // Твой бэкенд ожидает два объекта: user_data и purchase_data
            body: JSON.stringify({
                user_data: { username: "dummy", password: "dummy_password" }, 
                purchase_data: { item_name: itemName, price: parseFloat(price) }
            })
        });

        const data = await response.json();
        statusP.classList.remove('hidden');

        if (response.ok) {
            statusP.innerText = `Успешно: ${data.message} (ID: ${data.purchase_id})`;
            statusP.className = "mt-4 text-sm text-green-400 font-bold";
            document.getElementById('purchase-item').value = '';
            document.getElementById('purchase-price').value = '';
        } else {
            statusP.innerText = "Ошибка: " + (data.detail || "Не удалось добавить");
            statusP.className = "mt-4 text-sm text-red-400 font-bold";
        }
    } catch (error) {
        console.error("Ошибка сети:", error);
        statusP.innerText = "Ошибка соединения с сервером";
        statusP.classList.remove('hidden');
        statusP.className = "mt-4 text-sm text-red-400";
    }
}
        function logout() {
            localStorage.removeItem('token');
            window.location.href = 'index.html';
        }

        // Запуск проверки при загрузке
        loadAdminData();
