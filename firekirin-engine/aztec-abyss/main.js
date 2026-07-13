const W = 1280, H = 720;
const BETS = [0.05, 0.10, 0.25, 0.50, 1, 2, 5, 10];
const C = { jade: 0x20e6b2, sun: 0xffc857, cyan: 0x39d8ff, red: 0xff4d67, ink: 0x071018 };

const WEAPONS = {
  sunbolt: { name: 'Sun Bolt', cost: 1, damage: 1, rate: 115, speed: 920, color: C.sun },
  jadenet: { name: 'Jade Net', cost: 4, damage: .8, rate: 410, speed: 700, color: C.jade, radius: 105, slow: 1800 },
  obsidian: { name: 'Obsidian Burst', cost: 8, damage: 3.3, rate: 670, speed: 620, color: C.red, radius: 125, aoe: true },
};

const FISH = [
  ['jade_piranha', 'Jade Piranha', 2, 2, 122, .55, 0x22d9a8, 0xffc857, 'sine', 20],
  ['sun_tetra', 'Sun-Disc Tetra', 3, 4, 108, .62, 0xffb83f, 0x4cf5d0, 'sine', 17],
  ['obsidian_snapper', 'Obsidian Snapper', 5, 8, 96, .72, 0x312347, 0xff4d67, 'zig', 14],
  ['turquoise_ray', 'Turquoise Ray', 8, 14, 78, .86, 0x2fcde0, 0x163d5a, 'glide', 11],
  ['temple_turtle', 'Temple Turtle', 12, 22, 56, .92, 0x5fa25b, 0xffc857, 'drift', 8],
  ['xolo_eel', 'Xolo Eel', 15, 30, 132, .94, 0x7a5be8, 0x20e6b2, 'serpent', 7],
  ['jaguar_shark', 'Jaguar Shark', 22, 50, 74, 1.08, 0xc8862d, 0x21130b, 'hunter', 5],
  ['golden_relic', 'Golden Relic Fish', 40, 160, 88, 1.04, 0xffd65a, 0xffffff, 'rush', 1],
].map(([id, name, hp, reward, speed, scale, body, accent, motion, weight]) => ({ id, name, hp, reward, speed, scale, body, accent, motion, weight }));

const BOSSES = [
  { id: 'quetzal_leviathan', name: 'Quetzal Leviathan', hp: 420, reward: 2200, body: 0x18c999, accent: 0x82f7ff },
  { id: 'obsidian_jaguar', name: 'Obsidian Jaguar Shark', hp: 560, reward: 3400, body: 0x2a1736, accent: 0xff5c72 },
  { id: 'sun_colossus', name: 'Sun Temple Colossus', hp: 720, reward: 5000, body: 0xd49b2e, accent: 0xfff1a6 },
];

const ui = Object.fromEntries([
  'credits-value','combo-value','wave-label','temple-meter','temple-value','bet-value','lock-value','hint-value',
  'boss-hud','boss-name','boss-phase','boss-fill','toast','auto-toggle','lock-toggle','relic-trigger'
].map(id => [id, document.getElementById(id)]));

let toastTimer;
function toast(text, ms = 850) {
  ui.toast.textContent = text;
  ui.toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => ui.toast.classList.remove('show'), ms);
}

function weightedFish() {
  let roll = Math.random() * FISH.reduce((n, f) => n + f.weight, 0);
  for (const fish of FISH) { roll -= fish.weight; if (roll <= 0) return fish; }
  return FISH[0];
}

class Abyss extends Phaser.Scene {
  constructor() {
    super('abyss');
    this.credits = 10000;
    this.bet = 1;
    this.weapon = 'sunbolt';
    this.auto = false;
    this.held = false;
    this.lastShot = 0;
    this.wave = 0;
    this.combo = 0;
    this.comboUntil = 0;
    this.meter = 0;
    this.lock = null;
    this.boss = null;
    this.freezeUntil = 0;
    this.relicReady = true;
  }

  create() {
    this.drawWorld();
    this.makeTextures();
    this.fishes = this.physics.add.group();
    this.bullets = this.physics.add.group();
    this.physics.add.overlap(this.bullets, this.fishes, this.hit, null, this);
    this.makeTurrets();
    this.makeReticle();
    this.bindInput();
    this.bindHud();
    this.time.addEvent({ delay: 520, loop: true, callback: this.botFire, callbackScope: this });
    this.nextWave();
    this.refresh();
    toast('ENTER THE ABYSS', 1300);
  }

