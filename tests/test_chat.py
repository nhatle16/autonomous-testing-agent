# Simulate keyboard input
def _inputs(*lines):
    # Create an iterator over the provided lines
    it = iter(lines)
    
    # Fake input() to read from the iterator
    def input_fn():
        try:
            return next(it)
        except StopIteration:
            raise EOFError from None
        
    return input_fn
