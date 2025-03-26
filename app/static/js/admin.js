document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('promptForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                if (key === 'categories' || key === 'tags') {
                    if (!data[key]) data[key] = [];
                    data[key].push(value);
                } else {
                    data[key] = value;
                }
            });

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value,
                        'Authorization': `Bearer ${document.cookie.split('; ').find(row => row.startsWith('access_token_cookie='))?.split('=')[1]}`
                    },
                    credentials: 'include',
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (result.success) {
                    window.location.href = '/admin/prompts';
                } else {
                    alert('Error: ' + JSON.stringify(result.errors));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while submitting the form');
            }
        });
    }
});