  drawWorld() {
    const g = this.add.graphics();
    for (let y = 0; y < H; y += 8) {
      const t = y / H;
      const color = Phaser.Display.Color.GetColor(2, 24 - Math.floor(t * 18), 38 - Math.floor(t * 27));
      g.fillStyle(color).fillRect(0, y, W, 9);
    }
    g.fillStyle(0x4bdfff, .035);
    for (let x = 50; x < W; x += 170) g.fillTriangle(x, 0, x + 40, 0, x + 180, H);
    g.fillStyle(0x010408, .82).fillRect(0, H - 115, W, 115);
    g.fillTriangle(190, H - 115, 355, H - 335, 520, H - 115);
    g.fillTriangle(760, H - 115, 930, H - 300, 1100, H - 115);
    this.bubbles = Array.from({ length: 42 }, () => {
      const b = this.add.circle(Phaser.Math.Between(0, W), Phaser.Math.Between(0, H), Phaser.Math.Between(1, 4), 0x9fefff, .12);
      b.speed = Phaser.Math.Between(8, 24); return b;
    });
  }

  makeTextures() {
    for (const f of FISH) this.fishTexture(f);
    for (const b of BOSSES) this.bossTexture(b);
    const g = this.make.graphics({ add: false });
    g.fillStyle(C.sun).fillCircle(10, 10, 6).fillStyle(0xffffff).fillCircle(10, 10, 2).generateTexture('sunbolt', 20, 20);
    g.clear().lineStyle(3, C.jade).strokeCircle(15, 15, 12).lineStyle(1, 0xffffff).strokeCircle(15, 15, 5).generateTexture('jadenet', 30, 30);
    g.clear().fillStyle(0x140d1d).fillCircle(14, 14, 10).lineStyle(3, C.red).strokeCircle(14, 14, 11).generateTexture('obsidian', 28, 28);
    g.destroy();
  }

  fishTexture(f) {
    const g = this.make.graphics({ add: false });
    g.fillStyle(f.body).fillEllipse(104, 56, 118, 62).fillTriangle(50, 56, 8, 18, 18, 56).fillTriangle(50, 56, 8, 94, 18, 56);
    g.fillStyle(f.accent, .85).fillTriangle(88, 32, 116, 4, 126, 35).fillTriangle(92, 80, 118, 106, 126, 78);
    g.lineStyle(4, f.accent, .9).strokeCircle(105, 56, 18).lineBetween(87, 56, 123, 56).lineBetween(105, 38, 105, 74);
    g.fillStyle(0xffffff).fillCircle(146, 46, 8).fillStyle(0x041017).fillCircle(149, 46, 4);
    g.generateTexture(f.id, 190, 112).destroy();
  }

  bossTexture(b) {
    const g = this.make.graphics({ add: false });
    g.fillStyle(b.body).fillEllipse(175, 95, 210, 104).fillTriangle(78, 95, 14, 24, 34, 95).fillTriangle(78, 95, 14, 166, 34, 95);
    g.fillStyle(b.accent, .9);
    for (let i = 0; i < 7; i++) g.fillTriangle(92 + i * 25, 51, 105 + i * 25, 10, 117 + i * 25, 54);
    g.lineStyle(6, b.accent).strokeEllipse(175, 95, 160, 76).strokeCircle(175, 95, 31);
    g.fillStyle(0xffffff).fillCircle(259, 75, 11).fillStyle(C.red).fillCircle(263, 75, 6);
    g.generateTexture(b.id, 330, 190).destroy();
  }

  makeTurrets() {
    const defs = [[225,H-70,C.cyan,true],[W-225,H-70,C.red,false],[225,70,C.jade,false],[W-225,70,C.sun,false]];
    this.turrets = defs.map(([x,y,color,human], i) => {
      const c = this.add.container(x,y).setDepth(30), base = this.add.graphics(), barrel = this.add.graphics();
      base.fillStyle(C.ink,.96).fillCircle(0,0,35).lineStyle(3,color,.75).strokeCircle(0,0,34).lineStyle(1,color,.3).strokeCircle(0,0,24);
      barrel.fillStyle(0x0b202a).fillRoundedRect(-7,-58,14,58,5).lineStyle(2,color,.8).strokeRoundedRect(-7,-58,14,58,5);
      if (y < H/2) barrel.rotation = Math.PI;
      const label = this.add.text(0, y > H/2 ? 31 : -31, human ? 'P1 · YOU' : `P${i+1} · BOT`, { fontFamily:'monospace', fontSize:'10px', color:`#${color.toString(16).padStart(6,'0')}` }).setOrigin(.5);
      c.add([base,barrel,label]); return { c, barrel, human };
    });
    this.player = this.turrets[0];
  }

