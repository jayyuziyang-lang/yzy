/* 扬说·产业链 第2期 — 光模块专题 */
(function() {
  'use strict';

  // ===== 导航栏滚动高亮 =====
  const sections = document.querySelectorAll('.section');
  const navLinks = document.querySelectorAll('.top-nav-links a');
  const tocLinks = document.querySelectorAll('.side-toc-inner a');

  function updateActiveLink() {
    let current = '';
    sections.forEach(function(section) {
      const rect = section.getBoundingClientRect();
      if (rect.top <= 120) {
        current = section.getAttribute('id');
      }
    });

    function setActive(links) {
      links.forEach(function(link) {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + current) {
          link.classList.add('active');
        }
      });
    }

    setActive(navLinks);
    setActive(tocLinks);
  }

  window.addEventListener('scroll', updateActiveLink, { passive: true });

  // ===== 回到顶部按钮 =====
  const backBtn = document.querySelector('.back-to-top');
  if (backBtn) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 600) {
        backBtn.classList.add('visible');
      } else {
        backBtn.classList.remove('visible');
      }
    }, { passive: true });
  }

  // ===== 品牌分割线 IntersectionObserver =====
  const dividers = document.querySelectorAll('.brand-divider');
  if (dividers.length && 'IntersectionObserver' in window) {
    const dividerObserver = new IntersectionObserver(
      function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.5 }
    );
    dividers.forEach(function(d) { dividerObserver.observe(d); });
  }

  // ===== 章节淡入动画 =====
  const fadeTargets = document.querySelectorAll('.section');
  if (fadeTargets.length && 'IntersectionObserver' in window) {
    fadeTargets.forEach(function(el) { el.classList.add('section-fade-in'); });
    const fadeObserver = new IntersectionObserver(
      function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
    );
    fadeTargets.forEach(function(el) { fadeObserver.observe(el); });
  }

  // ===== 品牌页脚 slogan 视差淡入 =====
  const footer = document.querySelector('.brand-footer');
  if (footer && 'IntersectionObserver' in window) {
    const footerObserver = new IntersectionObserver(
      function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
          }
        });
      },
      { threshold: 0.2 }
    );
    footer.style.opacity = '0';
    footer.style.transform = 'translateY(20px)';
    footer.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    footerObserver.observe(footer);
  }

  // ===== 视频播放/暂停按钮 =====
  var videoContainers = document.querySelectorAll('.video-container');
  videoContainers.forEach(function(container) {
    var video = container.querySelector('video');
    var btn = container.querySelector('.video-play-btn');
    if (!video || !btn) return;

    function togglePlay() {
      if (video.paused) {
        video.play().then(function() {
          btn.textContent = '\u23f8';
          btn.classList.add('playing');
          btn.setAttribute('aria-label', '\u6682\u505c');
        }).catch(function() {});
      } else {
        video.pause();
        btn.textContent = '\u25b6';
        btn.classList.remove('playing');
        btn.setAttribute('aria-label', '\u64ad\u653e');
      }
    }

    function onPlay() {
      btn.textContent = '\u23f8';
      btn.classList.add('playing');
      btn.setAttribute('aria-label', '\u6682\u505c');
    }

    function onPause() {
      btn.textContent = '\u25b6';
      btn.classList.remove('playing');
      btn.setAttribute('aria-label', '\u64ad\u653e');
    }

    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      togglePlay();
    });

    video.addEventListener('click', togglePlay);
    video.addEventListener('play', onPlay);
    video.addEventListener('pause', onPause);
    video.addEventListener('ended', onPause);
  });

  // ===== 初始激活 =====
  updateActiveLink();
})();
