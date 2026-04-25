// ============================================================
// ChemSpark 極 — main controller (redesigned)
// ============================================================

const DATA_PATH = 'questions';
const AUDIO_PATH = 'audio';

const SPEED_MAP = {
  slow: { rate: 1.11, label: 'ゆっくり' },
  natural: { rate: 1.25, label: 'ナチュラル' },
  fast: { rate: 1.43, label: '早め' },
};

const CATEGORY_LABELS = {
  definition: '定義',
  property: '性質',
  classification: '分類',
  procedure: '手順',
  confusion: '混同注意',
  mnemonic: '語呂合わせ',
  comprehensive: '総合',
};

// 6 major chapters (教科書の「編」→「章」), each with sections (「章」→「節」)
const CHAPTER_GROUPS = [
  {
    id: 'group1', num: '1', title: '物質の構成と化学結合', icon: '🔬',
    sections: [
      { id: 'ch1-1', num: '1', title: '物質の構成', enabled: true },
      { id: 'ch1-2', num: '2', title: '物質の構成粒子', enabled: true },
      { id: 'ch1-3', num: '3', title: '化学結合', enabled: true },
      { id: 'ch1-4', num: '4', title: '物質量と化学反応式', enabled: true },
    ],
  },
  {
    id: 'group2', num: '2', title: '物質の状態', icon: '🧪',
    sections: [
      { id: 'ch2-1', num: '1', title: '物質の三態と状態変化', enabled: true },
      { id: 'ch2-2', num: '2', title: '気体の法則', enabled: true },
      { id: 'ch2-3', num: '3', title: '溶液の性質', enabled: true },
    ],
  },
  {
    id: 'group3', num: '3', title: '物質の変化', icon: '⚡',
    sections: [
      { id: 'ch3-1', num: '1', title: '化学反応とエネルギー', enabled: true },
      { id: 'ch3-2', num: '2', title: '化学反応の速さとしくみ', enabled: true },
      { id: 'ch3-3', num: '3', title: '化学平衡', enabled: true },
      { id: 'ch3-4', num: '4', title: '酸と塩基の反応', enabled: true },
      { id: 'ch3-5', num: '5', title: '酸化還元反応', enabled: true },
    ],
  },
  {
    id: 'group4', num: '4', title: '無機物質', icon: '💎',
    sections: [
      { id: 'ch4-1', num: '1', title: '非金属元素', enabled: true },
      { id: 'ch4-2', num: '2', title: '典型金属元素', enabled: true },
      { id: 'ch4-3', num: '3', title: '遷移元素', enabled: true },
      { id: 'ch4-4', num: '4', title: '無機物質と人間生活', enabled: true },
    ],
  },
  {
    id: 'group5', num: '5', title: '有機化合物', icon: '🧬',
    sections: [
      { id: 'ch5-1', num: '1', title: '有機化合物の分類と分析', enabled: true },
      { id: 'ch5-2', num: '2', title: '脂肪族炭化水素', enabled: true },
      { id: 'ch5-3', num: '3', title: 'アルコールと関連化合物', enabled: true },
      { id: 'ch5-4', num: '4', title: '芳香族化合物', enabled: true },
      { id: 'ch5-5', num: '5', title: '高分子化合物の基礎', enabled: true },
    ],
  },
  {
    id: 'group6', num: '6', title: '天然有機化合物と高分子化合物', icon: '🌿',
    sections: [
      { id: 'ch6-1', num: '1', title: '天然高分子化合物', enabled: true },
      { id: 'ch6-2', num: '2', title: '合成高分子化合物', enabled: true },
      { id: 'ch6-3', num: '3', title: '高分子化合物と人間生活', enabled: true },
    ],
  },
];

// Flat list for lookup convenience
const CHAPTERS = CHAPTER_GROUPS.flatMap(g =>
  g.sections.map(s => ({ ...s, title: `第${g.num}章-${s.num} ${s.title}`, groupTitle: g.title }))
);

// ------------------------------------------------------------
// state
// ------------------------------------------------------------
const state = {
  chapter: 'ch1-1',
  chapterData: null,
  questionList: [],
  currentIndex: 0,
  answers: [],
  answered: false,
  shuffledChoices: [],
  options: loadOptions(),
  audio: {
    current: null,
    token: 0,
  },
};

