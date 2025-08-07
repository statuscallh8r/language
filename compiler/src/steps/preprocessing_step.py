from dataclasses import replace
from processor_base import MacroProcessingStep
from macro_registry import MacroContext, MacroRegistry
from node import Macro
from logger import default_logger
from error_types import ErrorType

class PreprocessingStep(MacroProcessingStep):
    """Handles preprocessing like access macro unrolling"""
    
    def __init__(self):
        super().__init__()
        # Create local registry for this step
        self.macros = MacroRegistry()
        
        # Initialize macros for this step
        self._register_macros()
        
    def _register_macros(self):
        """Register all preprocessing macros"""
        # Import and register comment macros
        from macros.comment_macros import COMMENT_MACROS, comments
        self.macros.add(*COMMENT_MACROS)(comments)
        
        # Register preprocessing macros
        @self.macros.add("local")
        def local(ctx: MacroContext):
            # TODO: Use dependency injection version if available
            from macro_base import di_registry
            if di_registry.has_macro("local"):
                instance = di_registry.get_instance("local")
                instance.preprocess(ctx)
            else:
                # Fallback to old implementation
                from macros.local_macro import local_preprocessing
                local_preprocessing(ctx)

        @self.macros.add("for")
        def preprocess_for(ctx: MacroContext):
            # TODO: Use dependency injection version if available
            from macro_base import di_registry
            if di_registry.has_macro("for"):
                instance = di_registry.get_instance("for")
                instance.preprocess(ctx)
            else:
                # Fallback to old implementation
                from macros.for_macro import for_preprocessing
                for_preprocessing(ctx)

        @self.macros.add("fn")
        def preprocess_fn(ctx: MacroContext):
            # TODO: Use dependency injection version if available
            from macro_base import di_registry
            if di_registry.has_macro("fn"):
                instance = di_registry.get_instance("fn")
                instance.preprocess(ctx)
            else:
                # Fallback to old implementation
                from macros.fn_macro import fn_preprocessing
                fn_preprocessing(ctx)

        @self.macros.add("param")
        def param_handler(ctx: MacroContext):
            # TODO: Use dependency injection version if available
            from macro_base import di_registry
            if di_registry.has_macro("param"):
                instance = di_registry.get_instance("param")
                instance.preprocess(ctx)
            else:
                # Fallback to old implementation
                from macros.fn_macro import param_preprocessing
                param_preprocessing(ctx)

        @self.macros.add("a", "an", "access")
        def access_handler(ctx: MacroContext):
            # TODO: Use dependency injection version if available
            from macro_base import di_registry
            if di_registry.has_macro("access"):
                instance = di_registry.get_instance("access")
                instance.preprocess(ctx)
            else:
                # Fallback to old implementation
                from macros.access_macros import access_preprocessing
                access_preprocessing(ctx)
        
    def process_node(self, ctx: MacroContext) -> None:
        """Process a single node using the preprocessor registry"""
        default_logger.macro(f"preprocessing node: {ctx.node.content}")
        
        # Validate indentation: ensure content doesn't start with whitespace
        if ctx.node.content and ctx.node.content[0].isspace():
            from error_types import ErrorType
            ctx.compiler.compile_error(ctx.node, 
                "this language only accepts tabs for indentation, not spaces! spaces are like, totally uncool. use tabs instead, they're way more precise and semantic.", 
                ErrorType.INVALID_INDENTATION)
            # Don't return early - let the processing continue so we don't break the pipeline
        
        # Process children first
        with default_logger.indent("macro", f"preprocessing children of {ctx.node.content}"):
            for i, child in enumerate(ctx.node.children):
                with default_logger.indent("macro", f"child {i}: {child.content}"):
                    with ctx.compiler.safely:
                        child_ctx = replace(ctx, node=child)
                        self.process_node(child_ctx)
        
        # Process current node  
        macro = str(ctx.compiler.get_metadata(ctx.node, Macro))
        all_preprocessors = self.macros.all()
        
        if macro in all_preprocessors:
            default_logger.macro(f"applying preprocessor for macro: {macro}")
            # print(f"macro for {ctx.node.content} seems to be {macro}")
            with ctx.compiler.safely:
                all_preprocessors[macro](ctx)
        else:
            default_logger.macro(f"no preprocessor for macro: {macro}")