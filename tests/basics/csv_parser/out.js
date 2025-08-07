let lines = new TextDecoder().decode(await Deno.readAll(Deno.stdin)).trim();
lines = lines.split("\n");
let i = 0;
let header = [];
let rows = [];
for (const line of lines) {
    if ((i === 0)) {
    header = line.split(",");
  } else {
    let zip = header.map((item, i) => [item, line.split(",")[i]]);
    let row = {};
    for (const kv of zip) {
    row[kv[0]] = kv[1];
  }
    rows.push(row)
  }
    i = (i + 1);
  }
for (const row of rows) {
    console.log(row.name);
  }
let age_over_30 = 0;
for (const row of rows) {
    if ((row.age <= 30)) {
    age_over_30 = (age_over_30 + 1);
  }
  }
console.log(age_over_30);