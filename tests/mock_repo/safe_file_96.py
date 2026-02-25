```ruby
class UserInput
  def initialize(input)
    @input = input
  end

  def process_input
    # Use 'send' instead of 'eval' to avoid the buffer overflow vulnerability
    send(@input)
  end
end

# Create an object of the 'UserInput' class with the argument being a symbol that represents a method to delete all files in the current directory
user_input = UserInput.new(:delete_all_files)

# Define the 'delete_all_files' method
def delete_all_files
  FileUtils.rm_r Dir.glob('*')
end

# Call the 'process_input' method on the created object
user_input.process_input
```