/* ==============================================
   《信息侦探：真假新闻挑战》v3.0 游戏逻辑
   10道真实案例 · 计时器 · 连击 · 撒花 · 二维码
   案例来源：中国互联网联合辟谣平台、各地网信办
   ============================================== */

// --- 题目数据（10道真实网络案例）---
const questions = [
  {
    id: 1,
    category: '食品安全',
    icon: '🥚',
    difficulty: '简单',
    rumorType: '伪科普谣言',
    title: '"激素蛋大量流入市场，吃了会导致儿童性早熟"',
    clue: '消息来自某些自媒体账号，声称"市面上90%鸡蛋含激素"，但未提供任何检测机构名称、检测报告编号或监管部门通报。相关说法已被"网信中国"列为年度典型谣言。',
    answer: '存疑',
    analysis: '该说法毫无科学依据。农业农村部对禽蛋产品有严格的质量安全监管体系，正规渠道销售的鸡蛋均经过检验检疫。此类谣言背后往往是不良商家为推销"土鸡蛋""无抗蛋"等高价产品而制造恐慌。核查方法：关注市场监管总局或农业农村部官网公告。',
    source: '中国互联网联合辟谣平台 2025年12月辟谣榜'
  },
  {
    id: 2,
    category: '灾害事故',
    icon: '🏚️',
    difficulty: '中等',
    rumorType: '伪造警情通报',
    title: '"某院士预测广东将发生8级以上大地震"',
    clue: '信息以"聊天截图"形式传播，声称某知名院士私下预测广东近期将发生8级以上大地震，配有伪造的"内部预警通知"图片。',
    answer: '存疑',
    analysis: '这是典型的伪造专家言论+拼接虚假图片的谣言。地震预测目前仍是全球科学难题，任何声称能精确预测地震时间、地点的说法均不科学。此类谣言利用公众对专家的信任制造恐慌。核查方法：通过中国地震局官网或官方微博核实地震信息，不要轻信"内部消息"截图。',
    source: '中国互联网联合辟谣平台 2025年度典型案例'
  },
  {
    id: 3,
    category: '公共卫生',
    icon: '🏥',
    difficulty: '简单',
    rumorType: '权威发布（真实）',
    title: '"国家卫健委官网发布冬春季呼吸道疾病防控提示"',
    clue: '信息来自国家卫健委官方网站（nhc.gov.cn），页面包含明确的发布时间、文件编号、具体防护建议和各级医疗机构联系方式。多家主流媒体（新华社、央视）进行了转载报道。',
    answer: '可信',
    analysis: '信息来源明确（卫健委官网），发布主体权威（国家级卫生行政部门），内容具有公共服务性质，且被多家正规媒体交叉验证。对于政府部门的官方公告，可通过访问其官网（.gov.cn域名）直接核实，或查看是否有主流新闻媒体跟进报道。',
    source: '国家卫生健康委员会官方网站'
  },
  {
    id: 4,
    category: '数据造假',
    icon: '📊',
    difficulty: '中等',
    rumorType: '危言耸听式数据',
    title: '"80后死亡率突破5.2%，每20个80后就有一个已经去世"',
    clue: '该说法以"数据图表"形式在微信群和朋友圈大量传播，声称引用"国家统计局数据"，但图表中未标注数据来源的具体报告名称、发布年份和统计口径。',
    answer: '存疑',
    analysis: '该说法夸大其词、危言耸听。经核查，国家统计局从未发布过"80后死亡率突破5.2%"的数据。部分传播者借机制造焦虑，进而推销保险或保健品。核查方法：对于统计数据类信息，直接访问国家统计局官网（stats.gov.cn）查询原始报告，而非轻信自媒体制作的"数据图表"。',
    source: '中国互联网联合辟谣平台 2025年3月辟谣榜'
  },
  {
    id: 5,
    category: '伪科普',
    icon: '💊',
    difficulty: '中等',
    rumorType: '伪科学营销',
    title: '"液体口罩"一喷就能防流感，效果比戴口罩更好"',
    clue: '某电商平台热销产品宣称"喷一喷形成隐形口罩""24小时防流感病毒"，商品页面引用了看似专业的"检测报告"，但报告出具机构不明，且未标注临床注册号。',
    answer: '存疑',
    analysis: '此类产品属于典型的夸大宣传。"液体口罩"概念未经国家药监局审批，所谓"防护效果"缺乏规范的临床试验验证。流感防护应以接种疫苗、佩戴口罩、勤洗手等经过科学验证的方法为主。核查方法：在药监局官网（nmpa.gov.cn）查询产品是否有正规医疗器械/药品注册证号。',
    source: '"网信中国"微信公众号 2026年1月'
  },
  {
    id: 6,
    category: '气象预警',
    icon: '🌤️',
    difficulty: '简单',
    rumorType: '官方预警（真实）',
    title: '"中央气象台发布寒潮蓝色预警：未来48小时多地将降温8-12℃"',
    clue: '信息来自中央气象台官方网站（nmc.cn），预警中包含明确的受影响地区列表、降温幅度范围、具体时间段和防御指南。央视《新闻联播》天气预报栏目也进行了播报。',
    answer: '可信',
    analysis: '气象预警信息应以各级气象部门官方发布为准。该信息要素完整（时间+区域+程度+建议），发布渠道权威（中央气象台），且被多家媒体交叉验证。遇到天气预警信息时，可通过"中国天气网"或各地气象局官方账号核实。',
    source: '中央气象台官方网站'
  },
  {
    id: 7,
    category: 'AI伪造',
    icon: '🤖',
    difficulty: '困难',
    rumorType: 'AI深度伪造',
    title: '"顶流男星在澳门赌场一夜输光10亿，现场视频曝光"',
    clue: '网传一段"澳门赌场监控视频"，画面中疑似某知名男星在赌桌前下注。但视频画质有明显AI生成痕迹，且该男星工作室已发声明称当日该男星在横店拍戏，有剧组多人可作证。',
    answer: '存疑',
    analysis: '这是2025年典型的AI造谣案例。网民徐某某利用AI工具生成虚假视频博取流量，已被公安机关依法行政拘留。AI生成的假视频通常存在面部光影不自然、口型与声音不同步、背景细节扭曲等特征。该案也提醒我们：有视频不一定有真相。核查方法：查看当事人官方社交账号是否有回应，主流媒体是否跟进报道。',
    source: '公安部"净网2025"专项行动典型案例'
  },
  {
    id: 8,
    category: '政策伪造',
    icon: '📜',
    difficulty: '中等',
    rumorType: '曲解政策原文',
    title: '"明年起向微信好友发送不雅照片、视频将被拘留，新法已通过"',
    clue: '该消息引用"新修订的《治安管理处罚法》"，但未提供具体条款编号和官方发布链接。经查，相关法条的真实内容与传播的说法有本质差异——法律规定的是"传播淫秽信息"的条件和情节界定，而非一刀切的"发送即违法"。',
    answer: '存疑',
    analysis: '这是对新修订法律的断章取义式误读。法律条文往往有严格的适用条件和情节界定，而谣言会将这些条件全部省略，制造"一律违法"的恐慌。核查方法：法律法规以全国人大官网（npc.gov.cn）或司法部官网发布的文本为准，不要轻信自媒体的"法条解读"。',
    source: '中国互联网联合辟谣平台 2025年12月辟谣榜'
  },
  {
    id: 9,
    category: '权威发布',
    icon: '🚀',
    difficulty: '中等',
    rumorType: '官方公告（真实）',
    title: '"中国载人航天工程办公室发布神舟二十号载人飞行任务标识及航天员名单"',
    clue: '信息来自中国载人航天工程官方网站（cmse.gov.cn），公告包含任务标识图案、航天员姓名和简历、发射时间窗口以及任务目标。新华社、人民日报等中央媒体均在头版进行了报道。',
    answer: '可信',
    analysis: '中国航天官方信息通常通过"中国载人航天"官方网站和官方微信公众号首发，随后被中央主流媒体广泛报道。信息呈现高度规范化的特征：有明确的任务编号、航天员完整简历、具体技术参数。此类重大科技新闻几乎不可能由自媒体"独家首发"。',
    source: '中国载人航天工程办公室'
  },
  {
    id: 10,
    category: '涉企谣言',
    icon: '🏢',
    difficulty: '困难',
    rumorType: '移花接木式造谣',
    title: '"某知名饮料品牌创始人当众拒喝自家产品，摆手说不敢喝"',
    clue: '一段十几秒的短视频在社交平台热传，字幕称"老板都不敢喝自家产品"。但视频画面中该创始人的手势和表情明显被剪辑拼接，原视频实为该创始人在其他场合与员工互动的画面。',
    answer: '存疑',
    analysis: '这是典型的"像素级真实、叙事级虚假"式造谣。视频素材本身是真实的，但通过恶意剪辑+误导性字幕+耸动解说，制造出了完全失实的叙事。据报道，此类涉企谣言曾导致某上市公司市值一周蒸发数十亿元，造谣者已被警方刑事拘留。核查方法：查找原始完整视频，关注企业官方公告和权威财经媒体的跟进报道。',
    source: '澎湃新闻 2026年6月报道'
  }
];

