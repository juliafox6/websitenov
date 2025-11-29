function checkPassword() {
    let value1 = document.getElementById('password').value;
    let value2 = document.getElementById('repeat').value;
    let but = document.querySelector('.button_login')
    let el = document.querySelector('.error');
    if (value1 !== value2) {
      el.classList.remove('up_hide');
      but.setAttribute('disabled', 'disabled');
    }
      else {
        el.classList.add('up_hide');
        but.removeAttribute('disabled');
      }
  }

  function checkFields() {
    // Личные данные (первая форма)
    let surname = document.getElementById('surname').value;
    let name = document.getElementById('name').value;
    let patron = document.getElementById('patron').value;
    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;
    let phone = document.getElementById('phone').value;

    // Тариф (вторая форма) - проверяем выбранную радиокнопку
    let selectedTariff = document.querySelector('input[name="tariff"]:checked');

    let but = document.querySelector('.button_login');
    let el = document.querySelector('.notification1');

    if (surname === '' || name === '' || patron === '' || email === '' ||
        password === '' || phone === '' || !selectedTariff) {
        el.classList.remove('up_hide');
        but.setAttribute('disabled', 'disabled');
    } else {
        el.classList.add('up_hide');
        but.removeAttribute('disabled');
    }
}

function submitAllForms() {
  // Собираем данные из обеих форм
  const formData = new FormData();

  // Данные из первой формы
  const personalForm = document.getElementById('personalForm');
  const personalData = new FormData(personalForm);
  for (let [key, value] of personalData) {
    formData.append(key, value);
  }

  // Данные из второй формы
  const tariffForm = document.getElementById('tariffForm');
  const tariffData = new FormData(tariffForm);
  for (let [key, value] of tariffData) {
    formData.append(key, value);
  }

  // Отправляем на сервер
  fetch('/signup.html', {
    method: 'POST',
    body: formData
  }).then(response => {
    window.location.href = response.url;
  });
}

  function toggleWalletForm(action) {
    const targetForm = document.querySelector(`.wallet-form[data-action="${action}"]`);
    if (!targetForm) {
      return;
    }
    document.querySelectorAll('.wallet-form').forEach((form) => {
      if (form !== targetForm) {
        form.classList.add('up_hide');
      }
    });
    targetForm.classList.toggle('up_hide');
    if (!targetForm.classList.contains('up_hide')) {
      const amountInput = targetForm.querySelector('input[name=\"amount\"]');
      if (amountInput) {
        amountInput.focus();
      }
    }
  }