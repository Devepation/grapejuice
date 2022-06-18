# Getting started with a contribution

There's a lot of things that need work in Grapejuice, such as:

- translations
- documentation
- writing code

Instructions for contributing to each part are listed below. They assume that you know how to make a merge request. [Here's some information](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html) if you're not sure how to.

## Translations

**Note:** The documentation is currently not translated.

To get started translating, first go to the Grapejuice repository and go to `src/grapejuice_common/assets/po`.

Afterwards, find the code for the language. For example, English is `en`.

If the language you want to add isn't there, follow the below instructions:

1. Run `xgettext --files-from=POTFILES.in --directory=../../../.. --output=[language code].po`.
2. Add the abbreviated language code to the `LINGUAS` file.

Now edit `[language code].po`. You can use a tool like [gtranslator](https://pkgs.org/search/?q=gtranslator) or edit the file with a text editor.

Afterwards, test your translations by installing Grapejuice from source. Once you confirm that Grapejuice looks correct, create a merge request!

## Documentation

Documentation is located in `documentation/src/docs`. It should be relatively easy to make your changes there.

To see your changes, do the following steps:

1. Install `python-virtualenv`.
2. Run `cd documentation`.
3. Run `make` and install the missing dependencies listed.
4. Run `make dist`.
5. Run `make serve`.

## Writing code

The code is organized into different directories in the `src` directory. In general:

- `grapejuice` handles GUI stuff.
- `grapejuice_common` manages Wine, configuration, updates, and logging.
- `grapejuiced` is the Grapejuice daemon, which is usually not used.
- `grapejuice_packaging` creates the Grapejuice packages and also installs Grapejuice locally.
