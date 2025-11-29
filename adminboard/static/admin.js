// Форма добавления книги
document.addEventListener('DOMContentLoaded', function() {
    const addBookForm = document.getElementById('addBookForm');
    const addBookMessage = document.getElementById('addBookMessage');

    if (addBookForm) {
        addBookForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(addBookForm);

            try {
                const response = await fetch('/api/add_book', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    showMessage(addBookMessage, data.message, 'success');
                    addBookForm.reset();
                } else {
                    showMessage(addBookMessage, data.message, 'error');
                }
            } catch (error) {
                showMessage(addBookMessage, 'Ошибка при добавлении книги', 'error');
            }
        });
    }

    // Форма поиска пользователя
    const searchUserForm = document.getElementById('searchUserForm');
    const searchResults = document.getElementById('searchResults');

    if (searchUserForm) {
        searchUserForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(searchUserForm);

            try {
                const response = await fetch('/api/search_users', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    displaySearchResults(data.users);
                } else {
                    searchResults.innerHTML = `<p class="message error">${data.message}</p>`;
                }
            } catch (error) {
                searchResults.innerHTML = '<p class="message error">Ошибка при поиске пользователей</p>';
            }
        });
    }

    // Форма смены тарифа
    const changeTariffForm = document.getElementById('changeTariffForm');
    const tariffMessage = document.getElementById('tariffMessage');

    if (changeTariffForm) {
        changeTariffForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(changeTariffForm);

            try {
                const response = await fetch('/api/change_tariff', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    showMessage(tariffMessage, data.message, 'success');
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    showMessage(tariffMessage, data.message, 'error');
                }
            } catch (error) {
                showMessage(tariffMessage, 'Ошибка при изменении тарифа', 'error');
            }
        });
    }

    // Форма смены статуса заказа
    const statusForms = document.querySelectorAll('.status-form');
    const statusMessage = document.getElementById('statusMessage');

    statusForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const orderId = form.dataset.orderId;
            const status = form.querySelector('.status-select').value;

            const formData = new FormData();
            formData.append('order_id', orderId);
            formData.append('status', status);

            try {
                const response = await fetch('/api/change_order_status', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    showMessage(statusMessage, data.message, 'success');
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    showMessage(statusMessage, data.message, 'error');
                }
            } catch (error) {
                showMessage(statusMessage, 'Ошибка при изменении статуса заказа', 'error');
            }
        });
    });

    // Форма оценки повреждений
    const assessDamageForm = document.getElementById('assessDamageForm');
    const damageMessage = document.getElementById('damageMessage');

    if (assessDamageForm) {
        assessDamageForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            if (!confirm('Вы уверены, что хотите закрыть заказ? Это действие вернет депозит пользователю (минус штрафы за повреждения).')) {
                return;
            }

            const formData = new FormData(assessDamageForm);

            try {
                const response = await fetch('/api/assess_damage', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    showMessage(damageMessage, data.message, 'success');
                    setTimeout(() => {
                        window.location.href = '/user/' + data.user_id;
                    }, 2000);
                } else {
                    showMessage(damageMessage, data.message, 'error');
                }
            } catch (error) {
                showMessage(damageMessage, 'Ошибка при обработке заказа', 'error');
            }
        });
    }
});

function showMessage(element, message, type) {
    if (!element) return;

    element.textContent = message;
    element.className = `message show ${type}`;

    setTimeout(() => {
        element.classList.remove('show');
    }, 5000);
}

function displaySearchResults(users) {
    const searchResults = document.getElementById('searchResults');

    if (!users || users.length === 0) {
        searchResults.innerHTML = '<p class="message error">Пользователи не найдены</p>';
        return;
    }

    let html = '<div class="search-results-list">';

    users.forEach(user => {
        html += `
            <div class="user-card">
                <h3>${user.last_name} ${user.first_name} ${user.patronymic || ''}</h3>
                <p><strong>Email:</strong> ${user.email}</p>
                <p><strong>Телефон:</strong> ${user.phone}</p>
                <p><strong>Депозит:</strong> ${user.deposit.toFixed(2)} у.е.</p>
                <p><strong>Тариф:</strong> ${user.tariff_name}</p>
                <a href="/user/${user.id}" class="btn btn-primary">Управление</a>
            </div>
        `;
    });

    html += '</div>';
    searchResults.innerHTML = html;
}

