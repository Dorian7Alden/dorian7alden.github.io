const fetchProblems = require('../api/fetch-problems.js');

(async () => {
    const problems = await fetchProblems();
    console.log(`共 ${problems.length} 道题目:`);
    problems.forEach(p => console.log(`  ${p.number}. ${p.title} (得分: ${p.obtainedScore}/${p.maxScore})`));
})();