// ------------------------------------------------------------
// storage helpers
// ------------------------------------------------------------
function loadOptions() {
  try {
    const stored = JSON.parse(localStorage.getItem('cs_opts') || '{}');
    return {
      shuffleQuestions: stored.shuffleQuestions ?? false,
      autoPlay: stored.autoPlay ?? true,
      autoNext: stored.autoNext ?? false,
      speed: stored.speed ?? 'slow',
      theme: stored.theme ?? 'dark',
    };
  } catch {
    return { shuffleQuestions: false, autoPlay: true, autoNext: false, speed: 'slow', theme: 'dark' };
  }
}

function saveOptions() {
  localStorage.setItem('cs_opts', JSON.stringify(state.options));
}

function loadHistory() {
  try { return JSON.parse(localStorage.getItem('cs_history') || '{}'); }
  catch { return {}; }
}

function saveHistory(history) {
  localStorage.setItem('cs_history', JSON.stringify(history));
}

function recordSessionResult(chapter, stats) {
  const history = loadHistory();
  const arr = history[chapter] || [];
  arr.push({ ts: Date.now(), ...stats });
  history[chapter] = arr.slice(-20);
  saveHistory(history);
}

// --- Mistake tracking ---
function loadMistakes() {
  try { return JSON.parse(localStorage.getItem('cs_mistakes') || '{}'); }
  catch { return {}; }
}

function saveMistakes(mistakes) {
  localStorage.setItem('cs_mistakes', JSON.stringify(mistakes));
}

function recordMistake(chapter, questionId) {
  const mistakes = loadMistakes();
  if (!mistakes[chapter]) mistakes[chapter] = {};
  mistakes[chapter][questionId] = (mistakes[chapter][questionId] || 0) + 1;
  saveMistakes(mistakes);
}

function getMistakeCount(chapter) {
  const mistakes = loadMistakes();
  return mistakes[chapter] ? Object.keys(mistakes[chapter]).length : 0;
}

function getMistakeIds(chapter) {
  const mistakes = loadMistakes();
  return mistakes[chapter] ? Object.keys(mistakes[chapter]) : [];
}

// --- Session progress (途中保存) ---
function saveSessionProgress() {
  const progress = {
    chapter: state.chapter,
    currentIndex: state.currentIndex,
    answers: state.answers,
    questionIds: state.questionList.map(q => q.id),
    timestamp: Date.now(),
  };
  localStorage.setItem('cs_session', JSON.stringify(progress));
}

function loadSessionProgress() {
  try { return JSON.parse(localStorage.getItem('cs_session') || 'null'); }
  catch { return null; }
}

function clearSessionProgress() {
  localStorage.removeItem('cs_session');
}

// ------------------------------------------------------------
// utils
// ------------------------------------------------------------
function $(sel) { return document.querySelector(sel); }

const KANJI_DIGITS = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
const KANJI_TO_NUM = { 一: 1, 二: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9 };

function buildChoiceRemap(q, shuffled) {
  const origToNew = new Map();
  q.choices.forEach((c, origIdx) => {
    const newIdx = shuffled.findIndex((sc) => sc.choice_id === c.choice_id);
    if (newIdx >= 0) origToNew.set(origIdx + 1, newIdx + 1);
  });
  return origToNew;
}

function remapChoiceRefs(text, q, shuffled) {
  if (!text) return text;
  const map = buildChoiceRemap(q, shuffled);
  return text
    .replace(/選択肢([1-9])/g, (m, d) => {
      const n = parseInt(d, 10);
      const nn = map.get(n);
      return nn ? `選択肢${nn}` : m;
    })
    .replace(/選択肢([一二三四五六七八九])/g, (m, d) => {
      const n = KANJI_TO_NUM[d];
      const nn = map.get(n);
      return nn ? `選択肢${KANJI_DIGITS[nn]}` : m;
    });
}

