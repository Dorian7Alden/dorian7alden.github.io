const pollStatus = require('../api/query-status.js');

(async () => {
    const status = await pollStatus(1);
    console.log(`结果: ${JSON.stringify(status.result).slice(0, 200)}`);
})();
