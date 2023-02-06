# 'text' is the input string to wrap
# 'line_length' is the max # characters per line
def wrap_text(text, line_length):
  # split input text into individual lines
  lines = text.split('\n')
  wrapped_text = ''

  for line in lines:
    # split line into a list of words
    words = line.split()
    current_line = ''

    for word in words:

      # if length of current_line + length of next word is within max line length
      if len(current_line) + len(word) <= line_length:

        # then keep adding current_line to this line
        current_line += word + ' '

      else:

        # finish current_line, add it to our output wrapped_text
        # also adds extra spaces for next line's indent
        wrapped_text += current_line.strip() + '\n   '

        # start new current_line
        current_line = word + ' '

    # add last line to our output
    wrapped_text += current_line.strip() + '\n'

  return wrapped_text