// --- 游戏状态 ---
const TIME_LIMIT = 15;
let currentIndex = 0;
let score = 0;
let streak = 0;
let maxStreak = 0;
let correctCount = 0;
let wrongCount = 0;
let totalTime = 0;
let timerInterval = null;
let timeLeft = TIME_LIMIT;
let answered = false;

// --- 粒子背景 ---
function initParticles() {
  const container = document.getElementById('particles');
  for (let i = 0; i < 25; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left = Math.random() * 100 + '%';
    p.style.animationDuration = (6 + Math.random() * 10) + 's';
    p.style.animationDelay = Math.random() * 8 + 's';
    p.style.width = (2 + Math.random() * 3) + 'px';
    p.style.height = p.style.width;
    container.appendChild(p);
  }
}

// --- 页面切换 ---
function goToPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const map = {
    'home': 'page-home',
    'briefing': 'page-briefing',
    'instructions': 'page-instructions',
    'question': 'page-question',
    'result': 'page-result',
    'share': 'page-share'
  };
  const el = document.getElementById(map[name]);
  if (el) {
    el.classList.add('active');
    el.scrollTop = 0;
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// --- 开始游戏 ---
function startGame() {
  currentIndex = 0;
  score = 0;
  streak = 0;
  maxStreak = 0;
  correctCount = 0;
  wrongCount = 0;
  totalTime = 0;
  answered = false;
  document.getElementById('liveScore').textContent = '0';
  document.getElementById('streakBadge').style.display = 'none';
  loadQuestion();
  goToPage('question');
}

// --- 计时器 ---
const RING_CIRCUMFERENCE = 2 * Math.PI * 26;

function startTimer() {
  timeLeft = TIME_LIMIT;
  const ring = document.getElementById('timerRing');
  const text = document.getElementById('timerText');
  const wrap = document.getElementById('timerWrap');

  ring.style.strokeDasharray = RING_CIRCUMFERENCE;
  ring.style.strokeDashoffset = '0';
  ring.style.stroke = '#4F46E5';
  text.textContent = TIME_LIMIT;
  wrap.classList.remove('urgent');

  clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    timeLeft--;
    const offset = RING_CIRCUMFERENCE * (1 - timeLeft / TIME_LIMIT);
    ring.style.strokeDashoffset = offset;
    text.textContent = timeLeft;

    if (timeLeft <= 5) {
      wrap.classList.add('urgent');
    }

    if (timeLeft <= 0) {
      clearInterval(timerInterval);
      if (!answered) {
        handleTimeout();
      }
    }
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
}

function handleTimeout() {
  answered = true;
  stopTimer();
  streak = 0;
  wrongCount++;
  document.getElementById('streakBadge').style.display = 'none';
  const q = questions[currentIndex];
  showFeedback(false, q.analysis, q.source);
}

// --- 加载题目 ---
function loadQuestion() {
  answered = false;
  const q = questions[currentIndex];

  document.getElementById('qProgress').textContent = (currentIndex + 1) + '/' + questions.length;
  document.getElementById('progressFill').style.width = (currentIndex / questions.length * 100) + '%';
  document.getElementById('qCategory').textContent = q.icon + ' ' + q.category + ' · ' + q.difficulty + ' · ' + q.rumorType;
  document.getElementById('qTitle').textContent = q.title;
  document.getElementById('qClue').textContent = q.clue;

  document.getElementById('choiceRow').style.display = 'flex';
  document.getElementById('feedbackPanel').style.display = 'none';

  startTimer();
}

// --- 提交答案 ---
function submitAnswer(userAnswer) {
  if (answered) return;
  answered = true;
  stopTimer();

  const q = questions[currentIndex];
  const isCorrect = (userAnswer === q.answer);
  const timeUsed = TIME_LIMIT - timeLeft;
  totalTime += timeUsed;

  if (isCorrect) {
    correctCount++;
    streak++;
    if (streak > maxStreak) maxStreak = streak;
    // 每题10分基础 + 连击加分
    let bonus = 0;
    if (streak >= 6) bonus = 8;
    else if (streak >= 4) bonus = 5;
    else if (streak >= 2) bonus = 3;
    score = Math.min(100, score + 10 + bonus);

    if (streak >= 2) {
      const badge = document.getElementById('streakBadge');
      badge.style.display = 'inline';
      document.getElementById('streakCount').textContent = streak;
      badge.style.animation = 'none';
      badge.offsetHeight;
      badge.style.animation = 'streakPulse 0.5s ease';
    }
  } else {
    streak = 0;
    wrongCount++;
    document.getElementById('streakBadge').style.display = 'none';
  }

  document.getElementById('liveScore').textContent = score;
  document.getElementById('progressFill').style.width = ((currentIndex + 1) / questions.length * 100) + '%';

  showFeedback(isCorrect, q.analysis, q.source);

  if (currentIndex >= questions.length - 1) {
    document.getElementById('btnNextLabel').textContent = '查看调查结论';
  }
}

// --- 显示反馈 ---
function showFeedback(isCorrect, analysis, source) {
  const panel = document.getElementById('feedbackPanel');
  document.getElementById('choiceRow').style.display = 'none';
  panel.style.display = 'block';

  if (isCorrect) {
    panel.className = 'feedback-panel correct';
    document.getElementById('fbIcon').textContent = '🎯';
    document.getElementById('fbText').textContent = '判断正确！';
    if (streak >= 4) {
      document.getElementById('fbText').textContent = '连战连捷！侦探的直觉锐不可当！';
    } else if (streak >= 2) {
      document.getElementById('fbText').textContent = '判断正确！状态正佳，继续保持！';
    }
  } else {
    panel.className = 'feedback-panel wrong';
    document.getElementById('fbIcon').textContent = '🔍';
    document.getElementById('fbText').textContent = '判断有误，来看看真相';
  }

  document.getElementById('fbAnalysis').innerHTML =
    '<p>' + analysis + '</p>' +
    '<p class="fb-source">来源：' + source + '</p>';

  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// --- 下一题 ---
function nextQuestion() {
  stopTimer();
  if (currentIndex < questions.length - 1) {
    currentIndex++;
    loadQuestion();
    document.getElementById('page-question').scrollTop = 0;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    showResult();
  }
}

// --- 显示结果 ---
function showResult() {
  goToPage('result');

  const percentage = score / 100;
  const ringFg = document.getElementById('scoreRing');
  const srCircum = 2 * Math.PI * 68;
  ringFg.style.strokeDasharray = srCircum;
  ringFg.style.strokeDashoffset = srCircum;
  ringFg.style.transition = 'none';

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      ringFg.style.transition = 'stroke-dashoffset 1.5s ease';
      ringFg.style.strokeDashoffset = srCircum * (1 - percentage);
    });
  });

  animateNumber('srNumber', 0, score, 1200);

  let rankName, rankIcon, rankEval;
  if (score <= 30) {
    rankName = '新闻小白';
    rankIcon = '📰';
    rankEval = '网络信息真假难辨，你还需要系统提升辨别能力。记住三个关键习惯：看来源、查原文、不急着转发。';
  } else if (score <= 50) {
    rankName = '见习观察员';
    rankIcon = '🔎';
    rankEval = '你已经有了基本警觉，但对复杂谣言还不够敏锐。多关注官方辟谣平台，建立核实信息的习惯。';
  } else if (score <= 70) {
    rankName = '进阶调查员';
    rankIcon = '👀';
    rankEval = '你已经具备较好的判断能力，大多数常见谣言骗不了你。面对AI深度伪造类内容时还需要更谨慎。';
  } else if (score <= 90) {
    rankName = '信息侦探';
    rankIcon = '🕵️';
    rankEval = '优秀！你的新闻辨别能力超过了大多数人。遇到可疑信息时，你已经形成了"先查证、再判断"的思维习惯。';
  } else {
    rankName = '新闻鉴别大师';
    rankIcon = '🏅';
    rankEval = '顶级水平！你拥有系统性的信息核查能力，能够从信息来源、证据链条、表达方式等多个维度发现关键信号。你就是朋友圈的"人肉辟谣机"！';
  }

  document.getElementById('rankName').textContent = rankName;
  document.getElementById('rankIcon').textContent = rankIcon;
  document.getElementById('rankEval').textContent = rankEval;

  document.getElementById('statCorrect').textContent = correctCount;
  document.getElementById('statWrong').textContent = wrongCount;
  document.getElementById('statMaxStreak').textContent = maxStreak;
  const total = correctCount + wrongCount;
  const avgTime = total > 0 ? Math.round(totalTime / total) : 0;
  document.getElementById('statAvgTime').textContent = avgTime + 's';

  if (score >= 70) {
    launchConfetti();
  }

  document.getElementById('shareScore').textContent = score + '分';
  document.getElementById('shareRank').textContent = rankName;

  setTimeout(() => {
    goToPage('share');
    generateQRCode();
  }, 3000);
}