function shuffle(arr) {
  const out = arr.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

function sleep(ms, token) {
  return new Promise((resolve) => {
    const t = setTimeout(() => resolve(true), ms);
    const check = () => {
      if (state.audio.token !== token) {
        clearTimeout(t);
        resolve(false);
      } else {
        requestAnimationFrame(check);
      }
    };
    requestAnimationFrame(check);
  });
}

function switchScreen(id) {
  document.querySelectorAll('.screen').forEach((s) => {
    s.classList.toggle('active', s.id === id);
  });
  window.scrollTo(0, 0);
}

// ------------------------------------------------------------
// theme
// ------------------------------------------------------------
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  state.options.theme = theme;
  saveOptions();
}

// ------------------------------------------------------------
// audio
// ------------------------------------------------------------
function cancelAudio() {
  state.audio.token++;
  if (state.audio.current) {
    try {
      state.audio.current.pause();
      state.audio.current.currentTime = 0;
    } catch (e) { /* ignore */ }
    state.audio.current = null;
  }
  document.querySelectorAll('.playing').forEach((el) => el.classList.remove('playing'));
}

function playClip(src, token) {
  return new Promise((resolve) => {
    if (state.audio.token !== token) return resolve(false);
    const audio = new Audio(src);
    audio.preservesPitch = true;
    audio.mozPreservesPitch = true;
    audio.webkitPreservesPitch = true;
    audio.playbackRate = SPEED_MAP[state.options.speed].rate;
    state.audio.current = audio;
    audio.addEventListener('ended', () => {
      if (state.audio.current === audio) state.audio.current = null;
      resolve(true);
    });
    audio.addEventListener('error', () => { console.warn('audio error:', src); resolve(false); });
    audio.play().catch((err) => { console.warn('audio play failed:', src, err); resolve(false); });
  });
}

function questionAudioPath(q, filename) {
  return `${AUDIO_PATH}/${state.chapter}/${q.id}/${filename}`;
}

function prefixAudioPath(voice, labelNumber) {
  return `${AUDIO_PATH}/common/${voice}/choice_prefix_${labelNumber}.mp3`;
}

async function playQuestionAudio() {
  cancelAudio();
  const token = state.audio.token;
  const q = state.questionList[state.currentIndex];
  await playClip(questionAudioPath(q, 'question.mp3'), token);
}

async function playAllAudio() {
  cancelAudio();
  const token = state.audio.token;
  const q = state.questionList[state.currentIndex];
  const voice = q.audio_voice;
  await playClip(questionAudioPath(q, 'question.mp3'), token);
  if (state.audio.token !== token) return;
  if (!(await sleep(750, token))) return;
  for (let i = 0; i < state.shuffledChoices.length; i++) {
    if (state.audio.token !== token) return;
    const c = state.shuffledChoices[i];
    const choiceEl = document.querySelector(`.choice-item[data-choice-id="${c.choice_id}"]`);
    choiceEl?.classList.add('playing');
    await playClip(prefixAudioPath(voice, i + 1), token);
    if (state.audio.token !== token) { choiceEl?.classList.remove('playing'); return; }
    await playClip(questionAudioPath(q, `${c.choice_id}.mp3`), token);
    choiceEl?.classList.remove('playing');
    if (state.audio.token !== token) return;
    if (i < state.shuffledChoices.length - 1) {
      if (!(await sleep(350, token))) return;
    }
  }
}

async function playChoiceAudio(choice) {
  cancelAudio();
  const token = state.audio.token;
  const q = state.questionList[state.currentIndex];
  const voice = q.audio_voice;
  const pos = state.shuffledChoices.findIndex((c) => c.choice_id === choice.choice_id);
  if (pos >= 0) {
    await playClip(prefixAudioPath(voice, pos + 1), token);
    if (state.audio.token !== token) return;
  }
  await playClip(questionAudioPath(q, `${choice.choice_id}.mp3`), token);
}

async function playExplanationAudio() {
  cancelAudio();
  const token = state.audio.token;
  const q = state.questionList[state.currentIndex];
  await playClip(questionAudioPath(q, 'explanation.mp3'), token);
}

