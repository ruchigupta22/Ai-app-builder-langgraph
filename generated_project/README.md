# Flappy Bird Canvas Game

A lightweight, pure‑JavaScript implementation of the classic **Flappy Bird** game using the HTML5 Canvas API. The game runs entirely in the browser with no external dependencies and adapts to different screen sizes.

---

## Setup

1. **Required files** – make sure the following files are present in the same directory:
   - `index.html` – the main page containing the `<canvas>` element.
   - `script.js` – game logic, rendering, and input handling.
   - `style.css` – basic styling for the page and canvas.
2. **Running the game**
   - The simplest way is to open `index.html` directly in a modern browser (double‑click the file).
   - For a more reliable experience (especially when loading assets), serve the folder with a static HTTP server, e.g.:
     ```bash
     # Python 3
     python -m http.server 8000

     # Then open http://localhost:8000 in your browser
     ```
   - Any static server (Node's `http-server`, `live-server`, etc.) will work.

---

## Gameplay Controls

- **Flap** – Click anywhere on the canvas **or** press the **Space** bar to make the bird flap upward.
- **Gravity** constantly pulls the bird down; the goal is to navigate through the gaps between moving pipes.
- **Scoring** – Each time the bird successfully passes a pipe pair, the score increments by one and is displayed in the top‑left corner.
- The game ends when the bird collides with a pipe or the ground, after which a *Game Over* overlay appears and you can restart by pressing **Space** or clicking.

---

## File Structure

```
project-root/
├── index.html      # HTML page with the <canvas> element and UI overlay
├── script.js       # Core game engine: rendering, physics, input, and state
├── style.css       # Page layout, canvas centering, responsive scaling
└── README.md       # Documentation (this file)
```

- **`index.html`** – Sets up the canvas, loads `script.js`, and provides a container for the score and game‑over messages.
- **`script.js`** – Contains all game constants, the main loop, sprite handling, collision detection, and user‑input listeners.
- **`style.css`** – Ensures the canvas scales responsively while preserving aspect ratio, and styles the overlay text.

---

## Customization

### Replacing Sprites
1. Prepare PNG images for the bird and pipe (same dimensions as the originals or adjust the drawing code).
2. In `script.js`, locate the image loading section (usually near the top) and replace the source URLs:
   ```javascript
   const birdImg = new Image();
   birdImg.src = "path/to/your/bird.png"; // replace

   const pipeImg = new Image();
   pipeImg.src = "path/to/your/pipe.png"; // replace
   ```
3. If the sprite dimensions differ, update the width/height constants (`BIRD_WIDTH`, `BIRD_HEIGHT`, `PIPE_WIDTH`, etc.) accordingly.

### Tweaking Game Constants
All tunable parameters are defined at the beginning of `script.js`:
```javascript
const GRAVITY = 0.5;          // How fast the bird falls
const FLAP_STRENGTH = -8;     // Upward velocity applied on flap
const PIPE_SPEED = 2;        // Horizontal pipe movement speed
const PIPE_GAP = 120;        // Vertical gap between top/bottom pipes
const PIPE_SPACING = 2000;   // Time (ms) between new pipe pairs
```
Modify these values to change difficulty, speed, or visual feel. After saving, refresh the page to see the changes.

---

## License

*Add your preferred license here (e.g., MIT, Apache 2.0, GPL‑3.0, etc.).*

---

**Responsive Design** – The canvas automatically scales to fit the browser window while maintaining the original aspect ratio, ensuring the game looks good on desktops, tablets, and mobile devices.
