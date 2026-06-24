/**
 * 柳琴戏非遗 H5 — 弹窗式答题 + 9题计分 + 海报生成
 */
(function () {
  'use strict';

  // ========== DOM 引用 ==========
  var progressFill = document.getElementById('globalProgressFill');
  var scoreNumber = document.getElementById('scoreNumber');
  var scoreCircle = document.getElementById('scoreCircle');
  var resultMessage = document.getElementById('resultMessage');
  var resultDetail = document.getElementById('resultDetail');
  var posterScore = document.getElementById('posterScore');
  var posterLabel = document.getElementById('posterLabel');
  var posterStars = document.getElementById('posterStars');
  var posterModal = document.getElementById('posterModal');
  var posterImage = document.getElementById('posterImage');
  var posterModalClose = document.getElementById('posterModalClose');
  var quizDialog = document.getElementById('quizDialog');
  var qdIcon = document.getElementById('qdIcon');
  var qdText = document.getElementById('qdText');
  var qdBtn = document.getElementById('qdBtn');

  // ========== 状态 ==========
  // 9道题: [coverQ, p2Q, p3Q, p4Q, p5Q, p6Q, p7-Q1, p7-Q2, p8Q]
  var userAnswers = new Array(9).fill(null);
  var quizLocked = new Array(9).fill(false);

  function calcScore() {
    var correct = 0;
    var keys = [
      QUIZ_DATA.cover.quiz.correct,
      QUIZ_DATA.page2.quiz.correct,
      QUIZ_DATA.page3.quiz.correct,
      QUIZ_DATA.page4.quiz.correct,
      QUIZ_DATA.page5.quiz.correct,
      QUIZ_DATA.page6.quiz.correct,
      QUIZ_DATA.page7.quiz1.correct,
      QUIZ_DATA.page7.quiz2.correct,
      QUIZ_DATA.page8.quiz.correct,
    ];
    for (var i = 0; i < 9; i++) {
      if (userAnswers[i] === keys[i]) correct++;
    }
    return correct;
  }

  // 页面→题目索引映射
  function getQuizIndices(slideIdx) {
    if (slideIdx === 0) return [0];           // cover
    if (slideIdx >= 1 && slideIdx <= 5) return [slideIdx]; // p2-p6 → q1-q5
    if (slideIdx === 6) return [6, 7];         // p7 → q6, q7
    if (slideIdx === 8) return [8];            // p8(closing) → q8
    return [];
  }

  function isPageComplete(slideIdx) {
    var indices = getQuizIndices(slideIdx);
    if (indices.length === 0) return true; // 非答题页
    for (var i = 0; i < indices.length; i++) {
      if (!quizLocked[indices[i]]) return false;
    }
    return true;
  }

  // ========== Swiper 初始化 ==========
  var swiper = new Swiper('.main-swiper', {
    direction: 'vertical',
    speed: 480,
    touchRatio: 1,
    resistance: true,
    resistanceRatio: 0,
    mousewheel: false,
    allowTouchMove: true,
    effect: 'slide',
    on: {
      slideChange: onSlideChange,
    },
  });

  function onSlideChange() {
    var idx = swiper.activeIndex;

    // 锁定未完成答题页的向前滑动
    swiper.allowSlidePrev = true;
    swiper.allowSlideNext = isPageComplete(idx);

    updateProgress();

    // P8 (slide 7)：得分揭晓
    if (idx === 7) animateScoreReveal();

    // P10 (slide 9)：渲染海报
    if (idx === 9) renderPoster();
  }

  // ========== 进度条 ==========
  function updateProgress() {
    var answered = userAnswers.filter(function (a) { return a !== null; }).length;
    progressFill.style.width = (answered / 9 * 100) + '%';
  }

  // ========== 弹窗系统 ==========
  function showDialog(isCorrect, msg) {
    qdIcon.innerHTML = isCorrect
      ? '<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#3D7A4F" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="8 12 11 15 16 9"/></svg>'
      : '<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#C4553D" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';
    qdText.textContent = msg;
    quizDialog.classList.add('active');
  }

  qdBtn.addEventListener('click', function () {
    quizDialog.classList.remove('active');
  });
  // 点击遮罩关闭
  quizDialog.addEventListener('click', function (e) {
    if (e.target === quizDialog) quizDialog.classList.remove('active');
  });

  // ========== 通用答题处理 ==========
  function setupQuiz(optsContainer, correctIdx, wrongMsg, correctMsg, answerIdx) {
    if (quizLocked[answerIdx]) return; // 已答过

    var optEls = optsContainer.querySelectorAll('.quiz-opt');

    optsContainer.addEventListener('click', function handler(e) {
      var opt = e.target.closest('.quiz-opt');
      if (!opt || quizLocked[answerIdx]) return;

      var chosen = parseInt(opt.dataset.i, 10);
      var isCorrect = chosen === correctIdx;

      userAnswers[answerIdx] = chosen;
      quizLocked[answerIdx] = true;

      // 弹窗
      showDialog(isCorrect, isCorrect ? correctMsg : wrongMsg);

      // 揭示正确答案
      optEls.forEach(function (o, i) {
        o.style.pointerEvents = 'none';
        if (i === correctIdx) {
          o.classList.add('reveal-correct');
        } else if (i === chosen && !isCorrect) {
          o.classList.add('reveal-incorrect');
        } else {
          o.classList.add('reveal-dimmed');
        }
      });

      // 更新状态
      updateProgress();
      onPageQuizComplete();
    });
  }

  // 页面答题完成后：解锁滑动 + 启用按钮
  function onPageQuizComplete() {
    var idx = swiper.activeIndex;
    swiper.allowSlideNext = isPageComplete(idx);

    // 启用对应按钮
    if (idx === 0) {
      document.getElementById('btnCoverNext').disabled = false;
    } else if (idx >= 1 && idx <= 5) {
      document.getElementById('btnNav' + (idx + 1)).disabled = false;
    } else if (idx === 6) {
      // page7: 两道题都答完才启用
      if (quizLocked[6] && quizLocked[7]) {
        document.getElementById('btnNav7').disabled = false;
      }
    }
    // idx 8 (closing) 按钮始终可用，不需要处理
  }

  // ========== 封面答题 ==========
  (function setupCoverQuiz() {
    var optsContainer = document.querySelector('.cover-quiz-opts');
    var correctIdx = QUIZ_DATA.cover.quiz.correct;
    var optEls = optsContainer.querySelectorAll('.cover-opt');

    optsContainer.addEventListener('click', function handler(e) {
      var opt = e.target.closest('.cover-opt');
      if (!opt || quizLocked[0]) return;

      var chosen = parseInt(opt.dataset.i, 10);
      var isCorrect = chosen === correctIdx;

      userAnswers[0] = chosen;
      quizLocked[0] = true;

      showDialog(isCorrect, isCorrect ? QUIZ_DATA.cover.quiz.correctMsg : QUIZ_DATA.cover.quiz.wrongMsg);

      // 揭示
      optEls.forEach(function (o, i) {
        o.style.pointerEvents = 'none';
        if (i === correctIdx) {
          o.classList.add('correct');
        } else if (i === chosen && !isCorrect) {
          o.classList.add('incorrect');
        } else {
          o.classList.add('dimmed');
        }
      });

      updateProgress();
      onPageQuizComplete();
    });
  })();

  // 封面按钮
  document.getElementById('btnCoverNext').addEventListener('click', function () {
    if (!quizLocked[0]) return;
    swiper.slideTo(1);
  });

  // ========== 页面2-6 答题初始化 ==========
  var pageQuizConfigs = [
    { page: 2, container: '[data-page="2"] .quiz-opts', data: QUIZ_DATA.page2.quiz, answerIdx: 1, btnId: 'btnNav2', slideTo: 2 },
    { page: 3, container: '[data-page="3"] .quiz-opts', data: QUIZ_DATA.page3.quiz, answerIdx: 2, btnId: 'btnNav3', slideTo: 3 },
    { page: 4, container: '[data-page="4"] .quiz-opts', data: QUIZ_DATA.page4.quiz, answerIdx: 3, btnId: 'btnNav4', slideTo: 4 },
    { page: 5, container: '[data-page="5"] .quiz-opts', data: QUIZ_DATA.page5.quiz, answerIdx: 4, btnId: 'btnNav5', slideTo: 5 },
    { page: 6, container: '[data-page="6"] .quiz-opts', data: QUIZ_DATA.page6.quiz, answerIdx: 5, btnId: 'btnNav6', slideTo: 6 },
  ];

  pageQuizConfigs.forEach(function (cfg) {
    var container = document.querySelector(cfg.container);
    if (!container) return;
    setupQuiz(container, cfg.data.correct, cfg.data.wrongMsg, cfg.data.correctMsg, cfg.answerIdx);

    document.getElementById(cfg.btnId).addEventListener('click', function () {
      if (!quizLocked[cfg.answerIdx]) return;
      swiper.slideTo(cfg.slideTo);
    });
  });

  // ========== 第7页（综合闯关·双题）==========
  (function setupPage7() {
    var quiz1Data = QUIZ_DATA.page7.quiz1;
    var quiz2Data = QUIZ_DATA.page7.quiz2;
    var c1 = document.querySelector('[data-page="7"] [data-sub="1"]');
    var c2 = document.querySelector('[data-page="7"] [data-sub="2"]');

    if (c1) setupQuiz(c1, quiz1Data.correct, quiz1Data.wrongMsg, quiz1Data.correctMsg, 6);
    if (c2) setupQuiz(c2, quiz2Data.correct, quiz2Data.wrongMsg, quiz2Data.correctMsg, 7);

    document.getElementById('btnNav7').addEventListener('click', function () {
      if (!quizLocked[6] || !quizLocked[7]) return;
      swiper.slideTo(7);
    });
  })();

  // ========== 第9页（收尾·首尾呼应）==========
  (function setupPage8() {
    var container = document.querySelector('[data-page="8"] .quiz-opts');
    if (!container) return;
    setupQuiz(container, QUIZ_DATA.page8.quiz.correct, QUIZ_DATA.page8.quiz.wrongMsg, QUIZ_DATA.page8.quiz.correctMsg, 8);

    document.getElementById('btnNav8').addEventListener('click', function () {
      swiper.slideTo(9);
    });
  })();

  // ========== 得分揭晓 ==========
  function animateScoreReveal() {
    var score = calcScore();
    var msg = QUIZ_DATA.scoreMessages[score];

    animateCounter(scoreNumber, 0, score, 800);

    var circumference = 2 * Math.PI * 68;
    var offset = circumference * (1 - score / 9);
    setTimeout(function () {
      scoreCircle.style.strokeDashoffset = offset;
    }, 300);

    resultMessage.textContent = msg.label;
    resultDetail.textContent = msg.detail;

    if (score <= 2) scoreCircle.style.stroke = '#9B8E7A';
    else if (score <= 5) scoreCircle.style.stroke = '#9B2D30';
    else if (score <= 7) scoreCircle.style.stroke = '#B8860B';
    else scoreCircle.style.stroke = '#B8860B';
  }

  function animateCounter(el, from, to, duration) {
    var start = performance.now();
    function tick(now) {
      var elapsed = now - start;
      var progress = Math.min(elapsed / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(from + (to - from) * eased);
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  document.getElementById('btnContinue').addEventListener('click', function () {
    swiper.slideTo(8);
  });

  // ========== 分享海报 ==========
  function renderPoster() {
    var score = calcScore();
    var msg = QUIZ_DATA.scoreMessages[score];
    posterScore.textContent = score;
    posterLabel.textContent = msg.label;

    var starsHTML = '';
    for (var i = 0; i < 5; i++) {
      if (i < msg.stars) {
        starsHTML += '<svg class="poster-star" viewBox="0 0 24 24" fill="#FBBF24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>';
      } else {
        starsHTML += '<svg class="poster-star empty" viewBox="0 0 24 24" fill="rgba(255,255,255,0.12)"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>';
      }
    }
    posterStars.innerHTML = starsHTML;
  }

  // ========== 海报 QR 码预渲染 ==========
  var qrCache = document.getElementById('qrCache');
  var qrReady = false;
  if (qrCache && typeof QRCode !== 'undefined') {
    try {
      new QRCode(qrCache, {
        text: 'https://jayyuziyang-lang.github.io/yzy/liuqin/',
        width: 100,
        height: 100,
        colorDark: '#1a1a1a',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.M
      });
      // QRCode 内部用 setTimeout 渲染，等 500ms 后可用
      setTimeout(function () { qrReady = true; }, 500);
    } catch (e) { qrReady = false; }
  }

  // ========== 海报生成工具函数 ==========
  function roundedRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.arcTo(x + w, y, x + w, y + r, r);
    ctx.lineTo(x + w, y + h - r);
    ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
    ctx.lineTo(x + r, y + h);
    ctx.arcTo(x, y + h, x, y + h - r, r);
    ctx.lineTo(x, y + r);
    ctx.arcTo(x, y, x + r, y, r);
    ctx.closePath();
  }

  // ========== 保存海报 ==========
  document.getElementById('btnSavePoster').addEventListener('click', function () {
    var score = calcScore();
    var msg = QUIZ_DATA.scoreMessages[score];

    var W = 750;
    var H = 1000;
    var canvas = document.createElement('canvas');
    canvas.width = W;
    canvas.height = H;
    var ctx = canvas.getContext('2d');

    var bgImg = new Image();
    bgImg.src = 'images/poster_bg.jpg';
    bgImg.onload = function () {
      // 1. 背景图（cover 模式居中裁剪）
      var iw = bgImg.width;
      var ih = bgImg.height;
      var scale = Math.max(W / iw, H / ih);
      var sw = W / scale;
      var sh = H / scale;
      var sx = (iw - sw) / 2;
      var sy = (ih - sh) / 2;
      ctx.drawImage(bgImg, sx, sy, sw, sh, 0, 0, W, H);

      // 2. 暗色叠加层
      ctx.fillStyle = 'rgba(0,0,0,0.28)';
      ctx.fillRect(0, 0, W, H);

      // 3. 顶部徽章
      ctx.fillStyle = 'rgba(255,255,255,0.12)';
      ctx.strokeStyle = 'rgba(255,255,255,0.18)';
      ctx.lineWidth = 2;
      var badgeW = 340;
      var badgeH = 48;
      var badgeX = (W - badgeW) / 2;
      var badgeY = 70;
      roundedRect(ctx, badgeX, badgeY, badgeW, badgeH, 24);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = '#fff';
      ctx.font = '600 22px "PingFang SC","Microsoft YaHei",sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('国家级非遗 · 临沂柳琴戏', W / 2, badgeY + badgeH / 2);

      // 4. 分数
      ctx.fillStyle = '#fff';
      ctx.font = '800 110px "PingFang SC","Microsoft YaHei",sans-serif';
      ctx.fillText(String(score), W / 2 - 14, 300);
      ctx.font = '400 34px "PingFang SC","Microsoft YaHei",sans-serif';
      ctx.fillStyle = 'rgba(255,255,255,0.55)';
      ctx.fillText('/9', W / 2 + 55, 300);

      // 5. 评语
      ctx.fillStyle = '#fff';
      ctx.font = '700 30px "PingFang SC","Microsoft YaHei",sans-serif';
      ctx.fillText(msg.label, W / 2, 365);

      // 6. 星星
      var starPath = new Path2D('M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z');
      var starSize = 36;
      var starGap = 14;
      var starTotalW = 5 * starSize + 4 * starGap;
      var starStartX = (W - starTotalW) / 2;
      var starY = 410;
      for (var s = 0; s < 5; s++) {
        ctx.save();
        ctx.translate(starStartX + s * (starSize + starGap) + starSize / 2, starY + starSize / 2);
        ctx.scale(starSize / 24, starSize / 24);
        ctx.fillStyle = s < msg.stars ? '#FBBF24' : 'rgba(255,255,255,0.12)';
        ctx.fill(starPath);
        ctx.restore();
      }

      // 7. 标语
      ctx.fillStyle = 'rgba(255,255,255,0.5)';
      ctx.font = '400 24px "PingFang SC","Microsoft YaHei",sans-serif';
      ctx.fillText('一缕拉魂腔，沂蒙柳琴魂', W / 2, 500);

      // 8. 底部分隔线
      ctx.strokeStyle = 'rgba(255,255,255,0.15)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(80, 560);
      ctx.lineTo(W - 80, 560);
      ctx.stroke();

      // 9. QR 码（从预渲染缓存复制）
      var qrSize = 110;
      var qrX = (W - qrSize) / 2;
      var qrY = 595;
      ctx.fillStyle = '#ffffff';
      roundedRect(ctx, qrX - 4, qrY - 4, qrSize + 8, qrSize + 8, 8);
      ctx.fill();
      if (qrReady && qrCache) {
        ctx.drawImage(qrCache, qrX, qrY, qrSize, qrSize);
      }

      // 10. 底部文字
      ctx.fillStyle = 'rgba(255,255,255,0.5)';
      ctx.font = '400 18px "PingFang SC","Microsoft YaHei",sans-serif';
      ctx.fillText('扫码参与柳琴戏知识挑战', W / 2, 740);

      // 11. 导出
      var dataUrl = canvas.toDataURL('image/png');
      posterImage.src = dataUrl;
      posterModal.classList.add('active');
    };
    bgImg.onerror = function () {
      alert('海报背景图加载失败，请确认 images/poster_bg.jpg 存在');
    };
  });

  posterModalClose.addEventListener('click', function () {
    posterModal.classList.remove('active');
  });
  posterModal.addEventListener('click', function (e) {
    if (e.target === posterModal) posterModal.classList.remove('active');
  });

  // ========== 重新探索 ==========
  document.getElementById('btnRetry').addEventListener('click', function () {
    resetAll();
    swiper.slideTo(0, 0);
  });

  function resetAll() {
    userAnswers = new Array(9).fill(null);
    quizLocked = new Array(9).fill(false);
    scoreCircle.style.strokeDashoffset = '427.26';
    progressFill.style.width = '0%';

    // 重置所有选项样式
    document.querySelectorAll('.quiz-opt, .cover-opt').forEach(function (el) {
      el.className = el.classList.contains('cover-opt') ? 'cover-opt' : 'quiz-opt';
      el.style.pointerEvents = 'auto';
    });

    // 重置按钮
    document.getElementById('btnCoverNext').disabled = true;
    for (var i = 2; i <= 7; i++) {
      var btn = document.getElementById('btnNav' + i);
      if (btn) btn.disabled = true;
    }

    swiper.allowSlideNext = true;
    swiper.allowSlidePrev = true;
  }

  // ========== Bilibili 视频播放器 ==========
  var biliPlayer = document.getElementById('biliPlayer');
  var biliFrame = document.getElementById('biliFrame');
  var biliTitle = document.getElementById('biliTitle');
  var biliPlayerClose = document.getElementById('biliPlayerClose');
  var biliLoadTimer = null;

  function openBiliPlayer(bvid, title) {
    biliTitle.textContent = title || '柳琴戏曲段';
    biliFrame.src = 'https://player.bilibili.com/player.html?bvid=' + bvid + '&autoplay=1&post=1';
    biliPlayer.classList.add('active');

    // 标记对应按钮为播放中
    document.querySelectorAll('.btn-audio').forEach(function (b) {
      if (b.dataset.bvid === bvid) b.classList.add('playing');
    });

    // 5秒后检测 iframe 是否加载成功，失败则打开新窗口
    clearTimeout(biliLoadTimer);
    biliLoadTimer = setTimeout(function () {
      if (biliPlayer.classList.contains('active')) {
        window.open('https://www.bilibili.com/video/' + bvid, '_blank');
      }
    }, 5000);
  }

  function closeBiliPlayer() {
    biliPlayer.classList.remove('active');
    biliFrame.src = '';
    document.querySelectorAll('.btn-audio.playing').forEach(function (b) { b.classList.remove('playing'); });
    clearTimeout(biliLoadTimer);
  }

  biliPlayerClose.addEventListener('click', closeBiliPlayer);

  // btn-audio 点击：打开Bilibili播放器
  document.querySelectorAll('.btn-audio').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var bvid = btn.dataset.bvid;
      var title = btn.dataset.title || btn.textContent.trim();
      if (!bvid) return;

      if (btn.classList.contains('playing')) {
        // 已播放中，关闭
        closeBiliPlayer();
      } else {
        openBiliPlayer(bvid, title);
      }
    });
  });

  // ========== 音频系统（手动播放，开头导入 → 导入2 → 柳琴戏唱段 → 循环）==========
  var audio1 = document.getElementById('audio1');
  var audio2 = document.getElementById('audio2');
  var audio3 = document.getElementById('audio3');
  var bgmToggle = document.getElementById('bgmToggle');
  var bgmIconPlay = bgmToggle.querySelector('.bgm-icon-play');
  var bgmIconPause = bgmToggle.querySelector('.bgm-icon-pause');
  var currentAudio = null;
  var audioPlaying = false;
  var userPaused = false;
  var audioPausedForVideo = false;

  function setPlayingState(playing) {
    audioPlaying = playing;
    if (playing) {
      bgmIconPlay.style.display = 'none';
      bgmIconPause.style.display = '';
      bgmToggle.classList.add('active');
    } else {
      bgmIconPlay.style.display = '';
      bgmIconPause.style.display = 'none';
      bgmToggle.classList.remove('active');
    }
  }

  // 为 opening.mp3 尾部静音设置 timeupdate 提前跳过
  // 当 currentTime 超过 data-skip-at 阈值时，视为内容结束
  function setupSkipTimer(audio, onEnd) {
    var skipAt = parseFloat(audio.dataset.skipAt);
    if (!skipAt || skipAt <= 0) return;
    audio.ontimeupdate = function () {
      if (audio.currentTime >= skipAt) {
        audio.pause();
        audio.ontimeupdate = null;
        audio.onended = null;
        if (onEnd) onEnd();
      }
    };
  }

  function playAudio(audio, onEnd) {
    if (!audio) return;
    // 清除前一个音频的所有事件
    [audio1, audio2, audio3].forEach(function (a) {
      if (a) { a.ontimeupdate = null; a.onended = null; }
    });
    if (currentAudio && currentAudio !== audio && !currentAudio.paused) {
      currentAudio.pause();
    }
    currentAudio = audio;
    audio.volume = 0.55;

    audio.play().then(function () {
      if (!audioPlaying) setPlayingState(true);
      audio.onended = function () { if (onEnd) onEnd(); };
      setupSkipTimer(audio, onEnd);
    }).catch(function (e) { if (onEnd) onEnd(); });
  }

  function startChain() {
    if (userPaused) return;
    playAudio(audio1, function () {
      playAudio(audio2, function () {
        playAudio(audio3, function () {
          if (!userPaused) startChain();
        });
      });
    });
  }

  function pauseChain() {
    [audio1, audio2, audio3].forEach(function (a) {
      if (a) { a.pause(); a.ontimeupdate = null; a.onended = null; }
    });
    setPlayingState(false);
    currentAudio = null;
  }

  // ========== 音频开关按钮（点击开始播放，之后暂停/恢复）==========
  bgmToggle.addEventListener('click', function () {
    if (audioPlaying) {
      pauseChain();
      userPaused = true;
    } else {
      userPaused = false;
      startChain();
    }
  });

  // Bilibili 播放器开关时暂停/恢复音频
  var biliOrigOpen = openBiliPlayer;
  openBiliPlayer = function (bvid, title) {
    if (audioPlaying) {
      pauseChain();
      audioPausedForVideo = true;
    }
    biliOrigOpen(bvid, title);
  };

  var biliOrigClose = closeBiliPlayer;
  closeBiliPlayer = function () {
    biliOrigClose();
    if (audioPausedForVideo) {
      audioPausedForVideo = false;
      userPaused = false;
      startChain();
    }
  };

  // ========== 分享系统（二维码 + 复制链接）==========
  var SHARE_URL = 'https://jayyuziyang-lang.github.io/yzy/liuqin/';
  var shareModal = document.getElementById('shareModal');
  var shareQrWrapper = document.getElementById('shareQrWrapper');
  var shareUrlText = document.getElementById('shareUrlText');
  var shareCopyToast = document.getElementById('shareCopyToast');

  // 预生成分享弹窗二维码
  if (shareQrWrapper && typeof QRCode !== 'undefined') {
    new QRCode(shareQrWrapper, { text: SHARE_URL, width: 200, height: 200,
      colorDark: '#2C2416', colorLight: '#ffffff'
    });
  }
  if (shareUrlText) shareUrlText.textContent = SHARE_URL;

  function openShareModal() {
    if (!shareModal) return;
    shareModal.classList.add('active');
  }

  function closeShareModal() {
    if (!shareModal) return;
    shareModal.classList.remove('active');
  }

  function copyShareLink() {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(SHARE_URL).then(function () {
        showCopyToast();
      }).catch(function () {
        fallbackCopy(SHARE_URL);
      });
    } else {
      fallbackCopy(SHARE_URL);
    }
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed'; ta.style.left = '-9999px'; ta.style.top = '-9999px';
    document.body.appendChild(ta);
    ta.focus(); ta.select();
    try { document.execCommand('copy'); showCopyToast(); } catch (e) {}
    document.body.removeChild(ta);
  }

  function showCopyToast() {
    if (!shareCopyToast) return;
    shareCopyToast.classList.add('show');
    setTimeout(function () { shareCopyToast.classList.remove('show'); }, 2000);
  }

  document.getElementById('btnShareQR').addEventListener('click', openShareModal);
  document.getElementById('btnCopyLink').addEventListener('click', copyShareLink);
  document.getElementById('shareModalClose').addEventListener('click', closeShareModal);
  document.getElementById('btnShareCopy').addEventListener('click', copyShareLink);
  shareModal.addEventListener('click', function (e) { if (e.target === shareModal) closeShareModal(); });

  // ========== 初始状态 ==========
  updateProgress();
  document.getElementById('btnCoverNext').disabled = true;

})();
