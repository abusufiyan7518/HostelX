// // Side Navigation JavaScript

// document.addEventListener('DOMContentLoaded', function() {
//     // Get all navigation items
//     const navItems = document.querySelectorAll('.nav-item');
//     const contentBody = document.getElementById('content-body');
    
//     // Content for each section
//     const contentData = {
//         'dashboard': {
//             title: 'Dashboard',
//             content: 'Welcome to your dashboard. Here you can see an overview of your hostel room details, fees, complaints, and more.'
//         },
//         'view-room': {
//             title: 'View Room Details',
//             content: 'Room Details: View your current room allocation, hostel information, bed number, roommates, and facilities.'
//         },
//         'request-transfer': {
//             title: 'Request Room Transfer',
//             content: 'Request a room transfer if you need to change your current room allocation. Fill out the transfer request form.'
//         },
//         'fee-status': {
//             title: 'View Fee Status',
//             content: 'Check your hostel fee payment status, due dates, and pending amounts.'
//         },
//         'pay-fees': {
//             title: 'Pay Fees',
//             content: 'Make online payment for your hostel fees. Multiple payment options available.'
//         },
//         'download-receipt': {
//             title: 'Download Fee Receipt',
//             content: 'Download your fee payment receipts for your records.'
//         },
//         'raise-complaint': {
//             title: 'Raise Complaint',
//             content: 'Submit a new complaint regarding hostel facilities, room issues, or any other concerns.'
//         },
//         'my-complaints': {
//             title: 'My Complaints',
//             content: 'View all your submitted complaints and their current status.'
//         },
//         'visitor-entry': {
//             title: 'Visitor Entry Registrations',
//             content: 'Register visitor entry requests and view approved/pending visitor requests.'
//         },
//         'notifications': {
//             title: 'Notifications',
//             content: 'View all your notifications, announcements, and important updates.'
//         },
//         'profile': {
//             title: 'Profile',
//             content: 'View and edit your profile information, contact details, and preferences.'
//         },
//         'logout': {
//             title: 'Logout',
//             content: 'You have been logged out successfully. Thank you for using the Student Dashboard.'
//         }
//     };
    
//     // Add click event to each nav item
//     navItems.forEach(item => {
//         item.addEventListener('click', function(e) {
//             e.preventDefault();
            
//             // Remove active class from all items
//             navItems.forEach(navItem => {
//                 navItem.classList.remove('active');
//             });
            
//             // Add active class to clicked item
//             this.classList.add('active');
            
//             // Get the href and extract the section name
//             const link = this.querySelector('.nav-link');
//             const href = link.getAttribute('href');
//             const section = href.replace('#', '');
            
//             // Update content
//             updateContent(section);
            
//             // Add animation to content
//             contentBody.style.opacity = '0';
//             contentBody.style.transform = 'translateY(20px)';
            
//             setTimeout(() => {
//                 contentBody.style.transition = 'all 0.4s ease';
//                 contentBody.style.opacity = '1';
//                 contentBody.style.transform = 'translateY(0)';
//             }, 100);
//         });
//     });
    
//     // Function to update content based on selected section
//     function updateContent(section) {
//         const data = contentData[section] || contentData['dashboard'];
        
//         contentBody.innerHTML = `
//             <div class="demo-card">
//                 <h2>${data.title}</h2>
//                 <p>${data.content}</p>
//                 <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #4A90E2;">
//                     <strong>Note:</strong> This is a demo navigation. In a real application, this would load the actual ${data.title.toLowerCase()} interface.
//                 </div>
//             </div>
//         `;
//     }
    
//     // Add hover effect sound (optional - can be enabled)
//     navItems.forEach(item => {
//         item.addEventListener('mouseenter', function() {
//             this.style.transform = 'translateX(4px)';
//         });
        
//         item.addEventListener('mouseleave', function() {
//             this.style.transform = 'translateX(0)';
//         });
//     });
    
//     // Console log for navigation tracking
//     navItems.forEach(item => {
//         item.addEventListener('click', function() {
//             const link = this.querySelector('.nav-link span');
//             console.log(`Navigated to: ${link.textContent}`);
//         });
//     });
    
//     // Initialize with dashboard content
//     updateContent('dashboard');
// });


document.addEventListener('DOMContentLoaded', function() {

    const navItems = document.querySelectorAll('.nav-item');

    // Active class handle
    navItems.forEach(item => {
        item.addEventListener('click', function() {

            // Remove active from all
            navItems.forEach(i => i.classList.remove('active'));

            // Add active to clicked
            this.classList.add('active');

        });
    });

    // Auto set active based on current URL
    const currentPath = window.location.pathname;

    navItems.forEach(item => {
        const link = item.querySelector('.nav-link');
        if (link.getAttribute('href') === currentPath) {
            item.classList.add('active');
        }
    });

});