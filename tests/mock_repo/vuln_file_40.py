```ruby
require 'net/http'
require 'uri'

def fetch_remote_content(url)
  uri = URI.parse(url)
  response = Net::HTTP.get_response(uri)
  response.body if response.is_a?(Net::HTTPSuccess)
end

puts "Enter URL:"
user_input = gets.chomp

content = fetch_remote_content(user_input)
puts content
```