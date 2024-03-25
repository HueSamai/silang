# silang

silang (slow interpreted language) is an interpreted, proecural-orientated language, similar to javascript. The interpreter is hand-written in python. I made this while reading the Crafting Intrpreters book.

# Run silang code
The file extension for silang is '.sil', and you can run silang code by cloning this repo, and using: 
```
> python main.py <file.sil>
```

# Syntax highlighting
I made a syntax highlighter using tree-sitter which you can find [here](https://github.com/HueSamai/tree-sitter-sil).

# Syntax
If you want to understand the syntax completely, check the "grammar.txt" file and the source code. The examples will also be helpful. 

A quick rundown: silang is very similar to javascript, but has some differences here and there. It also ignores whitespace, so all indenting is purely for visual aid.

Okay let's do the basics.

```javascript
// this is a comment in silang
```

We can use the print statement to print something to the standard output. Semi-colons come at the end of a statement, except for if it is a block statement. 
```javascript
print "Hello, World!\n"; // note: as you can see, the print statement doesn't print a newline automatically at the end for us.
print 2 + 8 * 7 / (9 - 2); // follows bidmas
```

Similarly we can also use an input expression to get input.
```py
input "Enter something: ";
```

silang supports expression statements.
```javascript
"this is just an expression";
```

Let's store the result in a variable. To declare a variable we can use the 'var' keyword.
```javascript
var something = input "Enter something: ";
print something;

something = "Reassigned value"; // we don't need to use 'var' because we aren't declaring it

var something = "Another value"; // will throw an error, because we have declared something already
```

We can also declare a variable without initiliasing it.
```javascript
var iWillUseThisLater;
```

Here are the different types in silang.
```javascript
var number = 0.1; // we have a number type, which is just a floating number. silang does not have integers. just floats.
var string = "this is a string!"; // silang declares strings with double quotes (no singles allowed), which internally are lists. 
var thisHasNoValue = novalue; // novalue is silang's null, because it's not like the other girls.
// note: the above line is the same as just declaring a variable without initiliasing it.
var boolean = true; // can also be false

var list = [1, 2, 3 [4, 5, 6], "lists can contain any type!", novalue];
```

Let's talk scopes.
```js
var number = 10;
// we can open a new block with {
// we can close it with }
// creating a block, creates a new scope
{
  // this scope can access variables declared in outer scopes
  print number; // prints 10
}

{
  print number; // prints 10
  var number = 2; // we can declare a new variable in this scope which shadows the outer 'number'
  print number; // prints 2

  var string = "value";
}

print number; // prints 10
print string; // throws an error, because string isn't declared in this scope.
```

We just have basic if statments for control flow in silang.
```javascript
// we don't need paranthesis
if true
  print 10;
else
  print 11; // this code won't be reached

// if's will execute the following statement, if their expression is true, and if it's false, the statement following the else will be executed
if false
  print "We don't need to have an else statement though";

// we can execute multiple statements by wrapping them in blocks (a block is seen as one statement)
if true
{
  print "yo\n";
  // AND
  print "yo again\n";
}
else
{
  print "Even though we have multiple statements in here, ";
  print "none of them will be run...";
}
```

silang has the usual boolean expressions.
```js

// this is confusing lol
print 8 == 10 or 7 > 3 and 5 <= 9 or 6 != -2 and !false or !true;

// we can also use variables as boolean expressions to check if they have a value or not
var a;
if a
  print "This will not print, because a is set to 'novalue'";

if !a
  print "This WILL print";

a = 10;

if a
  print "This will also print";

if b             // this will throw an error, because b is not defined
  print "Oh no!";

```

Since if statements are statements, we can also have if else statements.
```javascript
var a = 10;
if a == 9
  print "a is 9";
else if a == 10
  print "a is 10";
```

Loops! In silang we have your basic C while and for loops.
```javascript
// the while loop will execute the following statement while the condition is true.
while true
  print a;

// note: we can use a block statement again like we did for the if statements to make the while statement execute multiple statements
// for loops look a bit different too

for var i = 0; i < 10; i += 1; print i; // will print 0123456789

// the first statement, boolean expression, and final statement of the for loop are all optional
for ;;;; // this is valid code. this will enter an infinite loop, that does nothing. the final ';' is for the body of the for loop.

```

Instead of break and continue, silang has stop and skip statements. They can also take an optional boolean expression afterwards to determine whether or not they should skip or stop.
```javascript
while true
  stop; // stops the loop

while true
  stop (input "Enter something: ") == ""; // this will stop the loop if we entered nothing.

var a = 0;
while a < 10
{
  skip a == 2; // will skip to next iteration if condition is met.
  print a; // will print 013456789
}

// the above loop is the same as
a = 0;
while a < 10
{
  if a == 2 skip;
  print a;
}

// stop and skip can also be used in for loops
```

Let's talk LISTS
```javascript
// declare a list
var myList = [1, 2, 3, 4];
print myList; // [1, 2, 3, 4]

// we can change an element in a list like so
myList[1] = 5;
print myList; // [1, 5, 3, 4] (because list indices start at 0)

print myList[2]; // we can also index a list in the same way
// above code prints 3

myList[0] = "lists can store multiple different types!";
myList[3] = ["even lists", "themselves!"];

print myList[10]; // error: index outside the bounds of list
```

> Note: Since there are no integers in silang, we can index lists using floating values without any errors. silang will just round the floating point value down to the nearest whole number.

```javascript
var list = [10, 9, 8];
print list[0.5]; // 10
```

Strings are also internally lists. So we can do most of the same stuff.
```javascript
var myString = "Hello, World!";
myString[0] = "J";
print myString; // Jello, World!

if myString[1] == "e"
  print "This is true!"

// strings do differ slightly to lists
// they can't hold any type as element
// you can only assign characters to string elements
myString[4] = "yo"; // will throw an error
```

There are also some escape codes for strings.
```javascript

var string = "Newline: \n, Tab: \t, Carriage return: \r"; // the regular escape codes

// we can also write a 2-digit hex number as an ascii character to the string by using '\'
var newString = "\00\10\ff\8f";

// this feature can be used to write any binary data to a file
"\00\01\02".write("output.bin");
```

Okay now FUNCTIONS!
```javascript
// you call functions like in everything C-like language. with paranthesis
// i'm going to call the built-in function 'num'. i'll talk about all the built-in functions later
print num("100") + 1;

// arguments are separated with commas
// we can see this by calling 'push', another built-in function to add a value to a list
var list = [1, 2];
push(list, 3); // list = [1, 2, 3];

// silang can give you an object orientated feel by calling functions with dot notation
// the above function call, can be also written in silang's dot notation like so
list.push(3);

// silang takes 'list' and just internally uses it as the first argument in the function, and then pushes the rest of the arguments one up, so 3 becomes the second argument.
// this works for all functions. so we can do it for the previous call of 'num'

print "100".num() + 1; // this is internally the exact same as the previous print statement
```

> Note: strings and lists are passed as references to functions, whereas clones are passed for all other values

```javascript
fun modifyString(string) string[0] = "H";

var myString = "Yello, World!";
myString.modifyString(); // using dot notation
print myString; // Hello, World!

// to get around this we can do something like this
myString = "Yello, World!";
modifyString(myString + ""); // adding an empty string means a separate string is created, so a copy of the string is passed to modifyString
print myString; // Yello, World!

// to do the same thing for a list, you can check the 'listops.sil' file under base. there is a 'copy' function
var myList = [1, 2, 3];
modifyString(myList); // we can pass a list to this function and the function will still work
print myList; // [H, 2, 3]

// using the copy function
myList = [1, 2, 3];
modifyString(myList.copy());
print myList; // [1, 2, 3]

// we can also code our own copy function
fun copy(list)
{
  var clone = [];
  for var i = 0; i < list.length(); i += 1; clone.push(list[i]);
  return clone;
}
```

Functions are first class objects, so we can do stuff like this.
```javascript
var myNum = num;

// myNum is the same as just calling num
print myNum("12") * 2; // prints 24
```

Okay let's declare our own functions now.
```javascript
// we use the 'fun' keyword to define a function, followed by parameters, separated by commas, enclosed in paranthesis, and then a statement, which is the body of our function
fun myFunction(a, b) print a + b;

// we can use the return statement to return a value
fun myOtherFunction(a, b)
{
  print a + b;
  return a + b;
}

// we can also have implicit returns, if our function body is just an expression statement
fun mult(a, b) a * b; // this will return a * b

fun div(a, b) {
  a / b; // this will NOT return a / b, because the function body is a block statement, NOT an expression statement
}

// we can ofcourse call our functions like before
myFunction(1, 2); // we can call our functions the same as before
print myOtherFunction(7, 80); 
print mult(9.6, -3);
print div(10, 2); // will print 'novalue'
```

Let's go over all the built-in functions now. (there aren't very many)
```javascript
var list = [1, 2, 3];

 // push: push an element to the end of the list
push(list, 4);
// OR using dot notation
list.push(4);

// pop: remove an element at the given index from the list and return it
var element = pop(list, 0);
// OR using dot notation
var element = list.pop(0);

// note: push and pop also work for strings, because they are lists internally

// length: get the length of a list (also a string)
print length("Goodbye, World!");
// OR using dot notation
print "Goodbye, World!".length();

// read: read the contents of a file at the given path and return it as a string
print read("example.txt");
// OR using dot notation
print "example.txt".read();

// write: write the given string to the given path
write("example.txt", "new file contents");
// you should be used to the dot notation by now...

// rng: get a random number from 0 to 1
print rng();

// seed: seed the random number generator
seed("this is a seed!");

// exists: check if a file exists
if exists("folder/file.txt") print "folder/file.txt".read();

// num: convert a string to a number
print num("100.01") + 10;

// round: round a number to the nearest whole number
print round(10.5); // will print 11
```

LASTLY, includes!

We can include another silang file using `#` at the start of a line, followed by the path to the file
```javascript
// relative paths work
#file.sil

// absolute paths should also work
#C:\base.sil

functionDefinedInBaseSil() // we can now call functions from a separate file!
```

Now you are an expert in silang! There is still some quirky behaviour in silang, but you will figure those things out while programming. If you are wondering about something, just check the source code.
