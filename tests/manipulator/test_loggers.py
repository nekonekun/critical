from critical.manipulator.loggers import customize_logger
import logging


def test_customize_logger():
    logger = logging.getLogger('critical')
    customize_logger('DEBUG')
    assert logger.level == 10
    customize_logger('INFO')
    assert logger.level == 20
    customize_logger(level_name='WARN',
                     format_='No information, just log entry')
    assert logger.level == 30
