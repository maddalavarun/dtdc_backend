import './style.css'

document.addEventListener('DOMContentLoaded', () => {
  // --- Mobile Menu Toggle ---
  const mobileBtn = document.getElementById('mobile-btn');
  const navMenu = document.getElementById('nav-menu');

  if (mobileBtn && navMenu) {
    mobileBtn.addEventListener('click', () => {
      navMenu.classList.toggle('active');
    });
  }

  // --- Smooth Scroll for Anchor Links ---
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      // Close mobile menu if open
      if (navMenu && navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
      }
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth'
        });
      }
    });
  });

  // --- Scroll Reveal Animation ---
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
      }
    });
  }, {
    threshold: 0.1
  });

  document.querySelectorAll('.hidden').forEach((el) => observer.observe(el));

  // --- 3D Tilt Effect for Service Cards ---
  const cards = document.querySelectorAll('.service-card');
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -10; // Max 10deg rotation
      const rotateY = ((x - centerX) / centerX) * 10;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
    });
  });

  // --- Tracking Input Logic ---
  const trackBtn = document.getElementById('hero-track-btn');
  const trackInput = document.getElementById('hero-track-input');
  const resultContainer = document.getElementById('tracking-result');

  if (trackBtn && trackInput) {
    trackBtn.addEventListener('click', () => {
      handleTracking();
    });

    trackInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        handleTracking();
      }
    });
  }

  async function handleTracking() {
    const trackingId = trackInput.value.trim();
    if (!trackingId) return;

    if (!resultContainer) return;

    // UI Reset
    trackBtn.disabled = true;
    resultContainer.classList.add('active'); // Show container
    resultContainer.innerHTML = '<div class="loader active"></div>';

    try {
      const response = await fetch('/api/track', { // Use proxy
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tracking_id: trackingId })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      updateTrackingUI(data);

    } catch (error) {
      console.error(error);
      resultContainer.innerHTML = `
            <div class="tracking-error">
                Unable to fetch details.<br>
                <span style="font-size: 0.8rem; font-weight: 400; color: #666;">Please check the ID or try again later.</span>
            </div>`;
    } finally {
      trackBtn.disabled = false;
    }
  }

  function updateTrackingUI(data) {
    // Basic validation of data structure
    if (!data || !data.status) {
      resultContainer.innerHTML = `<div class="tracking-error">No status found for this ID.</div>`;
      return;
    }

    const { status, latest_event } = data;
    // Fallback if latest_event is missing but status exists
    const activity = latest_event?.activity || status;
    const location = latest_event?.location || '';
    const timestamp = latest_event?.timestamp || '';

    resultContainer.innerHTML = `
          <div>
              <span class="tracking-status-badge">${status}</span>
              <div class="tracking-event">
                  <div class="tracking-location">${activity}</div>
                  ${location ? `<div style="font-size: 0.95rem; margin-bottom:4px; color: #444;">${location}</div>` : ''}
                  ${timestamp ? `<div class="tracking-event-time">${timestamp}</div>` : ''}
              </div>
          </div>
      `;
  }
});