  makeReticle() {
    this.reticle = this.add.graphics().setDepth(35).setVisible(false);
    this.reticle.lineStyle(2,C.jade).strokeCircle(0,0,42).lineStyle(1,C.sun).strokeCircle(0,0,32);
    this.reticle.lineBetween(-52,0,-31,0).lineBetween(31,0,52,0).lineBetween(0,-52,0,-31).lineBetween(0,31,0,52);
  }

  bindInput() {
    this.input.on('pointermove', p => { this.aimX = p.worldX; this.aimY = p.worldY; });
    this.input.on('pointerdown', (p, over = []) => { this.aimX = p.worldX; this.aimY = p.worldY; if (!over.some(o => o.getData('fish'))) this.held = true; });
    this.input.on('pointerup', () => this.held = false);
    this.input.on('gameout', () => this.held = false);
    this.keys = this.input.keyboard.addKeys('ONE,TWO,THREE,A,L,F,Q,E,SPACE');
  }

  bindHud() {
    document.querySelectorAll('[data-weapon]').forEach(b => b.addEventListener('click', () => this.choose(b.dataset.weapon)));
    document.getElementById('bet-down').addEventListener('click', () => this.changeBet(-1));
    document.getElementById('bet-up').addEventListener('click', () => this.changeBet(1));
    ui['auto-toggle'].addEventListener('click', () => this.toggleAuto());
    ui['lock-toggle'].addEventListener('click', () => this.lockNearest());
    ui['relic-trigger'].addEventListener('click', () => this.relic());
  }

  choose(id) {
    this.weapon = id;
    document.querySelectorAll('[data-weapon]').forEach(b => b.classList.toggle('active', b.dataset.weapon === id));
    toast(WEAPONS[id].name.toUpperCase(), 600);
  }
  changeBet(n) { this.bet = Phaser.Math.Clamp(this.bet + n, 0, BETS.length - 1); this.refresh(); }
  toggleAuto() { this.auto = !this.auto; ui['auto-toggle'].classList.toggle('active', this.auto); toast(this.auto ? 'AUTO FIRE ON' : 'AUTO FIRE OFF'); }

  nextWave() {
    this.wave++;
    ui['wave-label'].textContent = `WAVE ${this.wave}`;
    if (this.wave % 5 === 0) return this.time.delayedCall(700, () => this.spawnBoss());
    const forms = ['LINE','WEDGE','ARC','STAIR','SPIRAL'], form = forms[(this.wave-1)%forms.length], count = Phaser.Math.Clamp(7 + this.wave, 8, 18), fish = weightedFish(), left = Math.random() > .5;
    toast(`${form} FORMATION`);
    for (let i=0;i<count;i++) this.time.delayedCall(i*90, () => {
      const y = 150 + (i%6)*70 + (form==='SPIRAL' ? Math.sin(i*.7)*85 : 0);
      const offset = form==='WEDGE' ? Math.abs(i-(count-1)/2)*25 : form==='ARC' ? Math.sin(i/(count-1)*Math.PI)*95 : form==='STAIR' ? (i%5)*20 : 0;
      this.spawnFish(fish,left,y,offset);
    });
  }

  spawnFish(type,left=true,y=H/2,offset=0) {
    const s = this.physics.add.sprite(left ? -100-offset : W+100+offset, y, type.id).setScale(type.scale).setFlipX(!left).setDepth(10).setInteractive({useHandCursor:true});
    s.body.setAllowGravity(false); s.body.setCircle(38,55,18);
    s.setData({ fish:true, name:type.name, hp:type.hp*(1+this.wave*.045), max:type.hp*(1+this.wave*.045), reward:type.reward, speed:type.speed*(1+this.wave*.018), baseY:y, phase:Math.random()*6.2, motion:type.motion, left, slowUntil:0, boss:false });
    s.on('pointerdown', p => { p.event?.stopPropagation?.(); this.setLock(s); });
    this.fishes.add(s); return s;
  }