// ------------------------------------------------------------
// start screen rendering
// ------------------------------------------------------------
function renderChapterList() {
  const list = $('#chapter-list');
  list.innerHTML = '';
  const mistakes = loadMistakes();
  const history = loadHistory();

  for (const group of CHAPTER_GROUPS) {
    // Calculate group-level stats
    const totalMistakes = group.sections.reduce((sum, s) => {
      return sum + (mistakes[s.id] ? Object.keys(mistakes[s.id]).length : 0);
    }, 0);
    const totalSessions = group.sections.reduce((sum, s) => {
      return sum + (history[s.id] ? history[s.id].length : 0);
    }, 0);

    // Accordion panel
    const panel = document.createElement('div');
    panel.className = 'accordion-panel';
    panel.dataset.groupId = group.id;

    // Panel header
    const header = document.createElement('button');
    header.className = 'accordion-header';
    header.innerHTML = `
      <div class="accordion-header-left">
        <span class="accordion-num">第${group.num}章</span>
        <span class="accordion-icon">${group.icon}</span>
      </div>
      <div class="accordion-header-center">
        <span class="accordion-title">${group.title}</span>
        <span class="accordion-meta">
          ${group.sections.length}節 · ${group.sections.length * 50}問
          ${totalMistakes > 0 ? `<span class="accordion-mistakes">🔥${totalMistakes}</span>` : ''}
          ${totalSessions > 0 ? `<span class="accordion-sessions">📊${totalSessions}回</span>` : ''}
        </span>
      </div>
      <span class="accordion-chevron">▾</span>
    `;

    // Panel body (sections)
    const body = document.createElement('div');
    body.className = 'accordion-body';

    for (const sec of group.sections) {
      const btn = document.createElement('button');
      btn.className = 'section-btn';
      btn.dataset.chapterId = sec.id;
      btn.disabled = !sec.enabled;

      const mistakeCount = mistakes[sec.id] ? Object.keys(mistakes[sec.id]).length : 0;
      const sectionHistory = history[sec.id];
      const lastScore = sectionHistory && sectionHistory.length > 0
        ? Math.round((sectionHistory[sectionHistory.length - 1].correct / sectionHistory[sectionHistory.length - 1].total) * 100)
        : null;

      btn.innerHTML = `
        <span class="section-num">第${sec.num}節</span>
        <span class="section-title">${sec.title}</span>
        <span class="section-info">
          <span class="section-qcount">50問</span>
          ${mistakeCount > 0 ? `<span class="mistake-badge">🔥${mistakeCount}</span>` : ''}
          ${lastScore !== null ? `<span class="section-score ${lastScore >= 80 ? 'good' : lastScore >= 60 ? 'mid' : 'low'}">${lastScore}%</span>` : ''}
        </span>
      `;

      btn.addEventListener('click', () => {
        document.querySelectorAll('.section-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.chapter = sec.id;
        openSettingsModal();
      });

      body.appendChild(btn);
    }

    // Toggle accordion
    header.addEventListener('click', () => {
      const isOpen = panel.classList.contains('open');
      // Close all first
      document.querySelectorAll('.accordion-panel').forEach(p => p.classList.remove('open'));
      if (!isOpen) panel.classList.add('open');
    });

    panel.appendChild(header);
    panel.appendChild(body);
    list.appendChild(panel);
  }
}


function renderMistakesSummary() {
  const el = $('#mistakes-summary');
  const mistakes = loadMistakes();
  const chapters = Object.keys(mistakes).filter(k => Object.keys(mistakes[k]).length > 0);
  if (chapters.length === 0) {
    el.innerHTML = '<em style="color:var(--text-muted)">ミスデータなし。演習を進めると記録されます。</em>';
    return;
  }
  const rows = chapters.map((cid) => {
    const count = Object.keys(mistakes[cid]).length;
    const chInfo = CHAPTERS.find(c => c.id === cid);
    const title = chInfo ? chInfo.title : cid;
    return `
      <div class="mistake-row">
        <span class="mistake-row-name">${title}</span>
        <span style="display:flex;align-items:center;gap:0.4rem;">
          <span class="mistake-row-count">${count}問</span>
          <button class="btn-retry-mistakes" data-chapter="${cid}">復習</button>
        </span>
      </div>
    `;
  });
  el.innerHTML = rows.join('');
  // bind retry buttons
  el.querySelectorAll('.btn-retry-mistakes').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const cid = btn.dataset.chapter;
      state.chapter = cid;
      startQuizMistakesOnly(cid);
    });
  });
}

