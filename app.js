/* ========================================
   ChemSpark 極 — App Logic
   ======================================== */

(() => {
  'use strict';

  // ── Chapter Registry ──
  const CHAPTERS = [
    { id: 'ch1-1', file: 'questions/ch1-1.json', title: '物質の構成' },
    { id: 'ch1-2', file: 'questions/ch1-2.json', title: '物質の構成粒子' },
    { id: 'ch1-3', file: 'questions/ch1-3.json', title: '化学結合' },
    { id: 'ch1-4', file: 'questions/ch1-4.json', title: '物質量と化学反応式' },
    { id: 'ch2-1', file: 'questions/ch2-1.json', title: '物質の三態と状態変化' },
    { id: 'ch2-2', file: 'questions/ch2-2.json', title: '気体' },
    { id: 'ch2-3', file: 'questions/ch2-3.json', title: '溶液' },
    { id: 'ch3-1', file: 'questions/ch3-1.json', title: '化学反応とエネルギー' },
    { id: 'ch3-2', file: 'questions/ch3-2.json', title: '化学反応の速さとしくみ' },
    { id: 'ch3-3', file: 'questions/ch3-3.json', title: '化学平衡' },
    { id: 'ch3-4', file: 'questions/ch3-4.json', title: '酸と塩基の反応' },
    { id: 'ch3-5', file: 'questions/ch3-5.json', title: '酸化還元反応と電池・電気分解' },
    { id: 'ch4-1', file: 'questions/ch4-1.json', title: '非金属元素' },
    { id: 'ch4-2', file: 'questions/ch4-2.json', title: '金属元素(I)－典型元素－' },
    { id: 'ch4-3', file: 'questions/ch4-3.json', title: '金属元素(II)－遷移元素－' },
    { id: 'ch4-4', file: 'questions/ch4-4.json', title: '無機物質と人間生活' },
    { id: 'ch5-1', file: 'questions/ch5-1.json', title: '有機化合物の分類と分析' },
    { id: 'ch5-2', file: 'questions/ch5-2.json', title: '脂肪族炭化水素' },
    { id: 'ch5-3', file: 'questions/ch5-3.json', title: 'アルコールと関連化合物' },
    { id: 'ch5-4', file: 'questions/ch5-4.json', title: '芳香族化合物' },
    { id: 'ch5-5', file: 'questions/ch5-5.json', title: '有機化合物と人間生活' },
    { id: 'ch6-1', file: 'questions/ch6-1.json', title: '天然有機化合物' },
    { id: 'ch6-2', file: 'questions/ch6-2.json', title: '合成高分子化合物' },
    { id: 'ch6-3', file: 'questions/ch6-3.json', title: '高分子化合物と人間生活' },
  ];

  const CATEGORY_LABELS = {
    definition: '定義',
    property: '性質',
    classification: '分類',
    procedure: '手順',
    confusion: '混同',
    mnemonic: '語呂合わせ',
    comprehensive: '総合',
  };

  const CATEGORY_EMOJI = {
    definition: '🔵',
    property: '🟢',
    classification: '🟡',
    procedure: '🟠',
    confusion: '🔴',
    mnemonic: '🟣',
    comprehensive: '⚫',
  };

  const DIFFICULTY_LABELS = ['', '★', '★★', '★★★', '★★★★', '★★★★★'];

  // ── State ──
  let state = {
    currentPage: 'top',
    mode: 'quiz', // 'quiz' or 'listen'
    chapterData: {},
    currentChapter: null,
    questions: [],
    currentIndex: 0,
    answered: false,
    score: 0,
    results: [],
    ttsEnabled: false,
    shuffled: false,
    progress: loadProgress(),
    // Listen mode state
    listenPlaying: false,
    listenPhase: 'idle', // 'idle', 'question', 'choices', 'answer', 'pause'
    listenSpeed: 1.0,
    listenAbort: null,
  };

  // ── DOM Refs ──
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  const pages = {
    top: $('#page-top'),
    quiz: $('#page-quiz'),
    listen: $('#page-listen'),
    result: $('#page-result'),
  };

  // ── Progress Persistence ──
  function loadProgress() {
    try {
      return JSON.parse(localStorage.getItem('chemspark_progress') || '{}');
    } catch { return {}; }
  }

  function saveProgress() {
    localStorage.setItem('chemspark_progress', JSON.stringify(state.progress));
  }

  function getChapterProgress(chId) {
    const p = state.progress[chId];
    if (!p) return { solved: 0, correct: 0 };
    return p;
  }

  function updateChapterProgress(chId, solved, correct) {
    if (!state.progress[chId]) state.progress[chId] = { solved: 0, correct: 0 };
    const p = state.progress[chId];
    p.solved = Math.max(p.solved, solved);
    p.correct = Math.max(p.correct, correct);
    saveProgress();
  }

  // ── Navigation ──
  function showPage(name) {
    Object.values(pages).forEach(p => p.classList.remove('active'));
    pages[name].classList.add('active');
    state.currentPage = name;
    window.scrollTo(0, 0);
  }

  // ── Data Loading ──
  async function loadChapter(chId) {
    if (state.chapterData[chId]) return state.chapterData[chId];
    const ch = CHAPTERS.find(c => c.id === chId);
    if (!ch) throw new Error('Chapter not found: ' + chId);
    const res = await fetch(ch.file);
    if (!res.ok) throw new Error('Failed to load: ' + ch.file);
    const data = await res.json();
    state.chapterData[chId] = data;
    return data;
  }

  // ── Top Page ──
  function renderTopPage() {
    // Stats
    let totalQ = 0, totalSolved = 0, totalCorrect = 0;
    CHAPTERS.forEach(ch => {
      totalQ += 50;
      const p = getChapterProgress(ch.id);
      totalSolved += p.solved;
      totalCorrect += p.correct;
    });
    $('#stat-total').textContent = totalQ;
    $('#stat-solved').textContent = totalSolved;
    $('#stat-accuracy').textContent = totalSolved > 0
      ? Math.round(totalCorrect / totalSolved * 100) + '%'
      : '—';

    // Chapter List
    const grid = $('#chapter-list');
    grid.innerHTML = '';
    CHAPTERS.forEach(ch => {
      const prog = getChapterProgress(ch.id);
      const pct = Math.round(prog.solved / 50 * 100);

      const card = document.createElement('div');
      card.className = 'chapter-card';
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');
      card.innerHTML = `
        <div class="chapter-number">${ch.id.replace('ch', '')}</div>
        <div class="chapter-info">
          <div class="chapter-title">${ch.title}</div>
          <div class="chapter-meta">50問 ・ ${prog.solved > 0 ? prog.solved + '問解答済 ・ ' + Math.round(prog.correct / Math.max(prog.solved,1) * 100) + '%正答' : '未着手'}</div>
          <div class="chapter-progress-bar">
            <div class="chapter-progress-fill" style="width:${pct}%"></div>
          </div>
        </div>
        <span class="material-symbols-rounded chapter-arrow">chevron_right</span>
      `;
      card.addEventListener('click', () => {
        if (state.mode === 'listen') {
          startListen(ch.id);
        } else {
          startQuiz(ch.id);
        }
      });
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          if (state.mode === 'listen') startListen(ch.id);
          else startQuiz(ch.id);
        }
      });
      grid.appendChild(card);
    });
  }

  // ── Quiz ──
  async function startQuiz(chId) {
    try {
      const data = await loadChapter(chId);
      state.currentChapter = chId;
      state.questions = [...data.questions];
      if (state.shuffled) shuffleArray(state.questions);
      state.currentIndex = 0;
      state.score = 0;
      state.results = [];
      state.answered = false;

      const ch = CHAPTERS.find(c => c.id === chId);
      $('#quiz-chapter-label').textContent = ch.id.replace('ch', '') + ' ' + ch.title;

      showPage('quiz');
      renderQuestion();
    } catch (err) {
      console.error(err);
      alert('データの読み込みに失敗しました: ' + err.message);
    }
  }

  function renderQuestion() {
    const q = state.questions[state.currentIndex];
    const total = state.questions.length;
    const idx = state.currentIndex;
    state.answered = false;

    // Progress
    $('#quiz-progress').textContent = `${idx + 1} / ${total}`;
    $('#progress-bar').style.width = `${(idx / total) * 100}%`;

    // Badges
    $('#q-category').textContent = (CATEGORY_EMOJI[q.category] || '') + ' ' + (CATEGORY_LABELS[q.category] || q.category);
    $('#q-difficulty').textContent = DIFFICULTY_LABELS[q.difficulty] || '';
    $('#q-type').textContent = q.question_type === 'correct' ? '正しいものを選べ' : '誤りを選べ';

    // Question text
    $('#q-text').textContent = q.question;

    // TTS
    if (state.ttsEnabled) speak(q.question);

    // Choices
    const list = $('#choices-list');
    list.innerHTML = '';
    q.choices.forEach((c, i) => {
      const btn = document.createElement('button');
      btn.className = 'choice-btn';
      btn.innerHTML = `
        <span class="choice-label">${c.label}</span>
        <span class="choice-text">${c.text}</span>
      `;
      btn.addEventListener('click', () => selectChoice(i));
      list.appendChild(btn);
    });

    // Hide explanation & next
    $('#explanation-card').classList.add('hidden');
    $('#btn-next').classList.add('hidden');

    // Animation
    const card = $('#question-card');
    card.style.animation = 'none';
    // eslint-disable-next-line no-unused-expressions
    card.offsetHeight;
    card.style.animation = '';
  }

  function selectChoice(idx) {
    if (state.answered) return;
    state.answered = true;

    const q = state.questions[state.currentIndex];
    const chosen = q.choices[idx];
    const isCorrect = chosen.is_correct;

    if (isCorrect) state.score++;
    state.results.push({ qId: q.id, correct: isCorrect });

    // Mark buttons
    const btns = $$('.choice-btn');
    btns.forEach((btn, i) => {
      btn.classList.add('disabled');
      if (q.choices[i].is_correct) btn.classList.add('correct');
      if (i === idx && !isCorrect) btn.classList.add('wrong');
    });

    // Show explanation
    const expCard = $('#explanation-card');
    expCard.classList.remove('hidden');

    $('#result-icon').innerHTML = isCorrect
      ? '<span style="color:var(--success)">🎉</span>'
      : '<span style="color:var(--error)">❌</span>';

    $('#explanation-text').textContent = q.explanation;

    // Trap info
    const trapDiv = $('#trap-info');
    trapDiv.innerHTML = '';
    q.choices.forEach(c => {
      if (c.trap_type && c.trap_detail) {
        const trapEl = document.createElement('div');
        trapEl.style.marginBottom = '6px';
        trapEl.innerHTML = `<span class="trap-label">${c.trap_type}</span> 選択肢${c.label}: ${c.trap_detail}`;
        trapDiv.appendChild(trapEl);
      }
    });

    // Mnemonic
    const mnEl = $('#mnemonic-info');
    if (q.mnemonic) {
      mnEl.classList.remove('hidden');
      $('#mnemonic-text').textContent = q.mnemonic;
    } else {
      mnEl.classList.add('hidden');
    }

    // TTS explanation
    if (state.ttsEnabled) {
      const msg = isCorrect ? '正解です。' : '不正解です。';
      speak(msg + q.explanation);
    }

    // Show next button
    const nextBtn = $('#btn-next');
    nextBtn.classList.remove('hidden');
    nextBtn.textContent = state.currentIndex < state.questions.length - 1 ? '次の問題 →' : '結果を見る →';

    // Smooth scroll to explanation
    setTimeout(() => {
      expCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  }

  function nextQuestion() {
    if (state.currentIndex < state.questions.length - 1) {
      state.currentIndex++;
      renderQuestion();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      finishQuiz();
    }
  }

  function finishQuiz() {
    const total = state.questions.length;
    const score = state.score;
    const pct = Math.round(score / total * 100);

    updateChapterProgress(state.currentChapter, total, score);

    showPage('result');

    const circle = $('#result-circle');
    circle.style.background = `conic-gradient(var(--accent) ${pct}%, var(--bg-card) ${pct}%)`;

    $('#result-score').textContent = score;
    $('#result-total').textContent = '/ ' + total;

    let heading, sub;
    if (pct >= 90) { heading = '🏆 素晴らしい！'; sub = '化学を極めつつあります。'; }
    else if (pct >= 70) { heading = '👏 よくできました！'; sub = 'もう少しで完璧です。間違えた問題を復習しましょう。'; }
    else if (pct >= 50) { heading = '📖 もう少し！'; sub = '基礎を固めてから再挑戦してみましょう。'; }
    else { heading = '💪 がんばろう！'; sub = '解説をよく読んで理解を深めましょう。'; }

    $('#result-heading').textContent = heading;
    $('#result-sub').textContent = sub;

    const grid = $('#result-detail-grid');
    grid.innerHTML = '';

    const categoryStats = {};
    state.results.forEach((r, i) => {
      const q = state.questions[i];
      if (!categoryStats[q.category]) categoryStats[q.category] = { total: 0, correct: 0 };
      categoryStats[q.category].total++;
      if (r.correct) categoryStats[q.category].correct++;
    });

    Object.entries(categoryStats).forEach(([cat, s]) => {
      const item = document.createElement('div');
      item.className = 'result-detail-item';
      const catPct = Math.round(s.correct / s.total * 100);
      item.innerHTML = `
        <div class="result-detail-value">${catPct}%</div>
        <div class="result-detail-label">${CATEGORY_EMOJI[cat] || ''} ${CATEGORY_LABELS[cat] || cat} (${s.correct}/${s.total})</div>
      `;
      grid.appendChild(item);
    });
  }

  // ── TTS Engine ──
  function speak(text) {
    return new Promise((resolve) => {
      if (!('speechSynthesis' in window)) { resolve(); return; }
      window.speechSynthesis.cancel();
      const utt = new SpeechSynthesisUtterance(text);
      utt.lang = 'ja-JP';
      utt.rate = state.listenSpeed || 0.95;
      utt.pitch = 1.0;

      const voices = window.speechSynthesis.getVoices();
      const jaVoice = voices.find(v => v.lang.startsWith('ja'));
      if (jaVoice) utt.voice = jaVoice;

      utt.onend = resolve;
      utt.onerror = resolve;
      window.speechSynthesis.speak(utt);
    });
  }

  function stopSpeaking() {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  }

  // ── Listen Mode ──
  async function startListen(chId) {
    try {
      const data = await loadChapter(chId);
      state.currentChapter = chId;
      state.questions = [...data.questions];
      if (state.shuffled) shuffleArray(state.questions);
      state.currentIndex = 0;
      state.listenPlaying = false;

      const ch = CHAPTERS.find(c => c.id === chId);
      $('#listen-chapter-label').textContent = ch.id.replace('ch', '') + ' ' + ch.title;

      showPage('listen');
      renderListenQuestion();
      updateListenUI();
    } catch (err) {
      console.error(err);
      alert('データの読み込みに失敗しました: ' + err.message);
    }
  }

  function renderListenQuestion() {
    const q = state.questions[state.currentIndex];
    const total = state.questions.length;
    const idx = state.currentIndex;

    // Progress
    $('#listen-progress').textContent = `${idx + 1} / ${total}`;
    $('#listen-progress-bar').style.width = `${(idx / total) * 100}%`;
    $('#listen-question-num').textContent = `問題 ${idx + 1} / ${total}`;

    // Prev/next buttons
    $('#listen-btn-prev').disabled = idx === 0;

    // Question transcript
    $('#listen-q-text').textContent = q.question;

    // Choices transcript
    const choicesList = $('#listen-choices-text');
    choicesList.innerHTML = '';
    q.choices.forEach(c => {
      const div = document.createElement('div');
      div.className = 'listen-choice-item';
      div.textContent = `${c.label}. ${c.text}`;
      div.dataset.label = c.label;
      choicesList.appendChild(div);
    });

    // Hide answer section
    const ansSection = $('#listen-section-answer');
    ansSection.classList.add('hidden');
    $('#listen-answer-text').textContent = '';

    // Reset active highlights
    $$('.listen-section').forEach(s => s.classList.remove('active'));
    $$('.listen-choice-item').forEach(c => {
      c.classList.remove('speaking', 'correct-answer');
    });

    // Status
    $('#listen-status').textContent = state.listenPlaying ? '再生中...' : 'タップして再生';
  }

  function updateListenUI() {
    const orb = $('#listen-orb');
    const icon = $('#listen-play-icon');
    if (state.listenPlaying) {
      orb.classList.add('playing');
      icon.textContent = 'pause';
    } else {
      orb.classList.remove('playing');
      icon.textContent = 'play_arrow';
    }
  }

  async function playListenSequence() {
    if (state.listenPlaying) return;
    state.listenPlaying = true;
    state.listenAbort = false;
    updateListenUI();

    const q = state.questions[state.currentIndex];

    // Utility: wait for ms or abort
    const wait = (ms) => new Promise(resolve => {
      const timer = setTimeout(resolve, ms);
      const checkAbort = setInterval(() => {
        if (state.listenAbort) {
          clearTimeout(timer);
          clearInterval(checkAbort);
          resolve();
        }
      }, 100);
    });

    // Phase 1: Read question
    if (state.listenAbort) { finishListenPhase(); return; }
    state.listenPhase = 'question';
    $('#listen-status').textContent = '問題文を読み上げ中...';
    $('#listen-section-q').classList.add('active');
    await speak(q.question);
    $('#listen-section-q').classList.remove('active');

    await wait(500);
    if (state.listenAbort) { finishListenPhase(); return; }

    // Phase 2: Read question type hint
    const typeHint = q.question_type === 'correct' ? '正しいものを選んでください。' : '誤りを含むものを選んでください。';
    await speak(typeHint);
    await wait(300);
    if (state.listenAbort) { finishListenPhase(); return; }

    // Phase 3: Read each choice
    state.listenPhase = 'choices';
    $('#listen-status').textContent = '選択肢を読み上げ中...';
    $('#listen-section-choices').classList.add('active');

    for (let i = 0; i < q.choices.length; i++) {
      if (state.listenAbort) { finishListenPhase(); return; }
      const c = q.choices[i];
      // Highlight current choice
      const items = $$('.listen-choice-item');
      items.forEach(el => el.classList.remove('speaking'));
      if (items[i]) items[i].classList.add('speaking');

      await speak(`選択肢${c.label}。${c.text}`);
      await wait(400);
    }

    $$('.listen-choice-item').forEach(el => el.classList.remove('speaking'));
    $('#listen-section-choices').classList.remove('active');

    await wait(800);
    if (state.listenAbort) { finishListenPhase(); return; }

    // Phase 4: Thinking time
    $('#listen-status').textContent = '考えてください...';
    await speak('考えてください。');
    await wait(3000);
    if (state.listenAbort) { finishListenPhase(); return; }

    // Phase 5: Reveal answer
    state.listenPhase = 'answer';
    const correctChoice = q.choices.find(c => c.is_correct);
    const answerText = `正解は選択肢${correctChoice.label}です。${q.explanation}`;

    // Show answer section
    const ansSection = $('#listen-section-answer');
    ansSection.classList.remove('hidden');
    ansSection.classList.add('active');
    $('#listen-answer-text').textContent = answerText;

    // Highlight correct choice
    const items = $$('.listen-choice-item');
    items.forEach(el => {
      if (el.dataset.label === correctChoice.label) {
        el.classList.add('correct-answer');
      }
    });

    $('#listen-status').textContent = '正解・解説を読み上げ中...';
    await speak(answerText);
    ansSection.classList.remove('active');

    await wait(1000);
    if (state.listenAbort) { finishListenPhase(); return; }

    // Auto-advance to next question
    if (state.currentIndex < state.questions.length - 1 && !state.listenAbort) {
      state.currentIndex++;
      state.listenPlaying = false;
      renderListenQuestion();
      // Auto-play next
      setTimeout(() => {
        if (state.currentPage === 'listen') playListenSequence();
      }, 500);
    } else {
      finishListenPhase();
      $('#listen-status').textContent = '全問題を読み上げ完了！';
    }
  }

  function finishListenPhase() {
    state.listenPlaying = false;
    state.listenPhase = 'idle';
    state.listenAbort = false;
    stopSpeaking();
    updateListenUI();
    $('#listen-status').textContent = 'タップして再生';
    $$('.listen-section').forEach(s => s.classList.remove('active'));
    $$('.listen-choice-item').forEach(c => c.classList.remove('speaking'));
  }

  function toggleListenPlay() {
    if (state.listenPlaying) {
      // Stop
      state.listenAbort = true;
      stopSpeaking();
      finishListenPhase();
    } else {
      playListenSequence();
    }
  }

  // ── Shuffle ──
  function shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  }

  // ── Event Bindings ──
  function bindEvents() {
    // Mode toggle
    $('#mode-quiz').addEventListener('click', () => {
      state.mode = 'quiz';
      $('#mode-quiz').classList.add('active');
      $('#mode-listen').classList.remove('active');
    });
    $('#mode-listen').addEventListener('click', () => {
      state.mode = 'listen';
      $('#mode-listen').classList.add('active');
      $('#mode-quiz').classList.remove('active');
    });

    // Back (quiz)
    $('#btn-back').addEventListener('click', () => {
      stopSpeaking();
      showPage('top');
      renderTopPage();
    });

    // Back (listen)
    $('#listen-btn-back').addEventListener('click', () => {
      state.listenAbort = true;
      stopSpeaking();
      finishListenPhase();
      showPage('top');
      renderTopPage();
    });

    // TTS toggle (quiz mode)
    $('#btn-tts').addEventListener('click', () => {
      state.ttsEnabled = !state.ttsEnabled;
      $('#btn-tts').classList.toggle('active', state.ttsEnabled);
      if (!state.ttsEnabled) stopSpeaking();
    });

    // Shuffle toggle
    $('#btn-shuffle').addEventListener('click', () => {
      state.shuffled = !state.shuffled;
      $('#btn-shuffle').classList.toggle('active', state.shuffled);
    });

    // Next
    $('#btn-next').addEventListener('click', nextQuestion);

    // Result buttons
    $('#btn-retry').addEventListener('click', () => {
      startQuiz(state.currentChapter);
    });
    $('#btn-home').addEventListener('click', () => {
      showPage('top');
      renderTopPage();
    });

    // Listen controls
    $('#listen-btn-play').addEventListener('click', toggleListenPlay);

    $('#listen-btn-prev').addEventListener('click', () => {
      if (state.currentIndex > 0) {
        state.listenAbort = true;
        stopSpeaking();
        finishListenPhase();
        state.currentIndex--;
        renderListenQuestion();
      }
    });

    $('#listen-btn-next-q').addEventListener('click', () => {
      if (state.currentIndex < state.questions.length - 1) {
        state.listenAbort = true;
        stopSpeaking();
        finishListenPhase();
        state.currentIndex++;
        renderListenQuestion();
      }
    });

    // Speed control
    const speeds = [0.8, 1.0, 1.2, 1.5];
    let speedIdx = 1;
    $('#listen-btn-speed').addEventListener('click', () => {
      speedIdx = (speedIdx + 1) % speeds.length;
      state.listenSpeed = speeds[speedIdx];
      $('.speed-label').textContent = speeds[speedIdx] + 'x';
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (state.currentPage === 'quiz') {
        if (!state.answered && e.key >= '1' && e.key <= '4') {
          const idx = parseInt(e.key) - 1;
          const btns = $$('.choice-btn');
          if (btns[idx]) selectChoice(idx);
        }
        if (state.answered && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          nextQuestion();
        }
      }
      if (state.currentPage === 'listen') {
        if (e.key === ' ') {
          e.preventDefault();
          toggleListenPlay();
        }
      }
    });

    // Preload voices for TTS
    if ('speechSynthesis' in window) {
      window.speechSynthesis.getVoices();
      window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
      };
    }
  }

  // ── Init ──
  function init() {
    bindEvents();
    renderTopPage();
    showPage('top');
  }

  // Boot
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
