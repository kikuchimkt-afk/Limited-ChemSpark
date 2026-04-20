// ============================================================
// 化学共通テスト演習 — main controller
// ============================================================

const DATA_PATH = 'questions';
const AUDIO_PATH = 'audio';

// The MP3 files were synthesized with Edge TTS `-10%` rate. Natural speed is
// restored by playing them back at ~1.11x (preservesPitch keeps it natural).
const SPEED_MAP = {
  slow: { rate: 1.0, label: 'ゆっくり' },
  natural: { rate: 1.11, label: 'ナチュラル' },
  fast: { rate: 1.25, label: '早め' },
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

// Available chapters (enabled flag lets us hide chapters without data yet).
const CHAPTERS = [
  { id: 'ch1-1', title: '第1章-1 物質の構成', enabled: true },
  { id: 'ch1-2', title: '第1章-2', enabled: false },
  { id: 'ch1-3', title: '第1章-3', enabled: false },
  // (further chapters added as data is prepared)
];

// ------------------------------------------------------------
// state
// ------------------------------------------------------------
const state = {
  chapter: 'ch1-1',
  chapterData: null,
  questionList: [], // array of question objects (in play order)
  currentIndex: 0,
  answers: [], // { qid, selectedChoiceId, correctChoiceId, correct }
  answered: false,
  shuffledChoices: [], // current question's choices in displayed order
  options: loadOptions(),
  audio: {
    current: null, // HTMLAudioElement
    token: 0,      // incremented to cancel in-flight sequences
  },
};

// ------------------------------------------------------------
// storage
// ------------------------------------------------------------
function loadOptions() {
  try {
    const stored = JSON.parse(localStorage.getItem('opts') || '{}');
    return {
      shuffleQuestions: stored.shuffleQuestions ?? false,
      autoPlay: stored.autoPlay ?? true,
      autoNext: stored.autoNext ?? false,
      speed: stored.speed ?? 'slow',
    };
  } catch {
    return {
      shuffleQuestions: false,
      autoPlay: true,
      autoNext: false,
      speed: 'slow',
    };
  }
}

function saveOptions() {
  localStorage.setItem('opts', JSON.stringify(state.options));
}

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem('history') || '{}');
  } catch {
    return {};
  }
}

function saveHistory(history) {
  localStorage.setItem('history', JSON.stringify(history));
}

function recordSessionResult(chapter, stats) {
  const history = loadHistory();
  const arr = history[chapter] || [];
  arr.push({ ts: Date.now(), ...stats });
  history[chapter] = arr.slice(-20); // keep last 20 sessions
  saveHistory(history);
}

