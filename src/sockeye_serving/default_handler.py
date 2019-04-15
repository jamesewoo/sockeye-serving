import pkg_resources

from .sockeye_handler import SockeyeHandler
from .text_processor import Detokenizer, JoshuaPreprocessor


class DefaultHandler(SockeyeHandler):
    """
    Consumes text of arbitrary length and returns its translation.
    """

    def initialize(self, context):
        super().initialize(context)
        scripts_path = pkg_resources.resource_filename('sockeye_serving', 'scripts')
        # get the language from the model name
        lang = context.model_name
        self.preprocessor = JoshuaPreprocessor(scripts_path, lang)
        self.postprocessor = Detokenizer(scripts_path)


_service = DefaultHandler()


def handle(data, context):
    return _service.handle(data, context)
