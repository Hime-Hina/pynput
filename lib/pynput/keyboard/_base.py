# coding=utf-8
# pynput
# Copyright (C) 2015 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import contextlib
import enum
import six
import threading
import unicodedata


class KeyCode(object):
    def __init__(self, vk=0, char=None, is_dead=False):
        self.vk = vk
        self.char = six.text_type(char) if char is not None else None
        self.is_dead = is_dead

        if self.is_dead:
            self.combining = unicodedata.lookup(
                'COMBINING ' + unicodedata.name(self.char))
            if not self.combining:
                raise KeyError(char)
        else:
            self.combining = None

    def __repr__(self):
        if self.is_dead:
            return '[%s]' % repr(self.char)
        if self.char is not None:
            return repr(self.char)
        else:
            return '<%d>' % self.vk

    def __str__(self):
        return repr(self)

    def join(self, key):
        """Applies this dead key to another key and returns the result.

        Joining a dead key with space (``' '``) or itself yields the non-dead
        version of this key, if one exists; for example,
        ``KeyCode.from_dead('~').join(KeyCode.from_char(' '))`` equals
        ``KeyCode.from_char('~')``.

        :param KeyCode dead: The dead key to join with another key.

        :param KeyCode key: The key to join with the dead key.

        :return: a key code

        :raises ValueError: if the keys cannot be joined
        """
        # Joining two of the same keycodes, or joining with space, yields the
        # non-dead version of the key
        if key.char == ' ' or (key.is_dead and key.char == self.char):
            return self.from_char(self.char)

        # Otherwise we combine the characters
        if key.char is not None:
            combined = unicodedata.normalize(
                'NFC',
                key.char + self.combining)
            if combined:
                return self.from_char(combined)

        raise ValueError(key)

    @classmethod
    def from_vk(self, vk):
        """Creates a key from a virtual key code.

        :param vk: The virtual key code.

        :return: a key code
        """
        return self(vk=vk)

    @classmethod
    def from_char(self, char):
        """Creates a key from a character.

        :param str char: The character.

        :return: a key code
        """
        return self(char=char)

    @classmethod
    def from_dead(self, char):
        """Creates a dead key.

        :param char: The dead key. This should be the unicode character
            representing the stand alone character, such as ``'~'`` for
            *COMBINING TILDE*.

        :return: a key code
        """
        return self(char=char, is_dead=True)


class Key(enum.Enum):
    """A class representing various buttons that may not correspond to
    letters. This includes modifier keys and function keys.

    The actual values for these items differ between platforms. Some platforms
    may have additional buttons, but these are guaranteed to be present
    everywhere.
    """
    #: A generic Alt key. This is a modifier.
    alt = 0

    #: The left Alt key. This is a modifier.
    alt_l = 0

    #: The right Alt key. This is a modifier.
    alt_r = 0

    #: The AltGr key. This is a modifier.
    alt_gr = 0

    #: The Backspace key.
    backspace = 0

    #: The CapsLock key.
    caps_lock = 0

    #: A generic command button. On *PC* platforms, this corresponds to the
    #: Super key or Windows key, and on *Mac* it corresponds to the Command
    #: key. This may be a modifier.
    cmd = 0

    #: The left command button. On *PC* platforms, this corresponds to the
    #: Super key or Windows key, and on *Mac* it corresponds to the Command
    #: key. This may be a modifier.
    cmd_l = 0

    #: The right command button. On *PC* platforms, this corresponds to the
    #: Super key or Windows key, and on *Mac* it corresponds to the Command
    #: key. This may be a modifier.
    cmd_r = 0

    #: A generic Ctrl key. This is a modifier.
    ctrl = 0

    #: The left Ctrl key. This is a modifier.
    ctrl_l = 0

    #: The right Ctrl key. This is a modifier.
    ctrl_r = 0

    #: The Delete key.
    delete = 0

    #: A down array key.
    down = 0

    #: The End key.
    end = 0

    #: The Enter or Return key.
    enter = 0

    #: The Esc key.
    esc = 0

    #: The function keys. F1 to F20 are defined.
    f1 = 0
    f2 = 0
    f3 = 0
    f4 = 0
    f5 = 0
    f6 = 0
    f7 = 0
    f8 = 0
    f9 = 0
    f10 = 0
    f11 = 0
    f12 = 0
    f13 = 0
    f14 = 0
    f15 = 0
    f16 = 0
    f17 = 0
    f18 = 0
    f19 = 0
    f20 = 0

    #: The Home key.
    home = 0

    #: A left arrow key.
    left = 0

    #: Trhe PageDown key.
    page_down = 0

    #: The Pageup key.
    page_up = 0

    #: A right arrow key.
    right = 0

    #: A generic Shift key. This is a modifier.
    shift = 0

    #: The left Shift key. This is a modifier.
    shift_l = 0

    #: The right Shift key. This is a modifier.
    shift_r = 0

    #: The Space key.
    space = 0

    #: The Tab key.
    tab = 0

    #: An up arrow key.
    up = 0

    #: The Insert key. This may be undefined for some platforms.
    insert = 0

    #: The Menu key. This may be udefined for some platforms.
    menu = 0

    #: The NumLock key. This may be undefined for some platforms.
    num_lock = 0

    #: The Pause/Break key. This may be undefined for some platforms.
    pause = 0

    #: The PrintScreen key. This may be undefined for some platforms.
    print_screen = 0

    #: The ScrollLock key. This may be undefined for some platforms.
    scroll_lock = 0


