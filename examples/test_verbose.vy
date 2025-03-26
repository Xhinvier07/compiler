// A sample Vypr program to test enhanced verbose output

func calculate_sum(numbers):
    var sum = 0
    loop num in numbers:
        sum = sum + num
    return sum

func calculate_average(numbers, n):
    var sum = calculate_sum(numbers)
    return sum / n

// Main program
var data = [0.10, 0.20, 0.30, 0.40, 0.50]
var total = calculate_sum(data)
print "Sum of data is: " ^ total

var avg = calculate_average(data, 5)
print "Average of data is: " ^ avg

// This is a comment 