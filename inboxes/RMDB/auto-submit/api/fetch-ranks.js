const cheerio = require("cheerio");
const fs = require("fs");

const config = JSON.parse(fs.readFileSync(__dirname + "/../config/config.json", "utf-8"));

const headers = {
    "accept": "text/html, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://course.educg.net",
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

const url = "https://course.educg.net//pages/contest/contest_rank_load.jsp";

const tasks = [
    { label: "problems", taskID: "2295989" },
    { label: "perf",     taskID: "13352925" },
];

const numericCols = new Set(["#", "得分", "tpc-x", "rmdb-max-rss-gb", "rank"]);

function parseRanks(html) {
    const $ = cheerio.load(html);

    const columns = [];
    $("#ContestRankTable thead th").each((_, th) => {
        columns.push($(th).text().trim().replace(/\(DESC\)/, "").trim());
    });

    const ranks = [];
    $("#ContestRankTable tbody tr").each((_, tr) => {
        const cells = $(tr).find("th, td");
        if (cells.length < columns.length) return;

        const entry = {};
        cells.each((i, cell) => {
            const value = $(cell).text().trim();
            const colName = columns[i];
            entry[colName] = numericCols.has(colName) ? parseFloat(value) || 0 : value;
        });

        ranks.push(entry);
    });

    return { columns, ranks };
}

async function fetchRanks() {
    const result = {};

    for (const { label, taskID } of tasks) {
        const response = await fetch(url, {
            method: "POST",
            headers,
            body: new URLSearchParams({ contestID: "6gutcJNDUrw", taskID }).toString(),
        });

        if (!response.ok) continue;

        const html = await response.text();
        result[label] = parseRanks(html);
    }

    fs.writeFileSync(__dirname + "/../data/ranks.json", JSON.stringify(result, null, 2));
    return result;
}

module.exports = fetchRanks;

if (require.main === module) {
    fetchRanks();
}
