/* ==========================================================================
   HK FITNESS — main.js
   Progressive enhancement only. The page is complete without it.
   ========================================================================== */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;

  /* ---------------------------------------------------------------------- */
  /* Header: solid background after leaving the hero, plus scroll progress.  */
  /* ---------------------------------------------------------------------- */
  var header = doc.querySelector('[data-header]');
  var progressBar = doc.querySelector('[data-scroll-progress]');
  var scrollTicking = false;

  function onScrollFrame() {
    var y = window.scrollY || window.pageYOffset;
    var docHeight = doc.documentElement.scrollHeight - window.innerHeight;

    if (header) {
      if (y > 24) {
        header.setAttribute('data-scrolled', '');
      } else {
        header.removeAttribute('data-scrolled');
      }
    }

    if (progressBar) {
      var ratio = docHeight > 0 ? Math.min(y / docHeight, 1) : 0;
      progressBar.style.transform = 'scaleX(' + ratio.toFixed(4) + ')';
    }

    scrollTicking = false;
  }

  function requestScrollFrame() {
    if (!scrollTicking) {
      scrollTicking = true;
      window.requestAnimationFrame(onScrollFrame);
    }
  }

  window.addEventListener('scroll', requestScrollFrame, { passive: true });
  window.addEventListener('resize', requestScrollFrame, { passive: true });
  onScrollFrame();

  /* ---------------------------------------------------------------------- */
  /* Mobile menu                                                            */
  /* ---------------------------------------------------------------------- */
  var navToggle = doc.querySelector('[data-nav-toggle]');
  var mobileMenu = doc.querySelector('[data-mobile-menu]');
  var closeTimer = null;

  function menuIsOpen() {
    return mobileMenu && mobileMenu.classList.contains('is-open');
  }

  function openMenu() {
    if (!mobileMenu || !navToggle) return;
    window.clearTimeout(closeTimer);
    mobileMenu.hidden = false;
    // Force a frame so the closing transition does not interfere.
    void mobileMenu.offsetHeight;
    mobileMenu.classList.add('is-open');
    navToggle.setAttribute('aria-expanded', 'true');
    navToggle.setAttribute('aria-label', 'Close menu');
    if (header) header.setAttribute('data-menu', 'open');
    root.classList.add('is-locked');
    var firstLink = mobileMenu.querySelector('a');
    if (firstLink) firstLink.focus({ preventScroll: true });
  }

  function closeMenu(returnFocus) {
    if (!mobileMenu || !navToggle) return;
    mobileMenu.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Open menu');
    if (header) header.removeAttribute('data-menu');
    root.classList.remove('is-locked');

    closeTimer = window.setTimeout(function () {
      if (!menuIsOpen()) mobileMenu.hidden = true;
    }, 360);

    if (returnFocus) navToggle.focus({ preventScroll: true });
  }

  if (navToggle && mobileMenu) {
    navToggle.addEventListener('click', function () {
      if (menuIsOpen()) {
        closeMenu(true);
      } else {
        openMenu();
      }
    });

    mobileMenu.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeMenu(false);
    });

    doc.addEventListener('keydown', function (event) {
      if (!menuIsOpen()) return;

      if (event.key === 'Escape') {
        event.preventDefault();
        closeMenu(true);
        return;
      }

      if (event.key !== 'Tab') return;

      // Keep focus inside the overlay while it is open.
      var focusables = mobileMenu.querySelectorAll('a[href], button:not([disabled])');
      if (!focusables.length) return;
      var first = focusables[0];
      var last = focusables[focusables.length - 1];

      if (event.shiftKey && doc.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && doc.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });

    window.addEventListener('resize', function () {
      if (menuIsOpen() && window.innerWidth > 900) closeMenu(false);
    });
  }

  /* ---------------------------------------------------------------------- */
  /* Scroll reveals                                                         */
  /* ---------------------------------------------------------------------- */
  var revealItems = Array.prototype.slice.call(doc.querySelectorAll('[data-reveal]'));

  function revealAll() {
    revealItems.forEach(function (el) {
      el.classList.add('is-in');
    });
  }

  if (!('IntersectionObserver' in window)) {
    revealAll();
  } else {
    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-in');
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.12 }
    );

    revealItems.forEach(function (el) {
      revealObserver.observe(el);
    });

    // Failsafe: never leave content invisible if the observer never fires.
    window.setTimeout(function () {
      if (!doc.querySelector('[data-reveal].is-in')) revealAll();
    }, 2500);
  }

  /* ---------------------------------------------------------------------- */
  /* Before / after comparison                                              */
  /* ---------------------------------------------------------------------- */
  var compare = doc.querySelector('[data-compare]');

  if (compare) {
    var compareRange = compare.querySelector('[data-compare-range]');
    var beforeImage = compare.querySelector('[data-compare-before]');
    var afterImage = compare.querySelector('[data-compare-after]');
    var caption = doc.querySelector('[data-compare-caption]');
    var cards = Array.prototype.slice.call(doc.querySelectorAll('[data-result]'));

    function setPosition(value) {
      var clamped = Math.max(0, Math.min(100, Number(value) || 0));
      compare.style.setProperty('--pos', String(clamped));
    }

    if (compareRange) {
      compareRange.addEventListener('input', function () {
        setPosition(compareRange.value);
      });
      setPosition(compareRange.value);
    }

    // Pointer drag is handled natively by the range input, which covers the
    // frame. Keyboard users keep arrow keys, Home and End.

    function selectResult(card) {
      if (!card || !beforeImage || !afterImage) return;

      cards.forEach(function (item) {
        var active = item === card;
        item.classList.toggle('is-active', active);
        item.setAttribute('aria-pressed', active ? 'true' : 'false');
      });

      var before = card.getAttribute('data-before');
      var after = card.getAttribute('data-after');
      var label = card.getAttribute('data-caption') || '';

      beforeImage.src = before;
      afterImage.src = after;
      beforeImage.alt = 'Client before training — ' + label.replace('Client transformation — ', '');
      afterImage.alt = 'The same client after training — ' + label.replace('Client transformation — ', '');

      if (caption) caption.textContent = label;

      if (compareRange) {
        compareRange.value = '50';
        setPosition(50);
      }
    }

    cards.forEach(function (card) {
      card.addEventListener('click', function () {
        selectResult(card);
      });
    });
  }

  /* ---------------------------------------------------------------------- */
  /* Studio carousel                                                        */
  /* ---------------------------------------------------------------------- */
  var slider = doc.querySelector('[data-slider]');

  if (slider) {
    var sliderTrack = slider.querySelector('[data-slider-track]');
    var slides = sliderTrack
      ? Array.prototype.slice.call(sliderTrack.querySelectorAll('[data-slide]'))
      : [];
    var sliderPrev = slider.querySelector('[data-slider-prev]');
    var sliderNext = slider.querySelector('[data-slider-next]');
    var sliderIndex = slider.querySelector('[data-slider-index]');
    var sliderTotal = slider.querySelector('[data-slider-total]');
    var sliderCaption = slider.querySelector('[data-slider-caption]');
    var sliderFrame = false;
    var sliderCurrent = 0;
    var sliderAuto = false;
    var sliderAutoTimer = 0;

    function pad(value) {
      return (value < 10 ? '0' : '') + value;
    }

    // `offsetLeft` is measured against the nearest positioned ancestor, which
    // the track is not, so positions are taken from the two client rects.
    function slideOffset(index) {
      var slide = slides[index];
      if (!slide) return 0;
      return (
        slide.getBoundingClientRect().left -
        sliderTrack.getBoundingClientRect().left +
        sliderTrack.scrollLeft
      );
    }

    function maxScroll() {
      return Math.max(0, sliderTrack.scrollWidth - sliderTrack.clientWidth);
    }

    function paintSlider() {
      var active = slides[sliderCurrent];

      if (sliderIndex) sliderIndex.textContent = pad(sliderCurrent + 1);
      if (sliderPrev) sliderPrev.disabled = sliderCurrent === 0;
      if (sliderNext) sliderNext.disabled = sliderCurrent === slides.length - 1;

      slides.forEach(function (slide, index) {
        slide.classList.toggle('is-active', index === sliderCurrent);
      });

      var caption = active ? active.getAttribute('data-caption') : '';
      if (sliderCaption && caption) sliderCaption.textContent = caption;
    }

    // Selecting a photograph also walks the strip along, but only as far as
    // the scroll range allows. The last photographs share the final position,
    // so the highlight and caption keep moving across them.
    function selectSlide(index) {
      sliderCurrent = Math.max(0, Math.min(slides.length - 1, index));
      paintSlider();

      sliderAuto = true;
      window.clearTimeout(sliderAutoTimer);
      sliderAutoTimer = window.setTimeout(function () {
        sliderAuto = false;
      }, 700);

      sliderTrack.scrollTo({
        left: Math.min(slideOffset(sliderCurrent), maxScroll()),
        behavior: 'smooth'
      });
    }

    // A wheel, drag or scrollbar hands control back to the scroll position.
    function releaseSlider() {
      window.clearTimeout(sliderAutoTimer);
      sliderAuto = false;
    }

    function syncSlider() {
      sliderFrame = false;
      if (sliderAuto) return;

      var closest = 0;
      var shortest = Infinity;

      slides.forEach(function (slide, index) {
        var distance = Math.abs(slideOffset(index) - sliderTrack.scrollLeft);
        if (distance < shortest) {
          shortest = distance;
          closest = index;
        }
      });

      if (closest === sliderCurrent) return;
      sliderCurrent = closest;
      paintSlider();
    }

    if (sliderTrack && slides.length) {
      if (sliderTotal) sliderTotal.textContent = pad(slides.length);

      if (sliderPrev) {
        sliderPrev.addEventListener('click', function () {
          selectSlide(sliderCurrent - 1);
        });
      }

      if (sliderNext) {
        sliderNext.addEventListener('click', function () {
          selectSlide(sliderCurrent + 1);
        });
      }

      // Arrow keys step one photograph at a time instead of the browser's
      // default nudge, which the snap points would round back anyway.
      sliderTrack.addEventListener('keydown', function (event) {
        if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
        event.preventDefault();
        releaseSlider();
        selectSlide(sliderCurrent + (event.key === 'ArrowRight' ? 1 : -1));
      });

      sliderTrack.addEventListener('wheel', releaseSlider, { passive: true });
      sliderTrack.addEventListener('pointerdown', releaseSlider, { passive: true });

      sliderTrack.addEventListener(
        'scroll',
        function () {
          if (sliderFrame) return;
          sliderFrame = true;
          window.requestAnimationFrame(syncSlider);
        },
        { passive: true }
      );

      window.addEventListener(
        'resize',
        function () {
          selectSlide(sliderCurrent);
        },
        { passive: true }
      );

      paintSlider();
    }
  }

  /* ---------------------------------------------------------------------- */
  /* Scrollspy: mark the section currently in view                          */
  /* ---------------------------------------------------------------------- */
  var navLinks = Array.prototype.slice.call(doc.querySelectorAll('.site-nav__list a[href^="#"]'));
  var sections = navLinks
    .map(function (link) {
      var id = link.getAttribute('href').slice(1);
      return doc.getElementById(id);
    })
    .filter(Boolean);

  if (sections.length && 'IntersectionObserver' in window) {
    var spy = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          navLinks.forEach(function (link) {
            var match = link.getAttribute('href') === '#' + entry.target.id;
            if (match) {
              link.setAttribute('aria-current', 'location');
            } else {
              link.removeAttribute('aria-current');
            }
          });
        });
      },
      { rootMargin: '-45% 0px -50% 0px' }
    );

    sections.forEach(function (section) {
      spy.observe(section);
    });
  }

  /* ---------------------------------------------------------------------- */
  /* Current year in the footer                                             */
  /* ---------------------------------------------------------------------- */
  var yearNode = doc.querySelector('[data-year]');
  if (yearNode) yearNode.textContent = String(new Date().getFullYear());
})();
