let global_var = "global";
let shadow_var = "outer";
console.log("Before do block:", global_var, shadow_var);
{
    let scoped_var = "scoped";
    let shadow_var = "inner";
    console.log("Inside do block:", global_var, scoped_var, shadow_var);
    shadow_var = "modified_inner";
    console.log("After modification in do block:", shadow_var);
  }
console.log("After do block:", global_var, shadow_var);