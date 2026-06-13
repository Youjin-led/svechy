// Quick syntax check for all tradelab modules
const modules = [
  'tradelab_market_phase',
  'tradelab_news_filter',
  'tradelab_run_once',
  'tradelab_incubate_once',
  'tradelab_daily_discovery',
  'tradelab_risk_controls'
];

let allOk = true;
for (const mod of modules) {
  try {
    require('./' + mod);
    console.log('✅ ' + mod + '.js — OK');
  } catch (e) {
    console.log('❌ ' + mod + '.js — ' + e.message);
    allOk = false;
  }
}

if (allOk) {
  console.log('\n🎉 All modules loaded successfully!');
} else {
  console.log('\n⚠️  Some modules have errors.');
  process.exit(1);
}
