# Command Factory Elevator Implementation

This sub-project is an example of a robot program using the command-based
framework.  In contrast to the `command_based` project, this one uses
"factory" methods in the subsystems to create commands and triggers.

These commands and triggers are the complete application programming
Interface (API) that a subsystem exposes to the rest of the program.
This approach keeps the implementation details even more contained
to the subsystem than in the `command_based` project.  

Note the main difference: `robot_container.py` and `autos.py` do not need 
to import ElevatorCommands nor ElevatorConstants as they do in `command_based`.
Knowledge of the heights is transmitted in the commands `set_home()`, `set_mid()`,
and the trigger object `is_at_height`.

Python takes a very relaxed approach to many things, like the visibility
of internals of a class.  There is a convention to start method names
with an underscore if they are intended to only be internal. Example:
`_move_to_position()`.  But this is a convention, not a strict rule.
If we were programming in Java or another language with stricter 
boundaries, we would declare the method `private` and the compiler
would prevent us from calling it from outside the class.

This sub-project is based on best practices guidance from ["BoVLB's FRC Tips"](
https://bovlb.github.io/frc-tips/commands/best-practices.html), which is in
turn based on another mentor's post on Chief Delphi.