// ------------------------------------------------------------
// utils
// ------------------------------------------------------------
function $(sel) {
  return document.querySelector(sel);
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
    // if token changes mid-sleep, resolve early so callers can abort.
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
// audio
// ------------------------------------------------------------
function cancelAudio() {
  state.audio.token++;
  if (state.audio.current) {
    try {
      state.audio.current.pause();
      state.audio.current.currentTime = 0;
    } catch (e) {
      // ignore
    }
    state.audio.current = null;
  }
  document.querySelectorAll('.playing').forEach((el) => {
    el.classList.remove('playing');
  });
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
    audio.addEventListener('error', () => {
      console.warn('audio error:', src);
      resolve(false);
    });
    audio.play().catch((err) => {
      console.warn('audio play failed:', src, err);
      resolve(false);
    });
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
  if (!(await sleep(1500, token))) return;

  for (let i = 0; i < state.shuffledChoices.length; i++) {
    if (state.audio.token !== token) return;
    const c = state.shuffledChoices[i];
    const choiceEl = document.querySelector(
      `.choice-item[data-choice-id="${c.choice_id}"]`,
    );
    choiceEl?.classList.add('playing');
    await playClip(prefixAudioPath(voice, i + 1), token);
    if (state.audio.token !== token) {
      choiceEl?.classList.remove('playing');
      return;
    }
    await playClip(questionAudioPath(q, `${c.choice_id}.mp3`), token);
    choiceEl?.classList.remove('playing');
    if (state.audio.token !== token) return;
    if (i < state.shuffledChoices.length - 1) {
      if (!(await sleep(700, token))) return;
    }
  }
}

async function playChoiceAudio(choice) {
  cancelAudio();
  const token = state.audio.token;
  const q = state.questionList[state.currentIndex];
  const voice = q.audio_voice;
  const pos = state.shuffledChoices.findIndex(
    (c) => c.choice_id === choice.choice_id,
  );
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
// start screen
// ------------------------------------------------------------
function renderChapterList() {
  const list = $('#chapter-list');
  list.innerHTML = '';
  for (const ch of CHAPTERS) {
    const btn = document.createElement('button');
    btn.className = 'chapter-btn';
    btn.dataset.chapterId = ch.id;
    btn.disabled = !ch.enabled;
    btn.innerHTML = `
      <span class="chapter-title">${ch.title}</span>
      <span class="chapter-meta">${ch.enabled ? '50問' : '準備中'}</span>
    `;
    if (ch.id === state.chapter) btn.classList.add('active');
    btn.addEventListener('click', () => {
      if (!ch.enabled) return;
      document.querySelectorAll('.chapter-btn').forEach((b) => {
        b.classList.remove('active');
      });
      btn.classList.add('active');
      state.chapter = ch.id;
    });
    list.appendChild(btn);
  }
}

function renderOptions() {
  $('#opt-shuffle-questions').checked = state.options.shuffleQuestions;
  $('#opt-auto-play').checked = state.options.autoPlay;
  $('#opt-auto-next').checked = state.options.autoNext;

  document.querySelectorAll('#opt-speed, #opt-speed-quiz').forEach((el) => {
    el.value = state.options.speed;
  });
}

function applySpeed(newSpeed) {
  if (!SPEED_MAP[newSpeed]) return;
  state.options.speed = newSpeed;
  saveOptions();
  document.querySelectorAll('#opt-speed, #opt-speed-quiz').forEach((el) => {
    if (el.value !== newSpeed) el.value = newSpeed;
  });
  if (state.audio.current) {
    state.audio.current.playbackRate = SPEED_MAP[newSpeed].rate;
  }
}

function renderHistory() {
  const history = loadHistory();
  const el = $('#history-summary');
  const chapters = Object.keys(history);
  if (chapters.length === 0) {
    el.innerHTML = '<em>まだ履歴はありません。</em>';
    return;
  }
  const rows = chapters.map((cid) => {
    const sessions = history[cid];
    const last = sessions[sessions.length - 1];
    const best = Math.max(
      ...sessions.map((s) => Math.round((s.correct / s.total) * 100)),
    );
    return `
      <div class="history-row">
        <span>${cid}  (${sessions.length}回)</span>
        <span>最終: ${last.correct}/${last.total} (${Math.round(
      (last.correct / last.total) * 100,
    )}%) · 最高: ${best}%</span>
      </div>
    `;
  });
  el.innerHTML = rows.join('');
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

  let questions =
    questionsOverride ?? state.chapterData.questions.slice();
  if (state.options.shuffleQuestions && !questionsOverride) {
    questions = shuffle(questions);
  }

  state.questionList = questions;
  state.currentIndex = 0;
  state.answers = [];

  switchScreen('quiz-screen');
  renderCurrentQuestion();
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

  // schedule auto-play after render
  if (state.options.autoPlay) {
    // small delay to allow user to read the question first
    setTimeout(() => {
      if (!state.answered) playAllAudio();
    }, 300);
  }
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

  // update choice styles
  document.querySelectorAll('.choice-item').forEach((el) => {
    el.disabled = true;
    const cid = el.dataset.choiceId;
    if (cid === correctChoice.choice_id) el.classList.add('correct');
    else if (cid === choice.choice_id) el.classList.add('wrong');
    else el.classList.add('dim');
  });

  // update score
  const correctCount = state.answers.filter((a) => a.correct).length;
  $('#score-correct').textContent = correctCount;
  $('#score-answered').textContent = state.answers.length;

  // progress bar
  const pct =
    ((state.currentIndex + 1) / state.questionList.length) * 100;
  $('#progress-bar-fill').style.width = `${pct}%`;

  // render feedback
  const fb = $('#feedback');
  fb.classList.remove('hidden', 'correct', 'wrong');
  fb.classList.add(correct ? 'correct' : 'wrong');
  $('#feedback-icon').textContent = correct ? '○' : '×';
  $('#feedback-text').textContent = correct
    ? '正解'
    : `不正解 (正解は選択肢${
        state.shuffledChoices.findIndex(
          (c) => c.choice_id === correctChoice.choice_id,
        ) + 1
      })`;

  $('#feedback-explanation').textContent = q.explanation;

  const evList = $('#feedback-evidence-list');
  evList.innerHTML = '';
  (q.evidence || []).forEach((ev) => {
    const li = document.createElement('li');
    li.innerHTML = `<code>${ev.source_id}</code>「${ev.quote}」`;
    evList.appendChild(li);
  });
  $('#feedback-evidence').style.display = (q.evidence || []).length
    ? ''
    : 'none';

  if (q.mnemonic) {
    $('#feedback-mnemonic').classList.remove('hidden');
    $('#feedback-mnemonic-text').textContent = q.mnemonic;
  } else {
    $('#feedback-mnemonic').classList.add('hidden');
  }

  fb.scrollIntoView({ behavior: 'smooth', block: 'center' });

  // auto-play explanation if enabled
  if (state.options.autoPlay) {
    setTimeout(() => playExplanationAudio(), 500);
  }

  // auto-next after correct + audio plays
  if (state.options.autoNext && correct) {
    setTimeout(() => {
      if (state.answered) nextQuestion();
    }, 4500);
  }
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

  const total = state.answers.length;
  const correct = state.answers.filter((a) => a.correct).length;
  $('#result-correct').textContent = correct;
  $('#result-total').textContent = total;
  $('#result-percent').textContent = `${Math.round(
    (correct / total) * 100,
  )}%`;

  // category breakdown
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

  // wrong list
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
  $('#btn-start').addEventListener('click', () => startQuiz());

  $('#opt-shuffle-questions').addEventListener('change', (e) => {
    state.options.shuffleQuestions = e.target.checked;
    saveOptions();
  });
  $('#opt-auto-play').addEventListener('change', (e) => {
    state.options.autoPlay = e.target.checked;
    saveOptions();
  });
  $('#opt-auto-next').addEventListener('change', (e) => {
    state.options.autoNext = e.target.checked;
    saveOptions();
  });

  document.addEventListener('change', (e) => {
    if (e.target && (e.target.id === 'opt-speed' || e.target.id === 'opt-speed-quiz')) {
      applySpeed(e.target.value);
    }
  });

  $('#btn-reset-history').addEventListener('click', () => {
    if (confirm('学習履歴を全て削除しますか？')) {
      localStorage.removeItem('history');
      renderHistory();
    }
  });

  $('#btn-back').addEventListener('click', () => {
    cancelAudio();
    switchScreen('start-screen');
    renderHistory();
  });

  $('#btn-play-question').addEventListener('click', playQuestionAudio);
  $('#btn-play-all').addEventListener('click', playAllAudio);
  $('#btn-stop-audio').addEventListener('click', cancelAudio);
  $('#btn-play-explanation').addEventListener('click', playExplanationAudio);

  $('#btn-next').addEventListener('click', nextQuestion);

  $('#btn-retry').addEventListener('click', () => startQuiz());
  $('#btn-retry-wrong').addEventListener('click', () => {
    const wrongIds = new Set(
      state.answers.filter((a) => !a.correct).map((a) => a.qid),
    );
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
    renderHistory();
  });

  // keyboard shortcuts on quiz screen
  document.addEventListener('keydown', (e) => {
    const quizActive = $('#quiz-screen').classList.contains('active');
    if (!quizActive) return;
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) return;

    if (['1', '2', '3', '4'].includes(e.key)) {
      const idx = parseInt(e.key, 10) - 1;
      const choice = state.shuffledChoices[idx];
      if (choice && !state.answered) handleChoice(choice);
    } else if (e.key === ' ' || e.key === 'Enter') {
      if (state.answered) {
        e.preventDefault();
        nextQuestion();
      }
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
  renderChapterList();
  renderOptions();
  renderHistory();
  bindEvents();
}

// Modules are deferred, so DOMContentLoaded may have already fired.
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
