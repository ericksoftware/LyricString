    // Form submission
    document.getElementById('addUserForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validate passwords match
        const password = document.getElementById('password').value;
        const passwordConfirm = document.getElementById('password_confirm').value;
        
        if (password !== passwordConfirm) {
            document.getElementById('errorMessage').textContent = 'Passwords do not match.';
            document.getElementById('errorModal').style.display = 'block';
            return;
        }
        
        const formData = new FormData(e.target);
        
        try {
            const response = await fetch('{% url "add_user_api" %}', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('successModal').style.display = 'block';
            } else {
                document.getElementById('errorMessage').textContent = data.error || 'An error occurred while adding the user.';
                document.getElementById('errorModal').style.display = 'block';
            }
        } catch (error) {
            document.getElementById('errorMessage').textContent = 'Network error. Please try again.';
            document.getElementById('errorModal').style.display = 'block';
        }
    });

    // Modal functions
    function closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    // Close modal when clicking outside of it
    window.onclick = function(event) {
        const modals = ['successModal', 'errorModal'];
        modals.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (event.target === modal) {
                closeModal(modalId);
            }
        });
    }