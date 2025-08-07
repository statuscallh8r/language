# Import all macro modules to ensure they register with the unified registry
from . import access_macros
# TODO: Migrated to DI - from . import builtin_macros 
# TODO: Migrated to DI - from . import collection_macros
from . import comment_macros
# TODO: Migrated to DI - from . import error_macros
# TODO: Migrated to DI - from . import exists_macro  # TODO: Added separated exists macro
from . import fn_macro  # TODO: Added separated fn macro
# TODO: Migrated to DI - from . import for_macro
from . import if_macro
from . import lang_call_macro  # TODO: Added separated 67lang:call macro
from . import literal_value_macros
from . import local_macro  # TODO: Added separated local macro
from . import noscope_macro
from . import scope_macro
# TODO: Migrated to DI - from . import solution_macro
# TODO: Migrated to DI - from . import utility_macros
# TODO: Migrated to DI - from . import while_macro