  spawnBoss() {
    const b = BOSSES[(Math.floor(this.wave/5)-1)%BOSSES.length];
    const s = this.physics.add.sprite(W+190,H/2,b.id).setScale(.82).setFlipX(true).setDepth(11).setInteractive({useHandCursor:true});
    s.body.setAllowGravity(false); s.body.setCircle(90,75,5);
    s.setData({ fish:true, name:b.name, hp:b.hp*(1+this.wave*.03), max:b.hp*(1+this.wave*.03), reward:b.reward, speed:42, baseY:H/2, phase:0, motion:'boss', left:false, slowUntil:0, boss:true, bossPhase:1 });
    s.on('pointerdown', p => { p.event?.stopPropagation?.(); this.setLock(s); });
    this.fishes.add(s); this.boss=s;
    ui['boss-hud'].hidden=false; ui['boss-name'].textContent=b.name.toUpperCase(); ui['boss-phase'].textContent='PHASE I'; ui['boss-fill'].style.width='100%';
    this.setLock(s); this.cameras.main.shake(700,.012); toast(`BOSS INBOUND\n${b.name.toUpperCase()}`,1500);
  }

  setLock(s) { if (!s?.active) return; this.lock=s; this.reticle.setVisible(true); ui['lock-value'].textContent=s.getData('name').toUpperCase(); ui['hint-value'].textContent=s.getData('boss')?'Boss lock engaged':'Tap another creature to switch'; ui['lock-toggle'].classList.add('active'); }
  clearLock() { this.lock=null; this.reticle.setVisible(false); ui['lock-value'].textContent='NONE'; ui['hint-value'].textContent='Tap a creature or press L'; ui['lock-toggle'].classList.remove('active'); }
  lockNearest() { const a=this.fishes.getChildren().filter(f=>f.active); if(!a.length)return this.clearLock(); const x=this.aimX||W/2,y=this.aimY||H/2; this.setLock(a.sort((p,q)=>Phaser.Math.Distance.Between(p.x,p.y,x,y)-Phaser.Math.Distance.Between(q.x,q.y,x,y))[0]); }

  shoot(time) {
    const w=WEAPONS[this.weapon], cost=w.cost*BETS[this.bet];
    if(time-this.lastShot<w.rate||this.credits<cost)return;
    const tx=this.lock?.active?this.lock.x:(this.aimX||W/2), ty=this.lock?.active?this.lock.y:(this.aimY||H/2), angle=Phaser.Math.Angle.Between(this.player.c.x,this.player.c.y,tx,ty);
    this.lastShot=time; this.credits-=cost; this.meter=Phaser.Math.Clamp(this.meter+Math.max(.18,cost*.08),0,100); this.fire(this.player,angle,w,0); this.refresh();
  }

  fire(turret,angle,w,owner) {
    turret.barrel.rotation=angle+Math.PI/2;
    const b=this.physics.add.image(turret.c.x+Math.cos(angle)*48,turret.c.y+Math.sin(angle)*48,w.id).setDepth(18);
    b.body.setAllowGravity(false); this.physics.velocityFromRotation(angle,w.speed,b.body.velocity);
    b.setData({owner,damage:w.damage*BETS[this.bet],radius:w.radius||0,slow:w.slow||0,aoe:!!w.aoe,color:w.color}); this.bullets.add(b);
    const flash=this.add.circle(b.x,b.y,10,w.color,.8).setDepth(22); this.tweens.add({targets:flash,alpha:0,scale:2,duration:120,onComplete:()=>flash.destroy()});
  }

  botFire() {
    const a=this.fishes.getChildren().filter(f=>f.active); if(!a.length)return;
    this.turrets.filter(t=>!t.human).forEach(t=>{if(Math.random()>.7)return;const f=a[Math.floor(Math.random()*a.length)],ang=Phaser.Math.Angle.Between(t.c.x,t.c.y,f.x,f.y);this.fire(t,ang,WEAPONS.sunbolt,1);});
  }

