const cheerio = require("cheerio");
const fs = require("fs");

const config = JSON.parse(fs.readFileSync(__dirname + "/../config/config.json", "utf-8"));

const headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": `"Microsoft Edge";v="149", "Chromium";v="149", "Not)A;Brand";v="24"`,
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": `"Linux"`,
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0"
};

headers["cookie"] = Object.entries(config.cookies).map(([k, v]) => `${k}=${v}`).join("; ");

const baseUrl = "https://course.educg.net/assignment/contestindex.jsp";

const tasks = [
    { assignID: "46965", contestID: "6gutcJNDUrw", taskID: "2295989" },
    { assignID: "47932", contestID: "6gutcJNDUrw", taskID: "13352925" },
];

function decodeEntities(str) {
    return cheerio.load("<div>" + str + "</div>")("div").text().replace(/&nbsp;/g, " ");
}

function parseHtml(html) {
    const $ = cheerio.load(html);
    const problems = [];

    $("tbody tr").each((_, tr) => {
        const $tr = $(tr);
        const $numCell = $tr.find("th").first();
        if (!$numCell.length) return;

        const num = parseInt($numCell.text().replace(".", ""));
        if (isNaN(num)) return;

        const $tds = $tr.find("td");

        const $titleLink = $tds.eq(0).find("a").first();
        const title = $titleLink.text().trim();

        const maxScore = parseFloat($tds.eq(1).text()) || 0;

        const $infoTd = $tds.eq(2);

        let lastSubmitTime = "";
        let obtainedScore = 0;
        const testResultParts = [];

        $infoTd.find("> div > p").each((_, p) => {
            const text = decodeEntities($(p).html() || "").trim();
            if (!text) return;

            if (text.startsWith("最后一次提交时间：")) {
                lastSubmitTime = text.replace("最后一次提交时间：", "");
            } else if (text.startsWith("得分：")) {
                obtainedScore = parseFloat(text.replace("得分：", "")) || 0;
            } else if (text === "AC") {
                obtainedScore = maxScore;
            } else {
                testResultParts.push(text);
            }
        });

        const $collapse = $infoTd.find(".collapse small");
        const compileDetail = $collapse.length ? decodeEntities($collapse.html() || "") : "";

        let reviewInfo = "";
        $infoTd.find("> div > small").each((_, el) => {
            reviewInfo += decodeEntities($(el).html() || "") + "\n";
        });

        problems.push({
            number: num,
            title,
            maxScore,
            obtainedScore,
            lastSubmitTime,
            testResult: testResultParts.join("\n"),
            reviewInfo: reviewInfo.trim(),
            compileDetail,
        });
    });

    problems.sort((a, b) => a.number - b.number);
    return problems;
}

async function fetchProblems() {
    const allProblems = [];

    for (const task of tasks) {
        const url = baseUrl + "?" + new URLSearchParams(task).toString();

        const response = await fetch(url, {
            method: "GET",
            headers,
        });

        if (!response.ok) continue;

        const html = await response.text();
        const problems = parseHtml(html);
        allProblems.push(...problems);
    }

    fs.writeFileSync(__dirname + "/../data/problems.json", JSON.stringify(allProblems, null, 2));
    return allProblems;
}

module.exports = fetchProblems;

if (require.main === module) {
    fetchProblems();
}
