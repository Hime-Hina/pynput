# coding=utf-8
# pynput
# Copyright (C) 2015-2024 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
The module containing mouse classes.

See the documentation for more information.
"""

# Button, Controller and Listener are not constants

import platform
from typing import Type

from .._util import Events as _Events

system = platform.system()
if system == "Windows":
    from ._win32 import Button, Controller, Listener
elif system == "Darwin":
    from ._darwin import Button, Controller, Listener
elif system == "Linux":
    from ._xorg import Button, Controller, Listener
else:
    from ._dummy import Button, Controller, Listener


class Events(_Events):
    """A mouse event listener supporting synchronous iteration over the events.

    Possible events are:

    :class:`Events.Move`
        The mouse was moved.

    :class:`Events.Click`
        A mouse button was pressed or released.

    :class:`Events.Scroll`
        The device was scrolled.
    """

    _ListenerClass = Listener

    class Move(_Events.Event):
        """A move event."""

        def __init__(
            self,
            x: int,
            y: int,
            timestamp: int,
            is_injected: bool,
        ):
            #: The X screen coordinate.
            self.x = x

            #: The Y screen coordinate.
            self.y = y

            self.timestamp = timestamp
            self.is_injected = is_injected

    class Click(_Events.Event):
        """A click event."""

        def __init__(
            self,
            x: int,
            y: int,
            button: Type[Button],
            pressed: bool,
            timestamp: int,
            is_injected: bool,
        ):
            #: The X screen coordinate.
            self.x = x

            #: The Y screen coordinate.
            self.y = y

            #: The button.
            self.button = button

            #: Whether the button was pressed.
            self.pressed = pressed

            self.timestamp = timestamp
            self.is_injected = is_injected

    class Scroll(_Events.Event):
        """A scroll event."""

        def __init__(
            self,
            x: int,
            y: int,
            dx: int,
            dy: int,
            timestamp: int,
            is_injected: bool,
        ):
            #: The X screen coordinate.
            self.x = x

            #: The Y screen coordinate.
            self.y = y

            #: The number of horisontal steps.
            self.dx = dx

            #: The number of vertical steps.
            self.dy = dy

            self.timestamp = timestamp
            self.is_injected = is_injected

    def __init__(self):
        super(Events, self).__init__(
            on_move=self.Move,
            on_click=self.Click,
            on_scroll=self.Scroll,
        )