  hit(b,f) {
    if(!b.active||!f.active)return;const d=b.data.values;this.damage(f,d.damage,d.owner,d.color);
    if(d.radius){const ring=this.add.circle(f.x,f.y,d.radius,d.color,.12).setStrokeStyle(3,d.color,.8).setDepth(20);this.tweens.add({targets:ring,alpha:0,scale:1.15,duration:350,onComplete:()=>ring.destroy()});
      this.fishes.getChildren().forEach(o=>{if(o.active&&Phaser.Math.Distance.Between(f.x,f.y,o.x,o.y)<=d.radius){if(d.slow)o.setData('slowUntil',this.time.now+d.slow);if(d.aoe&&o!==f)this.damage(o,d.damage*.62,d.owner,d.color);}});
    }
    b.destroy();
  }

  damage(f,n,owner,color) {
    f.setData('hp',f.getData('hp')-n);f.setTintFill(color);this.time.delayedCall(60,()=>f.active&&f.clearTint());this.float(f.x,f.y-35,`-${n.toFixed(1)}`,'#ffffff',13);
    if(f.getData('boss'))this.phase(f);if(f.getData('hp')<=0)this.kill(f,owner);
  }

  phase(b) {
    const ratio=b.getData('hp')/b.getData('max'), next=ratio<=.33?3:ratio<=.66?2:1, old=b.getData('bossPhase');
    ui['boss-fill'].style.width=`${Math.max(0,ratio*100)}%`;
    if(next>old){b.setData('bossPhase',next);b.setData('speed',42*(1+next*.28));ui['boss-phase'].textContent=`PHASE ${['I','II','III'][next-1]}`;toast(`PHASE ${['I','II','III'][next-1]}`);this.cameras.main.shake(350,.007*next);for(let i=0;i<next+2;i++)this.spawnFish(weightedFish(),Math.random()>.5,Phaser.Math.Between(160,H-150));}
  }

  kill(f,owner) {
    const boss=f.getData('boss'), reward=f.getData('reward')*BETS[this.bet], name=f.getData('name');
    if(owner===0){this.credits+=reward;this.meter=Phaser.Math.Clamp(this.meter+(boss?25:Math.min(4,reward*.08)),0,100);this.combo=this.time.now<=this.comboUntil?this.combo+1:1;this.comboUntil=this.time.now+1500;if(this.combo>=2)toast(`${this.combo}× TEMPLE COMBO`,600);this.float(f.x,f.y-50,`+${reward.toFixed(2)}`,'#ffc857',21);}
    this.burst(f.x,f.y,boss?C.sun:C.jade,boss?32:12);if(this.lock===f)this.clearLock();f.destroy();
    if(boss){this.boss=null;ui['boss-hud'].hidden=true;toast(`${name.toUpperCase()} DEFEATED`,1400);this.cameras.main.shake(750,.014);this.time.delayedCall(1500,()=>this.nextWave());}
    this.refresh();
  }

  relic() {
    if(!this.relicReady)return;this.relicReady=false;this.freezeUntil=this.time.now+4200;ui['relic-trigger'].classList.add('active');toast('TIME RELIC ACTIVATED',1000);this.cameras.main.flash(180,90,255,220,false);
    this.time.delayedCall(12000,()=>{this.relicReady=true;ui['relic-trigger'].classList.remove('active');toast('RELIC RECHARGED',600);});
  }

  templeBonus() { this.meter=0;const bonus=250*Math.max(1,BETS[this.bet]);this.credits+=bonus;toast(`SUN TEMPLE BONUS\n+${bonus.toFixed(2)}`,1500);this.cameras.main.flash(350,255,196,55,false);this.burst(W/2,H/2,C.sun,60);this.refresh(); }
  burst(x,y,color,count){for(let i=0;i<count;i++){const p=this.add.circle(x,y,Phaser.Math.Between(2,5),color,.9).setDepth(25),a=Math.random()*Math.PI*2,d=Phaser.Math.Between(35,145);this.tweens.add({targets:p,x:x+Math.cos(a)*d,y:y+Math.sin(a)*d,alpha:0,scale:.2,duration:Phaser.Math.Between(350,750),onComplete:()=>p.destroy()});}}
  float(x,y,text,color,size){const t=this.add.text(x,y,text,{fontFamily:'monospace',fontSize:`${size}px`,color,fontStyle:'bold',stroke:'#000',strokeThickness:4}).setOrigin(.5).setDepth(40);this.tweens.add({targets:t,y:y-42,alpha:0,duration:650,onComplete:()=>t.destroy()});}

