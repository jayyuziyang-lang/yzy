/**
 * lazy-video.js — 视频懒加载方案
 *
 * 原理：利用 IntersectionObserver 在视频进入视口前 300px 时加载并播放。
 * 替代 preload="metadata" 方案，减少首次页面加载的数据量。
 * 适合 GitHub Pages 等静态部署场景（无服务端优化能力）。
 *
 * GitHub 首页使用同类方案：IntersectionObserver + preload="none"
 */

(function() {
  'use strict';

  // 检测 IntersectionObserver 支持（不支持时回退为立即加载）
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.lazy-video').forEach(function(v) {
      var mp4 = v.getAttribute('data-mp4');
      if (mp4) {
        var s = document.createElement('source');
        s.src = mp4;
        s.type = 'video/mp4';
        v.appendChild(s);
        v.load();
      }
    });
    return;
  }

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (!entry.isIntersecting) return;

      var video = entry.target;
      var mp4 = video.getAttribute('data-mp4');

      if (mp4) {
        var source = document.createElement('source');
        source.src = mp4;
        source.type = 'video/mp4';
        video.appendChild(source);
        video.load();
        // 播放尝试（autoplay 策略可能阻止，静默 catch）
        var playPromise = video.play();
        if (playPromise && typeof playPromise.catch === 'function') {
          playPromise.catch(function() {
            // 浏览器阻止自动播放是正常的，poster 会显示
          });
        }
      }

      observer.unobserve(video);
    });
  }, {
    rootMargin: '300px'  // 提前 300px 开始加载
  });

  document.querySelectorAll('.lazy-video').forEach(function(video) {
    observer.observe(video);
  });

})();