function renderHistory() {
  const history = loadHistory();
  const el = $('#history-summary');
  const chapters = Object.keys(history);
  if (chapters.length === 0) {
    el.innerHTML = '<em style="color:var(--text-muted)">まだ履歴はありません。</em>';
    return;
  }
  const rows = chapters.map((cid) => {
    const sessions = history[cid];
    const last = sessions[sessions.length - 1];
    const best = Math.max(...sessions.map((s) => Math.round((s.correct / s.total) * 100)));
    const chInfo = CHAPTERS.find(c => c.id === cid);
    const title = chInfo ? chInfo.title : cid;
    return `
      <div class="history-row">
        <span>${title} (${sessions.length}回)</span>
        <span>最終: ${last.correct}/${last.total} (${Math.round((last.correct / last.total) * 100)}%) · 最高: ${best}%</span>
      </div>
    `;
  });
  el.innerHTML = rows.join('');
}

// ------------------------------------------------------------
// settings modal
// ------------------------------------------------------------
function openSettingsModal() {
  const modal = $('#settings-modal');
  const chInfo = CHAPTERS.find(c => c.id === state.chapter);
  $('#modal-chapter-name').textContent = chInfo ? chInfo.title : state.chapter;

  const mistakeCount = getMistakeCount(state.chapter);
  $('#mistake-count-label').textContent = `${mistakeCount}問`;
  const mistakeRadio = document.querySelector('input[name="quiz-mode"][value="mistakes"]');
  if (mistakeCount === 0) {
    mistakeRadio.disabled = true;
    mistakeRadio.closest('.radio-card').style.opacity = '0.4';
  } else {
    mistakeRadio.disabled = false;
    mistakeRadio.closest('.radio-card').style.opacity = '1';
  }
  // reset to all
  document.querySelector('input[name="quiz-mode"][value="all"]').checked = true;

  // apply current options
  document.querySelectorAll('.speed-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.speed === state.options.speed);
  });
  $('#modal-shuffle').checked = state.options.shuffleQuestions;
  $('#modal-autoplay').checked = state.options.autoPlay;
  $('#modal-autonext').checked = state.options.autoNext;

  modal.classList.remove('hidden');
}

function closeSettingsModal() {
  $('#settings-modal').classList.add('hidden');
}

