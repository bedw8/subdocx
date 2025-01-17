# subdocx - replace values of a `docx` document systematically 

The purpose of this is to ease the generation of documents from templates, substituing specified variable keywords with custom values, *keeping the original format of the document*.   

Concept:


Features:
- Substitute variables with custom values, without altering the sentences format and styles. This mean original font, font size, font style (bold, italic, underline), font color, highlighting, etc., are preserved.   
- Handles every piece of text in a document, including tables and *text frames*.
- It allows users to specify the substitution text format. E.g: substituing a document variable with `datetime` object with custom `strftime` format or any other custom python function.
- If wanted, each variable can be subtitued on multiple parts of the document with different formats on  
- It provides a way to generate different documents from variables named similarly, with a specified pattern (With an input like `{name='Bob', payment_1='100', payment_2='200'}` it would generate *two* documents. One for each Bob's payments).
- It provides an easy way to generate multiple documents from a Pandas DataFrame containing the values to be sustituted.
- It provides a way to define how the files will be named, enabling users to define custom naming schema from data variables. E.g: The data `{name='Bob', payment_1='100', payment_2='200'}` with a naming schema of `Payment_Receipt_{name}` would end with files named `Payment_Receipt_Bob_1.docx` and `Payment_Receipt_Bob_2.docx`

### Similar projects
- python-docx-replace

```
