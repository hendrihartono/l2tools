const body = document.querySelector('body');
const btn = document.querySelector('.btn');
const icon = document.querySelector('.btn__icon');

// Store dark mode status in localStorage
function store(value) {
  localStorage.setItem('darkmode', value);
}

// Load the dark mode status from localStorage
function load() {
  const darkmode = localStorage.getItem('darkmode');
  if (!darkmode) {
    store(false);
    icon.classList.add('fa-sun');
  } else if (darkmode == 'true') { // Dark mode activated
    body.classList.add('darkmode');
    icon.classList.add('fa-moon');
  } else { // Dark mode disabled
    icon.classList.add('fa-sun');
  }
}

load();

btn.addEventListener('click', () => {
  body.classList.toggle('darkmode');
  icon.classList.add('animated');

  // Save dark mode status
  store(body.classList.contains('darkmode'));

  if (body.classList.contains('darkmode')) {
    icon.classList.remove('fa-sun');
    icon.classList.add('fa-moon');
  } else {
    icon.classList.remove('fa-moon');
    icon.classList.add('fa-sun');
  }

  setTimeout(() => {
    icon.classList.remove('animated');
  }, 500)
});
