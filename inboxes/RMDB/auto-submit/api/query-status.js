const fs = require("fs");

const config = JSON.parse(fs.readFileSync(__dirname + "/../config/config.json", "utf-8"));
const params = JSON.parse(fs.readFileSync(__dirname + "/../config/params.json", "utf-8"));

const headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "priority": "u=1, i",
    "referer": "https://course.educg.net/assignment/showOJPProcessMsg.jsp",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Linux\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0",
    "x-requested-with": "XMLHttpRequest"
};

headers["cookie"] = Object.entries(config.cookies).map(([k, v]) => `${k}=${v}`).join("; ");

const baseUrl = "https://course.educg.net/assignment/showOJPProcessJSON.jsp";

const POLL_INTERVAL = 5000;
const MAX_POLLS = 360;

async function queryStatus(number) {
    const p = params.find(e => e.number === number);
    if (!p) {
        console.error(`找不到题目 number=${number}`);
        return null;
    }

    const url = baseUrl + "?" + new URLSearchParams({
        assignID: p.assignID,
        problemID: p.problemID,
        userID: config.userID,
        buaa: String(Math.random()),
    }).toString();

    const response = await fetch(url, { method: "GET", headers });
    if (!response.ok) {
        return { error: `HTTP ${response.status}` };
    }

    const text = await response.text();
    try {
        return JSON.parse(text);
    } catch {
        return { raw: text };
    }
}

async function pollStatus(number) {
    const p = params.find(e => e.number === number);
    if (!p) {
        console.error(`找不到题目 number=${number}`);
        return null;
    }

    console.log(`查询题目 ${p.number} (${p.title}) ...`);

    for (let i = 0; i < MAX_POLLS; i++) {
        const result = await queryStatus(number);
        console.log(`  第 ${i + 1} 次: ${JSON.stringify(result).slice(0, 200)}`);

        if (!result || result.error || result.raw) {
            return { number: p.number, title: p.title, result };
        }

        if (Array.isArray(result) && result.length > 0 && result[0].ret !== undefined) {
            if (result[0].ret !== "0") {
                return { number: p.number, title: p.title, result };
            }
        }

        await new Promise(r => setTimeout(r, POLL_INTERVAL));
    }

    return { number: p.number, title: p.title, result: { timeout: true } };
}

module.exports = pollStatus;

if (require.main === module) {
    const number = parseInt(process.argv[2]);
    if (isNaN(number)) {
        console.error("用法: node query-status.js <number>");
        process.exit(1);
    }
    pollStatus(number);
}
