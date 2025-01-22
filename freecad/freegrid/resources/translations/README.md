# About translating FreeGrid Workbench

> [!NOTE]
> All commands **must** be run in `./freecad/freegrid/resources/translations/` directory.

> [!IMPORTANT]
> If you want to update/release the files you need to have installed
> `lupdate` and `lrelease` from **Qt6** version. Using the versions from
> Qt5 is not advised because they're buggy.

| language | translated strings | completion |
|:----|:----:|:-----:|
|de|16|12%|
|el|23|18%|
|es-AR|126|100%|
|es-ES|126|100%|
|fr|11|8%|
|it|16|12%|
|pl|61|48%|
|sv-SE|11|8%|

## Updating translations template file

To update the template file from source files you should use this command:

```shell
./update_translation.sh -u
```

Once done you can commit the changes and upload the new file to CrowdIn platform
at <https://crowdin.com/project/freecad-addons> webpage and find the **FreeGrid** project.

## Creating file for missing locale

### Using script

To create a file for a new language with all **FreeGrid** translatable strings execute
the script with `-u` flag plus your locale:

```shell
./update_translation.sh -u ja
```

### Renaming file

Also you can rename new `FreeGrid.ts` file by appending the locale code,
for example, `FreeGrid_ja.ts` for Japanese and change

```xml
<TS version="2.1">
```

to

```xml
<TS version="2.1" language="ja" sourcelanguage="en">
```

As of 2024/10/28 the supported locales on FreeCAD
(according to `FreeCADGui.supportedLocales()`) are 44:

```python
{'English': 'en', 'Afrikaans': 'af', 'Arabic': 'ar', 'Basque': 'eu',
'Belarusian': 'be', 'Bulgarian': 'bg', 'Catalan': 'ca',
'Chinese Simplified': 'zh-CN', 'Chinese Traditional': 'zh-TW', 'Croatian': 'hr',
'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl', 'Filipino': 'fil', 'Finnish': 'fi',
 'French': 'fr', 'Galician': 'gl', 'Georgian': 'ka', 'German': 'de', 'Greek': 'el',
 'Hungarian': 'hu', 'Indonesian': 'id', 'Italian': 'it', 'Japanese': 'ja',
 'Kabyle': 'kab', 'Korean': 'ko', 'Lithuanian': 'lt', 'Norwegian': 'no',
 'Polish': 'pl', 'Portuguese': 'pt-PT', 'Portuguese, Brazilian': 'pt-BR',
 'Romanian': 'ro', 'Russian': 'ru', 'Serbian': 'sr', 'Serbian, Latin': 'sr-CS',
 'Slovak': 'sk', 'Slovenian': 'sl', 'Spanish': 'es-ES', 'Spanish, Argentina': 'es-AR',
'Swedish': 'sv-SE', 'Turkish': 'tr', 'Ukrainian': 'uk', 'Valencian': 'val-ES',
'Vietnamese': 'vi'}
```

## Translating

To edit your language file open your file in `Qt Linguist` from `qt5-tools`/`qt6-tools`
package or in a text editor like `xed`, `mousepad`, `gedit`, `nano`, `vim`/`nvim`,
`geany` etc. and translate it.

Alternatively you can visit the **FreeCAD-addons** project on CrowdIn platform
at <https://crowdin.com/project/freecad-addons> webpage and find your language,
once done, look for the **FreeGrid** project.

## Finding potential typos

You can use the `aspell` command along with `awk` to potentially find some typos on the translation.
Also you need to install the language package, `aspell-es` for Spanish.

```sh
awk 'BEGIN { RS="</translation>" } /<translation>/ { sub(/.*<translation>/, ""); print }' \
  STEMFIE_es-ES.ts | aspell --lang=es list | sort | uniq
```

## Compiling translations

To convert all `.ts` files to `.qm` files (merge) you can use this command:

```shell
./update_translation.sh -R
```

If you are a translator that wants to update only their language file
to test it on **FreeCAD** before doing a PR you can use this command:

```shell
./update_translation.sh -r ja
```

This will update the `.qm` file for your language (Japanese in this case).

## Sending translations

Now you can contribute your translated `.ts` file to **FreeGrid** repository,
also include the `.qm` file.

<https://github.com/instancezero/in3dca-freegrid>

## More information

You can read more about translating external workbenches here:

<https://wiki.freecad.org/Translating_an_external_workbench>
