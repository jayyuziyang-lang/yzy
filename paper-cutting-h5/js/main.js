/* ============================================================
   《一纸千年》主逻辑
   页面切换 + 12页交互 + 状态管理
   ============================================================ */

const App = (() => {
  /* ---------- 全局状态 ---------- */
  const state = {
    currentPage: 0,
    totalPages: 12,
    isTransitioning: false,
    quizScore: 0,
    quizCurrent: 0,
    quizAnswered: false,
    puzzlePiecesPlaced: 0,
    puzzleTotal: 4,
    scratchPercent: 0,
    touchStartY: 0,
    touchStartX: 0,
  };

  /* ---------- DOM 缓存 ---------- */
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  const pagesContainer = $('#pagesContainer');
  const progressDots = $('#progressDots');
  const musicToggle = $('#musicToggle');
  let scratchCanvas, scratchCtx;

  /* ==========================================================
     页面切换
     ========================================================== */
  function goToPage(index) {
    if (index < 0 || index >= state.totalPages || state.isTransitioning) return;
    state.isTransitioning = true;
    state.currentPage = index;
    pagesContainer.style.transform = `translateY(-${index * 100}vh)`;
    updateProgressDots();
    triggerPageEnter(index);
    setTimeout(() => { state.isTransitioning = false; }, 520);
  }

  function nextPage() { goToPage(state.currentPage + 1); }
  function prevPage() { goToPage(state.currentPage - 1); }

  /* 滚轮切换（桌面） */
  let wheelDebounce = 0;
  document.addEventListener('wheel', (e) => {
    if (state.currentPage === 9) return; // 祝福卡页面不拦截滚动
    e.preventDefault();
    const now = Date.now();
    if (now - wheelDebounce < 800) return;
    wheelDebounce = now;
    if (e.deltaY > 20) nextPage();
    else if (e.deltaY < -20) prevPage();
  }, { passive: false });

  /* 触摸切换（移动端） */
  document.addEventListener('touchstart', (e) => {
    state.touchStartY = e.touches[0].clientY;
    state.touchStartX = e.touches[0].clientX;
  }, { passive: true });

  document.addEventListener('touchend', (e) => {
    // 不让祝福卡输入区域触发页面切换
    if (e.target.closest('.cardgen-form') || e.target.closest('.quiz-container')) return;
    const dy = state.touchStartY - e.changedTouches[0].clientY;
    const dx = Math.abs(state.touchStartX - e.changedTouches[0].clientX);
    if (Math.abs(dy) < 50 || dx > Math.abs(dy)) return;
    if (dy > 0) nextPage();
    else prevPage();
  });

  /* 键盘切换 */
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') { e.preventDefault(); nextPage(); }
    if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') { e.preventDefault(); prevPage(); }
  });

  /* ---------- 进度指示器 ---------- */
  function buildProgressDots() {
    progressDots.innerHTML = Array.from({ length: state.totalPages }, (_, i) =>
      `<div class="progress-dot${i === 0 ? ' active' : ''}" data-page="${i}"></div>`
    ).join('');
    progressDots.addEventListener('click', (e) => {
      const dot = e.target.closest('.progress-dot');
      if (dot) goToPage(parseInt(dot.dataset.page));
    });
  }

  function updateProgressDots() {
    $$('.progress-dot').forEach((d, i) => {
      d.classList.toggle('active', i === state.currentPage);
    });
  }

  /* ==========================================================
     页面入场触发
     ========================================================== */
  function triggerPageEnter(index) {
    switch (index) {
      case 1: initIntroCards(); break;
      case 6: initScratchCanvas(); break;
    }
  }

  /* ==========================================================
     音乐开关
     ========================================================== */
  function initMusic() {
    musicToggle.addEventListener('click', () => {
      musicToggle.classList.toggle('playing');
      // 音频占位 — 如需真实音频，替换为 Audio() 对象
    });
  }

  /* ==========================================================
     第1页 — 文化引入卡片淡入
     ========================================================== */
  function initIntroCards() {
    const cards = $$('.intro-card');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });
    cards.forEach(card => observer.observe(card));

    // 备用：直接显示（某些浏览器不支持 IntersectionObserver）
    setTimeout(() => {
      cards.forEach((card, i) => {
        setTimeout(() => card.classList.add('visible'), i * 200);
      });
    }, 300);
  }

  /* ==========================================================
     第2页 — 历史时间轴
     ========================================================== */
  function initTimeline() {
    const nodes = $$('.timeline-node');
    nodes.forEach(node => {
      node.addEventListener('click', () => {
        nodes.forEach(n => n.classList.remove('active'));
        node.classList.add('active');
      });
    });
  }

  /* ==========================================================
     第3页 — 纹样卡片翻转
     ========================================================== */
  function initPatternCards() {
    $$('.pattern-card').forEach(card => {
      card.addEventListener('click', () => {
        card.classList.toggle('flipped');
      });
    });
  }

  /* ==========================================================
     第4页 — 剪纸工艺步骤
     ========================================================== */
  function initCraftSteps() {
    $$('.craft-step').forEach(step => {
      step.addEventListener('click', () => {
        $$('.craft-step').forEach(s => s.classList.remove('active'));
        step.classList.add('active');
      });
    });
  }

  /* ==========================================================
     第5页 — 拖拽拼窗花
     ========================================================== */
  function initPuzzle() {
    const pieces = $$('.puzzle-piece');
    const zones = $$('.target-zone');
    const zoneRects = [];
    const puzzlePage = $('.page-puzzle');

    // 缓存目标区域位置
    function cacheZoneRects() {
      zoneRects.length = 0;
      zones.forEach((z, i) => {
        const r = z.getBoundingClientRect();
        zoneRects[i] = {
          left: r.left + r.width / 2,
          top: r.top + r.height / 2,
          zone: parseInt(z.dataset.zone),
        };
      });
    }

    pieces.forEach(piece => {
      piece.addEventListener('pointerdown', (e) => {
        e.preventDefault();
        piece.setPointerCapture(e.pointerId);
        piece.classList.add('dragging');
        cacheZoneRects();

        const rect = piece.getBoundingClientRect();
        const offsetX = e.clientX - rect.left;
        const offsetY = e.clientY - rect.top;
        const startLeft = piece.style.left || '0px';
        const startTop = piece.style.top || '0px';
        const parentRect = piece.parentElement.getBoundingClientRect();

        function onMove(ev) {
          const x = ev.clientX - parentRect.left - offsetX;
          const y = ev.clientY - parentRect.top - offsetY;
          piece.style.position = 'relative';
          piece.style.left = x + 'px';
          piece.style.top = y + 'px';
          piece.style.zIndex = '10';

          // 检测是否靠近目标区域
          zones.forEach(z => z.classList.remove('hover'));
          const cx = ev.clientX;
          const cy = ev.clientY;
          for (const zr of zoneRects) {
            const dist = Math.sqrt((cx - zr.left) ** 2 + (cy - zr.top) ** 2);
            if (dist < 50) {
              const targetZone = zones[zr.zone];
              if (!targetZone.classList.contains('matched')) {
                targetZone.classList.add('hover');
              }
            }
          }
        }

        function onUp(ev) {
          piece.classList.remove('dragging');
          piece.style.zIndex = '';

          const cx = ev.clientX;
          const cy = ev.clientY;
          let matched = false;

          for (const zr of zoneRects) {
            const dist = Math.sqrt((cx - zr.left) ** 2 + (cy - zr.top) ** 2);
            if (dist < 50) {
              const targetZone = zones[zr.zone];
              if (!targetZone.classList.contains('matched')) {
                // 吸附
                const zr2 = targetZone.getBoundingClientRect();
                const pr2 = piece.parentElement.getBoundingClientRect();
                piece.style.left = (zr2.left - pr2.left) + 'px';
                piece.style.top = (zr2.top - pr2.top) + 'px';
                targetZone.classList.add('matched');
                targetZone.classList.remove('hover');
                piece.classList.add('placed');
                state.puzzlePiecesPlaced++;
                matched = true;

                if (state.puzzlePiecesPlaced >= state.puzzleTotal) {
                  setTimeout(() => {
                    $('#puzzleComplete').style.display = 'flex';
                  }, 400);
                }
                break;
              }
            }
          }

          zones.forEach(z => z.classList.remove('hover'));

          // 未匹配 -> 回弹
          if (!matched) {
            piece.style.left = startLeft;
            piece.style.top = startTop;
          }

          piece.removeEventListener('pointermove', onMove);
          piece.removeEventListener('pointerup', onUp);
        }

        piece.addEventListener('pointermove', onMove);
        piece.addEventListener('pointerup', onUp);
        piece.addEventListener('pointercancel', onUp);
      });

      // 防止触摸时页面切换
      piece.addEventListener('touchstart', (e) => {
        e.stopPropagation();
      });
    });
  }

  function resetPuzzle() {
    state.puzzlePiecesPlaced = 0;
    $$('.puzzle-piece').forEach(p => {
      p.classList.remove('placed');
      p.style.left = '';
      p.style.top = '';
    });
    $$('.target-zone').forEach(z => z.classList.remove('matched'));
    $('#puzzleComplete').style.display = 'none';
  }

  /* ==========================================================
     第6页 — Canvas 擦除显影
     ========================================================== */
  function initScratchCanvas() {
    scratchCanvas = $('#scratchCanvas');
    if (!scratchCanvas) return;

    const container = $('#scratchContainer');
    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;

    scratchCanvas.width = rect.width * dpr;
    scratchCanvas.height = rect.height * dpr;
    scratchCanvas.style.width = rect.width + 'px';
    scratchCanvas.style.height = rect.height + 'px';

    scratchCtx = scratchCanvas.getContext('2d');
    scratchCtx.scale(dpr, dpr);
    scratchCtx.fillStyle = '#F8EED8';
    scratchCtx.fillRect(0, 0, rect.width, rect.height);

    // 添加纹理线条模拟纸张
    scratchCtx.strokeStyle = 'rgba(200,180,150,0.3)';
    scratchCtx.lineWidth = 0.5;
    for (let i = 0; i < 20; i++) {
      scratchCtx.beginPath();
      scratchCtx.moveTo(Math.random() * rect.width, Math.random() * rect.height);
      scratchCtx.lineTo(Math.random() * rect.width, Math.random() * rect.height);
      scratchCtx.stroke();
    }

    let isScratching = false;

    function scratch(x, y) {
      scratchCtx.globalCompositeOperation = 'destination-out';
      scratchCtx.beginPath();
      scratchCtx.arc(x, y, 28, 0, Math.PI * 2);
      scratchCtx.fill();
      checkScratchProgress();
    }

    function getPos(e) {
      const r = scratchCanvas.getBoundingClientRect();
      return {
        x: (e.clientX || (e.touches && e.touches[0].clientX)) - r.left,
        y: (e.clientY || (e.touches && e.touches[0].clientY)) - r.top,
      };
    }

    scratchCanvas.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      isScratching = true;
      const pos = getPos(e);
      scratch(pos.x, pos.y);
    });

    scratchCanvas.addEventListener('pointermove', (e) => {
      if (!isScratching) return;
      e.preventDefault();
      const pos = getPos(e);
      scratch(pos.x, pos.y);
    });

    scratchCanvas.addEventListener('pointerup', () => { isScratching = false; });
    scratchCanvas.addEventListener('pointerleave', () => { isScratching = false; });
    scratchCanvas.addEventListener('pointercancel', () => { isScratching = false; });

    // 防止触摸事件冒泡导致页面切换
    scratchCanvas.addEventListener('touchstart', (e) => { e.stopPropagation(); });
    scratchCanvas.addEventListener('touchmove', (e) => { if (isScratching) e.stopPropagation(); });
  }

  function checkScratchProgress() {
    const canvas = scratchCanvas;
    const ctx = scratchCtx;
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.width / dpr;
    const h = canvas.height / dpr;

    // 缩小采样以提高性能
    const scale = 4;
    const sw = Math.floor(w / scale);
    const sh = Math.floor(h / scale);
    const offCanvas = document.createElement('canvas');
    offCanvas.width = sw;
    offCanvas.height = sh;
    const offCtx = offCanvas.getContext('2d');
    offCtx.drawImage(canvas, 0, 0, w, h, 0, 0, sw, sh);

    const imageData = offCtx.getImageData(0, 0, sw, sh);
    const pixels = imageData.data;
    let transparent = 0;
    const total = sw * sh;

    for (let i = 3; i < pixels.length; i += 4) {
      if (pixels[i] === 0) transparent++;
    }

    state.scratchPercent = Math.round((transparent / total) * 100);
    $('#scratchPercent').textContent = state.scratchPercent;
    const fillEl = $('#scratchFill');
    if (fillEl) {
      const afterEl = fillEl.querySelector('::after');
      fillEl.style.setProperty('--pct', state.scratchPercent + '%');
    }
    // 更新进度条
    const bar = $('#scratchFill');
    if (bar) bar.style.background = `linear-gradient(to right, var(--red) ${state.scratchPercent}%, rgba(177,18,38,0.15) ${state.scratchPercent}%)`;

    if (state.scratchPercent >= 50 && !state._scratchAutoRevealed) {
      state._scratchAutoRevealed = true;
      setTimeout(() => {
        // 完全清除遮罩
        scratchCtx.globalCompositeOperation = 'destination-out';
        scratchCtx.fillRect(0, 0, w, h);
        $('#scratchPercent').textContent = '100';
        $('#scratchComplete').style.display = 'block';
      }, 500);
    }
  }

  /* ==========================================================
     第7页 — 地域风格切换
     ========================================================== */
  const regionData = [
    { name: '陕西剪纸', tag: '古朴粗犷',
      desc: '陕西剪纸保留了汉唐雄风，造型古朴大气，线条粗犷有力。陕北剪纸以安塞、延川为代表，充满黄土高原的生活气息，题材多为农耕、放牧、节庆场景，是中国北方剪纸的典型代表。' },
    { name: '河北蔚县剪纸', tag: '色彩鲜艳',
      desc: '蔚县剪纸以阴刻为主、阳刻为辅，最独特的是"点染"上色技法——在刻好的白宣纸上用白酒调色点染，色彩艳丽透明。与传统单色剪纸不同，蔚县剪纸宛如纸上工笔画。' },
    { name: '扬州剪纸', tag: '细腻典雅',
      desc: '扬州剪纸线条清秀流畅，构图精巧雅致。受扬州画派影响，剪纸追求"绘画感"，以花卉、山水为主要题材。2006年被列入首批国家级非遗名录。' },
    { name: '山西剪纸', tag: '构图饱满',
      desc: '山西剪纸构图饱满、造型夸张，民俗意味浓厚。中阳、广灵等地剪纸风格独特，兼具粗犷与细腻。山西剪纸与面塑、刺绣等民间艺术相互交融。' },
    { name: '山东剪纸', tag: '造型朴实',
      desc: '山东剪纸造型朴实敦厚，乡土气息浓郁。胶东窗花以线条流畅著称，鲁西南剪纸多用锯齿纹和月牙纹，风格鲜明。剪纸广泛用于婚嫁、年节等民俗活动。' },
  ];

  function initRegions() {
    // 各地域SVG生成函数
    const regionSvgs = {
      0: `<svg viewBox="0 0 200 160" class="region-svg"><rect x="15" y="8" width="170" height="144" rx="8" fill="#B11226" opacity="0.9"/><polygon points="100,22 130,50 120,85 80,85 70,50" fill="none" stroke="#F8EED8" stroke-width="2.5"/><circle cx="100" cy="55" r="10" fill="#D8A24A" opacity="0.8"/><rect x="55" y="100" width="90" height="24" rx="12" fill="none" stroke="#D8A24A" stroke-width="1.5"/><text x="100" y="116" text-anchor="middle" fill="#D8A24A" font-size="11" font-family="serif">古朴粗犷</text></svg>`,
      1: `<svg viewBox="0 0 200 160" class="region-svg"><rect x="15" y="8" width="170" height="144" rx="8" fill="#C41E3A" opacity="0.9"/><circle cx="65" cy="55" r="20" fill="none" stroke="#F8EED8" stroke-width="2"/><circle cx="135" cy="55" r="20" fill="none" stroke="#F8EED8" stroke-width="2"/><circle cx="100" cy="80" r="20" fill="#D8A24A" opacity="0.7"/><circle cx="65" cy="55" r="6" fill="#F8EED8" opacity="0.8"/><circle cx="135" cy="55" r="6" fill="#F8EED8" opacity="0.8"/><rect x="55" y="108" width="90" height="24" rx="12" fill="none" stroke="#D8A24A" stroke-width="1.5"/><text x="100" y="124" text-anchor="middle" fill="#D8A24A" font-size="11" font-family="serif">色彩鲜艳 刻工精细</text></svg>`,
      2: `<svg viewBox="0 0 200 160" class="region-svg"><rect x="15" y="8" width="170" height="144" rx="8" fill="#B11226" opacity="0.9"/><path d="M100,30 Q120,50 100,70 Q80,50 100,30" fill="none" stroke="#F8EED8" stroke-width="2"/><path d="M100,50 Q130,75 100,100 Q70,75 100,50" fill="none" stroke="#F8EED8" stroke-width="1.5"/><path d="M100,70 Q110,85 100,100" fill="none" stroke="#D8A24A" stroke-width="2"/><circle cx="100" cy="35" r="4" fill="#D8A24A" opacity="0.8"/><rect x="55" y="115" width="90" height="24" rx="12" fill="none" stroke="#D8A24A" stroke-width="1.5"/><text x="100" y="131" text-anchor="middle" fill="#D8A24A" font-size="11" font-family="serif">线条秀丽 细腻典雅</text></svg>`,
      3: `<svg viewBox="0 0 200 160" class="region-svg"><rect x="15" y="8" width="170" height="144" rx="8" fill="#9B1B30" opacity="0.9"/><rect x="50" y="25" width="100" height="80" rx="5" fill="none" stroke="#F8EED8" stroke-width="2.5"/><rect x="60" y="35" width="80" height="60" rx="3" fill="none" stroke="#F8EED8" stroke-width="1.5"/><circle cx="100" cy="65" r="15" fill="#D8A24A" opacity="0.7"/><rect x="55" y="115" width="90" height="24" rx="12" fill="none" stroke="#D8A24A" stroke-width="1.5"/><text x="100" y="131" text-anchor="middle" fill="#D8A24A" font-size="11" font-family="serif">构图饱满 民俗味浓</text></svg>`,
      4: `<svg viewBox="0 0 200 160" class="region-svg"><rect x="15" y="8" width="170" height="144" rx="8" fill="#B11226" opacity="0.9"/><path d="M60,30 L140,30 L150,55 L140,80 L60,80 L50,55Z" fill="none" stroke="#F8EED8" stroke-width="2"/><circle cx="100" cy="55" r="12" fill="none" stroke="#D8A24A" stroke-width="2"/><circle cx="100" cy="55" r="5" fill="#D8A24A" opacity="0.8"/><rect x="55" y="100" width="90" height="24" rx="12" fill="none" stroke="#D8A24A" stroke-width="1.5"/><text x="100" y="116" text-anchor="middle" fill="#D8A24A" font-size="11" font-family="serif">造型朴实 乡土浓郁</text></svg>`,
    };

    const tabs = $$('.region-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const idx = parseInt(tab.dataset.region);
        const data = regionData[idx];
        $('#regionSvg').outerHTML = regionSvgs[idx];
        $('#regionName').textContent = data.name;
        $('#regionTag').textContent = data.tag;
        $('#regionDesc').textContent = data.desc;
      });
    });
  }

  /* ==========================================================
     第8页 — 知识问答
     ========================================================== */
  const quizData = [
    {
      q: '中国剪纸常见于哪些生活场景？',
      options: ['A. 节庆装饰', 'B. 婚俗礼仪', 'C. 祈福纳祥', 'D. 以上都是'],
      answer: 3,
    },
    {
      q: '"鱼"纹样在剪纸中通常寓意什么？',
      options: ['A. 风调雨顺', 'B. 年年有余', 'C. 步步高升', 'D. 长寿健康'],
      answer: 1,
    },
    {
      q: '中国剪纸被列入联合国教科文组织非遗代表作名录是哪一年？',
      options: ['A. 2001', 'B. 2005', 'C. 2009', 'D. 2015'],
      answer: 2,
    },
    {
      q: '剪纸最常见的颜色为什么是红色？',
      options: ['A. 象征喜庆吉祥', 'B. 因为价格便宜', 'C. 因为没有其他颜色', 'D. 因为不能染色'],
      answer: 0,
    },
    {
      q: '剪纸属于哪类艺术？',
      options: ['A. 民间美术', 'B. 油画艺术', 'C. 西方雕塑', 'D. 现代摄影'],
      answer: 0,
    },
  ];

  function initQuiz() { renderQuiz(); }

  function renderQuiz() {
    if (state.quizCurrent >= quizData.length) {
      showQuizResult();
      return;
    }
    state.quizAnswered = false;
    const q = quizData[state.quizCurrent];
    $('#quizQuestion').textContent = q.q;
    $('#quizCurrent').textContent = state.quizCurrent + 1;
    $('#quizScoreDisplay').textContent = state.quizScore;

    const optionsHtml = q.options.map((opt, i) =>
      `<button class="quiz-option" data-idx="${i}">${opt}</button>`
    ).join('');
    $('#quizOptions').innerHTML = optionsHtml;

    $$('.quiz-option').forEach(btn => {
      btn.addEventListener('click', () => {
        if (state.quizAnswered) return;
        state.quizAnswered = true;
        const idx = parseInt(btn.dataset.idx);
        const correct = idx === q.answer;

        // 高亮正确答案
        $$('.quiz-option').forEach((b, i) => {
          b.classList.add('disabled');
          if (i === q.answer) b.classList.add('correct');
        });
        if (!correct) btn.classList.add('wrong');

        if (correct) {
          state.quizScore++;
          $('#quizScoreDisplay').textContent = state.quizScore;
        }

        setTimeout(() => {
          state.quizCurrent++;
          renderQuiz();
        }, 1200);
      });
    });
  }

  function showQuizResult() {
    $('#quizContainer').style.display = 'none';
    const resultDiv = $('#quizResult');
    resultDiv.style.display = 'block';

    const total = quizData.length;
    const score = state.quizScore;

    let stamp, text;
    if (score === total) { stamp = '优'; text = '满分传承人！你对剪纸文化了如指掌。'; }
    else if (score >= 3) { stamp = '良'; text = `答对 ${score}/${total} 题，剪纸知识掌握得不错！`; }
    else { stamp = '学'; text = `答对 ${score}/${total} 题，再多了解一些剪纸文化吧～`; }

    $('#resultStamp').textContent = stamp;
    $('#resultText').textContent = text;
  }

  function resetQuiz() {
    state.quizCurrent = 0;
    state.quizScore = 0;
    state.quizAnswered = false;
    $('#quizContainer').style.display = 'block';
    $('#quizResult').style.display = 'none';
    $('#quizScoreDisplay').textContent = '0';
    renderQuiz();
  }

  /* ==========================================================
     第9页 — 祝福卡生成
     ========================================================== */
  function initCardGen() {
    // 主题按钮
    $$('#cardgenThemes .theme-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        $$('#cardgenThemes .theme-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });

    // 实时预览
    const nameInput = $('#cardName');
    const msgInput = $('#cardMessage');
    const updatePreview = () => {
      $('#cardTo').textContent = nameInput.value || '送给最好的朋友';
      $('#cardGreeting').textContent = msgInput.value || '万事如意';
      const activeTheme = $('.theme-btn.active');
      if (activeTheme) $('#cardThemeSymbol').textContent = activeTheme.dataset.theme;
    };
    nameInput.addEventListener('input', updatePreview);
    msgInput.addEventListener('input', updatePreview);

    // 卡片日期
    const now = new Date();
    $('#cardDate').textContent = `${now.getFullYear()}.${now.getMonth()+1}.${now.getDate()}`;
  }

  function generateCard() {
    const name = $('#cardName').value || '送给最好的朋友';
    const msg = $('#cardMessage').value || '万事如意';
    const theme = ($('.theme-btn.active') || {}).dataset?.theme || '福';

    $('#cardTo').textContent = name;
    $('#cardGreeting').textContent = msg;
    $('#cardThemeSymbol').textContent = theme;
    $('#btnSaveCard').style.display = 'inline-block';
  }

  function saveCard() {
    const card = $('#blessingCard');
    if (typeof html2canvas === 'undefined') {
      alert('图片保存功能加载中，请稍后再试。');
      return;
    }
    html2canvas(card, { scale: 2, backgroundColor: null }).then(canvas => {
      const link = document.createElement('a');
      link.download = '一纸千年-剪纸祝福卡.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
    }).catch(() => {
      alert('保存失败，请重试。');
    });
  }

  /* ==========================================================
     第10页 — 传承保护关键词
     ========================================================== */
  function initHeritageKeywords() {
    $$('.keyword-header').forEach(header => {
      header.addEventListener('click', () => {
        const item = header.parentElement;
        item.classList.toggle('open');
      });
    });
  }

  /* ==========================================================
     分享功能 + QR码
     ========================================================== */
  function initShare() {
    const pageUrl = window.location.href;
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(pageUrl)}`;
    const qrImg = $('#qrCode');
    if (qrImg) qrImg.src = qrUrl;
  }

  function sharePage() {
    const pageUrl = window.location.href;
    if (navigator.share) {
      navigator.share({
        title: '一纸千年 · 非遗剪纸文化互动体验',
        text: '一把剪刀，一张红纸，剪出千年民俗记忆。',
        url: pageUrl,
      }).catch(() => {});
    } else {
      navigator.clipboard.writeText(pageUrl).then(() => {
        alert('链接已复制到剪贴板，快去分享给朋友吧！');
      }).catch(() => {
        prompt('复制以下链接分享给朋友：', pageUrl);
      });
    }
  }

  /* ==========================================================
     全局初始化
     ========================================================== */
  function init() {
    buildProgressDots();
    initMusic();
    initTimeline();
    initPatternCards();
    initCraftSteps();
    initPuzzle();
    initQuiz();
    initCardGen();
    initRegions();
    initHeritageKeywords();
    initShare();
  }

  /* ---------- 公共 API ---------- */
  return {
    goToPage,
    nextPage,
    prevPage,
    resetPuzzle,
    resetQuiz,
    generateCard,
    saveCard,
    sharePage,
    init,
  };
})();

/* 启动 */
document.addEventListener('DOMContentLoaded', () => App.init());
