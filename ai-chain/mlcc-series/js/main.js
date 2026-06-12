/**
 * MLCC 科普网页 — 交互脚本
 * 功能: 锚点平滑滚动、章节高亮、回到顶部
 */
(function () {
  "use strict";

  // ============================================================
  // 配置
  // ============================================================
  const SCROLL_OFFSET = 80;   // 顶部导航高度偏移
  const DEBOUNCE_MS = 80;     // 滚动事件防抖

  // ============================================================
  // DOM 引用
  // ============================================================
  const topNavLinks = document.querySelectorAll(".top-nav-links a");
  const sideTocLinks = document.querySelectorAll(".side-toc-inner a");
  const backToTopBtn = document.getElementById("back-to-top");
  const allSections = document.querySelectorAll(".section[id]");

  // ============================================================
  // 平滑滚动锚点 (覆盖原生 smooth，支持偏移)
  // ============================================================
  function smoothScrollTo(targetId) {
    const target = document.getElementById(targetId);
    if (!target) return;
    const top = target.getBoundingClientRect().top + window.pageYOffset - SCROLL_OFFSET - 20;
    window.scrollTo({ top, behavior: "smooth" });
  }

  // 顶部导航点击
  topNavLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const targetId = this.getAttribute("href").replace("#", "");
      smoothScrollTo(targetId);
    });
  });

  // 左侧目录点击
  sideTocLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const targetId = this.getAttribute("href").replace("#", "");
      smoothScrollTo(targetId);
    });
  });

  // ============================================================
  // 章节高亮 (IntersectionObserver)
  // ============================================================
  function getCurrentSectionId() {
    let currentId = "";
    const viewportMiddle = window.innerHeight / 3; // 上1/3处
    allSections.forEach(function (section) {
      const rect = section.getBoundingClientRect();
      if (rect.top <= viewportMiddle + 50) {
        currentId = section.id;
      }
    });
    return currentId;
  }

  function updateActiveLinks(currentId) {
    // 更新顶部导航
    topNavLinks.forEach(function (link) {
      link.classList.toggle(
        "active",
        link.getAttribute("href") === "#" + currentId
      );
    });
    // 更新左侧目录
    sideTocLinks.forEach(function (link) {
      link.classList.toggle(
        "active",
        link.getAttribute("href") === "#" + currentId
      );
    });
  }

  let scrollTicking = false;
  window.addEventListener("scroll", function () {
    if (!scrollTicking) {
      requestAnimationFrame(function () {
        const currentId = getCurrentSectionId();
        updateActiveLinks(currentId);

        // 回到顶部按钮显隐
        if (backToTopBtn) {
          backToTopBtn.classList.toggle(
            "visible",
            window.pageYOffset > 500
          );
        }

        scrollTicking = false;
      });
      scrollTicking = true;
    }
  });

  // ============================================================
  // 回到顶部按钮
  // ============================================================
  if (backToTopBtn) {
    backToTopBtn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // ============================================================
  // 初始状态
  // ============================================================
  document.addEventListener("DOMContentLoaded", function () {
    // 初始高亮
    const initialId = window.location.hash
      ? window.location.hash.replace("#", "")
      : "s1";
    updateActiveLinks(initialId);

    // 如果有 hash，滚动到对应位置
    if (window.location.hash) {
      setTimeout(function () {
        smoothScrollTo(window.location.hash.replace("#", ""));
      }, 100);
    }
  });
})();
