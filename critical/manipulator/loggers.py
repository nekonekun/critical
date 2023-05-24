import logging
from rich.logging import RichHandler, Console

FORMAT = '<%(name)s> %(message)s'


def customize_logger(level_name: str = 'WARN', format_: str = FORMAT) -> None:
    logging.basicConfig(format=format_,
                        datefmt="[%X]",
                        handlers=[RichHandler(omit_repeated_times=False,
                                              console=Console(width=120))])
    logging.getLogger('critical').setLevel(level_name)


consumers_logger = logging.getLogger('critical.consumer')
filters_logger = logging.getLogger('critical.filter')
formatters_logger = logging.getLogger('critical.formatter')
handlers_logger = logging.getLogger('critical.handler')
main_logger = logging.getLogger('critical.main')
middlewares_logger = logging.getLogger('critical.middleware')
senders_logger = logging.getLogger('critical.sender')
