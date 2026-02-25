```ruby
def vulnerable_method(user_input)
  eval(user_input)
end

vulnerable_method("system('rm -rf /')")
```