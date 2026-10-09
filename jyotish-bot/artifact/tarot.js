/* Tarot deck: 78 cards with upright and reversed meanings in the Rider-Waite-Smith tradition.
   The meanings are written for this page (traditional symbolism, original wording). */
(function (root) {
  const J = root.J || (root.J = {});
  // [name, keywords, upright, reversed]
  const MAJOR = [
    ["The Fool", "beginnings, leap of faith, innocence", "A fresh start. You are about to step into something new without knowing exactly where it leads - trust it, travel light, stay curious.", "Recklessness or a start you keep postponing. Look before you jump, or stop waiting for a perfect moment that will not come."],
    ["The Magician", "skill, willpower, making it happen", "You already have the tools. Focus, decide, and act - this is a time when effort turns into results quickly.", "Scattered energy, or talent not being used. Watch for manipulation - yours or someone else's."],
    ["The High Priestess", "intuition, hidden knowledge, waiting", "Not everything is visible yet. Listen to your gut and keep your counsel; the answer comes from inside, not from more noise.", "Ignoring your instincts, or secrets coming out. You may be too dependent on others' opinions."],
    ["The Empress", "nurture, abundance, comfort", "Growth, care and creativity. A fertile period - for projects, relationships or literally family. Look after your body and surroundings.", "Over-giving or smothering, or neglecting yourself. Creative block until you rest."],
    ["The Emperor", "structure, authority, father figure", "Order, rules and leadership. Take charge, set boundaries, build a stable plan. Can point to a strict father or boss.", "Rigidity, control or an authority that oppresses. Or the opposite - no discipline at all."],
    ["The Hierophant", "tradition, teachers, institutions", "Conventional paths: study, exams, religion, family customs, established organisations. A mentor or formal system helps.", "Breaking with tradition, questioning rules that no longer fit. Rebellion - useful or not."],
    ["The Lovers", "choice, union, values", "A meaningful relationship or an important choice that should follow your real values. Alignment of heart and head.", "Imbalance or disharmony in a relationship, or a choice made against your values."],
    ["The Chariot", "drive, control, victory", "Push forward with determination; you win by steering opposing forces in one direction. Travel or a move is possible.", "Losing direction, pulled in two ways, aggression without control."],
    ["Strength", "courage, patience, inner strength", "Quiet strength - handling a difficult person or emotion with patience instead of force. You are tougher than you think.", "Self-doubt, low energy, or temper getting the better of you."],
    ["The Hermit", "solitude, reflection, guidance", "Step back and think. A period of study, introspection or solitude that brings clarity. A wise guide may appear.", "Isolation that has gone too far, loneliness, or refusing advice."],
    ["Wheel of Fortune", "cycles, change, turning point", "Things are turning. Luck shifts, a new cycle starts; go with the change rather than fight it.", "A run of bad luck or resisting a change that is coming anyway."],
    ["Justice", "fairness, truth, consequences", "Decisions, contracts and legal matters; cause and effect. You get what is fair - be honest and balanced.", "Unfairness, dishonesty, avoiding accountability, a biased decision."],
    ["The Hanged Man", "pause, surrender, new perspective", "A pause or delay that is useful. Let go of control, look at the situation from a different angle.", "Stalling, pointless sacrifice, or resisting a pause you need."],
    ["Death", "endings, transformation, transition", "Something is ending so something else can begin - a job, phase or relationship. Rarely literal; it is about change.", "Clinging to what is over, fear of change, a slow drawn-out ending."],
    ["Temperance", "balance, moderation, healing", "Blend, balance and patience. Moderation in habits; healing through steady small steps.", "Excess, imbalance, impatience - too much of something."],
    ["The Devil", "attachment, temptation, addiction", "Something has a hold on you - a habit, a person, money, a fear. Recognising the chain is the first step to dropping it.", "Breaking free from an unhealthy attachment, or facing a dependency honestly."],
    ["The Tower", "sudden upheaval, revelation", "A sudden shake-up that breaks false structures - a shock, a revelation, an unexpected change. Painful but clearing.", "Avoiding a needed collapse, or a disaster narrowly averted; fear of change."],
    ["The Star", "hope, renewal, calm", "Hope and healing after a hard time. Things get lighter; trust the future and be open.", "Discouragement, lost faith, feeling disconnected."],
    ["The Moon", "illusion, anxiety, the unknown", "Uncertainty and mixed signals. Not everything is as it seems; fears and imagination run high - wait for clarity.", "Confusion lifting, truth coming out, fears fading."],
    ["The Sun", "joy, success, vitality", "Success, warmth and confidence. Good energy, things go well, clarity and visibility.", "Temporary dullness, over-optimism, success that is delayed but not denied."],
    ["Judgement", "reckoning, awakening, a call", "A wake-up call or reckoning. Review the past, forgive, and answer a calling. A second chance.", "Self-doubt, harsh self-judgement, ignoring the call."],
    ["The World", "completion, achievement, travel", "Completion and fulfilment - a cycle closes successfully. Possible travel or international links.", "Unfinished business, delays to completion, shortcuts that leave gaps."],
  ];
  const SUITS = { Wands: "fire - work, ambition, energy, creativity", Cups: "water - emotions, love, relationships, intuition",
    Swords: "air - thoughts, conflict, communication, decisions", Pentacles: "earth - money, job, body, home, practical life" };
  const MINOR = {
    Wands: [
      ["inspiration, new venture", "A spark - a new project, idea or opportunity full of energy. Act on it.", "Delays, lack of motivation, an idea that does not take off."],
      ["planning, future decisions", "Planning ahead and choosing a direction; the world is bigger than your current place.", "Fear of the unknown, poor planning, playing safe."],
      ["expansion, looking ahead", "Plans start working; expansion, possibly abroad. Waiting for ships to come in.", "Obstacles to growth, delays, frustration with the pace."],
      ["celebration, home, stability", "Celebration, homecoming, a stable happy base - events like weddings or housewarmings.", "Instability at home, transition, a celebration postponed."],
      ["competition, conflict", "Competition and friction - many voices, rivalry, sparring. Useful if kept healthy.", "Avoiding conflict, or disputes becoming personal."],
      ["recognition, victory", "Public success and recognition - praise, a win, confidence rising.", "Ego, fall from grace, lack of recognition."],
      ["defending your position", "Standing your ground against challenges; you hold the high ground.", "Overwhelmed, giving up, defensiveness."],
      ["speed, movement, news", "Things move fast - messages, travel, quick progress.", "Delays, frustration, plans stuck."],
      ["resilience, last stretch", "Tired but nearly there - persistence and caution after past setbacks.", "Exhaustion, paranoia, giving up just before the end."],
      ["burden, responsibility", "Carrying too much - overwork and responsibility. Delegate or put something down.", "Dropping burdens, or collapse under them."],
      ["enthusiastic messenger, exploration", "Enthusiastic news or a curious, adventurous young person. Exploration of a new interest.", "Hasty news, setbacks to a new venture, restlessness."],
      ["action, adventure, impulsive energy", "Bold action, travel, chasing a passion - energetic but impatient.", "Recklessness, haste, anger."],
      ["confidence, warmth, determination", "Confident, warm and independent; a magnetic woman or this energy in you.", "Jealousy, insecurity, demanding behaviour."],
      ["vision, leadership, entrepreneur", "Visionary leadership, the entrepreneur, a bold man or this energy in you.", "Impulsiveness, arrogance, high expectations."],
    ],
    Cups: [
      ["new feelings, love, compassion", "A new emotional beginning - love, friendship, creativity or spiritual opening.", "Blocked emotions, emptiness, holding feelings back."],
      ["partnership, mutual attraction", "A connection of equals - romance, friendship or partnership with mutual respect.", "Imbalance, broken communication, a split."],
      ["friendship, celebration, community", "Friends, celebrations, reunions - joy shared with others.", "Gossip, overindulgence, a third party in a relationship."],
      ["apathy, contemplation", "Boredom or discontent - ignoring what is offered. Something new is on the table if you look.", "New awareness, choosing to re-engage."],
      ["loss, grief, regret", "Focusing on what was lost; regret and disappointment. Two cups still stand behind you.", "Acceptance, moving on, forgiveness."],
      ["nostalgia, childhood, innocence", "Memories, childhood, an old friend or place - kindness and simple pleasures.", "Stuck in the past, unrealistic nostalgia."],
      ["choices, illusion, wishful thinking", "Many options and daydreams - not all are real. Choose carefully.", "Clarity, cutting through illusion, making a choice."],
      ["walking away, disappointment", "Leaving something that no longer satisfies to search for more meaning.", "Fear of leaving, aimless drifting, staying too long."],
      ["contentment, wish fulfilled", "The 'wish card' - satisfaction, comfort, getting what you wanted.", "Smugness, materialism, an unfulfilled wish."],
      ["harmony, family, happiness", "Emotional fulfilment, a happy family and home.", "Family disconnection, broken expectations at home."],
      ["sensitive message, creativity", "A gentle message, creative or emotional news, an intuitive young person.", "Emotional immaturity, creative block, an unwelcome surprise."],
      ["romance, charm, an offer", "A romantic proposal or invitation; following the heart. A charming person.", "Moodiness, unrealistic romance, being let down."],
      ["compassion, intuition, care", "Emotionally deep, caring and intuitive; a nurturing woman or this energy in you.", "Emotional insecurity, codependence, martyrdom."],
      ["emotional balance, diplomacy", "Calm control of emotions, a wise, diplomatic man or this energy in you.", "Emotional manipulation, moodiness, coldness."],
    ],
    Swords: [
      ["clarity, breakthrough, truth", "A breakthrough in thinking - clarity, truth, a sharp decision.", "Confusion, misinformation, harsh words."],
      ["stalemate, difficult choice", "Blocked emotions and avoidance - a decision you are refusing to make.", "Information overload, confusion, a stalemate breaking."],
      ["heartbreak, grief, painful truth", "Emotional pain - heartbreak, separation, hurtful words.", "Recovery, releasing pain, forgiveness."],
      ["rest, recovery, retreat", "Rest and recuperation after stress; take a break before the next push.", "Restlessness, burnout, refusing to rest."],
      ["conflict, winning at a cost", "A conflict where someone wins but relationships suffer; ego and tension.", "Reconciliation, making amends, past resentment."],
      ["transition, moving on", "Leaving trouble behind for calmer waters - a move or travel to a better place.", "Unresolved baggage, resistance to transition."],
      ["deception, strategy, getting away with something", "Strategy or sneakiness - someone acting alone or behind backs.", "Coming clean, a secret exposed, conscience."],
      ["restriction, feeling trapped", "Feeling stuck by your own thinking - the restrictions are weaker than they seem.", "Release, new perspective, freedom."],
      ["anxiety, worry, sleepless nights", "Anxiety and overthinking, worst-case thinking at night.", "Hope, reaching out, worries easing."],
      ["painful ending, rock bottom", "A painful ending or betrayal - the worst is here, so it can only get better.", "Recovery, survival, refusing to let it end."],
      ["curiosity, new ideas, vigilance", "Curious and talkative energy, new ideas, alert to news; a sharp young person.", "Gossip, scattered energy, all talk."],
      ["ambition, fast action, forceful", "Rushing ahead with ideas and arguments - decisive but blunt.", "Impulsiveness, burnout, no direction."],
      ["independence, clear judgement", "Clear, independent and direct; a sharp-minded woman or this energy in you.", "Coldness, bitterness, cruelty in words."],
      ["intellect, authority, truth", "Logic and authority - a fair, analytical man (lawyer, officer, expert) or this energy in you.", "Abuse of power, manipulation, harsh judgement."],
    ],
    Pentacles: [
      ["new financial opportunity", "A new money, job or health opportunity - a solid start.", "A missed chance, poor planning, bad investment."],
      ["juggling, adaptability", "Balancing priorities - money, time, work-life. Flexible but busy.", "Over-committed, disorganised, money juggling going wrong."],
      ["teamwork, skill, learning", "Collaboration and craftsmanship - your skill gets recognised in a team.", "Poor teamwork, lack of effort, low quality."],
      ["saving, security, holding on", "Holding on to money or control - security, but maybe too tightly.", "Overspending, or letting go of control."],
      ["hardship, loss, feeling left out", "Financial or health hardship, feeling excluded. Help is nearer than you think.", "Recovery from hardship, spiritual comfort."],
      ["generosity, giving and receiving", "Giving and receiving - charity, a loan, fair exchange.", "Debt, one-sided generosity, strings attached."],
      ["patience, long-term investment", "Hard work that pays off slowly; evaluate your investment of time.", "Impatience, poor returns, effort without reward."],
      ["diligence, mastery, practice", "Steady skill-building, apprenticeship, focused work.", "Perfectionism, or lack of focus and ambition."],
      ["independence, self-sufficiency", "Financial independence, comfort earned through your own work.", "Over-investment in work, financial setbacks."],
      ["wealth, family, legacy", "Long-term wealth and family security - inheritance, family business, roots.", "Family disputes over money, instability."],
      ["study, new skill, opportunity", "A studious, practical beginner - learning, a job offer, news about money.", "Lack of progress, procrastination, unfulfilled goals."],
      ["routine, hard work, reliability", "Slow and steady - routine, responsibility, methodical work.", "Boredom, laziness, feeling stuck in routine."],
      ["practical care, abundance", "Practical, generous and grounded; a nurturing provider or this energy in you.", "Work-home imbalance, self-neglect, financial worry."],
      ["wealth, security, leadership", "Material success and security - a successful businessman or this energy in you.", "Greed, materialism, stubbornness."],
    ],
  };
  const RANKS = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"];
  const DECK = MAJOR.map(([name, keywords, up, rev], i) => ({ id: "M" + i, name, arcana: "Major", number: i, suit: null, keywords, up, rev }));
  for (const [suit, rows] of Object.entries(MINOR)) rows.forEach(([keywords, up, rev], i) =>
    DECK.push({ id: suit[0] + i, name: `${RANKS[i]} of ${suit}`, arcana: "Minor", number: i + 1, suit, suitTheme: SUITS[suit], keywords, up, rev }));
  const SPREADS = {
    one: { label: "One card", positions: ["The answer / the energy around your question"] },
    three: { label: "Past - Present - Future", positions: ["Past - what led here", "Present - where you are", "Future - where it is heading"] },
    love: { label: "Relationship (3)", positions: ["You", "The other person", "The connection between you"] },
    career: { label: "Career (3)", positions: ["Current situation", "Obstacle", "Advice"] },
    celtic: { label: "Celtic Cross (10)", positions: ["Present situation", "Challenge (crossing)", "Root / foundation", "Recent past", "Best possible outcome",
      "Near future", "Your attitude", "Outside influences", "Hopes and fears", "Likely outcome"] },
  };
  // unbiased shuffle with the browser's crypto RNG
  function shuffle(n) {
    const a = [...Array(n).keys()], r = new Uint32Array(1);
    for (let i = n - 1; i > 0; i--) { root.crypto.getRandomValues(r); const j = r[0] % (i + 1); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  }
  function coin() { const r = new Uint8Array(1); root.crypto.getRandomValues(r); return r[0] < 77; }  // ~30% reversed
  J.TAROT = { DECK, SPREADS, SUITS, shuffle, coin };
  if (typeof module !== "undefined") module.exports = J;
})(typeof window !== "undefined" ? window : globalThis);
