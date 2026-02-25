```ruby
class User
  def initialize(name)
    @name = name
  end

  def method_missing(method_name, *args, &block)
    return super unless method_name.to_s.start_with?('get_')
    instance_variable_get("@#{method_name[4..-1]}")
  end
end

user = User.new('Alice')
puts user.send('get_name') # Alice
```