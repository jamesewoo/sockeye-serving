import os

from .sockeye_handler import SockeyeHandler
from .text_processor import ChineseCharPreprocessor, Detokenizer


class ChineseHandler(SockeyeHandler):
    """
    Consumes Chinese text of arbitrary length and returns its translation.
    """

    def initialize(self, context):
        super().initialize(context)
        scripts_path = os.path.join(self.basedir, 'scripts')
        self.preprocessor = ChineseCharPreprocessor(scripts_path)
        self.postprocessor = Detokenizer(scripts_path)


_service = ChineseHandler()


def handle(data, context):
    return _service.handle(data, context)
