    // Form submission
    document.getElementById('genreForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        
        try {
            const url = '{% if is_edit %}{% url "update_genre_api" genre.id %}{% else %}{% url "add_genre_api" %}{% endif %}';
            const response = await fetch(url, {
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
                document.getElementById('errorMessage').textContent = data.error || `An error occurred while {% if is_edit %}updating{% else %}adding{% endif %} the genre.`;
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