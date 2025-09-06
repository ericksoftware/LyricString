 // Toggle dropdown menu
        document.querySelectorAll('.profile-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const dropdown = this.closest('.profile-dropdown');
                dropdown.classList.toggle('active');
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            document.querySelectorAll('.profile-dropdown').forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        });

        // Prevent dropdown from closing when clicking inside
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        });

        // Burger menu functionality
        const burgerMenu = document.getElementById('burgerMenu');
        const mobileNavMenu = document.getElementById('mobileNavMenu');

        burgerMenu.addEventListener('click', function() {
            this.classList.toggle('active');
            mobileNavMenu.classList.toggle('active');
            
            // Prevent body scrolling when menu is open
            if (mobileNavMenu.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = 'auto';
            }
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!burgerMenu.contains(e.target) && !mobileNavMenu.contains(e.target)) {
                burgerMenu.classList.remove('active');
                mobileNavMenu.classList.remove('active');
                document.body.style.overflow = 'auto';
            }
        });

        // Close mobile menu when a link is clicked
        mobileNavMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                burgerMenu.classList.remove('active');
                mobileNavMenu.classList.remove('active');
                document.body.style.overflow = 'auto';
            });
        });