// ------------------------------------------------------------
// quiz
// ------------------------------------------------------------
async function startQuiz(questionsOverride = null) {
  const chapter = state.chapter;
  try {
    if (!state.chapterData || state.chapterData.metadata.chapter !== chapter) {
      const resp = await fetch(`${DATA_PATH}/${chapter}.json`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      state.chapterData = await resp.json();
    }
  } catch (err) {
    alert(
      '問題データの読み込みに失敗しました。\n\n' +
      'ブラウザで file:// として直接開いた場合はフェッチが制限されます。\n' +
      '同梱の "serve.py" を実行してから http://localhost:8000 でアクセスしてください。\n\n' +
      `エラー: ${err.message}`,
    );
    return;
  }

  let questions = questionsOverride ?? state.chapterData.questions.slice();
  if (state.options.shuffleQuestions && !questionsOverride) {
    questions = shuffle(questions);
  }

  state.questionList = questions;
  state.currentIndex = 0;
  state.answers = [];
  clearSessionProgress();

  switchScreen('quiz-screen');
  renderCurrentQuestion();
}

async function startQuizMistakesOnly(chapter) {
  state.chapter = chapter;
  try {
    if (!state.chapterData || state.chapterData.metadata.chapter !== chapter) {
      const resp = await fetch(`${DATA_PATH}/${chapter}.json`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      state.chapterData = await resp.json();
    }
  } catch (err) {
    alert(`データ読み込みエラー: ${err.message}`);
    return;
  }

  const mistakeIds = getMistakeIds(chapter);
  if (mistakeIds.length === 0) {
    alert('この章にはミス記録がありません。');
    return;
  }

  const mistakeQs = state.chapterData.questions.filter(q => mistakeIds.includes(q.id));
  startQuiz(mistakeQs);
}

function renderCurrentQuestion() {
  cancelAudio();
  state.answered = false;
  $('#feedback').classList.add('hidden');

  const q = state.questionList[state.currentIndex];

  $('#progress-current').textContent = state.currentIndex + 1;
  $('#progress-total').textContent = state.questionList.length;
  const pct = ((state.currentIndex) / state.questionList.length) * 100;
  $('#progress-bar-fill').style.width = `${pct}%`;

  const correctCount = state.answers.filter((a) => a.correct).length;
  $('#score-correct').textContent = correctCount;
  $('#score-answered').textContent = state.answers.length;

  $('#q-category').textContent = CATEGORY_LABELS[q.category] ?? q.category;
  $('#q-subcategory').textContent = q.sub_category || '';
  $('#q-subcategory').style.display = q.sub_category ? '' : 'none';
  $('#q-difficulty').textContent = '★'.repeat(q.difficulty || 1);

  $('#q-text').textContent = q.question;

  state.shuffledChoices = shuffle(q.choices);
  const list = $('#choice-list');
  list.innerHTML = '';
  state.shuffledChoices.forEach((c, i) => {
    const item = document.createElement('button');
    item.className = 'choice-item';
    item.dataset.choiceId = c.choice_id;
    item.innerHTML = `
      <span class="choice-label">${i + 1}</span>
      <span class="choice-text"></span>
      <span class="choice-audio-btn" title="この選択肢を再生">🔊</span>
    `;
    item.querySelector('.choice-text').textContent = c.text;
    item.querySelector('.choice-audio-btn').addEventListener('click', (ev) => {
      ev.stopPropagation();
      if (!state.answered) playChoiceAudio(c);
    });
    item.addEventListener('click', () => handleChoice(c));
    list.appendChild(item);
  });

  // sync speed selector
  $('#opt-speed-quiz').value = state.options.speed;

  if (state.options.autoPlay) {
    setTimeout(() => {
      if (!state.answered) playAllAudio();
    }, 300);
  }

  // save progress
  saveSessionProgress();
}

function handleChoice(choice) {
  if (state.answered) return;
  state.answered = true;
  cancelAudio();

  const q = state.questionList[state.currentIndex];
  const correct = choice.is_correct === true;
  const correctChoice = q.choices.find((c) => c.is_correct);

  state.answers.push({
    qid: q.id,
    selectedChoiceId: choice.choice_id,
    correctChoiceId: correctChoice.choice_id,
    correct,
  });

  // record mistake
  if (!correct) {
    recordMistake(state.chapter, q.id);
  }

  // update choice styles
  document.querySelectorAll('.choice-item').forEach((el) => {
    el.disabled = true;
    const cid = el.dataset.choiceId;
    if (cid === correctChoice.choice_id) el.classList.add('correct');
    else if (cid === choice.choice_id) el.classList.add('wrong');
    else el.classList.add('dim');
  });

  const correctCount = state.answers.filter((a) => a.correct).length;
  $('#score-correct').textContent = correctCount;
  $('#score-answered').textContent = state.answers.length;

  const pct = ((state.currentIndex + 1) / state.questionList.length) * 100;
  $('#progress-bar-fill').style.width = `${pct}%`;

  // feedback
  const fb = $('#feedback');
  fb.classList.remove('hidden', 'correct', 'wrong');
  fb.classList.add(correct ? 'correct' : 'wrong');
  $('#feedback-icon').textContent = correct ? '○' : '×';
  $('#feedback-text').textContent = correct
    ? '正解'
    : `不正解 (正解は選択肢${
        state.shuffledChoices.findIndex((c) => c.choice_id === correctChoice.choice_id) + 1
      })`;

  $('#feedback-explanation').textContent = remapChoiceRefs(q.explanation, q, state.shuffledChoices);

  const evList = $('#feedback-evidence-list');
  evList.innerHTML = '';
  (q.evidence || []).forEach((ev) => {
    const li = document.createElement('li');
    li.innerHTML = `<code>${ev.source_id}</code>「${ev.quote}」`;
    evList.appendChild(li);
  });
  $('#feedback-evidence').style.display = (q.evidence || []).length ? '' : 'none';

  // Per-choice breakdown (display only, no audio)
  const cdList = $('#feedback-choice-detail-list');
  cdList.innerHTML = '';
  state.shuffledChoices.forEach((c, i) => {
    const li = document.createElement('li');
    let marker, detail, cssClass;
    if (c.is_correct) {
      // The correct answer (for "correct" type) or the wrong statement (for "incorrect" type)
      marker = q.type === 'incorrect' ? '×' : '○';
      detail = q.type === 'incorrect' ? (c.trap_detail || '誤りを含む記述。') : '正解';
      cssClass = q.type === 'incorrect' ? 'choice-detail-wrong' : 'choice-detail-correct';
    } else {
      // Wrong choice for "correct" type, or correct distractor for "incorrect" type
      if (q.type === 'incorrect' && !c.trap_detail) {
        marker = '○';
        detail = 'この記述は正しい。';
        cssClass = 'choice-detail-correct';
      } else {
        marker = q.type === 'incorrect' ? '○' : '×';
        detail = c.trap_detail || c.text;
        cssClass = q.type === 'incorrect' ? 'choice-detail-correct' : 'choice-detail-wrong';
      }
    }
    li.className = cssClass;
    li.innerHTML = `<span class="choice-detail-label">選択肢${i + 1}</span>`
      + `<span class="choice-detail-marker ${cssClass === 'choice-detail-correct' ? 'marker-correct' : 'marker-wrong'}">${marker}</span>`
      + `<span class="choice-detail-text">${detail}</span>`;
    cdList.appendChild(li);
  });
  const cdDetails = $('#feedback-choice-details');
  cdDetails.removeAttribute('open');

  if (q.mnemonic) {
    $('#feedback-mnemonic').classList.remove('hidden');
    $('#feedback-mnemonic-text').textContent = q.mnemonic;
  } else {
    $('#feedback-mnemonic').classList.add('hidden');
  }

  fb.scrollIntoView({ behavior: 'smooth', block: 'center' });

  if (state.options.autoPlay) {
    setTimeout(() => playExplanationAudio(), 500);
  }

  if (state.options.autoNext && correct) {
    setTimeout(() => { if (state.answered) nextQuestion(); }, 4500);
  }

  // save progress
  saveSessionProgress();
}

function nextQuestion() {
  if (state.currentIndex + 1 >= state.questionList.length) {
    showResult();
    return;
  }
  state.currentIndex++;
  renderCurrentQuestion();
}

// ------------------------------------------------------------
// result
// ------------------------------------------------------------
function showResult() {
  cancelAudio();
  clearSessionProgress();

  const total = state.answers.length;
  const correct = state.answers.filter((a) => a.correct).length;
  $('#result-correct').textContent = correct;
  $('#result-total').textContent = total;
  $('#result-percent').textContent = `${Math.round((correct / total) * 100)}%`;

  const byCat = {};
  for (const ans of state.answers) {
    const q = state.questionList.find((x) => x.id === ans.qid);
    const cat = q.category;
    if (!byCat[cat]) byCat[cat] = { correct: 0, total: 0 };
    byCat[cat].total++;
    if (ans.correct) byCat[cat].correct++;
  }
  const breakdownEl = $('#result-by-category');
  breakdownEl.innerHTML = '';
  for (const [cat, s] of Object.entries(byCat)) {
    const pct = (s.correct / s.total) * 100;
    const row = document.createElement('div');
    row.className = 'result-breakdown-row';
    row.innerHTML = `
      <span class="cat-name">${CATEGORY_LABELS[cat] ?? cat}</span>
      <div class="cat-bar"><div class="cat-bar-fill" style="width:${pct}%"></div></div>
      <span>${s.correct}/${s.total}</span>
    `;
    breakdownEl.appendChild(row);
  }

  const wrongEl = $('#result-wrong-list');
  wrongEl.innerHTML = '';
  for (const ans of state.answers.filter((a) => !a.correct)) {
    const q = state.questionList.find((x) => x.id === ans.qid);
    const correctChoice = q.choices.find((c) => c.is_correct);
    const div = document.createElement('div');
    div.className = 'wrong-item';
    div.innerHTML = `
      <span class="wrong-q">Q: ${q.question}</span>
      <span>正解: ${correctChoice.text}</span>
    `;
    wrongEl.appendChild(div);
  }

  recordSessionResult(state.chapter, { correct, total });
  switchScreen('result-screen');
}

// ------------------------------------------------------------
// event wiring
// ------------------------------------------------------------
function bindEvents() {
  // Theme toggle
  $('#btn-theme-toggle').addEventListener('click', () => {
    const next = state.options.theme === 'dark' ? 'light' : 'dark';
    applyTheme(next);
  });

  // Nav brand -> go home
  $('#nav-brand').addEventListener('click', () => {
    cancelAudio();
    switchScreen('start-screen');
    renderChapterList();
    renderMistakesSummary();
    renderHistory();
  });

  // Modal: speed buttons
  document.querySelectorAll('.speed-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.options.speed = btn.dataset.speed;
      saveOptions();
    });
  });

  // Modal: close
  $('#btn-modal-close').addEventListener('click', closeSettingsModal);
  $('#settings-modal').addEventListener('click', (e) => {
    if (e.target === $('#settings-modal')) closeSettingsModal();
  });

  // Modal: start quiz
  $('#btn-start-quiz').addEventListener('click', () => {
    // read modal state
    state.options.shuffleQuestions = $('#modal-shuffle').checked;
    state.options.autoPlay = $('#modal-autoplay').checked;
    state.options.autoNext = $('#modal-autonext').checked;
    saveOptions();

    const mode = document.querySelector('input[name="quiz-mode"]:checked').value;
    closeSettingsModal();

    if (mode === 'mistakes') {
      startQuizMistakesOnly(state.chapter);
    } else {
      startQuiz();
    }
  });

  // Speed change in quiz
  document.addEventListener('change', (e) => {
    if (e.target && e.target.id === 'opt-speed-quiz') {
      state.options.speed = e.target.value;
      saveOptions();
      if (state.audio.current) {
        state.audio.current.playbackRate = SPEED_MAP[state.options.speed].rate;
      }
    }
  });

  // History reset
  $('#btn-reset-history').addEventListener('click', () => {
    if (confirm('学習履歴を全て削除しますか？')) {
      localStorage.removeItem('cs_history');
      renderHistory();
    }
  });

  // Mistakes reset
  $('#btn-reset-mistakes').addEventListener('click', () => {
    if (confirm('ミス記録を全て削除しますか？')) {
      localStorage.removeItem('cs_mistakes');
      renderMistakesSummary();
      renderChapterList();
    }
  });

  // Quiz controls
  $('#btn-back').addEventListener('click', () => {
    cancelAudio();
    saveSessionProgress();
    switchScreen('start-screen');
    renderChapterList();
    renderMistakesSummary();
    renderHistory();
  });

  $('#btn-play-question').addEventListener('click', playQuestionAudio);
  $('#btn-play-all').addEventListener('click', playAllAudio);
  $('#btn-stop-audio').addEventListener('click', cancelAudio);
  $('#btn-play-explanation').addEventListener('click', playExplanationAudio);
  $('#btn-next').addEventListener('click', nextQuestion);

  // Result buttons
  $('#btn-retry').addEventListener('click', () => startQuiz());
  $('#btn-retry-wrong').addEventListener('click', () => {
    const wrongIds = new Set(state.answers.filter((a) => !a.correct).map((a) => a.qid));
    if (wrongIds.size === 0) {
      alert('間違えた問題はありません。');
      return;
    }
    const wrongQs = state.questionList.filter((q) => wrongIds.has(q.id));
    startQuiz(wrongQs);
  });
  $('#btn-to-start').addEventListener('click', () => {
    cancelAudio();
    switchScreen('start-screen');
    renderChapterList();
    renderMistakesSummary();
    renderHistory();
  });

  // keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    const quizActive = $('#quiz-screen').classList.contains('active');
    if (!quizActive) return;
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) return;

    if (['1', '2', '3', '4'].includes(e.key)) {
      const idx = parseInt(e.key, 10) - 1;
      const choice = state.shuffledChoices[idx];
      if (choice && !state.answered) handleChoice(choice);
    } else if (e.key === ' ' || e.key === 'Enter') {
      if (state.answered) { e.preventDefault(); nextQuestion(); }
    } else if (e.key === 'p' || e.key === 'P') {
      playAllAudio();
    } else if (e.key === 's' || e.key === 'S') {
      cancelAudio();
    }
  });
}

// ------------------------------------------------------------
// init
// ------------------------------------------------------------
function init() {
  applyTheme(state.options.theme);
  renderChapterList();
  renderMistakesSummary();
  renderHistory();
  bindEvents();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