class Controller(object):
    """A controller for sending virtual keyboard events to the system.
    """
    #: The virtual key codes
    _KeyCode = KeyCode

    #: The various keys.
    _Key = Key

    class InvalidKeyException(Exception):
        """The exception raised when and invalid ``key`` parameter is passed to
        either :meth:`Controller.press` or :meth:`Controller.release`.

        Its first argument is the ``key`` parameter.
        """
        pass

    class InvalidCharacterException(Exception):
        """The exception raised when and invalid character is encountered in
        the string passed to :meth:`Controller.type`.

        Its first argument is the index of the character in the string, and the
        second the character.
        """
        pass

    def __init__(self):
        self._modifiers_lock = threading.RLock()
        self._modifiers = set()
        self._caps_lock = False
        self._dead_key = None

        K = self._Key

        #: The keys used as modifiers; the first value in each tuple is the
        #: base modifier to use for subsequent modifiers.
        self._MODIFIER_KEYS = (
            (K.alt_gr, (K.alt_gr.value,)),
            (K.alt,    (K.alt.value,   K.alt_l.value,   K.alt_r.value)),
            (K.cmd,    (K.cmd.value,   K.cmd_l.value,   K.cmd_r.value)),
            (K.ctrl,   (K.ctrl.value,  K.ctrl_l.value,  K.ctrl_r.value)),
            (K.shift,  (K.shift.value, K.shift_l.value, K.shift_r.value)))

    def press(self, key):
        """Presses a key.

        A key may be either a string of length 1, one of the :class:`Key`
        members or a :class:`KeyCode`.

        Strings will be transformed to :class:`KeyCode` using
        :meth:`KeyCode.char`. Members of :class:`Key` will be translated to
        their :meth:`~Key.value`.

        :param key: The key to press.

        :raises InvalidKeyException: if the key is invalid

        :raises ValueError: if ``key`` is a string, but its length is not ``1``
        """
        self._dispatch(self._resolve(key), True)

    def release(self, key):
        """Releases a key.

        A key may be either a string of length 1, one of the :class:`Key`
        members or a :class:`KeyCode`.

        Strings will be transformed to :class:`KeyCode` using
        :meth:`KeyCode.char`. Members of :class:`Key` will be translated to
        their :meth:`~Key.value`.

        :param key: The key to release. If this is a string, it is passed to
            :meth:`touches` and the returned releases are used.

        :raises InvalidKeyException: if the key is invalid

        :raises ValueError: if ``key`` is a string, but its length is not ``1``
        """
        self._dispatch(self._resolve(key), False)

    def touch(self, key, is_press):
        """Calls either :meth:`press` or :meth:`release` depending on the value
        of ``is_press``.

        :param key: The key to press or release.

        :param bool is_press: Whether to press the key.
        """
        if is_press:
            self.press(key)
        else:
            self.release(key)

    @contextlib.contextmanager
    def pressed(self, *args):
        """Executes a block with some keys pressed.

        :param keys: The keys to keep pressed.
        """
        for key in args:
            self.press(key)

        try:
            yield
        finally:
            for key in reversed(args):
                self.press(key)

    def type(self, string):
        """Types a string.

        This method will send all key presses and releases necessary to type
        all characters in the string.

        :param str string: The string to type.

        :raises InvalidCharacterException: if an untypable character is
            encountered
        """
        for i, character in enumerate(string):
            try:
                self.press(character)
                self.release(character)

            except ValueError:
                raise self.InvalidCharacterException(i, character)

    @property
    @contextlib.contextmanager
    def modifiers(self):
        """The currently pressed modifier keys.
        """
        with self._modifiers_lock:
            yield self._modifiers

    @property
    def alt_pressed(self):
        """Whether any *alt* key is pressed.
        """
        with self.modifiers as modifiers:
            return self._Key.alt in modifiers

    @property
    def alt_gr_pressed(self):
        """Whether *altgr* is pressed.
        """
        with self.modifiers as modifiers:
            return self._Key.alt_gr in modifiers

    @property
    def ctrl_pressed(self):
        """Whether any *ctrl* key is pressed.
        """
        with self.modifiers as modifiers:
            return self._Key.ctrl in modifiers

    @property
    def shift_pressed(self):
        """Whether any *shift* key is pressed, or *caps lock* is toggled.
        """
        if self._caps_lock:
            return True

        with self.modifiers as modifiers:
            return self._Key.shift in modifiers

    def _dispatch(self, key, is_press):
        """Dispatches a press or release.

        This method selects the correct platform implementation. It also
        handles any platform indepentent key actions.

        :param key: The key.

        :param bool is_press: Whether this is a press event.

        :raises ValueError: if ``key`` is a string, but its length is not ``1``
        """

        # Check whether the key is a modifier
        modifier = self._as_modifier(key)
        if modifier:
            with self.modifiers as modifiers:
                if is_press:
                    modifiers.add(modifier)
                else:
                    try:
                        modifiers.remove(modifier)
                    except KeyError:
                        pass

        # Otherwise, let the platform implementation handle it
        if is_press:
            # Update caps lock state
            if is_press and key == self._Key.caps_lock.value:
                self._caps_lock = not self._caps_lock

            # If we currently have a dead key pressed, join it with this key
            if self._dead_key:
                try:
                    key = self._dead_key.join(key)
                except ValueError:
                    self._handle(self._dead_key, True)
                    self._handle(self._dead_key, False)
                self._dead_key = None

            # If the key is a dead key, keep it for later
            if key.is_dead:
                self._dead_key = key
                return

        else:
            # Ignore released dead keys
            if key.is_dead:
                return

        self._handle(key, is_press)

    def _resolve(self, key):
        """Resolves a key to a :class:`KeyCode` instance.

        :param key: The key to resolve.

        :return: a key code, or ``None`` if it cannot be resolved
        """
        # Use the value for the key constants
        if key in self._Key:
            return key.value

        # Convert strings to key codes
        if isinstance(key, six.string_types):
            if len(key) != 1:
                raise ValueError(key)
            return self._KeyCode.from_char(key)

        # Assume this is a proper key
        if isinstance(key, self._KeyCode):
            if key.char is not None and self.shift_pressed:
                return self._KeyCode.from_char(key.char.upper())
            else:
                return key

    def _as_modifier(self, key):
        """Returns a key as the modifier used internally is defined.

        This method will convert values like :attr:`Key.alt_r.value` and
        :attr:`Key.shift_l.value` to :attr:`Key.alt` and :attr:`Key.shift`.

        :param key: The possible modifier key.

        :return: the base modifier key, or ``None`` if ``key`` is not a
            modifier
        """
        for base, modifiers in self._MODIFIER_KEYS:
            if key in modifiers:
                return base

    def _handle(self, key, is_press):
        """The platform implementation of the actual emitting of keyboard
        events.

        This is a platform dependent implementation.

        :param Key key: The key to handle.

        :param bool is_press: Whether this is a key press event.
        """
        raise NotImplementedError()
