const fs = require('fs');
const path = require('path');

const root = process.argv[2];
if (!root) {
  console.error('Usage: node tools/tune_fake_hero_logos.js <site-root>');
  process.exit(1);
}

const cssPath = path.join(root, 'styles.css');
let css = fs.readFileSync(cssPath, 'utf8');
const block = `

/* Fictional hero logo composition tuning */
@media (min-width: 981px) {
  .hero {
    grid-template-columns: minmax(0, 0.96fr) 390px;
    column-gap: 46px;
  }

  .hero-copy {
    position: relative;
    z-index: 2;
    max-width: 610px;
  }

  .hero-visual {
    position: relative;
    z-index: 1;
    justify-self: end;
    width: 390px;
    transform: translateX(28px);
  }

  .hero-logo-board-fake {
    width: 390px;
    height: 330px;
  }

  .hero-logo-board-fake .fake-logo {
    min-height: 54px;
    padding: 9px 13px;
  }

  .fake-logo strong {
    font-size: 24px;
  }

  .fake-logo i {
    width: 24px;
    height: 24px;
  }

  .fake-logo-nova {
    left: 1%;
    top: 18%;
    width: 116px;
  }

  .fake-logo-lumen {
    left: 20%;
    top: 7%;
    width: 146px;
  }

  .fake-logo-orbit {
    right: 19%;
    top: 22%;
    width: 130px;
  }

  .fake-logo-vesta {
    right: -2%;
    top: 14%;
    width: 132px;
  }

  .fake-logo-aura {
    left: 8%;
    top: 43%;
    width: 238px;
    height: 70px;
  }

  .fake-logo-cosmo {
    left: 3%;
    bottom: 15%;
    width: 208px;
  }

  .fake-logo-medix {
    right: -1%;
    bottom: 8%;
    width: 210px;
  }
}
`;

if (!css.includes('Fictional hero logo composition tuning')) {
  css = `${css.trimEnd()}${block}\n`;
}
fs.writeFileSync(cssPath, css, 'utf8');
console.log('Tuned fictional hero logo composition');
