let input = new TextDecoder().decode(await Deno.readAll(Deno.stdin)).trim();
let words = input.split("\n");
let groups = {};
for (const word of words) {
    let key = word.split("").sort().join();;
    if (![(key in groups)].some(x => x)) {
    groups[key] = [];
  }
    groups[key].push(word);
  }
for (const group of Object.values(groups)) {
    console.log(group.join(" "));
  }