```ruby
def calculate(input)
  eval(input)
end

puts "Enter calculation:"
user_input = gets.chomp

begin
  result = calculate(user_input)
  puts "Result: #{result}"
rescue Exception => e
  puts "Invalid input"
end
```