const fs = require("fs");

const config = JSON.parse(fs.readFileSync(__dirname + "/../config/config.json", "utf-8"));
const params = JSON.parse(fs.readFileSync(__dirname + "/../config/params.json", "utf-8"));

const headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cache-control": "max-age=0",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://course.educg.net",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Linux\"",
    "sec-fetch-dest": "iframe",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0"
};

headers["cookie"] = Object.entries(config.cookies).map(([k, v]) => `${k}=${v}`).join("; ");

const url = "https://course.educg.net/assignment/showOJPProcessMsg.jsp";

const submitStartTime = Date.now();

async function submit(number, branch = "main") {
    const p = params.find(e => e.number === number);
    if (!p) return null;

    headers["referer"] = `https://course.educg.net/assignment/programOJPList_ce.jsp?assignID=${p.assignID}&proNum=${p.proNum}&libCenter=false`;

    const wtime = Math.floor((Date.now() - submitStartTime) / 1000);

    const body = new URLSearchParams({
        doSubmit: "true",
        byCE: "true",
        wtime: String(wtime),
        javaMainCLass: "Main",
        progLanguage: "gitlab",
        problemID: p.problemID,
        assignID: p.assignID,
        cgsoucecode: config.cgsoucecode + " --branch=" + branch,
    }).toString();

    const response = await fetch(url, {
        method: "POST",
        headers,
        body,
    });

    const text = await response.text();
    return { number: p.number, title: p.title, status: response.status, body: text };
}

module.exports = submit;

if (require.main === module) {
    const number = parseInt(process.argv[2]);
    const branch = process.argv[3] || "main";
    if (!isNaN(number)) submit(number, branch);
}
