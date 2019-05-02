import os

import pytest
from mms.context import Context

from sockeye_serving import sockeye_handler, default_handler, ko_handler, zh_handler


@pytest.fixture
def my_ctx():
    model_dir = os.path.join(os.path.dirname(__file__), 'resources')
    return Context(model_name='test',
                   model_dir=model_dir,
                   manifest='manifest',
                   batch_size=1,
                   gpu=0,
                   mms_version='1.0.3')


def check_initialize(handler: sockeye_handler.SockeyeHandler, context: Context):
    handler.initialize(context)
    assert handler.initialized
    assert handler.translator
    assert handler.preprocessor
    assert handler.postprocessor


def test_default_handler(my_ctx):
    check_initialize(default_handler.DefaultHandler(), my_ctx)


def test_ko_handler(my_ctx):
    check_initialize(ko_handler.KoreanHandler(), my_ctx)


def test_zh_handler(my_ctx):
    check_initialize(zh_handler.ChineseHandler(), my_ctx)
