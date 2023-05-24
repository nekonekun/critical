from critical.manipulator.formatters import CopyFieldFormatter
from critical.manipulator.formatters import SimpleMailFormatter


def test_copy_filed(composer):
    formatter = CopyFieldFormatter('short_message')
    gelf = composer.gelf()
    formatter_output = formatter.format(gelf)
    assert formatter_output == gelf.short_message

    formatter = CopyFieldFormatter('_full_message')
    gelf = composer.gelf()
    formatter_output = formatter.format(gelf)
    assert formatter_output == gelf.full_message_

    formatter = CopyFieldFormatter('full_message_')
    gelf = composer.gelf()
    formatter_output = formatter.format(gelf)
    assert formatter_output == gelf.full_message_

    formatter = CopyFieldFormatter.from_dict({'field': 'full_message_'})


def test_simple_main(composer):
    formatter = SimpleMailFormatter(subject_field='short_message',
                                    body_field='short_message')
    gelf = composer.gelf()
    formatter_output = formatter.format(gelf)
    assert formatter_output.startswith('Subject: ')
    assert len(formatter_output.split('\n')) >= 3

    formatter = SimpleMailFormatter(subject_field='gl2_remote_ip_',
                                    body_field='full_message_')
    gelf = composer.gelf()
    formatter_output = formatter.format(gelf)
    assert formatter_output.startswith('Subject: ')
    assert len(formatter_output.split('\n')) >= 3

    formatter = SimpleMailFormatter.from_dict({'subject_field': 'short_message',
                                               'body_field': 'short_message'})
    formatter_output = formatter.format(gelf)
    assert formatter_output.startswith('Subject: ')
    assert len(formatter_output.split('\n')) >= 3
