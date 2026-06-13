const fs = require('fs');
const path = require('path');

const root = process.argv[2];
if (!root) {
  console.error('Usage: node tools/update_fake_hero_logos.js <site-root>');
  process.exit(1);
}

const indexPath = path.join(root, 'index.html');
const cssPath = path.join(root, 'styles.css');

let index = fs.readFileSync(indexPath, 'utf8');
const oldBoard = /<div class="hero-logo-board">[\s\S]*?<\/div>\s*<\/div>\s*<\/a>/;
const newBoard = `<div class="hero-logo-board hero-logo-board-fake">
              <span class="hero-logo-tile fake-logo fake-logo-nova" aria-label="Пример выдуманного логотипа NOVA"><i></i><strong>NOVA</strong></span>
              <span class="hero-logo-tile fake-logo fake-logo-lumen" aria-label="Пример выдуманного логотипа LUMEN"><i></i><strong>LUMEN</strong></span>
              <span class="hero-logo-tile fake-logo fake-logo-orbit" aria-label="Пример выдуманного логотипа ORBIT"><i></i><strong>ORBIT</strong></span>
              <span class="hero-logo-tile fake-logo fake-logo-vesta" aria-label="Пример выдуманного логотипа VESTA"><i></i><strong>VESTA</strong></span>
              <span class="hero-logo-tile fake-logo fake-logo-aura" aria-label="Пример выдуманного логотипа AURA"><i></i><strong>AURA</strong></span>
              <span class="hero-logo-tile fake-logo fake-logo-cosmo" aria-label="Пример выдуманного логотипа COSMO"><i></i><strong>COSMO</strong></span>
              <span class="hero-logo-tile fake-logo fake-logo-medix" aria-label="Пример выдуманного логотипа MEDIX"><i></i><strong>MEDIX</strong></span>
            </div>
          </div>
        </a>`;

if (!oldBoard.test(index)) {
  throw new Error('Hero logo board not found');
}
index = index.replace(oldBoard, newBoard);
index = index.replace(/styles\.css\?v=20260611-[A-Za-z0-9]+/g, 'styles.css?v=20260612-fakelogos1');
fs.writeFileSync(indexPath, index, 'utf8');

let css = fs.readFileSync(cssPath, 'utf8');
const block = `

/* Fictional hero logo composition */
.hero-logo-board-fake .hero-logo-tile img {
  display: none;
}

.hero-logo-board-fake .fake-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-width: 118px;
  min-height: 62px;
  padding: 10px 16px;
  color: #0e0e0e;
  border: 2px solid rgba(14, 14, 14, 0.82);
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(255, 255, 255, 0.9)),
    radial-gradient(circle at 20% 15%, rgba(212, 175, 55, 0.28), transparent 42%);
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.16);
  letter-spacing: 0;
}

.fake-logo strong {
  display: block;
  font-size: clamp(18px, 2vw, 29px);
  line-height: 1;
  font-weight: 950;
  white-space: nowrap;
  letter-spacing: 0;
}

.fake-logo i {
  position: relative;
  display: block;
  flex: 0 0 auto;
  width: 28px;
  height: 28px;
}

.fake-logo-nova i {
  border: 6px solid #154b3d;
  border-right-color: transparent;
  border-radius: 50%;
}

.fake-logo-lumen i {
  width: 24px;
  height: 34px;
  background: linear-gradient(90deg, #163f36 0 36%, transparent 36% 52%, #163f36 52% 100%);
  border-radius: 3px;
  transform: skewX(-10deg);
}

.fake-logo-orbit i {
  border: 3px solid #1b4b5d;
  border-radius: 50%;
}

.fake-logo-orbit i::after {
  content: "";
  position: absolute;
  inset: 9px -8px;
  border-top: 3px solid #1b4b5d;
  transform: rotate(-22deg);
}

.fake-logo-vesta i {
  background:
    linear-gradient(135deg, #18433a 0 47%, transparent 47%),
    linear-gradient(45deg, transparent 52%, #18433a 52%);
  border-radius: 4px;
}

.fake-logo-aura i {
  border-radius: 8px;
  background:
    linear-gradient(45deg, transparent 0 40%, #17483e 40% 60%, transparent 60%),
    linear-gradient(-45deg, transparent 0 40%, #17483e 40% 60%, transparent 60%);
}

.fake-logo-cosmo i {
  background:
    radial-gradient(circle at 30% 30%, #17483e 0 5px, transparent 6px),
    radial-gradient(circle at 70% 30%, #17483e 0 5px, transparent 6px),
    radial-gradient(circle at 50% 70%, #17483e 0 5px, transparent 6px);
}

.fake-logo-medix i {
  background: #17483e;
  clip-path: polygon(38% 0, 62% 0, 62% 38%, 100% 38%, 100% 62%, 62% 62%, 62% 100%, 38% 100%, 38% 62%, 0 62%, 0 38%, 38% 38%);
}

.fake-logo-nova {
  left: 5%;
  top: 17%;
  width: 132px;
  transform: rotate(-8deg);
}

.fake-logo-lumen {
  left: 19%;
  top: 8%;
  width: 168px;
  transform: rotate(3deg);
}

.fake-logo-orbit {
  right: 25%;
  top: 21%;
  width: 150px;
  transform: rotate(-4deg);
}

.fake-logo-vesta {
  right: 5%;
  top: 13%;
  width: 142px;
  transform: rotate(5deg);
}

.fake-logo-aura {
  left: 12%;
  top: 43%;
  width: 270px;
  height: 74px;
  transform: rotate(-2deg);
}

.fake-logo-cosmo {
  left: 7%;
  bottom: 14%;
  width: 235px;
  transform: rotate(2deg);
}

.fake-logo-medix {
  right: 4%;
  bottom: 8%;
  width: 245px;
  transform: rotate(-5deg);
}

@media (max-width: 760px) {
  .hero-logo-board-fake .fake-logo {
    min-width: 86px;
    min-height: 46px;
    padding: 8px 10px;
    gap: 7px;
  }

  .fake-logo strong {
    font-size: 17px;
  }

  .fake-logo i {
    width: 20px;
    height: 20px;
  }

  .fake-logo-nova {
    left: 5%;
    top: 14%;
    width: 96px;
  }

  .fake-logo-lumen {
    left: 28%;
    top: 8%;
    width: 118px;
  }

  .fake-logo-orbit {
    right: 8%;
    top: 22%;
    width: 108px;
  }

  .fake-logo-vesta {
    right: 2%;
    top: 45%;
    width: 108px;
  }

  .fake-logo-aura {
    left: 8%;
    top: 39%;
    width: 176px;
    height: 58px;
  }

  .fake-logo-cosmo {
    left: 4%;
    bottom: 13%;
    width: 156px;
  }

  .fake-logo-medix {
    right: 4%;
    bottom: 5%;
    width: 150px;
  }
}
`;

if (!css.includes('Fictional hero logo composition')) {
  css = `${css.trimEnd()}${block}\n`;
}
fs.writeFileSync(cssPath, css, 'utf8');

console.log('Updated hero logos to fictional marks');
