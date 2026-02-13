const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const tile = 32;
const level = [
  '####################',
  '#S.......#........E#',
  '#.#####..#..####...#',
  '#....K...#.....K...#',
  '#.###########..##..#',
  '#.......K............'.slice(0,20),
  '####################'
];

let player = {x:1,y:1};
let keys = 0;
let message = 'Собери 3 карты и иди к выходу';
const cards = [];
let exit = {x:18,y:1};
const pressed = new Set();

for(let y=0;y<level.length;y++){
  for(let x=0;x<level[y].length;x++){
    const c = level[y][x];
    if(c==='S') player={x,y};
    if(c==='K') cards.push({x,y,taken:false});
    if(c==='E') exit={x,y};
  }
}

addEventListener('keydown', e=>{
  pressed.add(e.key.toLowerCase());
  if(e.key==='Escape') reset();
  if(e.key.toLowerCase()==='e') interact();
});
addEventListener('keyup', e=> pressed.delete(e.key.toLowerCase()));

function wall(x,y){
  return level[y]?.[x] === '#';
}

function update(){
  let dx=0,dy=0;
  if(pressed.has('a')||pressed.has('arrowleft')) dx=-1;
  if(pressed.has('d')||pressed.has('arrowright')) dx=1;
  if(pressed.has('w')||pressed.has('arrowup')) dy=-1;
  if(pressed.has('s')||pressed.has('arrowdown')) dy=1;

  if(dx && !wall(player.x+dx, player.y)) player.x+=dx;
  if(dy && !wall(player.x, player.y+dy)) player.y+=dy;

  if(player.x===exit.x && player.y===exit.y){
    message = keys>=3 ? 'Победа! Ты сбежал.' : `Выход закрыт: ${keys}/3`;
  }
}

function interact(){
  for(const c of cards){
    const near = Math.abs(c.x-player.x)+Math.abs(c.y-player.y)<=1;
    if(near && !c.taken){
      c.taken=true; keys++; message=`Карта получена (${keys}/3)`; return;
    }
  }
  message='Рядом ничего нет';
}

function draw(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  for(let y=0;y<level.length;y++){
    for(let x=0;x<level[y].length;x++){
      ctx.fillStyle = level[y][x]==='#' ? '#30457a' : '#1b2a4f';
      ctx.fillRect(x*tile,y*tile,tile,tile);
    }
  }

  for(const c of cards){
    if(c.taken) continue;
    ctx.fillStyle='#b893ff';
    ctx.fillRect(c.x*tile+8,c.y*tile+8,16,16);
  }

  ctx.fillStyle = keys>=3 ? '#67d07f' : '#9d5f5f';
  ctx.fillRect(exit.x*tile+6,exit.y*tile+6,20,20);

  ctx.fillStyle='#7ac7ff';
  ctx.fillRect(player.x*tile+6,player.y*tile+6,20,20);

  ctx.fillStyle='#e8eeff';
  ctx.fillRect(0, level.length*tile, canvas.width, canvas.height-level.length*tile);
  ctx.fillStyle='#0b1020';
  ctx.font='16px sans-serif';
  ctx.fillText(`Ключ-карты: ${keys}/3`, 10, level.length*tile+24);
  ctx.fillText(message, 10, level.length*tile+44);
}

function reset(){
  keys=0; message='Собери 3 карты и иди к выходу';
  player={x:1,y:1};
  cards.forEach(c=>c.taken=false);
}

function loop(){ update(); draw(); requestAnimationFrame(loop); }
loop();
