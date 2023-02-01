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
        wrapped_text += current_line.strip() + '\n    '

        # start new current_line
        current_line = word + ' '

    # add last line to our output
    wrapped_text += current_line.strip() + '\n'

  return wrapped_text

response_poem = 'Glasses perched atop my face\nForehead framed between two lenses\nCheek bones rising for the lens’ embrace\nLips curving under the gaze of vision care\nA picture frame for the depth of my stare\nEyebrows aiding in the smile of my face\nMouth curved and alive under every lash\nEyelashes extending with an arch of grace\nA portrait of perfection and warm embrace'

print(response_poem)

wrapped_string = wrap_text(response_poem, 32)
print(wrapped_string)
