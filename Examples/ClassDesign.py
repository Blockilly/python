'''
# Example 1 — Simple Caesar Cipher Script
A minimal script showing the basic algorithm. To reuse this script, one has to copy/paste this code into another script
and then make necessary changes to customize the updated script.
'''

def caesar_encrypt(text, shift):
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            offset = (ord(ch) - base + shift) % 26
            result.append(chr(base + offset))
        else:
            result.append(ch)
    return ''.join(result)

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

message = "Attack at dawn"
encrypted = caesar_encrypt(message, 3)
decrypted = caesar_decrypt(encrypted, 3)


'''
# Example 2 — Class Version (No Encapsulation)
Shows how functions move into classes. Moving the functions into classes is a way to "group" common functionality.  
But it doesn't qualify as a "Complete" class. The data in the class is visible to anyone who wants to access it, 
meaning it isn't encapsulated.
'''

class Rotor:
    def __init__(self):
        self.characters = [chr(ord('A') + i) for i in range(26)]

    def rotate(self, shift):
        shift = shift % 26
        self.characters = self.characters[shift:] + self.characters[:shift]

    def index_of(self, ch):
        return self.characters.index(ch.upper())

class CaesarCipher:
    def __init__(self, shift):
        self.shift = shift
        self.rotor = Rotor()

    def encrypt(self, text):
        result = []
        for ch in text:
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                offset = (ord(ch) - base + self.shift) % 26
                result.append(chr(base + offset))
            else:
                result.append(ch)
        return ''.join(result)

    def decrypt(self, text):
        return self.encrypt(text, -self.shift)

cipher = CaesarCipher(3)
cipher.encrypt("HELLO")

'''
# Example 3 — Encapsulated Version
Internal data is private and accessed through properties.
A design is *encapsulated* when:
- internal data is private
- access happens through public methods or properties
- the class protects its internal state
- the interface is clean and controlled
'''

class Rotor:
    def __init__(self):
        self.__characters = [chr(ord('A') + i) for i in range(26)]

    @property
    def characters(self):
        return list(self.__characters)

    def rotate(self, shift):
        shift = shift % 26
        self.__characters = self.__characters[shift:] + self.__characters[:shift]

    def index_of(self, ch):
        return self.__characters.index(ch.upper())

class CaesarCipher:
    def __init__(self, shift):
        self.__shift = shift
        self.__rotor = Rotor()

    @property
    def shift(self):
        return self.__shift

    @property
    def rotor(self):
        return self.__rotor

    def encrypt(self, text):
        result = []
        for ch in text:
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                offset = (ord(ch) - base + self.__shift) % 26
                result.append(chr(base + offset))
            else:
                result.append(ch)
        return ''.join(result)

cipher = CaesarCipher(3)
cipher.encrypt("WORLD")


'''
# Example 4 — Modular Version
Internal helpers break down responsibilities. A design is *modular* when:
- each method has a single responsibility
- internal helpers break down complex tasks
- responsibilities are separated cleanly
- no method does more than one conceptual thing
'''

class Rotor:
    def __init__(self):
        self.__characters = [chr(ord('A') + i) for i in range(26)]

    @property
    def characters(self):
        return list(self.__characters)

    def rotate(self, shift):
        shift = shift % 26
        self.__characters = self.__characters[shift:] + self.__characters[:shift]

    def index_of(self, ch):
        return self.__characters.index(ch.upper())

class CaesarCipher:
    def __init__(self, shift):
        self.__shift = shift
        self.__rotor = Rotor()

    def __shift_char(self, ch, amount):
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            offset = (ord(ch) - base + amount) % 26
            return chr(base + offset)
        return ch

    def __process_text(self, text, amount):
        return ''.join(self.__shift_char(ch, amount) for ch in text)

    def encrypt(self, text):
        return self.__process_text(text, self.__shift)

cipher = CaesarCipher(3)
cipher.encrypt("MODULAR")


'''
# Example 5 — Robust Version
Input validation and defensive programming. A design is *robust* when:
- it validates inputs
- it rejects invalid states
- it raises clear errors when misused
- it handles edge cases predictably
'''

class Rotor:
    def __init__(self):
        self.__characters = [chr(ord('A') + i) for i in range(26)]

    @property
    def characters(self):
        return list(self.__characters)

    def rotate(self, shift):
        if not isinstance(shift, int):
            raise TypeError("Shift must be an integer")
        shift = shift % 26
        self.__characters = self.__characters[shift:] + self.__characters[:shift]

    def index_of(self, ch):
        if not isinstance(ch, str) or len(ch) != 1:
            raise ValueError("Character must be a single letter")
        return self.__characters.index(ch.upper())

class CaesarCipher:
    def __init__(self, shift):
        if not isinstance(shift, int):
            raise TypeError("Shift must be an integer")
        self.__shift = shift
        self.__rotor = Rotor()

    def __shift_char(self, ch, amount):
        if not isinstance(ch, str) or len(ch) != 1:
            raise ValueError("Character must be a single character")
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            offset = (ord(ch) - base + amount) % 26
            return chr(base + offset)
        return ch

    def __process_text(self, text, amount):
        if not isinstance(text, str):
            raise TypeError("Text must be a string")
        return ''.join(self.__shift_char(ch, amount) for ch in text)

    def encrypt(self, text):
        return self.__process_text(text, self.__shift)

