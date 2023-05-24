from critical.manipulator.formatters import CopyFieldFormatter


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
