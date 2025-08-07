let input = new TextDecoder().decode(await Deno.readAll(Deno.stdin)).trim();
let words = input.split("\n");
let count = {};
for (const word of words) {
    count[word] = (1 + count[word]);
  }
console.log(count);