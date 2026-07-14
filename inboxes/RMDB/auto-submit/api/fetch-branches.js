const { execSync } = require("child_process");

function fetchBranches() {
  const output = execSync("git branch -r", {
    encoding: "utf-8",
    cwd: process.cwd(),
  });

  return output
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line && !line.includes("->")) // 排除 HEAD 别名
    .map((line) => line.replace(/^origin\//, "")); // 去掉 origin/ 前缀
}

module.exports = fetchBranches;

if (require.main === module) {
  const branches = fetchBranches();
  console.log(branches.join("\n"));
}
