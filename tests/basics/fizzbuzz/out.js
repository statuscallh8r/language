let fizz_divisor;
let buzz_divisor;
let n;
if (Deno.isatty(Deno.stdin.rid)) {
    fizz_divisor = prompt("fizz? ");
    buzz_divisor = prompt("buzz? ");
    n = prompt("n? ");
  } else {
    let input = new TextDecoder().decode(await Deno.readAll(Deno.stdin)).trim();
    input = input.split("\n");
    fizz_divisor = input[0];
    buzz_divisor = input[1];
    n = input[2];
  }
let i = 0;
while ((i <= n)) {
    let out = "";
    if (((i % fizz_divisor) === 0)) {
    out = (out + "fizz");
  }
    if (((i % buzz_divisor) === 0)) {
    out = (out + "buzz");
  }
    if ((out === "")) {
    out = i;
  }
    console.log(out);
    i = (i + 1);
  }