import FreeCAD

if FreeCAD.GuiUp:
    from PySide.QtCore import QT_TRANSLATE_NOOP
    from FreeCAD.Qt import translate
else:

    def QT_TRANSLATE_NOOP(context: str, source_text: str) -> str:
        """Dummy function to mark strings for translation without actually translating them."""
        return source_text

    def translate(context: str, source_text: str, disambiguation: str = None) -> str:
        """
        Translate a text string.

        Arguments:
            context: The context in which the text appears.
            source_text: The text to translate.
            disambiguation (optional): A comment for the translator.

        Returns:
            str: The translated text.
        """
        return source_text
