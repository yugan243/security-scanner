```ruby
class User
  attr_accessor :name

  def initialize(name)
    @name = name
  end
end

def greet_user(user)
  puts "Hello, #{user.name}!"
end

input = gets.chomp
user = User.new(input)
greet_user(user)
```