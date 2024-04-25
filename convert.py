
import vpype
import vpype_cli


# vpype read /Users/mik/Downloads/Drawing\ 1-4.svg trim 1 1 linemerge --tolerance 0.1mm linesort scaleto 16cm 7cm layout  tight gwrite --profile my_own_plotter ~/test/test.gcode


"vpype -c vpype.toml read /Users/mik/Downloads/Drawing\ 1-4.svg trim 1 1 linemerge --tolerance 0.1mm linesort scaleto 16cm 7cm layout  tight gwrite --profile my_own_plotter ~/test/test.gcode"

import vpype_cli
vpype_cli.execute("read input.svg trim 1 1 linemerge --tolerance 0.1mm linesort scaleto 16cm 7cm layout  tight gwrite --profile my_own_plotter output.gcode", global_opt="-c config.toml")