cipher = CaesarCipher(3)
cipher.encrypt("ROBUST")


'''
Example 6 — Scalable Version
Supports any ordered character sequence, avoids magic numbers. A design is *scalable* when:
- it adapts to new requirements without rewriting core logic
- it avoids magic numbers
- it supports larger or different alphabets
- it grows without breaking existing behavior
'''

class Rotor:
    def __init__(self, sequence=None):
        if sequence is None:
            sequence = [chr(code) for code in range(ord('A'), ord('Z') + 1)]
        self.__characters = list(sequence)

    @property
    def characters(self):
        return list(self.__characters)

    @property
    def size(self):
        return len(self.__characters)

    def rotate(self, shift):
        shift = shift % self.size
        self.__characters = self.__characters[shift:] + self.__characters[:shift]

    def index_of(self, ch):
        return self.__characters.index(ch)

    def __getitem__(self, index):
        return self.__characters[index]


class CaesarCipher:
    def __init__(self, shift, sequence=None):
        self.__shift = shift
        self.__rotor = Rotor(sequence)

    def __shift_char(self, ch, amount):
        if ch in self.__rotor.characters:
            idx = self.__rotor.index_of(ch)
            new_index = (idx + amount) % self.__rotor.size
            return self.__rotor[new_index]
        return ch

    def __process_text(self, text, amount):
        return ''.join(self.__shift_char(ch, amount) for ch in text)

    def encrypt(self, text):
        return self.__process_text(text, self.__shift)


sequence = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
cipher = CaesarCipher(5, sequence)
print(cipher.encrypt("HELLO 2026"))


'''
**Complete**
A class is *complete* when it fully encapsulates the behavior and responsibilities of its domain, 
providing every operation the user needs without relying on external helper functions or unfinished logic. 
All required steps are implemented internally, with no gaps, missing features, or half‑formed methods that 
force the caller to patch functionality from the outside. A complete class stands on its own: users can 
perform all intended actions directly through its interface, confident that the module contains everything 
necessary to operate correctly, consistently, and without extension.
'''

class CaesarCipher:
    """
    A complete, modular, robust, scalable, and encapsulated Caesar cipher.

    - Complete: supports full encryption/decryption with no missing behavior
    - Modular: each method has a single responsibility
    - Robust: validates inputs and rejects invalid states
    - Scalable: supports any ordered character sequence, no magic numbers
    - Encapsulated: internal data is private and accessed through properties
    """

    def __init__(self, shift, sequence=None):
        # --- Robustness: validate shift ---
        if not isinstance(shift, int):
            raise TypeError("Shift must be an integer")

        # --- Scalability: allow any ordered sequence ---
        if sequence is None:
            sequence = [chr(code) for code in range(ord('A'), ord('Z') + 1)]

        if not isinstance(sequence, (list, tuple)):
            raise TypeError("Sequence must be a list or tuple")

        if not all(isinstance(ch, str) and len(ch) == 1 for ch in sequence):
            raise ValueError("Sequence must contain single-character strings")

        # --- Encapsulation: private internal state ---
        self.__shift = shift
        self.__sequence = list(sequence)

    # ============================================================
    # Accessors (Encapsulation)
    # ============================================================

    @property
    def shift(self):
        return self.__shift

    @property
    def sequence(self):
        return list(self.__sequence)

    @property
    def size(self):
        return len(self.__sequence)

    # ============================================================
    # Internal Helpers (Modularity)
    # ============================================================

    def __index_of(self, ch):
        """Return index of character in the sequence."""
        if ch not in self.__sequence:
            raise ValueError(f"Character '{ch}' not found in sequence")
        return self.__sequence.index(ch)

    def __shift_char(self, ch, amount):
        """Shift a single character using the sequence."""
        if not isinstance(ch, str) or len(ch) != 1:
            raise ValueError("Character must be a single character")

        if ch in self.__sequence:
            idx = self.__index_of(ch)
            new_index = (idx + amount) % self.size
            return self.__sequence[new_index]

        return ch  # Non-sequence characters pass through unchanged

    def __process_text(self, text, amount):
        """Apply a shift to an entire string."""
        if not isinstance(text, str):
            raise TypeError("Text must be a string")

        return ''.join(self.__shift_char(ch, amount) for ch in text)

    # ============================================================
    # Public Behavior (Completeness)
    # ============================================================

    def encrypt(self, text):
        return self.__process_text(text, self.__shift)

    def decrypt(self, text):
        return self.__process_text(text, -self.__shift)

    # ============================================================
    # Dunders (Completeness + Usability)
    # ============================================================

    def __repr__(self):
        return f"CaesarCipher(shift={self.__shift}, size={self.size})"

    def __call__(self, text):
        """Calling the object encrypts the text."""
        return self.encrypt(text)

    def __eq__(self, other):
        return (
            isinstance(other, CaesarCipher)
            and self.__shift == other.__shift
            and self.__sequence == other.__sequence
        )


# ============================================================
# Example Usage
# ============================================================

sequence = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
cipher = CaesarCipher(5, sequence)

message = "HELLO 2026"
encrypted = cipher.encrypt(message)
decrypted = cipher.decrypt(encrypted)

print("Sequence:", cipher.sequence)
print("Original:", message)
print("Encrypted:", encrypted)
print("Decrypted:", decrypted)
print("Cipher repr:", repr(cipher))
print("Cipher call:", cipher("TEST123"))