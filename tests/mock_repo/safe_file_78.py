```ruby
def safe_method(user_input)
  begin
    puts eval(user_input)
  rescue SecurityError => e
    puts "SecurityError: #{e}"
  rescue SyntaxError => e
    puts "SyntaxError: #{e}"
  end
end

puts "Enter some Ruby code:"
user_input = gets.chomp

safe_method(user_input)
```