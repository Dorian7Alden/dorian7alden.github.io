const submit = require('../api/submit.js');

(async () => {
    // 提交题目 1，默认 main 分支
    const result = await submit(1);
    console.log(`状态: ${result.status}`);
    console.log(`响应: ${result.body.slice(0, 200)}`);
})();
