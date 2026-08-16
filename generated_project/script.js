// script.js - Core game logic for Flappy Bird clone

// ------------------------------------------------------------
// Canvas & Global Constants
// ------------------------------------------------------------
const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');

// Game constants
const GRAVITY = 0.5;
const FLAP_STRENGTH = -8;
const PIPE_SPEED = 2;
const PIPE_INTERVAL = 1500; // ms between pipes
const GAP_HEIGHT = 150;
const BIRD_WIDTH = 34;
const BIRD_HEIGHT = 24;
const GROUND_HEIGHT = 50;

// Asset loading
const birdImg = new Image();
birdImg.src = 'assets/bird.png';

const pipeTopImg = new Image();
pipeTopImg.src = 'assets/pipe-top.png';

const pipeBottomImg = new Image();
pipeBottomImg.src = 'assets/pipe-bottom.png';

// ------------------------------------------------------------
// Bird Class
// ------------------------------------------------------------
class Bird {
  constructor() {
    this.x = 80;
    this.y = canvas.height / 2;
    this.width = BIRD_WIDTH;
    this.height = BIRD_HEIGHT;
    this.velocity = 0;
  }

  flap() {
    this.velocity = FLAP_STRENGTH;
  }

  update() {
    // Apply gravity
    this.velocity += GRAVITY;
    this.y += this.velocity;

    // Prevent bird from leaving the top of the canvas
    if (this.y < 0) {
      this.y = 0;
      this.velocity = 0;
    }
  }

  draw() {
  if (birdImg.complete && birdImg.naturalWidth !== 0) {
    ctx.drawImage(birdImg, this.x, this.y, this.width, this.height);
  } else {
    ctx.fillStyle = '#f7d51d';
    ctx.fillRect(this.x, this.y, this.width, this.height);
  }
}
}

// ------------------------------------------------------------
// Pipe Class
// ------------------------------------------------------------
class Pipe {
  constructor() {
    this.width = 52; // typical pipe width
    this.gapHeight = GAP_HEIGHT;
    this.speed = PIPE_SPEED;
    this.x = canvas.width;
    // Gap's top Y coordinate (where the opening starts)
    const minGapY = GROUND_HEIGHT;
    const maxGapY = canvas.height - GROUND_HEIGHT - this.gapHeight;
    this.gapY = Math.random() * (maxGapY - minGapY) + minGapY;
    this.scored = false; // used for scoring once per pipe
  }

  update() {
    this.x -= this.speed;
  }

  draw() {
  const topPipeHeight = pipeTopImg.height || (canvas.height - this.gapY - this.gapHeight);
  const bottomPipeHeight = pipeBottomImg.height || (canvas.height - this.gapY - this.gapHeight);

  if (pipeTopImg.complete && pipeTopImg.naturalWidth !== 0) {
    ctx.drawImage(pipeTopImg, this.x, this.gapY - topPipeHeight, this.width, topPipeHeight);
  } else {
    ctx.fillStyle = '#2ecc71';
    ctx.fillRect(this.x, this.gapY - topPipeHeight, this.width, topPipeHeight);
  }

  if (pipeBottomImg.complete && pipeBottomImg.naturalWidth !== 0) {
    ctx.drawImage(pipeBottomImg, this.x, this.gapY + this.gapHeight, this.width, bottomPipeHeight);
  } else {
    ctx.fillStyle = '#2ecc71';
    ctx.fillRect(this.x, this.gapY + this.gapHeight, this.width, bottomPipeHeight);
  }
}

  isOffScreen() {
    return this.x + this.width < 0;
  }
}