// --- 数字滚动动画 ---
function animateNumber(elId, from, to, duration) {
  const el = document.getElementById(elId);
  const start = performance.now();
  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(from + (to - from) * eased);
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// --- 撒花 ---
function launchConfetti() {
  const container = document.getElementById('confetti');
  const colors = ['#F59E0B', '#EF4444', '#22C55E', '#3B82F6', '#EC4899', '#8B5CF6', '#FACC15'];
  for (let i = 0; i < 60; i++) {
    const piece = document.createElement('div');
    piece.className = 'confetti-piece';
    piece.style.left = Math.random() * 100 + '%';
    piece.style.top = -(Math.random() * 40) + 'px';
    piece.style.background = colors[Math.floor(Math.random() * colors.length)];
    piece.style.width = (6 + Math.random() * 10) + 'px';
    piece.style.height = (6 + Math.random() * 10) + 'px';
    piece.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
    piece.style.animationDuration = (2 + Math.random() * 3) + 's';
    piece.style.animationDelay = Math.random() * 0.8 + 's';
    container.appendChild(piece);
    setTimeout(() => piece.remove(), 4000);
  }
}

// --- QR 码 ---
function generateQRCode() {
  const img = document.getElementById('qrImage');
  const url = window.location.href;
  const qrUrl = 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=' + encodeURIComponent(url);
  img.src = qrUrl;
  img.onerror = function() {
    img.style.display = 'none';
    const hint = document.querySelector('.qr-hint');
    if (hint) {
      hint.textContent = '请部署后使用草料二维码(cli.im)生成二维码';
      hint.style.color = '#F59E0B';
    }
  };
}

// --- 复制链接 ---
function copyLink() {
  const fb = document.getElementById('copyFeedback');
  const url = window.location.href;
  const showMsg = (msg, color) => {
    fb.textContent = msg;
    fb.style.color = color;
    setTimeout(() => { fb.textContent = ''; }, 3000);
  };
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(url).then(
      () => showMsg('链接已复制，可分享给朋友！', '#22C55E'),
      () => fallbackCopy(url, showMsg)
    );
  } else {
    fallbackCopy(url, showMsg);
  }
}

function fallbackCopy(text, showMsg) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.left = '-9999px';
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand('copy');
    showMsg('链接已复制，可分享给朋友！', '#22C55E');
  } catch (e) {
    showMsg('请手动复制浏览器地址栏链接', '#EF4444');
  }
  document.body.removeChild(ta);
}

// --- 重新开始 ---
function restartGame() {
  currentIndex = 0;
  score = 0;
  streak = 0;
  maxStreak = 0;
  correctCount = 0;
  wrongCount = 0;
  totalTime = 0;
  answered = false;
  document.getElementById('liveScore').textContent = '0';
  document.getElementById('streakBadge').style.display = 'none';
  loadQuestion();
  goToPage('question');
}

// --- 初始化 ---
document.addEventListener('DOMContentLoaded', () => {
  initParticles();
  document.getElementById('progressFill').style.width = '0%';
});
