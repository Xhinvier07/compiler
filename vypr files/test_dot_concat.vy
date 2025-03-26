// Test caret string concatenation

func greet(name):
    return "Hello, " ^ name ^ "!"

var name = "World"
var greeting = greet(name)
print greeting

// Test numeric concatenation
var num = 42
print "The answer is: " ^ num

// Test array concatenation without indexing
var items = [1, 2, 3]
print "Items: " ^ items 