// ------------------------------------------------------------
// Game Class – orchestrates everything
// ------------------------------------------------------------
class Game {
  constructor(canvas, ctx) {
    this.canvas = canvas;
    this.ctx = ctx;
    this.bird = new Bird();
    this.pipes = [];
    this.score = 0;
    this.lastPipeTime = 0; // timestamp of last pipe spawn
    this.gameState = 'running'; // 'running' | 'over'

    // Bind input handlers
    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && this.gameState === 'running') {
        this.bird.flap();
      }
    });
    this.canvas.addEventListener('mousedown', () => {
      if (this.gameState === 'running') this.bird.flap();
    });
    const restartBtn = document.getElementById('restart-btn');
    if (restartBtn) {
      restartBtn.addEventListener('click', () => this.restart());
    }
  }

  start() {
    this.gameState = 'running';
    requestAnimationFrame(this.loop.bind(this));
  }

  loop(timestamp) {
    if (!this.lastPipeTime) this.lastPipeTime = timestamp;
    const delta = timestamp - this.lastPipeTime;

    this.update(timestamp);
    this.render();

    if (this.gameState === 'running') {
      requestAnimationFrame(this.loop.bind(this));
    }
  }

  update(timestamp) {
    // Bird movement
    this.bird.update();

    // Pipe movement
    this.pipes.forEach((pipe) => pipe.update());
    // Remove off‑screen pipes
    this.pipes = this.pipes.filter((pipe) => !pipe.isOffScreen());

    // Spawn new pipe if interval elapsed
    if (timestamp - this.lastPipeTime > PIPE_INTERVAL) {
      this.pipes.push(new Pipe());
      this.lastPipeTime = timestamp;
    }

    // Collision detection
    if (this.checkCollisions()) {
      this.gameOver();
      return;
    }

    // Scoring – count when bird passes a pipe
    this.pipes.forEach((pipe) => {
      if (!pipe.scored && pipe.x + pipe.width < this.bird.x) {
        pipe.scored = true;
        this.score += 1;
      }
    });
  }

  render() {
    // Clear canvas
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Optional background – simple sky colour
    this.ctx.fillStyle = '#70c5ce'; // sky blue
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height - GROUND_HEIGHT);

    // Ground
    this.ctx.fillStyle = '#ded895'; // ground colour
    this.ctx.fillRect(
      0,
      this.canvas.height - GROUND_HEIGHT,
      this.canvas.width,
      GROUND_HEIGHT
    );

    // Draw bird and pipes
    this.bird.draw();
    this.pipes.forEach((pipe) => pipe.draw());

    // Draw score
    this.ctx.fillStyle = '#fff';
    this.ctx.font = '24px Arial';
    this.ctx.fillText('Score: ' + this.score, 10, 30);
  }

  checkCollisions() {
    // Ground collision
    if (this.bird.y + this.bird.height >= this.canvas.height - GROUND_HEIGHT) {
      return true;
    }

    // Pipe collisions (AABB)
    for (const pipe of this.pipes) {
      // Top pipe rectangle
      const topRect = {
        x: pipe.x,
        y: 0,
        width: pipe.width,
        height: pipe.gapY,
      };
      // Bottom pipe rectangle
      const bottomRect = {
        x: pipe.x,
        y: pipe.gapY + pipe.gapHeight,
        width: pipe.width,
        height: this.canvas.height - pipe.gapY - pipe.gapHeight - GROUND_HEIGHT,
      };

      if (this.rectIntersect(this.bird, topRect) || this.rectIntersect(this.bird, bottomRect)) {
        return true;
      }
    }
    return false;
  }

  rectIntersect(a, b) {
    return (
      a.x < b.x + b.width &&
      a.x + a.width > b.x &&
      a.y < b.y + b.height &&
      a.y + a.height > b.y
    );
  }

  gameOver() {
    this.gameState = 'over';
    // Show overlay with final score
    const overlay = document.getElementById('game-over');
    const finalScoreEl = document.getElementById('final-score');
    if (finalScoreEl) finalScoreEl.textContent = 'Your score: ' + this.score;
    if (overlay) overlay.classList.remove('hidden');
  }

  restart() {
    // Reset game state
    this.bird = new Bird();
    this.pipes = [];
    this.score = 0;
    this.lastPipeTime = 0;
    this.gameState = 'running';
    // Hide overlay
    const overlay = document.getElementById('game-over');
    if (overlay) overlay.classList.add('hidden');
    // Restart loop
    requestAnimationFrame(this.loop.bind(this));
  }
}

// ------------------------------------------------------------
// Entry point – instantiate and start the game
// ------------------------------------------------------------
const game = new Game(canvas, ctx);
game.start();

// Export for potential external access (e.g., debugging)
window.game = game;
