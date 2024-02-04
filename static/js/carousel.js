let selectedIndex = null; // Start with no selected index

function selectDot(index) {
    const dots = document.querySelectorAll('.dot');
    const contentBoxes = document.querySelectorAll('.content-box');

    // If the same dot is clicked, deselect it
    if (selectedIndex === index) {
        contentBoxes[index].style.transform = 'scale(1)';
        dots[index].classList.remove('active');
        selectedIndex = null; // Deselect
    } else {
        // Remove 'active' class from all dots and reset transform on all content boxes
        dots.forEach(dot => dot.classList.remove('active'));
        contentBoxes.forEach(box => box.style.transform = 'scale(1)');

        // Add 'active' class to the selected dot and enlarge the corresponding content box
        dots[index].classList.add('active');
        contentBoxes[index].style.transform = 'scale(1.5)';
        contentBoxes[index].style.transition = 'transform 0.3s ease'; // Smooth transition for scaling

        // Update the selected index
        selectedIndex = index;
    }
}

function setupDotListeners() {
    const dots = document.querySelectorAll('.dot');
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => selectDot(index));
    });
}

// Initialize the carousel when the document is fully loaded
window.onload = setupDotListeners;