  refresh(){ui['credits-value'].textContent=this.credits.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});ui['bet-value'].textContent=BETS[this.bet].toFixed(2);ui['combo-value'].textContent=this.combo>=2?`${this.combo}× COMBO`:'NO COMBO';ui['temple-meter'].style.width=`${this.meter}%`;ui['temple-value'].textContent=`${Math.floor(this.meter)}%`;}

  update(time,delta) {
    if(Phaser.Input.Keyboard.JustDown(this.keys.ONE))this.choose('sunbolt');if(Phaser.Input.Keyboard.JustDown(this.keys.TWO))this.choose('jadenet');if(Phaser.Input.Keyboard.JustDown(this.keys.THREE))this.choose('obsidian');if(Phaser.Input.Keyboard.JustDown(this.keys.A))this.toggleAuto();if(Phaser.Input.Keyboard.JustDown(this.keys.L))this.lockNearest();if(Phaser.Input.Keyboard.JustDown(this.keys.F))this.relic();if(Phaser.Input.Keyboard.JustDown(this.keys.Q))this.changeBet(-1);if(Phaser.Input.Keyboard.JustDown(this.keys.E))this.changeBet(1);
    if(this.lock&&!this.lock.active)this.clearLock();if(this.lock?.active){this.reticle.setPosition(this.lock.x,this.lock.y);this.reticle.rotation+=delta*.0012;}
    const tx=this.lock?.active?this.lock.x:(this.aimX||W/2),ty=this.lock?.active?this.lock.y:(this.aimY||H/2);this.player.barrel.rotation=Phaser.Math.Angle.Between(this.player.c.x,this.player.c.y,tx,ty)+Math.PI/2;
    if(this.held||this.auto||this.keys.SPACE.isDown){if(this.auto&&!this.lock)this.lockNearest();this.shoot(time);}if(this.combo&&time>this.comboUntil){this.combo=0;this.refresh();}if(this.meter>=100)this.templeBonus();
    this.bubbles.forEach(b=>{b.y-=b.speed*delta/1000;if(b.y<-8){b.y=H+8;b.x=Phaser.Math.Between(0,W);}});
    this.fishes.getChildren().forEach(f=>{if(!f.active)return;const d=f.data.values,mod=time<this.freezeUntil&&!d.boss?.08:time<d.slowUntil?.38:1,spd=d.speed*mod*delta/1000;d.phase+=delta*.001;
      if(d.boss){if(f.x>W*.76)d.left=false;if(f.x<W*.24)d.left=true;f.x+=(d.left?1:-1)*spd;f.y=H/2+Math.sin(d.phase*1.25)*150;f.setFlipX(!d.left);}else{f.x+=(d.left?1:-1)*spd;if(d.motion==='sine')f.y=d.baseY+Math.sin(d.phase*2.2)*25;if(d.motion==='zig')f.y=d.baseY+Math.sin(d.phase*4.3)*48;if(d.motion==='glide')f.y=d.baseY+Math.cos(d.phase*1.3)*55;if(d.motion==='drift')f.y=d.baseY+Math.sin(d.phase*.75)*34;if(d.motion==='serpent')f.y=d.baseY+Math.sin(d.phase*5.6)*70;if(d.motion==='hunter')f.y+=(H/2-f.y)*.002;if(d.motion==='rush')f.x+=(d.left?1:-1)*spd*.8;}
      if(!d.boss&&(f.x<-180||f.x>W+180)){if(this.lock===f)this.clearLock();f.destroy();}
    });
    this.bullets.getChildren().forEach(b=>{if(b.active&&(b.x<-80||b.x>W+80||b.y<-80||b.y>H+80))b.destroy();});
    if(!this.boss&&this.fishes.getChildren().filter(f=>f.active).length===0&&!this.pending){this.pending=true;this.time.delayedCall(900,()=>{this.pending=false;this.nextWave();});}
  }
}

new Phaser.Game({
  type: Phaser.AUTO, parent: 'game-container', width: W, height: H, backgroundColor: '#01070d',
  physics: { default: 'arcade', arcade: { gravity: { x:0, y:0 }, debug:false } },
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH, width:W, height:H },
  render: { antialias:true, pixelArt:false }, scene:[Abyss]
});
