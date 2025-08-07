console.log("All true?", [true, false, true].every(x => x));
console.log("Any true?", [true, false, true].some(x => x));
console.log("None true?", ![true, false, true].some(x => x));
console.log("All in empty list?", true);