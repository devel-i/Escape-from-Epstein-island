const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const W = canvas.width;
const H = canvas.height;
const HALF_H = H / 2;
const FOV = Math.PI / 3;
const RAYS = 260;
const MAX_D = 18;
const SCALE = W / RAYS;

const map = [
  '############',
  '#S...#....E#',
  '#.##.#.##..#',
  '#....#..K..#',
  '#.##.##.##.#',
  '#..K....#..#',
  '#.####..#K.#',
  '#......##..#',
  '############',
];

let px = 1.5, py = 1.5, pa = 0;
let exit = {x: 10.5, y: 1.5};
const cards = [];
const walls = new Set();
const keys = {v: 0};
const pressed = new Set();
let msg = 'Собери 3 карты и иди к выходу';

for (let y = 0; y < map.length; y++) {
  for (let x = 0; x < map[y].length; x++) {
    const c = map[y][x];
    if (c === '#') walls.add(`${x},${y}`);
    if (c === 'S') { px = x + 0.5; py = y + 0.5; }
    if (c === 'E') exit = {x: x + 0.5, y: y + 0.5};
    if (c === 'K') cards.push({x: x + 0.5, y: y + 0.5, taken: false});
  }
}

addEventListener('keydown', e => pressed.add(e.key.toLowerCase()));
addEventListener('keyup', e => pressed.delete(e.key.toLowerCase()));

function isWall(x, y) {
  return walls.has(`${Math.floor(x)},${Math.floor(y)}`);
}

function move(dt) {
  const sp = dt * 2.6;
  const rs = dt * 1.9;
  let dx = 0, dy = 0;

  if (pressed.has('w') || pressed.has('arrowup')) { dx += Math.cos(pa) * sp; dy += Math.sin(pa) * sp; }
  if (pressed.has('s') || pressed.has('arrowdown')) { dx -= Math.cos(pa) * sp; dy -= Math.sin(pa) * sp; }
  if (pressed.has('a')) { dx += Math.sin(pa) * sp; dy -= Math.cos(pa) * sp; }
  if (pressed.has('d')) { dx -= Math.sin(pa) * sp; dy += Math.cos(pa) * sp; }
  if (pressed.has('q') || pressed.has('arrowleft')) pa -= rs;
  if (pressed.has('e') || pressed.has('arrowright')) pa += rs;

  if (!isWall(px + dx, py)) px += dx;
  if (!isWall(px, py + dy)) py += dy;

  for (const c of cards) {
    if (!c.taken && Math.hypot(c.x - px, c.y - py) < 0.5) {
      c.taken = true;
      keys.v += 1;
      msg = `Карта найдена (${keys.v}/3)`;
    }
  }

  if (Math.hypot(exit.x - px, exit.y - py) < 0.6) {
    msg = keys.v >= 3 ? 'Победа! Ты сбежал с острова.' : `Выход закрыт: ${keys.v}/3`;
  }
}

function cast() {
  const start = pa - FOV / 2;
  for (let i = 0; i < RAYS; i++) {
    const ra = start + (i / RAYS) * FOV;
    let d = 0.02;
    while (d < MAX_D) {
      const x = px + Math.cos(ra) * d;
      const y = py + Math.sin(ra) * d;
      if (isWall(x, y)) {
        const corr = d * Math.cos(pa - ra);
        const h = Math.min(H, 840 / Math.max(corr, 0.001));
        const s = Math.max(45, 255 - corr * 25);
        ctx.fillStyle = `rgb(${s / 2},${s / 2 + 10},${s})`;
        ctx.fillRect(i * SCALE, HALF_H - h / 2, SCALE + 1, h);
        break;
      }
      d += 0.02;
    }
  }
}

function drawSprites() {
  const sprites = [];
  for (const c of cards) {
    if (c.taken) continue;
    const dx = c.x - px, dy = c.y - py;
    const dist = Math.hypot(dx, dy);
    let ang = Math.atan2(dy, dx) - pa;
    while (ang > Math.PI) ang -= Math.PI * 2;
    while (ang < -Math.PI) ang += Math.PI * 2;
    if (Math.abs(ang) < FOV / 2 + 0.25) {
      const proj = 520 / dist;
      const sx = (ang + FOV / 2) / FOV * W;
      sprites.push({dist, x: sx - proj / 4, y: HALF_H - proj / 2, w: proj / 2, h: proj, color: '#b893ff'});
    }
  }

  {
    const dx = exit.x - px, dy = exit.y - py;
    const dist = Math.hypot(dx, dy);
    let ang = Math.atan2(dy, dx) - pa;
    while (ang > Math.PI) ang -= Math.PI * 2;
    while (ang < -Math.PI) ang += Math.PI * 2;
    if (Math.abs(ang) < FOV / 2 + 0.25) {
      const proj = 620 / dist;
      const sx = (ang + FOV / 2) / FOV * W;
      sprites.push({dist, x: sx - proj / 3, y: HALF_H - proj / 2, w: proj / 1.5, h: proj, color: keys.v >= 3 ? '#68d37b' : '#a06262'});
    }
  }

  sprites.sort((a, b) => b.dist - a.dist);
  for (const s of sprites) {
    ctx.fillStyle = s.color;
    ctx.fillRect(s.x, s.y, s.w, s.h);
  }
}

function drawUI() {
  ctx.fillStyle = '#0a1020';
  ctx.fillRect(0, H - 94, W, 94);
  ctx.fillStyle = '#e5edff';
  ctx.font = '26px sans-serif';
  ctx.fillText(`Ключи: ${keys.v}/3`, 16, H - 58);
  ctx.font = '21px sans-serif';
  ctx.fillStyle = '#b9c5ea';
  ctx.fillText(msg, 16, H - 24);
}

let last = performance.now();
function loop(t) {
  const dt = Math.min(0.033, (t - last) / 1000);
  last = t;

  move(dt);

  ctx.fillStyle = '#101b33';
  ctx.fillRect(0, 0, W, HALF_H);
  ctx.fillStyle = '#22355f';
  ctx.fillRect(0, HALF_H, W, HALF_H);

  cast();
  drawSprites();
  drawUI();

  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);
