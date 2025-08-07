let lines = new TextDecoder().decode(await Deno.readAll(Deno.stdin)).trim();
lines = lines.split("\n");
let modules = {};
for (const line of lines) {
    let module = {};
    let kv = line split = ":";;
    module.id
    module.deps
    if ((kv[1] === "")) {
    module.deps
  }
    modules id = None;
  }
let build_order = [];
let dep_loops = [];
function visit(module, chain) {
    if (module.visited) {
    return;
  }
    module.visited
    let next_chain = chain.slice;
    next_chain.push(module.id)
    for (const dep_id of module.deps) {
    if ((dep_id in next_chain)) {
    let dep_loop = [];
    dep_loop.push(dep_id)
    for (const chain_dep_id of next_chain.slice) {
    dep_loop.push(chain_dep_id)
    if ((chain_dep_id === dep_id)) {
    break;
  }
  }
    dep_loop.reverse
    dep_loops.push(dep_loop.join(" → "))
  } else {
    visit(modules.id, next_chain);
  }
  }
    build_order.push(module.id)
  }
for (const module of Object.values(modules)) {
    visit(module, []);
  }
if ((1 <= dep_loops.length)) {
    console.log(("ERROR: there are dependency loops.\n" + dep_loops.join("\n")));
  } else {
    console.log(build_order.join("\n"));
  }