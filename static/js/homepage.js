let slideIndex = 1;
const slides = document.getElementsByClassName("slide");
const dots = document.getElementsByClassName("dot");

$('.slider-container').on('touchstart', function(event) {
  const xClick = event.originalEvent.touches[0].pageX;

  $(this).on('touchmove', function(event) {
    const xMove = event.originalEvent.touches[0].pageX;
    const sensitivityInPx = 8;

    if (Math.floor(xClick - xMove) > sensitivityInPx) {
      plusSlides(1);
      $(this).off('touchmove');
    } 
    else if (Math.floor(xClick - xMove) < -sensitivityInPx) {
      plusSlides(-1);
      $(this).off('touchmove');
    }
  });
});

// Function to show a specific slide
function showSlides(n) {
  if (n > slides.length) {
    slideIndex = 1;
  }
  if (n < 1) {
    slideIndex = slides.length;
  }

  // Hide all slides
  for (let i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }

  // Remove the "active" class from all dots
  for (let i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }

  // Display the current slide and mark its corresponding dot as active
  slides[slideIndex - 1].style.display = "block";
  dots[slideIndex - 1].className += " active";
}

// Function to advance to the next slide
function plusSlides(n) {
  showSlides((slideIndex += n));
}

// Function to navigate to a specific slide
function currentSlide(n) {
  showSlides((slideIndex = n));
}

// Automatically advance to the next slide every 3 seconds (3000 milliseconds)
setInterval(function () {
  plusSlides(1);
}, 5000);

// Initialize the slider
showSlides(slideIndex);