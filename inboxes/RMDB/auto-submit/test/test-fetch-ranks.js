const fetchRanks = require('../api/fetch-ranks.js');

(async () => {
    const ranks = await fetchRanks();
    console.log(`problems 排行榜: ${ranks.problems.ranks.length} 条`);
    console.log(`perf 排行榜:     ${ranks.perf.ranks.length} 条`);
})();
